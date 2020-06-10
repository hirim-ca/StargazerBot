import discord
from discord.ext import commands
import asyncio
import re

import json
import pandas as pd
import numpy as np

import utils


class Backdoor(commands.Cog):
    """ Backdoor modlue that provides managerial and datamining functions. """

    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    async def getMessageInChannel(self, ctx, *args):
        """ 
        Export all messages in the specified channel to output.
        Usage: [prefix]getMessageInChannel [#channel] [limit] [output path]
        Generates a csv file in the specified output path.
        """

        if not await self.bot.is_owner(ctx.author):
            await ctx.send("You must be a developer to use that function.")
            return


        channel_id = int(re.search(r'<#(.*)>', args[0]).group(1))
        channel = self.bot.get_channel(channel_id)
        if int(args[1]) == -1:
            limit = None
        else:
            limit = int(args[1])
        output_path = self.bot.output_path + args[2]

        if channel:
            # prepare data

            await ctx.send(f"Getting messages from <#{ channel_id }>.")

            msgs = await channel.history(limit=limit).flatten()
            
            def parse_msg():
                for msg in msgs:
                    embed_astext = ""
                    for embed in msg.embeds:
                        embed_astext += json.dumps(embed.to_dict())

                    attachments = list(map(lambda x: x.url, msg.attachments))
                    attachment_urls = ",".join(attachments)

                    yield msg.id, msg.author.id, msg.created_at, msg.content, embed_astext, attachment_urls

            output = pd.DataFrame(parse_msg(), columns=["message_id", "author_id", "created_at", 
                                           "content", "embed", "attachment_urls"])
                
            # export data

            output = output.set_index("message_id")

            try:
                output.to_csv(output_path)
                await ctx.send(f"<@{ ctx.author.id }> Channel messages exported to { output_path }.")

            except Exception as ex:
                await ctx.send(f"Export failed, reason:\n`{ ex }`")
                return

        else:
            await ctx.send("Channel not found.")
        
    @commands.command()
    async def dbStatus(self, ctx):
        """ Check the status of the database. Sends status to ctx. """

        if not await self.bot.is_owner(ctx.author):
            await ctx.send("You must be a developer to use that function.")
            return

        self.bot.db.connect()

        if self.bot.db.conn:
            await ctx.send(f"Connected to { self.bot.db.host }, port { self.bot.db.port }.")
        else:
            await ctx.send("Database is offline.")

        self.bot.db.closeConn()

    @commands.command()
    async def clearChannel(self, ctx, *args):
        """ 
        Purge all messages from channel specified
        Usage: clearChannel [#channel] [limit]
        """

        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You must be a admin to use that function.")
            return

        channel_id = int(re.search(r'<#(.*)>', args[0]).group(1))
        channel = self.bot.get_channel(channel_id)
        if int(args[1]) == -1:
            limit = None
        else:
            limit = int(args[1])

        if channel:

            await ctx.send(f"Purging channel <#{ channel_id }>. (Might take a while)")

            msgs = await channel.history(limit=limit).flatten()
            
            for msg in msgs:
                await msg.delete()

            await ctx.send(f"<@{ctx.author.id}> Channel <#{ channel_id }> purged successfully.")

        else:
            await ctx.send("Channel not found.")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, msg):
        """ Disable this function if you are sane, will you? """
        
        server = self.bot.get_guild(msg.guild_id)
        owner = self.bot.get_user(self.bot.owner_id)

        if (owner in server.members):
            if msg.cached_message and not msg.cached_message.author.bot:
                await owner.send(f"A message was deleted in **{ server.name }**:", embed=utils.createEmbed(msg.cached_message))

def setup(bot):
    bot.add_cog(Backdoor(bot))