import discord
from discord.ext import commands
from QuentiumBot import HandleData, get_translations, is_owner, match_id

# Basic command configs
cmd_name = "autorole"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class AutoroleAdminConfig(commands.Cog):
    """Automatic role command in Admin Config section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=True
    )
    @commands.guild_only()
    async def autorole_cmd(self, ctx, *, args=None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
            prefix_server = data[3]
        else:
            lang_server = "en"
            prefix_server = "+"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if not(ctx.message.author.guild_permissions.manage_roles or is_owner(ctx)):  # Quentium user IDs
                return await ctx.send(cmd_tran["msg_perm_roles_user"].format(ctx.message.author.name))
            if not ctx.message.channel.guild.me.guild_permissions.manage_roles:
                return await ctx.send(cmd_tran["msg_perm_roles_bot"])
            if not args:
                return await ctx.send(cmd_tran["msg_invalid_arg"].format(prefix_server))
            else:
                if any([x == args.lower() for x in ["remove", "delete"]]):
                    await HandleData.change_autorole(self, ctx, None)
                    return await ctx.send(cmd_tran["msg_role_deleted"])
                elif any([x == args.lower() for x in ["show", "see"]]):
                    data = await HandleData.get_data(self, "data")
                    saved_role = data[str(ctx.message.guild.id)]["autorole_server"]
                    if saved_role == None:
                        return await ctx.send(cmd_tran["msg_role_not_defined"])
                    else:
                        role = discord.utils.get(ctx.message.guild.roles, id=saved_role)
                        if role == None:
                            return await ctx.send(cmd_tran["msg_unknown_role"])
                        else:
                            return await ctx.send(cmd_tran["msg_current_role"].format(role.name))
                elif match_id(args):
                    role = discord.utils.get(ctx.message.guild.roles, id=match_id(args))
                else:
                    for role in ctx.message.guild.roles:
                        if args.lower() == role.name.lower():
                            role = discord.utils.get(ctx.message.guild.roles, name=role.name)
                            break
                    else:
                        return await ctx.send(cmd_tran["msg_invalid_role"])

                await HandleData.change_autorole(self, ctx, role.id)
                return await ctx.send(cmd_tran["msg_role_set"].format(role.name))

def setup(client):
    client.add_cog(AutoroleAdminConfig(client))
