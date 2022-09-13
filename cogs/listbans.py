import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

# Basic command configs
cmd_name = "listbans"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class ListbansInfos(commands.Cog):
    """List bans command in Information section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.guild_only()
    async def listbans_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Get the member ban list
            list_banned = await ctx.guild.bans()
            if list_banned:
                # List all the bans
                content = "\n- ".join([x[1].name for x in list_banned])
            else:
                content = cmd_tran["msg_any"]
            # Send an embed
            embed = nextcord.Embed(color=0x664211)
            embed.title = cmd_tran["msg_title"]
            embed.description = "- " + content
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(ListbansInfos(client))
