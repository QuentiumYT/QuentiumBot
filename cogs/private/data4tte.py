import discord, asyncio
from discord.ext import commands
from QuentiumBot import HandleData, get_translations, exec_command, windows

# Basic command configs
cmd_name = "data4tte"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class Data4TTEQuentium(commands.Cog):
    """Generates data for the TimeToEat project (private)"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.is_owner()
    async def data4tte_cmd(self, ctx, *, number="130"):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

        authorized = [246943045105221633, 324570532324442112, 224928390694567936, 272412092248752137]
        # Quentium's / vectokse / Jaguar AF user ID
        if any(x == ctx.message.author.id for x in authorized):
            if not number.isdecimal():
                number = "130"

            temp = await ctx.send(cmd_tran["msg_sending_data"])
            if windows:
                await exec_command("python scripts/data4tte.py " + number, ctx.message)
            else:
                await exec_command("python3 scripts/data4tte.py " + number, ctx.message)
            await asyncio.sleep(5)
            await ctx.message.delete()
            await temp.delete()

def setup(client):
    client.add_cog(Data4TTEQuentium(client))
