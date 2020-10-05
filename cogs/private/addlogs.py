import discord, os, asyncio
from discord.ext import commands
from datetime import datetime
from QuentiumBot import HandleData, get_translations, is_owner

# Basic command configs
cmd_name = "addlogs"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class AddLogsQuentium(commands.Cog):
    """Add logs command for QuentiumYT (private)"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.is_owner()
    async def addlogs_cmd(self, ctx, *, logs=None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if logs:
                # Write the date and args to the file
                infos_logs = " --- ".join([datetime.now().strftime("%d.%m.%Y - %H:%M"), logs])
                with open("data/logs.txt", "a", encoding="utf-8") as file:
                    file.write(infos_logs + "\n")
                await asyncio.sleep(5)
            # Delete the user message
            await ctx.message.delete()

def setup(client):
    client.add_cog(AddLogsQuentium(client))
