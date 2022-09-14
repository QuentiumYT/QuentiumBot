import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

# Basic command configs
cmd_name = "clear"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class ClearAdminRights(commands.Cog):
    """Clear command in Administration Rights section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.guild_only()
    async def clear_cmd(self, ctx, *, number=None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Check user perms
            if not ctx.message.channel.permissions_for(ctx.message.author).manage_messages:
                return await ctx.send(cmd_tran["msg_perm_manage_msg_user"].format(ctx.message.author.name))
            # Check bot perms
            if not ctx.message.channel.guild.me.guild_permissions.manage_messages:
                return await ctx.send(cmd_tran["msg_perm_manage_msg_bot"])
            # No number given
            if not number:
                return await ctx.send(cmd_tran["msg_specify_number"])

            # Get the first number given and check if it's decimal
            if number.split()[0].isdecimal():
                number = int(number.split()[0])
                # Number between 1 and 99 if errors
                if number < 99 and number > 0:
                    limit = number + 1
                    # Clear the messages
                    await ctx.message.channel.purge(limit=limit)
                else:
                    await ctx.send(cmd_tran["msg_limit_number"])
            else:
                await ctx.send(cmd_tran["msg_invalid_number"])

def setup(client):
    client.add_cog(ClearAdminRights(client))
