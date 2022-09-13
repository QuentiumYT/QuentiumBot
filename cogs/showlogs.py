import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

# Basic command configs
cmd_name = "showlogs"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class ShowlogsFeedback(commands.Cog):
    """Show logs command in Feedback section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def showlogs_cmd(self, ctx):
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
            embed = nextcord.Embed(color=0xFFFF11)
            embed.title = cmd_tran["msg_logs_bot"]
            embed.url = tran["GLOBAL"]["website_url"]
            counter = 1
            # Read the log file
            with open("data/logs.txt", "r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    # Get data with three dash delimiter
                    line_time, line_content = line.replace("+", prefix_server).split(" --- ")
                    # Add the field and replace double point with line break
                    embed.add_field(name=f"#{counter} / {line_time}",
                                    value=line_content.replace("..", ".\n"),
                                    inline=True)
                    # Log count
                    counter += 1
            embed.set_footer(text=cmd_tran["msg_logs_infos"],
                             icon_url=tran["GLOBAL"]["logo_bot"])
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(ShowlogsFeedback(client))
