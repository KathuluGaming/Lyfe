import asyncio, utils.functions
from asyncinit import asyncinit
from classes.inventory import Inventory
from classes.bank import Bank

@asyncinit
class User:

    async def __init__(self, id):
        await self.define(id)

    async def define(self, id):
        user = bot.get_user(id)
        # Extending discord.User stopped working for no reason so you'll need
        # to access it by using self.discord:
        self.discord = user
        self.inventory = await Inventory(user)
        self.balance = await utils.functions.getBalance(user)
        self.bank = await Bank(user)

    async def setup(self):
        item = await utils.functions.getItem("shoppingcart")
        await utils.functions.prepareItem(item)
        await bot.inventories.upsert({
            "_id": self.discord.id,
            "inventory": [item],
            "balance": 100,
            "bankbalance": 0,
            "banklimit": 0,
            "job": None,
            "titles": []
        })
        self.define(self.discord)

    async def update(self):
        await bot.inventories.upsert({
            "_id": self.discord.id,
            "inventory": self.inventory,
            "balance": self.balance,
            "bankbalance": self.bank.balance,
            "banklimit": self.bank.limit
        })
