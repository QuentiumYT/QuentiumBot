import discord
from discord.ext import commands
from QuentiumBot import HandleData, get_translations, get_config, debug

# Basic command configs
cmd_name = "shareme"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class SharemeInfos(commands.Cog):
    """Shareme command in Information section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=False
    )
    async def shareme_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if debug:
                await ctx.send(cmd_tran["msg_shareme"] + get_config("TEST", "invite"))
            else:
                await ctx.send(cmd_tran["msg_shareme"] + get_config("PUBLIC", "invite"))

def setup(client):
    client.add_cog(SharemeInfos(client))
