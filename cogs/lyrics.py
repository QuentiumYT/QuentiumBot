import nextcord, requests, re
from nextcord.ext import commands
from bs4 import BeautifulSoup
from QuentiumBot import storage, get_translations, get_config

# Basic command configs
cmd_name = "lyrics"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class LyricsUtilities(commands.Cog):
    """Lyrics command in Utilities section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def lyrics_cmd(self, ctx, *, music=None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # No music given
            if not music:
                return await ctx.send(cmd_tran["msg_specify_music"])

            # Fetch the best results with the args
            request_url = "https://api.genius.com/search/"
            query = {"q": music}
            headers = {"Authorization": "Bearer " + get_config("GLOBAL", "token_genius")}
            r = requests.get(request_url, params=query, headers=headers).json()

            # Genius API return no music
            if not r["response"]["hits"]:
                return await ctx.send(cmd_tran["msg_not_found"])

            # Get the lyrics path and request the webpage
            path_lyrics = r["response"]["hits"][0]["result"]["path"]
            genius_url = "https://genius.com" + path_lyrics
            page = requests.get(genius_url)
            html = BeautifulSoup(page.text, "html.parser")

            # Find whatever class is containing lyrics
            # Tip from https://github.com/johnwmillr/LyricsGenius/blob/master/lyricsgenius/genius.py#L133
            lyrics_div = html.find("div", class_=re.compile("^lyrics$|Lyrics__Root"))
            if "Lyrics__Root" in str(lyrics_div):
                # Clean the lyrics since get_text() fails to convert "</br/>"
                lyrics = str(lyrics_div).replace("<br/></div>", "\n\n").replace("<br/>", "\n").replace("&amp;", "&")
                # Add extra break lines at the beginning and end (parse like old lyrics)
                lyrics = "\n\n" + lyrics + "\n\n"
            else:
                # Get only the text of the page
                lyrics = lyrics_div.get_text()
            # Remove extra tags
            lyrics = re.sub(r"(\<.*?\>)", "", lyrics)

            if not lyrics_div:
                return await ctx.send(cmd_tran["msg_no_lyrics"])

            # If length is too long, the song does not contain lyrics
            if len(lyrics) > 6000:
                return await ctx.send(cmd_tran["msg_too_long"])

            # Get music details
            title = r["response"]["hits"][0]["result"]["full_title"]
            image = r["response"]["hits"][0]["result"]["header_image_url"]
            # Lyric found doesn't contain any arg given, warn the user
            if not any(x.lower() in title.lower() for x in music.split()):
                await ctx.send(cmd_tran["msg_not_match"])
                await ctx.send(cmd_tran["msg_result_found"].format(music))

            # Send an embed with lyrics
            embed = nextcord.Embed(color=0x11FFFF)
            embed.title = cmd_tran["msg_lyrics"].format(title)
            embed.description = None
            embed.set_thumbnail(url=image)
            # Every block of lyrics is added in a field
            for block in lyrics.split("\n\n")[1:-1]:
                splitted = block.split("\n", 1)
                if splitted[0] != "":
                    if not len(splitted) == 1:
                        if len(splitted[1]) >= 1024:
                            embed.add_field(name=splitted[0],
                                            value=splitted[1][0:1023])
                        else:
                            embed.add_field(name=splitted[0],
                                            value=splitted[1])
                    else:
                        # Filed contains nothing add notes
                        embed.add_field(name=splitted[0], value=":notes:" * 6)
            embed.set_footer(text=tran["GLOBAL"][lang_server]["requested_by"].format(ctx.message.author.name),
                             icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(LyricsUtilities(client))
