import discord
from discord.ext import commands
from QuentiumBot import HandleData, get_translations

# Basic command configs
cmd_name = "absent"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class AbsentFLC(commands.Cog):
    """Absent command in France Les Cités section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.guild_only()
    async def absent_cmd(self, ctx, *, reason=None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            await HandleData.retrieve_data(self, ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if ctx.guild.id == 371687157817016331: # France Les Cités server ID
                if ctx.message.channel.id == 552484372251410437: # France Les Cités absent channel ID
                    # Check bot perms
                    if not ctx.message.channel.guild.me.guild_permissions.manage_roles:
                        return await ctx.send(cmd_tran["msg_perm_roles_bot"])

                    # Get the absent role
                    role = discord.utils.get(ctx.message.guild.roles, name="Absent")
                    # Get the nickname or the username of the member
                    member_name = ctx.message.author.nick if ctx.message.author.nick else ctx.message.author.name
                    if not role in ctx.message.author.roles:
                        # No reason given
                        if reason is None:
                            await ctx.message.delete()
                            return await ctx.message.author.send(cmd_tran["msg_specify_reason"])
                        # Add the absent role
                        await ctx.message.author.add_roles(role)
                        # Send a message in the channel and to the user as well
                        await ctx.send(cmd_tran["msg_absent_reason"].format(member_name, reason))
                        try:
                            await ctx.message.author.send(cmd_tran["msg_join_absent"])
                        except:
                            # User has disabled PM messages
                            pass
                    else:
                        # Remove the absent role
                        await ctx.message.author.remove_roles(role)
                        # Send a message in the channel and to the user as well
                        await ctx.send(cmd_tran["msg_is_back"].format(member_name))
                        try:
                            await ctx.message.author.send(cmd_tran["msg_join_present"])
                        except:
                            # User has disabled PM messages
                            pass
                    await ctx.message.delete()

def setup(client):
    client.add_cog(AbsentFLC(client))
