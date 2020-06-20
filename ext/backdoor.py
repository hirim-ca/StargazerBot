import discord
from discord.ext import commands
import asyncio

import utils

class Backdoor(commands.Cog):
    """ Module that contains owner only commands to monitor and control the runtime status of the bot. """

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.is_owner()
    async def stExit(self, ctx):
        """ Force the bot to shutdown. """

        await ctx.send("Bot shutting down.")
        await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def dbStat(self, ctx):
        """ Check the status of the database. Sends status to ctx. """

        self.bot.db.connect()

        if self.bot.db.conn:
            await ctx.send(f"Connected to database.")
        else:
            await ctx.send("Database is offline.")

        self.bot.db.closeConn()


def setup(bot):
    bot.add_cog(Backdoor(bot))