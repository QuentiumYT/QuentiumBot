import discord, json, random, re, requests
from discord.ext import commands
from QuentiumBot import GetData, get_translations

# Basic command configs
cmd_name = "embed"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

with open("data/embed_colors.json", encoding="utf-8", errors="ignore") as file:
    colors_embed = json.loads(file.read(), strict=False)

class EmbedUtilities(commands.Cog):
    """Embed command in Utilities section"""

    def __init__(self, client):
        self.client = client

    # Function to create a random hex color
    def random_color(self):
        rc = lambda: random.randint(0, 255)
        return int("0x%02X%02X%02X" % (rc(), rc(), rc()), 16)

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=False
    )
    async def embed_cmd(self, ctx, *, args=None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await GetData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
            prefix_server = data[3]
        else:
            lang_server = "en"
            prefix_server = "+"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if not args:
                return await ctx.send(cmd_tran["msg_no_args"].format(prefix_server))

            content = [x.strip() for x in re.split(r".=", args)[1:]]
            sep = re.findall(r".=", args)
            title = description = color = thumbnail = footer = url = author = None
            for x in range(len(sep)):
                if "T=" == sep[x]:
                    title = content[x]
                if "D=" == sep[x]:
                    description = content[x]
                if "C=" == sep[x]:
                    color = content[x]
                if "I=" == sep[x]:
                    thumbnail = content[x]
                if "F=" == sep[x]:
                    footer = content[x]
                if "U=" == sep[x]:
                    url = content[x]
                if "A=" == sep[x]:
                    author = content[x]
            if all(x is None for x in [title, description, color, thumbnail, footer, url, author]):
                if len(args) <= 255:
                    title = args
                else:
                    title = None
                    description = args
            if not title:
                if description and len(args) <= 255:
                    title = description
                    description = None
            if color == "random":
                color = self.random_color()
            elif color is not None:
                if any([x for x in colors_embed.keys() if x == color]):
                    color = int(colors_embed[color], 16)
                else:
                    if color.isdigit():
                        color = int(color)
                        if color >= 16777215:
                            color = 16777215
                    else:
                        try:
                            color = int("0x" + color.replace("#", "").replace("0x", ""), 16)
                            if color >= 16777215:
                                color = 16777215
                        except:
                            return await ctx.send(cmd_tran["msg_wrong_color"])
            else:
                color = self.random_color()
            embed = discord.Embed(color=color)
            embed.title = title
            embed.description = description
            embed.url = url
            if thumbnail:
                if not "http" in thumbnail:
                    thumbnail = "https://" + thumbnail.split("//", 1)[-1]
                try:
                    if "image/" in str(requests.get(thumbnail).headers):
                        embed.set_thumbnail(url=thumbnail)
                    else:
                        embed.set_thumbnail(url=tran["GLOBAL"]["logo_question"])
                except:
                    embed.set_thumbnail(url=tran["GLOBAL"]["logo_question"])
            if author:
                embed.set_author(name=author)
            if footer:
                if not footer == "None":
                    embed.set_footer(text=footer)
            else:
                embed.set_footer(text=ctx.message.author.name,
                                 icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(EmbedUtilities(client))
