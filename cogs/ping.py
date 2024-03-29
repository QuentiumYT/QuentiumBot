import nextcord, time
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

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
        pass_context=True
    )
    async def ping_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Ping the time to trigger text typing
            before = time.perf_counter()
            await ctx.trigger_typing()
            ping_bot = round((time.perf_counter() - before) * 1000)
            # Ping the sending message latency
            before = time.perf_counter()
            tmp = await ctx.send(cmd_tran["msg_ping_test"])
            ping_msg = round((time.perf_counter() - before) * 1000)
            # Delete the test message
            await tmp.delete()
            # Send both pings
            await ctx.send(cmd_tran["msg_pong"].format(ping_bot, ping_msg))

def setup(client):
    client.add_cog(PingInfos(client))
