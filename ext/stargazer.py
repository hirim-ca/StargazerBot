import re
from configparser import ConfigParser
from math import floor
from datetime import datetime
import pandas as pd
import numpy as np

import discord
from discord.ext import commands
import asyncio

import utils


class Stargazer(commands.Cog):
    """  
    Core module that manages the invaluable quotes nominated by users. 
    Contains the help command.
    """

    def __init__(self, bot):
 
        self.bot = bot

        self.config = ConfigParser()
        self.config.read("config.ini")

        self.star_reacts = self.config.get("STARGAZER", "STAR_REACT").split(' ')
        self.star_react_emoji = self.config.get("STARGAZER", "STAR_REACT_EMOJI")
        self.min_react = int(self.config.get("STARGAZER", "MIN_REACT"))
        self.star_tier_gap = int(self.config.get("STARGAZER", "STAR_TIER_GAP"))
        self.datatable_name = self.config.get("STARGAZER", "DATATABLE_NAME")
        self.highlight_colors = self.config.get("STARGAZER", "HIGHLIGHT_COLOR").split(' ')
        self.rank_limit = int(self.config.get("STARGAZER", "RANK_LIMIT"))


    @commands.Cog.listener()
    async def on_ready(self):
        """ 
        Called when module is ready.
        Sets the default starboard channel and highlight colors.
        """

        self.star_channel = self.bot.get_channel(int(self.config.get("STARGAZER", "STAR_CHANNEL")))

        for i, rgb in enumerate(self.highlight_colors):
            r, g, b = rgb.split(",")
            self.highlight_colors[i] = discord.Color.from_rgb(int(r), int(g), int(b))


    async def processStars(self, msg, deletion=False):
        """ 
        Called when a star reaction is added or removed.
        Process the message and sync information to database.
        msg: a discord.Message object
        deletion: check for special cases for reaction deletion.
        """

        # check if message send by bot
        if msg.author.bot:
            return

        reactions = msg.reactions
        reaction = None

        quote_indb = self.bot.db.get(
            self.datatable_name,
            columns = ["message_id", "embed_id", "legacy"],
            constraints=f"WHERE message_id='{ msg.id }'"
        )

        # check if lecacy, avoid if legacy
        if not quote_indb.empty and quote_indb.iloc[0]["legacy"]:
            return

        # check for reaction presence

        for reaction_iter in reactions:

            if utils.getEmojiName(reaction_iter.emoji) == self.star_react_emoji:
                reaction = reaction_iter
                break

        else:
            if deletion and not quote_indb.empty:
                embed = await self.star_channel.fetch_message(int(quote_indb.iloc[0]['embed_id']))
                await embed.delete()
                self.bot.db.delete(self.datatable_name, constraints=f"WHERE message_id='{ msg.id }'")

            return

        # update quote presence in server and db
        

        if quote_indb.empty and reaction.count >= self.min_react:
            # sends embed and upload quote to db

            embed = await self.star_channel.send(
                f":{ self.star_reacts[0] }: **{ reaction.count }**",
                embed=utils.createEmbed(msg, color=self.highlight_colors[0])
            )

            created_at = embed.created_at.strftime('%Y-%m-%d %H:%M:%S')

            self.bot.db.insert(
                self.datatable_name, 
                message_id = f"'{ msg.id }'",
                channel_id = f"'{ msg.channel.id }'",
                author_id = f"'{ msg.author.id }'",
                embed_id = f"'{ embed.id }'",
                created_at = f"'{ created_at }'",
                score = str(reaction.count)
            )

        elif not quote_indb.empty and reaction.count >= self.min_react:
            # update embed and db

            embed = await self.star_channel.fetch_message(int(quote_indb.iloc[0]['embed_id']))
            
            if floor(reaction.count / self.star_tier_gap) < len(self.star_reacts):
                embed_icon_id = self.star_reacts[floor(reaction.count / self.star_tier_gap)]
            else:
                embed_icon_id = self.star_reacts[-1]
            
            if floor(reaction.count / self.star_tier_gap) < len(self.highlight_colors):
                embed_color = self.highlight_colors[floor(reaction.count / self.star_tier_gap)]
            else:
                embed_color = self.highlight_colors[-1]


            await embed.edit(
                content=f":{ embed_icon_id }: **{ reaction.count }**",
                embed=utils.createEmbed(msg, color=embed_color)
            )

            self.bot.db.update(
                self.datatable_name, 
                constraints = f"WHERE message_id = '{ msg.id }'", 
                score = str(reaction.count)
            )

        elif not quote_indb.empty and deletion and reaction.count < self.min_react:
            # delete embed and remove record

            embed = await self.star_channel.fetch_message(int(quote_indb.iloc[0]['embed_id']))
            await embed.delete()
            self.bot.db.delete(self.datatable_name, constraints=f"WHERE message_id='{ msg.id }'")


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, reaction):
        """ 
        Called when a reaction is added.
        Checks if the reaction is star_reaction and processStar(msg) if it is.
        """
        
        emoji_name = utils.getEmojiName(reaction.emoji.name)

        if emoji_name == self.star_react_emoji:
            channel = self.bot.get_channel(reaction.channel_id)
            msg = await channel.fetch_message(reaction.message_id)

            if msg:
                await self.processStars(msg)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, reaction):
        """ 
        Called when a reaction is removed.
        Checks if the reaction is star_reaction and processStar(msg) if it is.
        """
        
        emoji_name = utils.getEmojiName(reaction.emoji.name)

        if emoji_name == self.star_react_emoji:
            channel = self.bot.get_channel(reaction.channel_id)
            msg = await channel.fetch_message(reaction.message_id)

            if msg:
                await self.processStars(msg, deletion=True)


    # commands

    @commands.command()
    async def help(self, ctx):
        """ The help command. Lists all commands avaliable. """

        await ctx.send("See https://github.com/hirim-ca/StargazerBot for the list of commands.")

    @commands.command()
    async def stChn(self, ctx, *args):
        """ 
        Show the current starboard channel or set a new starboard channel.
        Usage: [prefix]stChn [#channel]
        """

        if not ctx.author.guild_permissions.administrator:
                await ctx.send("You must be a admin to use that function.")
                return

        if len(args) >= 1:
            # check if channel if valid
            channel_id = int(re.search(r'<#(.*)>', args[0]).group(1))
            channel = self.bot.get_channel(channel_id)

            if channel:
                self.star_channel = channel
                await ctx.send(f"Starboard channel set to <#{ channel_id }>.")
            else:
                await ctx.send("Invalid channel.")
        
        else:
            await ctx.send(f"Starboard channel is currently set to <#{ self.star_channel.id }>.")

    @commands.command()
    async def rkQt(self, ctx):
        """ Displays top RANK_LIMIT number of quotes sorted by scores. """
        
        # prepare data

        tops = self.bot.db.get(
            self.datatable_name, 
            columns = ["message_id", "channel_id", "author_id", "score"],
            constraints = f"ORDER BY score DESC, created_at DESC LIMIT { self.rank_limit+50 } "
        ) # limit + 50 in case of deleted messages(312 fix)
      
        tops["user"] = tops["author_id"].map(lambda x: self.bot.get_user(int(x)))
        tops = tops.dropna()
        tops["name"] = tops["user"].map(lambda row: row.display_name)
        tops["channel"] = tops["channel_id"].map(lambda x: self.bot.get_channel(int(x)))

        # suggest a better solution if you see this
        messages = []
        ids = tops["message_id"].tolist()
        for i, row in tops["channel"].iteritems():
            try:
                msg = await row.fetch_message(ids[i])
                messages.append(msg)
            except:
                messages.append(np.NaN)
            
        tops["message"] = messages
        tops = tops.dropna() # erase deleted messages
        tops["content"] = tops["message"].map(lambda row: row.content)

        top1 = tops.iloc[0]
        others = tops.iloc[1:self.rank_limit-1]

        # format output

        # top 1

        embed = discord.Embed(
            title = "",
            description = f"{ top1['content'] }\n[View message]({ top1['message'].jump_url })\n ", 
            color = self.highlight_colors[-1]
        )

        embed.set_author(name=top1["name"], icon_url=top1["user"].avatar_url_as(static_format="png"))
        
        embed.add_field(name="Rank", value="#1", inline=True)
        embed.add_field(name="Score", value=f"{ top1['score'] }", inline=True)

        # others

        i = 2

        def appendToEmbed(row):
            nonlocal i

            embed.add_field(
                name=f"------------------------\n#{ i }: **{ row['score'] }** points | By: **{ row['name'] }**",
                value=f"{ row['content'] }\n[View message]({ row['message'].jump_url })",
                inline=False
            )

            i += 1

        others.apply(lambda row: appendToEmbed(row), axis=1)

        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=self.bot.name, icon_url=self.bot.user.avatar_url_as(static_format='png'))

        # print

        await ctx.send(f"<@{ ctx.author.id }> Here you go!", embed=embed)

    @commands.command()
    async def rkAt(self, ctx):
        """ Displays top RANK_LIMIT number of users sorted by their total scores. """

        # prepare data

        tops = self.bot.db.get(
            self.datatable_name, 
            columns = ["author_id", "SUM(score)"],
            constraints = f"GROUP BY author_id ORDER BY SUM(score) DESC LIMIT { self.rank_limit+10 } "
        )

        tops["user"] = tops["author_id"].map(lambda x: self.bot.get_user(int(x)))
        tops = tops.dropna()
        tops["name"] = tops["user"].map(lambda row: row.display_name)

        top1 = tops.iloc[0]
        others = tops.iloc[1:self.rank_limit-1]

        # format output

        # top 1

        embed = discord.Embed(
            title = "#1",
            description = f"Has gained **{ top1['SUM(score)'] }** points. ", 
            color = self.highlight_colors[-1]
        )

        embed.set_author(name=top1["name"], icon_url=top1["user"].avatar_url_as(static_format="png"))

        # others

        i = 2

        def appendToEmbed(row):
            nonlocal i

            embed.add_field(
                name=f"------------------------\n#{ i }: **{ row['SUM(score)'] }** points",
                value=f"{ row['name'] }",
                inline=False
            )

            i += 1

        others.apply(lambda row: appendToEmbed(row), axis=1)

        embed.timestamp = datetime.utcnow()
        embed.set_footer(text=self.bot.name, icon_url=self.bot.user.avatar_url_as(static_format='png'))

        # print

        await ctx.send(f"<@{ ctx.author.id }> Here you go!", embed=embed)

    @commands.command()
    async def rand(self, ctx, *args):
        """ 
        Sends a random quote (from user). 
        Usage: rand or rand [@user]
        """

        if len(args):

            # check for valid user
            match = re.search(r'<@!(.*)>', args[0])
            target_id = None

            if match:
                target_id = int(match.group(1))
            else:
                match = re.search(r'<@(.*)>', args[0])
                if not match:
                    await ctx.send("Invalid user.")
                    return
                target_id = int(match.group(1))

            # get quote
            rand_quote = self.bot.db.get(
                self.datatable_name, 
                columns = ["message_id", "channel_id", "author_id"],
                constraints = f"WHERE author_id = '{ target_id }' ORDER BY RANDOM() LIMIT 1"
            )

        else:
            rand_quote = self.bot.db.get(
                self.datatable_name, 
                columns = ["message_id", "channel_id", "author_id"],
                constraints = f"ORDER BY RANDOM() LIMIT 1"
            )

        if not rand_quote.empty:
            # if valid quote

            rand_quote = rand_quote.iloc[0]
            channel = self.bot.get_channel(int(rand_quote['channel_id']))
            msg = await channel.fetch_message(int(rand_quote['message_id']))

            await ctx.send(embed=utils.createEmbed(msg, color=self.highlight_colors[-1]))

        else:
            await ctx.send("User doesn't have a highlighted quote.")

    @commands.command()
    async def desc(self, ctx, *args):
        """ 
        Checks the user's quote status.
        Usage: desc [@user]
        """

        # check for valid syntax
        match = re.search(r'<@!(.*)>', args[0])
        target_id = None

        if match:
            target_id = int(match.group(1))
        else:
            match = re.search(r'<@(.*)>', args[0])
            if not match:
                return
            target_id = int(match.group(1))
            
        # get quotes from user
        user_quotes = self.bot.db.get(
            self.datatable_name, 
            columns = ["message_id", "channel_id", "author_id", "score"],
            constraints = f"WHERE author_id = '{ target_id }' ORDER BY score DESC, created_at DESC"
        )

        if not user_quotes.empty:
            # generate user stat from quote

            sum = user_quotes['score'].sum()
            mean = int(round(user_quotes['score'].mean()))
            count = user_quotes['score'].count()

            top_quote = user_quotes.iloc[0]

            channel = self.bot.get_channel(int(top_quote['channel_id']))
            msg = await channel.fetch_message(int(top_quote['message_id']))

            # post

            embed = discord.Embed(
                title = "Top Quote",
                description = msg.content,
                color = self.highlight_colors[-1]
            )

            embed.add_field(name="Number of Quotes", value=str(count), inline=True)
            embed.add_field(name="Total Points Gained", value=str(sum), inline=True)
            embed.add_field(name="Average Points per Quote", value=str(mean), inline=True)

            embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url_as(static_format="png"))
            embed.set_thumbnail(url=msg.author.avatar_url_as(static_format="png"))


            embed.timestamp = datetime.utcnow()
            embed.set_footer(text=self.bot.name, icon_url=self.bot.user.avatar_url_as(static_format='png'))

            await ctx.send(f"<@{ ctx.author.id }> Here you go!", embed=embed)

        else:
            await ctx.send("User doesn't have a highlighted quote.")



def setup(bot):
    bot.add_cog(Stargazer(bot))
