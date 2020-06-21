import glob
from configparser import ConfigParser

import asyncio
import discord
import utils
from discord.ext import commands


class StargazerBot(commands.Bot): 
    """ The Discord bot """

    def __init__(self, *args, **kwargs):
        print("Initializing StargazerBot")

        super().__init__(*args, **kwargs)
        self.name = kwargs.get("name")
        self.db = kwargs.get("db")
        self.output_path = kwargs.get("output_path")
        self.remove_command("help")

        print("Loading extentions...")
        for ext in glob.glob(kwargs.get("ext_path", "") + "*.py"):
            print("Loading " + ext)

            try:
                # linux regrex
                self.load_extension(ext.replace('/', '.')[:-3])
            except:
                # windows regrex
                self.load_extension(ext.replace('\\', '.')[:-3])

            print(ext + "loaded")

    def run(self, *args):
        """ Call this function to start the bot. """

        self.loop.run_until_complete(self.start(*args))


    # events

    async def on_ready(self):
        """ 
        The deafualt function called on startup.
        Displays fancy stuff about the bot.
        """

        await self.change_presence(activity=discord.Game(f"{ self.command_prefix }help"))
        print("Bot is ready.")


    async def on_message(self, message):
        """ The deafualt function called when a messeage is sent by user. """

        if message.author.bot:
            return

        if ":kyarushocked:" in message.content:
            # lol
            await message.channel.send("<:kyarushocked:705832784475717773>")

        await self.process_commands(message)
