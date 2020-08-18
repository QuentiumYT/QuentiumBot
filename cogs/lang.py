import discord
from discord.ext import commands
from QuentiumBot import GetData, get_translations, is_owner

# Basic command configs
cmd_name = "lang"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class LangAdminConfig(commands.Cog):
    """Lang command in Admin Config section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=True
    )
    @commands.guild_only()
    async def lang_cmd(self, ctx, *, args=None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await GetData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if not(ctx.message.author.guild_permissions.administrator or is_owner(ctx)):
                return await ctx.send(cmd_tran["msg_perm_admin_user"].format(ctx.message.author.name))
            if not args:
                return await ctx.send(cmd_tran["msg_specify_lang"])
            else:
                if any(args == x for x in ["fr", "en"]):
                    if lang_server == args:
                        await ctx.send(cmd_tran["msg_lang_same"])
                    else:
                        await GetData.change_lang(self, ctx, args)
                        # Lang changed before sending the msg
                        await ctx.send(tran[cmd_name][args]["msg_lang_set"])
                else:
                    return await ctx.send(cmd_tran["msg_lang_not_exist"])

def setup(client):
    client.add_cog(LangAdminConfig(client))
