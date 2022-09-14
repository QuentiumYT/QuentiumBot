import nextcord, json, random, re, requests
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

# Basic command configs
cmd_name = "embed"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

with open("data/embed_colors.json", "r", encoding="utf-8", errors="ignore") as file:
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
        pass_context=True
    )
    async def embed_cmd(self, ctx, *, args=None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
            prefix_server = data[3]
        else:
            lang_server = "en"
            prefix_server = "+"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # No args given
            if not args:
                return await ctx.send(cmd_tran["msg_invalid_arg"].format(prefix_server))

            # Get a list of every argument given
            content = [x.strip() for x in re.split(r".=", args)[1:]]
            sep = re.findall(r".=", args)
            title = description = color = thumbnail = footer = url = author = None
            # Separate arguments in variables
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

            # If no argument is given using the formatting, set the text as title
            if all(x is None for x in [title, description, color, thumbnail, footer, url, author]):
                # Discord title length limit is 255 chars
                if len(args) <= 255:
                    title = args
                else:
                    title = None
                    description = args

            # If only description is given, set as title
            if not title:
                if description and len(args) <= 255:
                    title = description
                    description = None

            # Using a random color
            if color == "random":
                color = self.random_color()
            # Find the given color
            elif color is not None:
                # If color is string inside JSON file
                if any(x for x in colors_embed.keys() if x == color.lower()):
                    color = int(colors_embed[color], 16)
                # Decimal color number
                elif color.isdigit():
                    color = int(color)
                    if color >= 16777215:
                        color = 16777215
                # Hexadecimal color string
                else:
                    try:
                        # Convert the hex to int value
                        color = int("0x" + color.replace("#", "").replace("0x", ""), 16)
                        if color >= 16777215:
                            color = 16777215
                    except:
                        return await ctx.send(cmd_tran["msg_invalid_color"])
            else:
                color = self.random_color()

            # Send the personal embed
            embed = nextcord.Embed(color=color)
            embed.title = title
            embed.description = description

            if url and not "http" in url:
                return await ctx.send(cmd_tran["msg_invalid_url_scheme"])
            embed.url = url

            if thumbnail:
                # Convert http to https or add it
                if not "http" in thumbnail:
                    thumbnail = "https://" + thumbnail.split("//", 1)[-1]
                try:
                    # Check if the picture is a real image
                    if "image/" in str(requests.get(thumbnail).headers):
                        embed.set_thumbnail(url=thumbnail)
                    else:
                        embed.set_thumbnail(url=tran["GLOBAL"]["logo_question"])
                except:
                    embed.set_thumbnail(url=tran["GLOBAL"]["logo_question"])

            if author:
                embed.set_author(name=author)

            if footer and footer != "None":
                embed.set_footer(text=footer)
            else:
                # Set author name and url in footer
                embed.set_footer(text=ctx.message.author.name,
                                 icon_url=ctx.message.author.avatar)

            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(EmbedUtilities(client))
