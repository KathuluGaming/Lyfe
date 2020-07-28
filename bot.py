import discord, json, platform, logging, os, time, motor.motor_asyncio
from discord.ext import commands
from pathlib import Path

import utils.json
from utils.mongo import Document

cwd = Path(__file__).parents[0]
cwd = str(cwd)

secret_file = json.load(open(cwd+"/bot_config/secrets.json"))
prefix = secret_file["prefix"]

bot = commands.Bot(command_prefix=prefix, case_insensitive=True, owner_id=259740408462966786)
bot.remove_command("help")

bot.config_token = secret_file["token"]
bot.connection_url = secret_file["mongo"]
bot.prefix = prefix
bot.blacklisted_users = []
bot.upsince = time.time()
bot.maintenancemode = False
bot.whitelisted = []

bot.errors = 0
bot.important_errors = 0

@bot.event
async def on_ready():
    print(f"-----\n{bot.user.name} Online\n-----\nPrefix: {bot.prefix}\n-----")
    status = secret_file["status"]
    if status == "online":
        await bot.change_presence(activity=discord.Game(name=f"{bot.prefix}help in {len(bot.guilds)} servers"))
    elif status == "idle":
        await bot.change_presence(activity=discord.Game(name=f"{bot.prefix}help in {len(bot.guilds)} servers"), status=discord.Status.idle)
    elif status == "streaming":
        await bot.change_presence(activity=discord.Streaming(name=f"{bot.prefix}help", url="https://twitch.tv/discord"))

    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["lyfe"]
    if status == "online":
        bot.db = bot.mongo["lyfe"]
    elif status == "idle":
        bot.db = bot.mongo["lyfebeta"]
    else:
        bot.db = bot.mongo["lyfeaqua"]
    bot.inventories = Document(bot.db, "inventories")
    bot.items = Document(bot.db, "items")
    bot.trades = Document(bot.db, "trades")
    bot.playershops = Document(bot.db, "playershops")
    print("Initialized database\n-----")

@bot.event
async def on_message(message):
    # Ignore bots
    if message.author.id == bot.user.id or message.author.bot:
        return

    # Blacklist system
    if secret_file["status"] != "idle":
        if message.author.id in bot.blacklisted_users:
            return
    else:
        if message.author.id not in bot.whitelisted:
            return

    # Auto responses go here
    if bot.user.mentioned_in(message) and message.mention_everyone is False:
        try:
            if "help" in message.content.lower() or "info" in message.content.lower():
                await message.channel.send(f"My prefix is `{bot.prefix}`")
        except discord.Forbidden:
            pass

    await bot.process_commands(message)

if __name__ == '__main__':
    for file in os.listdir(cwd+"/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

bot.run(bot.config_token, reconnect=True)
