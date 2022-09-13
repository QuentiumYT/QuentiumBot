import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

# Basic command configs
cmd_name = "cookie"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class CookieTheSweMaster(commands.Cog):
    """Get some cookies command in TheSweMaster section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def cookie_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if ctx.guild.id == 199189022894063627: # TheSweMaster server ID
                author = ctx.message.author.name
                # Emojis that are not cookies
                not_cookie = ["MrCookie"]
                # Get all emojis containing cookie
                cookies = [x for x in self.client.emojis if "cookie" in str(x.name).lower() and not any(y == str(x.name) for y in not_cookie)]
                msg_cookies = "".join([str(x) for x in cookies])
                await ctx.send(cmd_tran["msg_cookies"].format(author, msg_cookies))

def setup(client):
    client.add_cog(CookieTheSweMaster(client))
