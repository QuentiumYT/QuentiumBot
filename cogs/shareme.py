import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations, get_config, debug

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
        pass_context=True
    )
    async def shareme_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Debug mode, send the testing invite link
            if debug:
                await ctx.send(cmd_tran["msg_shareme"] + get_config("TEST", "invite"))
            # Public invite link
            else:
                await ctx.send(cmd_tran["msg_shareme"] + get_config("PUBLIC", "invite"))

def setup(client):
    client.add_cog(SharemeInfos(client))
