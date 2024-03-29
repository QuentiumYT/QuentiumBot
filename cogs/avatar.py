import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

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
        pass_context=True
    )
    async def avatar_cmd(self, ctx, *, member: nextcord.Member = None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # No member, using the author
            if not member:
                member = ctx.message.author
            # Retrieve the biggest avatar size
            icon = str(member.avatar)
            icon1 = icon.split(".", 999)
            icon2 = "".join(icon1[len(icon1) - 1])
            icon3 = icon.replace(icon2, "")
            if "gif" in icon:
                avatar = icon3 + "gif?size=1024"
            else:
                avatar = icon3 + "png?size=1024"
            # Send an embed
            title = member.name + "#" + member.discriminator
            content = "[Avatar URL]({})".format(avatar)
            embed = nextcord.Embed(color=0x15F2C6)
            embed.title = f"**{title}**"
            embed.description = content
            embed.set_image(url=avatar)
            embed.set_footer(text=tran["GLOBAL"][lang_server]["requested_by"].format(ctx.message.author.name),
                             icon_url=ctx.message.author.avatar)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(AvatarUtilities(client))
