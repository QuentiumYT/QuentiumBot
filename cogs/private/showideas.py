import nextcord, os, asyncio
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

# Basic command configs
cmd_name = "showideas"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class ShowIdeasQuentium(commands.Cog):
    """Show ideas command for QuentiumYT (private)"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.is_owner()
    async def showideas_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

        feedback_file = "feedback.txt"

        # Create a basic embed
        embed = nextcord.Embed(color=0x115050)
        embed.title = cmd_tran["msg_ideas"]
        embed.description = cmd_tran["msg_none"]

        # If feedback file does not exist
        if not os.path.isfile(feedback_file):
            embed.description = cmd_tran["msg_empty_file"]
        else:
            # Set the description to all the file content
            with open(feedback_file, "r", encoding="utf-8", errors="ignore") as file:
                embed.description = "".join(file.readlines())

        # Send the embed temporary
        tmp = await ctx.send(embed=embed)
        await asyncio.sleep(5)
        # After 5 seconds, delete both messages for privacy
        await ctx.message.delete()
        await tmp.delete()

def setup(client):
    client.add_cog(ShowIdeasQuentium(client))
