import discord
from discord.ext import commands
import asyncio
import re
import os
from datetime import datetime

import json
import pandas as pd
import numpy as np

from configparser import ConfigParser
import utils


class ServerData(commands.Cog):
    """ Serverdata modlue that provides log managerial and datamining functions. """

    def __init__(self, bot):
        self.bot = bot

        self.config = ConfigParser()
        self.config.read("config.ini")

        self.datatable_name = self.config.get("SERVERDATA", "DATATABLE_NAME")
        
    @commands.command()
    async def getMsg(self, ctx, *args):
        """ 
        Export all messages in the specified channel to output.
        Usage: [prefix]getMsg [#channel] [limit]
        Generates a csv file in the specified output path.
        """
        limit = int(args[1])

        if (limit == -1 or limit > 100) and not ctx.author.guild_permissions.administrator:
            await ctx.send("You must be a admin to use that limit.")
            return

        if limit == -1:
            limit = None


        channel_id = int(re.search(r'<#(.*)>', args[0]).group(1))
        channel = self.bot.get_channel(channel_id)

        output_path = self.bot.output_path + f"{ utils.getMd5(datetime.utcnow().timestamp) }" + ".csv"

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
                await ctx.send(f"<@{ ctx.author.id }> Here you go!", file=discord.File(output_path))
                os.remove(output_path)

            except Exception as ex:
                await ctx.send(f"Export failed, reason:\n`{ ex }`")
                return

        else:
            await ctx.send("Channel not found.")


    @commands.command()
    async def clChn(self, ctx, *args):
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

            await channel.purge(limit=limit)

            await ctx.send(f"<@{ctx.author.id}> Channel <#{ channel_id }> purged successfully.")

        else:
            await ctx.send("Channel not found.")


    @commands.command()
    async def getAc(self, ctx):
        """ Get or remove access to deleted messages in channel. """

        if not ctx.author.guild_permissions.administrator:
            await ctx.send("You must be a admin to user that function.")
            return

        in_list = self.bot.db.get(
            self.datatable_name,
            columns = ['user_id'],
            constraints = f"WHERE user_id = '{ ctx.author.id }' AND guild_id='{ ctx.guild.id }'"
        )

        if not in_list.empty:
            # remove

            self.bot.db.delete(
                self.datatable_name,
                constraints = f"WHERE user_id = '{ ctx.author.id }' AND guild_id='{ ctx.guild.id }'"
            )

            await ctx.send("Your access has been removed.")
            return

        else:
            # opt in

            self.bot.db.insert(
                self.datatable_name,
                user_id = f"'{ ctx.author.id }'", 
                guild_id = f"'{ ctx.guild.id }'"
            )

            await ctx.send("You have been granted access to deleted messages.")


    @commands.Cog.listener()
    async def on_raw_message_delete(self, msg):
        """ Default function called when a message is deleted. """
        
        # Sends the deleted message to admins with access previleges.

        server = self.bot.get_guild(msg.guild_id)
        owner = self.bot.get_user(self.bot.owner_id)

        access_admins = self.bot.db.get(
            self.datatable_name,
            columns = ['user_id'],
            constraints = f"WHERE guild_id='{ msg.guild_id }'"
        )

        users = access_admins['user_id'].map(lambda x: self.bot.get_user(int(x)))

        if msg.cached_message and not msg.cached_message.author.bot and not len(users):
            for user in users:
                await user.send(f"A message was deleted in **{ server.name }**:", embed=utils.createEmbed(msg.cached_message))


def setup(bot):
    bot.add_cog(ServerData(bot))