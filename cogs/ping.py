import discord, time
from discord.ext import commands
from QuentiumBot import HandleData, get_translations

# Basic command configs
cmd_name = "ping"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class PingInfos(commands.Cog):
    """Ping command in Statistics section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=True
    )
    @commands.guild_only()
    async def ping_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            before = time.perf_counter()
            await ctx.trigger_typing()
            ping_bot = round((time.perf_counter() - before) * 1000)
            before = time.perf_counter()
            tmp = await ctx.send(cmd_tran["msg_ping_test"])
            ping_msg = round((time.perf_counter() - before) * 1000)
            await tmp.delete()
            await ctx.send(cmd_tran["msg_pong"].format(ping_bot, ping_msg))

def setup(client):
    client.add_cog(PingInfos(client))
