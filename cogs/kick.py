import discord
from discord.ext import commands
from QuentiumBot import GetData, get_translations

# Basic command configs
cmd_name = "kick"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class KickAdministration(commands.Cog):
    """Kick command in Administration section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=True
    )
    @commands.guild_only()
    async def kick_cmd(self, ctx, *, member: discord.Member = None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await GetData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Check user perms
            if not ctx.message.author.guild_permissions.kick_members:
                return await ctx.send(cmd_tran["msg_perm_kick_user"].format(ctx.message.author.name))
            # Check bot perms
            if not ctx.message.guild.me.guild_permissions.kick_members:
                return await ctx.send(cmd_tran["msg_perm_kick_bot"])
            if not member:
                return await ctx.send(cmd_tran["msg_mention_user"].format(ctx.message.author.name))
            await member.kick()
            embed = discord.Embed(color=0xFF1111)
            embed.description = cmd_tran["msg_been_kicked"].format(member.name)
            return await ctx.send(embed=embed)

def setup(client):
    client.add_cog(KickAdministration(client))
