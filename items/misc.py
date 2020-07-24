import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate

class Misc(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ Misc Cog loaded")

    @commands.command()
    async def feed(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        if data is None:
            return await ctx.send("You haven't initialized your inventory yet.")

        inventory = data["inventory"]

        found = False
        for i in inventory:
            if i["name"] == "Dragon":
                found = True

        if not found:
            return await ctx.send("You don't have a :dragon: **Dragon** in your inventory.")

        found = False
        for i in inventory:
            if i["name"] == "Frog":
                found = True
                if i["quantity"] == 1:
                    inventory.remove(i)
                else:
                    i["quantity"] -= 1

        if not found:
            return await ctx.send("You don't have a :frog: **Frog** in your inventory.")

        if random.randint(0, 100) != 50:
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            return await ctx.send("You fed a :frog: **Frog** to your :dragon: **Dragon**.")

        embed = discord.Embed(title=":tada: Your :dragon: **Dragon** evolved into an <:reddragon:733766679036952646> **Evolved Dragon**", description="The chances of this event occuring are 1% - Well done!", color=discord.Color.green())
        await ctx.send(embed=embed)

        locked = False

        for i in inventory:
            if i["name"] == "Dragon":
                if ["locked"]:
                    locked = True
                if i["quantity"] == 1:
                    inventory.remove(i)
                else:
                    i["quantity"] -= 1

        items = await self.bot.items.find("items")
        items = items["items"]
        item = items["evolveddragon"]

        name, emoji = item["name"], item["emoji"]

        given = False
        for i in inventory:
            if i["name"] == name:
                i["quantity"] += 1
                given = True

        if not given:
            del item["emoji"], item["value"], item["description"], item["rarity"]
            item["locked"] = locked
            item["quantity"] = 1
            inventory.append(item)

        await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})

    @commands.command()
    async def avatar(self, ctx, user):
        if len(ctx.message.mentions) == 0:
            try:
                user = self.bot.get_user(int(user))
                if user is None:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            except ValueError:
                return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
        else:
            user = ctx.message.mentions[0]

        embed = discord.Embed(title=f"**{user.name}'s** Avatar", color=discord.Color.dark_blue())
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    @avatar.error
    async def avatar_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(title=f"**{ctx.author.name}'s** Avatar", color=discord.Color.dark_blue())
            embed.set_image(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def _8Ball(self, ctx, *, question=None):
        if not question:
            return await ctx.send(":8ball: **8Ball:** Well that's cool but you actually have to ask something.")
        responses = ["Outlook unclear, try again later", "Sorry m8, try again", "mhm", "I don't know, you tell me", "lol", "Absolutely!", "Absolutely not!", "It's a yes from me", "It's a no from me", "Do what Jesus would do", "Nahhhh", "Sure I guess...", "It's plausible", "I don't think you'll like the answer...", "I think it's best I spare you of the truth."]
        wisdom = random.choice(responses)
        await ctx.send(f":8ball: **8Ball:** {wisdom}")

    @commands.command()
    async def frogtop(self, ctx):
        data = await self.bot.inventories.get_all()
        first, second, third, fourth, fifth = {}, {}, {}, {}, {}
        all = {}
        for item in data:
            for i in item["inventory"]:
                if i["name"] == "Frog":
                    all[item["_id"]] = i["quantity"]

        all = sorted(all.items(), key=lambda k: k[1], reverse=True)

        try:
            first_user = self.bot.get_user(int(all[0][0]))
        except IndexError:
            first_user = None

        try:
            second_user = self.bot.get_user(int(all[1][0]))
        except IndexError:
            second_user = None

        try:
            third_user = self.bot.get_user(int(all[2][0]))
        except IndexError:
            third_user = None

        try:
            fourth_user = self.bot.get_user(int(all[3][0]))
        except IndexError:
            fourth_user = None

        try:
            fifth_user = self.bot.get_user(int(all[4][0]))
        except IndexError:
            fifth_user = None

        entries = []

        try:
            entries.append(["1st", first_user, all[0][1]])
        except IndexError:
            pass

        try:
            entries.append(["2nd", second_user, all[1][1]])
        except IndexError:
            pass

        try:
            entries.append(["3rd", third_user, all[2][1]])
        except IndexError:
            pass

        try:
            entries.append(["4th", fourth_user, all[3][1]])
        except IndexError:
            pass

        try:
            entries.append(["5th", fifth_user, all[4][1]])
        except IndexError:
            pass


        output = ("```" + tabulate(entries, tablefmt="simple", headers=["#", "Player", "Amount"]) + "```")
        embed = discord.Embed(title=":frog: Most Frogs:", description=output, color=discord.Color.gold())
        await ctx.send(embed=embed)

    @frogtop.error
    async def frogtop_error(self, ctx, error):
        self.bot.errors += 1
        self.bot.important_errors += 1
        embed = discord.Emebd(title=":x: Leaderboard Error", description="There was an error fetching infortmation. If you wish, you may [report this](https://discord.gg/zAZ3vKJ).")
        await ctx.send(embed=embed)

    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- FIND ---------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def find(self, ctx, *, item):
        data = await self.bot.inventories.get_all()
        first, second, third, fourth, fifth = {}, {}, {}, {}, {}
        all = {}
        items = await self.bot.items.find("items")
        items = items["items"]
        item = item.replace(" ", "").lower()
        if item not in items:
            return await ctx.send("That item does not exist.\n**Tip:** Items in commands generally don't contain spaces!")
        item = items[item]
        name, emoji = item["name"], item["emoji"]

        for item in data:
            for i in item["inventory"]:
                if i["name"] == name:
                    all[item["_id"]] = i["quantity"]

        all = sorted(all.items(), key=lambda k: k[1], reverse=True)
        entries = []
        count = 0
        while True:
            try:
                rand = random.choice(all)
            except IndexError:
                entries.append(["None", 0, 0])
                break
            user = self.bot.get_user(int(rand[0]))
            if user != None:
                found = False
                for i in entries:
                    if i[2] == user.id:
                        found = True
                        count -= 1

                if not found:
                    entries.append([user, rand[1], user.id])
            else:
                count -= 1
            count += 1

            if count >= len(all) or count > 4:
                break

        output = ("```" + tabulate(entries, tablefmt="simple", headers=["Player", "Amount", "User ID"]) + "```")
        embed = discord.Embed(title=f"{emoji} Owners of {name}s:", description=output, color=discord.Color.gold())
        await ctx.send(embed=embed)

    @find.error
    async def find_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f"Usage: `{self.bot.prefix}find (item)`")


    # --------------------------------------------------------------------------
    # ----- COMMAND: -----------------------------------------------------------
    # ----- BEG ----------------------------------------------------------------
    # --------------------------------------------------------------------------

    @commands.command()
    async def beg(self, ctx):
        data = await self.bot.inventories.find(ctx.author.id)
        user = ctx.author
        if data["job"] is None:
            nojob = discord.Embed(title=f":dollar:  {user.name} is begging for money!", description=f"I think {user.name} should get a job! Do `,jobs` for more infortmation!", color=discord.Color.gold())
            await ctx.send(embed=nojob)
        else:
            hasjob = discord.Embed(title=f":dollar:  {user.name} is begging for money!", description=f"I think {user.name} should do their job! Do `,work` to work!", color=discord.Color.gold())
            await ctx.send(embed=hasjob)


def setup(bot):
    bot.add_cog(Misc(bot))
