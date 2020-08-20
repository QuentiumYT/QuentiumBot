import discord
from discord.ext import commands
from QuentiumBot import HandleData, get_translations

# Basic command configs
cmd_name = "avatar"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class AvatarUtilities(commands.Cog):
    """Avatar command in Utilities section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=False
    )
    async def avatar_cmd(self, ctx, *, member: discord.Member = None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if not member:
                member = ctx.message.author
            icon = str(member.avatar_url)
            icon1 = icon.split(".", 999)
            icon2 = "".join(icon1[len(icon1) - 1])
            icon3 = icon.replace(icon2, "")
            if "gif" in icon:
                avatar_url = icon3 + "gif?size=1024"
            else:
                avatar_url = icon3 + "png?size=1024"
            title = member.name + "#" + member.discriminator
            content = "[Avatar URL]({})".format(avatar_url)
            embed = discord.Embed(color=0x15F2C6)
            embed.title = f"**{title}**"
            embed.description = content
            embed.set_image(url=avatar_url)
            embed.set_footer(text=tran["GLOBAL"][lang_server]["requested_by"].format(ctx.message.author.name),
                             icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(AvatarUtilities(client))
