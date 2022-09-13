import nextcord, os, asyncio
from nextcord.ext import commands
from datetime import datetime
from QuentiumBot import storage, get_translations

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
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

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
