import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations, is_owner, match_id

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
        pass_context=True
    )
    @commands.guild_only()
    async def autorole_cmd(self, ctx, *, args=None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
            autorole_server = data[2]
            prefix_server = data[3]
        else:
            lang_server = "en"
            autorole_server = None
            prefix_server = "+"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Check user perms or owner
            if not (ctx.message.author.guild_permissions.manage_roles or is_owner(ctx)):
                return await ctx.send(cmd_tran["msg_perm_roles_user"].format(ctx.message.author.name))
            # Check bot perms
            if not ctx.message.channel.guild.me.guild_permissions.manage_roles:
                return await ctx.send(cmd_tran["msg_perm_roles_bot"])
            # No args given
            if not args:
                return await ctx.send(cmd_tran["msg_invalid_arg"].format(prefix_server))

            # Remove the autorole
            if any(x == args.lower() for x in ["remove", "delete"]):
                await storage.change_autorole(self, ctx, None)
                return await ctx.send(cmd_tran["msg_role_deleted"])
            # See the autorole
            if any(x == args.lower() for x in ["show", "see"]):
                if not autorole_server:
                    return await ctx.send(cmd_tran["msg_role_not_defined"])
                # Get the role object
                role = nextcord.utils.get(ctx.message.guild.roles, id=autorole_server)
                if not role:
                    # Delete the role if it was deleted from the server
                    await storage.change_autorole(self, ctx, None)
                    return await ctx.send(cmd_tran["msg_unknown_role"])
                return await ctx.send(cmd_tran["msg_current_role"].format(role.name))

            # If the role is any kind of ID
            if match_id(args):
                role = nextcord.utils.get(ctx.message.guild.roles, id=match_id(args))
            # Find the role using it's name
            else:
                for role in ctx.message.guild.roles:
                    # Match the argument with all roles names
                    if args.lower() == role.name.lower():
                        role = nextcord.utils.get(ctx.message.guild.roles, name=role.name)
                        break
                else:
                    return await ctx.send(cmd_tran["msg_invalid_role"])

            # Modify the role in the config
            await storage.change_autorole(self, ctx, role.id)
            await ctx.send(cmd_tran["msg_role_set"].format(role.name))

def setup(client):
    client.add_cog(AutoroleAdminConfig(client))
