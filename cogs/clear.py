import discord
from discord.ext import commands
from QuentiumBot import HandleData, get_translations

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
        pass_context=True,
        no_pm=True
    )
    @commands.guild_only()
    async def clear_cmd(self, ctx, *, args=None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if not ctx.message.author.permissions_in(ctx.message.channel).manage_messages:
                return await ctx.send(cmd_tran["msg_perm_manage_msg_user"].format(ctx.message.author.name))
            if not ctx.message.channel.guild.me.guild_permissions.manage_messages:
                return await ctx.send(cmd_tran["msg_perm_manage_msg_bot"])
            if not args:
                await ctx.send(cmd_tran["msg_specify_number"])
            else:
                if args.split()[0].isdecimal():
                    number = int(args.split()[0])
                    if number < 99 and number > 0:
                        limit = number + 1
                        await ctx.message.channel.purge(limit=limit)
                    else:
                        return await ctx.send(cmd_tran["msg_limit_number"])
                else:
                    await ctx.send(cmd_tran["msg_invalid_number"])

def setup(client):
    client.add_cog(ClearAdminRights(client))
