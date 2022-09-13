import nextcord, asyncio
from nextcord.ext import commands
from QuentiumBot import storage, get_translations, exec_command, windows

# Basic command configs
cmd_name = "menu4tte"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class Menu4TTEQuentium(commands.Cog):
    """Sends all menus for the TimeToEat project (private)"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.is_owner()
    async def menu4tte_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

        authorized = [246943045105221633, 324570532324442112, 224928390694567936, 272412092248752137]
        # Quentium's / vectokse / Jaguar AF user ID
        if any(x == ctx.message.author.id for x in authorized):
            temp = await ctx.send(cmd_tran["msg_sending_data"])
            if windows:
                await exec_command("python scripts/menu4tte.py", ctx.message)
            else:
                await exec_command("python3 scripts/menu4tte.py", ctx.message)
            await asyncio.sleep(5)
            await ctx.message.delete()
            await temp.delete()

def setup(client):
    client.add_cog(Menu4TTEQuentium(client))
