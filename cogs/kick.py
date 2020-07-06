import discord, json
from discord.ext import commands

with open("data/translations.json", "r", encoding="utf-8", errors="ignore") as file:
    translations = json.loads(file.read(), strict=False)

class KickAdministration(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(
        name="kick",
        aliases=translations["kick"]["fr"]["aliases"].split("/"),
        pass_context=True,
        no_pm=True
    )
    @commands.guild_only()
    async def kick_cmd(self, ctx, *, member: discord.Member = None):
        lang_server = "en"

        if not ctx.message.author.bot == True:
            if not ctx.message.author.guild_permissions.kick_members:
                return await ctx.send(translations["kick"][lang_server]["msg_perm_kick_user"].format(author=ctx.message.author.name))
            if not ctx.message.guild.me.guild_permissions.kick_members:
                return await ctx.send(translations["kick"][lang_server]["msg_perm_kick_bot"])
            if not member:
                return await ctx.send(translations["kick"][lang_server]["msg_mention_user"].format(author=ctx.message.author.name))
            await member.kick()
            embed = discord.Embed(description=translations["kick"][lang_server]["msg_been_kicked"].format(member=member.name), color=0xFF0000)
            return await ctx.send(embed=embed)

def setup(client):
    client.add_cog(KickAdministration(client))
