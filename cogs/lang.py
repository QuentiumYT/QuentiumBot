import discord
from discord.ext import commands
from QuentiumBot import HandleData, get_translations, is_owner

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
        pass_context=True
    )
    @commands.guild_only()
    async def lang_cmd(self, ctx, *, lang=None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Check user perms or owner
            if not(ctx.message.author.guild_permissions.administrator or is_owner(ctx)):
                return await ctx.send(cmd_tran["msg_perm_admin_user"].format(ctx.message.author.name))
            # No args given
            if not lang:
                return await ctx.send(cmd_tran["msg_specify_lang"])

            # Check if lang is existing
            if any(lang == x for x in ["fr", "en", "de"]):
                if lang_server == lang:
                    await ctx.send(cmd_tran["msg_lang_same"])
                else:
                    await HandleData.change_lang(self, ctx, lang)
                    # Lang changed before sending the msg
                    await ctx.send(tran[cmd_name][lang]["msg_lang_set"])
            else:
                await ctx.send(cmd_tran["msg_lang_not_exist"])

def setup(client):
    client.add_cog(LangAdminConfig(client))
