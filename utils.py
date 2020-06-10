import discord
from discord.ext import commands
import asyncio
import emoji

def createEmbed(msg, **kwags):
    """ 
    Create a embed featuring the given message. 
    Returns a discord.Embed.
    """


    embed = discord.Embed(
            title = "",
            description = f"{ msg.content }\n\n[View message]({ msg.jump_url })",
            color = kwags.get("color", discord.Colour.blue())
        )

    embed.set_author(name=msg.author.display_name, icon_url=msg.author.avatar_url_as(static_format="png"))
    embed.timestamp = msg.created_at
    if len(msg.attachments) > 0:
        embed.set_image(url=msg.attachments[0].url)
    embed.set_footer(text=f"{ msg.guild.name } | { msg.channel.name }")

    return embed
    
def getEmojiName(emoji_):
    """
    Gets the str name of the unicode emoji.
    """
    name = emoji.demojize(emoji_)

    if ':' in name: return name[1:-1]
    else: return name