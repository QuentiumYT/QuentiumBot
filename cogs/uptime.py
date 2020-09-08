import discord
from discord.ext import commands
from datetime import datetime
from QuentiumBot import HandleData, get_translations, start_time

# Basic command configs
cmd_name = "uptime"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class UptimeInfos(commands.Cog):
    """Uptime command in Statistics section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def uptime_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Get the number of seconds since the bot started
            time = (datetime.now() - start_time).total_seconds()
            # Calculates the days, hours, minutes, seconds with divmod
            m, s = divmod(int(time), 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            # Send the formatted uptime
            await ctx.send(cmd_tran["msg_uptime"].format(d, h, m, s))

def setup(client):
    client.add_cog(UptimeInfos(client))
