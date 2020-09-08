import discord
from discord.ext import commands
from QuentiumBot import HandleData, get_translations, match_id, is_owner

# Basic command configs
cmd_name = "prefix"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class PrefixAdminConfig(commands.Cog):
    """Prefix command in Admin Config section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def prefix_cmd(self, ctx, *, args=None):
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
            # Check user perms or owner
            if not(ctx.message.author.guild_permissions.administrator or is_owner(ctx)):
                return await ctx.send(cmd_tran["msg_perm_admin_user"].format(ctx.message.author.name))
            # No args given
            if not args:
                return await ctx.send(cmd_tran["msg_invalid_arg"].format(prefix_server))

            # Delete the prefix variations
            if any(x == args for x in ["delete", "reset", "remove", "suppr"]):
                # Prefix is already default
                if not prefix_server == "+":
                    await HandleData.change_prefix(self, ctx, "+")
                return await ctx.send(cmd_tran["msg_prefix_reset"])
            elif match_id(args):
                return await ctx.send(cmd_tran["msg_invalid_arg"].format(prefix_server))

            # Change the prefix with arguments
            await HandleData.change_prefix(self, ctx, args)
            await ctx.send(cmd_tran["msg_prefix_changed"].format(args))

def setup(client):
    client.add_cog(PrefixAdminConfig(client))
