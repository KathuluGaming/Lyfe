import discord, platform, datetime, logging, random
from discord.ext import commands
import platform, datetime
from pathlib import Path
cwd = Path(__file__).parents[1]
cwd = str(cwd)
import utils.json
from tabulate import tabulate

class Playershops(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("+ PlayerShops Cog loaded")

    @commands.command(aliases=['playershops', 'pshops', 'playershop'])
    async def pshop(self, ctx, argument=None, item=None, cq=None, cq2=None):
        entries = []

        # ADD

        if argument == "add":
            if item is None or cq is None:
                return await ctx.send(f"Usage: `{self.bot.prefix}pshop add (item) (cost) [quantity]`")

            data = await self.bot.inventories.find(ctx.author.id)
            items = await self.bot.items.find("items")
            items = items["items"]

            if item.lower() not in items:
                return await ctx.send("That item does not exist.")

            item = items[item.lower()]
            name, emoji = item["name"], item["emoji"]

            try:
                if cq2 is None:
                    cq2 = 1
                quantity = int(cq2)
            except Exception:
                return await ctx.send("Please enter a valid quantity.\n**Tip:** Items in commands generally don't contain spaces!")

            inventory = data["inventory"]
            found = False
            for i in inventory:
                if i["name"] == name:
                    if i["locked"] is True:
                        return await ctx.send(f"{emoji} **{name}** is locked in your inventory.")
                    if i["quantity"] < quantity:
                        return await ctx.send(f"You don't have that many {emoji} **{name}s**.")
                    i["quantity"] -= quantity
                    if i["quantity"] == 0:
                        inventory.remove(i)
                    found = True
            if not found:
                return await ctx.send(f"You don't have {emoji} **{name}** in your inventory.")

            try:
                price = int(cq)
            except Exception:
                return await ctx.send("Please enter a valid price.\n**Tip:** Items in commands generally don't contain spaces!")

            data = await self.bot.playershops.find(ctx.author.id)
            if data is None:
                shop = []
            else:
                shop = data["shop"]
                for i in shop:
                    if i["item"] == name.replace(" ", "").lower():
                        return await ctx.send("You already have that listed in your shop.")

            shop.append({"item": name.replace(" ", "").lower(), "price": price, "stock": quantity})
            await self.bot.playershops.upsert({"_id": ctx.author.id, "shop": shop})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})
            await ctx.send(f"Added **{quantity} {emoji} {name}s**  to your shop.")

        # REMOVE

        elif argument == "remove":
            if item is None:
                return await ctx.send(f"Usage: `{self.bot.prefix}pshop remove (item)`")

            items = await self.bot.items.find("items")
            items = items["items"]

            if item.lower() not in items:
                return await ctx.send("That item does not exist.")

            item = items[item.lower()]
            name, emoji = item["name"], item["emoji"]

            data = await self.bot.playershops.find(ctx.author.id)
            if data is None:
                return await ctx.send("You don't have a shop.")

            shop = data["shop"]
            found = False
            for i in shop:
                if i["item"] == name.replace(" ", "").lower():
                    quantity = i["stock"]
                    shop.remove(i)
                    found = True
            if not found:
                return await ctx.send(f"You aren't selling {emoji} **{name}**")

            player_data = await self.bot.inventories.find(ctx.author.id)
            inventory = player_data["inventory"]

            found = False
            for i in inventory:
                if i["name"] == name:
                    i["quantity"] += quantity
                    found = True

            if not found:
                del item["emoji"], item["value"], item["description"], item["rarity"]
                item["locked"] = False
                item["quantity"] = quantity
                inventory.append(item)

            await ctx.send(f"Removed {emoji} **{name}** from your shop.")
            if len(shop) == 0:
                await self.bot.playershops.delete(ctx.author.id)
            else:
                await self.bot.playershops.upsert({"_id": ctx.author.id, "shop": shop})

            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": inventory})


        # BUY

        elif argument == "buy": # ,pshop buy 1231231 shoppingcart 1
            if item is None or cq is None:
                return await ctx.send(f"Usage: `{self.bot.prefix}pshop buy (user) (item) [quantity]`")

            user = item
            if len(ctx.message.mentions) == 0:
                try:
                    if self.bot.get_user(int(user)) == None:
                        return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
                    else:
                        user = self.bot.get_user(int(user))
                except ValueError:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            else:
                user = ctx.message.mentions[0]

            user_shop_data = await self.bot.playershops.find(user.id)
            if user_shop_data is None:
                return await ctx.send("This user doesn't have a shop.")

            if user == ctx.author:
                return await ctx.send("That's pointless.")

            shop = user_shop_data["shop"]

            item = cq
            try:
                if cq2 is None:
                    cq2 = 1
                quantity = int(cq2)
            except Exception:
                return await ctx.send("Please enter a valid quantity.\n**Tip:** Items in commands generally don't contain spaces!")

            item = item.replace(" ", "").lower()
            items = await self.bot.items.find("items")
            items = items["items"]
            if item not in items:
                return await ctx.send("That item does not exist.")
            item = items[item]
            name, emoji = item["name"], item["emoji"]

            raw_name = item["name"].replace(" ", "").lower()

            found = False
            for i in shop:
                if i["item"] == raw_name:
                    price = i["price"]
                    stock = i["stock"]
                    found = True
            if not found:
                return await ctx.send(f"**{user}** is not selling a {emoji} **{name}")

            user_data = await self.bot.inventories.find(user.id)
            user_inventory = user_data["inventory"]
            user_balance = user_data["balance"]


            if quantity > stock:
                return await ctx.send(f"That quantity is too great. There aren't that many for sale.")

            author_data = await self.bot.inventories.find(ctx.author.id)
            if author_data is None:
                return await ctx.send("I'm suprised you made it this far without initializing your inventory. Go do that though.")
            author_inventory = author_data["inventory"]
            author_balance = author_data["balance"]
            if author_balance < price * quantity:
                return await ctx.send(f"$`{price * quantity}` is required to purchase this. You only have $`{author_balance}` and need another $`{price * quantity - author_balance}` to afford this.")

            # Set balances
            author_balance -= int(price * quantity)
            user_balance += int(price * quantity)

            # Set buyer's inventory
            given = False
            for i in author_inventory:
                if i["name"] == name:
                    i["quantity"] += 1
                    given = True

            if not given:
                del item["emoji"], item["value"], item["description"], item["rarity"]
                item["locked"] = False
                item["quantity"] = 1
                author_inventory.append(item)

            # Change shop
            for i in shop:
                if i["item"] == raw_name:
                    i["stock"] -= quantity
                    if i["stock"] == 0:
                        shop.remove(i)

            embed = discord.Embed(title=f"Purchase Successful", description=f"Purchased: {emoji} **{name}**\nQuantity: `{quantity}`\nMoney spent: $`{price * quantity}`\nNew balance: $`{author_balance}`", color=discord.Color.gold())
            await self.bot.inventories.upsert({"_id": ctx.author.id, "inventory": author_inventory})
            await self.bot.inventories.upsert({"_id": ctx.author.id, "balance": author_balance})
            await self.bot.inventories.upsert({"_id": user.id, "balance": user_balance})
            if len(shop) == 0:
                await self.bot.playershops.delete(user.id)
            else:
                await self.bot.playershops.upsert({"_id": user.id, "shop": shop})
            await ctx.send(embed=embed)


        # SPECIFIC

        elif argument == "show" or argument == "view":
            if item is None:
                user = ctx.author
            elif len(ctx.message.mentions) == 0:
                try:
                    if self.bot.get_user(int(item)) == None:
                        return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
                    else:
                        user = self.bot.get_user(int(item))
                except ValueError:
                    return await ctx.send("I couldn't find that user.\n**Tip:** Mention them or use their id.")
            else:
                user = ctx.message.mentions[0]

            data = await self.bot.inventories.find(user.id)
            inventory = data["inventory"]

            data = await self.bot.playershops.find(user.id)
            if data is None:
                return await ctx.send("This user doesn't have a shop.")

            items = await self.bot.items.find("items")
            items = items["items"]

            shop = data["shop"]
            for i in shop:
                entries.append([items[i["item"]]["name"], f'${i["price"]}', i["stock"]])

            if entries == []:
                entries.append(["OUT", "OF", "STOCK"])

            output = ("```" + tabulate(entries, tablefmt="simple", headers=["Item", "Price", "Stock"]) + "```")
            embed = discord.Embed(title=f":shopping_cart: **{user.name}'s** Shop", description=output, color=discord.Color.gold())
            await ctx.send(embed=embed)


        # SHOW ALL

        else:
            shops = await self.bot.playershops.get_all()
            if shops == []:
                entries.append(["None", 0, 0])
                output = ("```" + tabulate(entries, tablefmt="simple", headers=["Player", "Items", "User ID"]) + "```")
                embed = discord.Embed(title=f":shopping_cart: Player Shops:", description=output, color=discord.Color.gold())
                return await ctx.send(embed=embed)
            else:
                for i in shops:
                    id = i["_id"]
                    user = self.bot.get_user(id)
                    if user is None:
                        return ctx.send("Finding the user failed.")
                    stock = len(i["shop"])
                    entries.append([user, stock, int(id)])

                output = ("```" + tabulate(entries, tablefmt="simple", headers=["Player", "Items", "User ID"]) + "```")
                embed = discord.Embed(title=f":shopping_cart: Player Shops:", description=output, color=discord.Color.gold())
                return await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Playershops(bot))