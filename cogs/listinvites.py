import discord
from discord.ext import commands
from QuentiumBot import GetData, get_translations

# Basic command configs
cmd_name = "listinvites"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class ListinvitesInfos(commands.Cog):
    """List invites command in Informations section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=True
    )
    @commands.guild_only()
    async def listinvites_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await GetData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            list_invites = await ctx.guild.invites()
            if list_invites:
                content = "\n- ".join([x.url for x in list_invites])
            else:
                content = cmd_tran["msg_any"]
            embed = discord.Embed(color=0x11FFFF)
            embed.title = cmd_tran["msg_title"]
            embed.description = "- " + content
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(ListinvitesInfos(client))
