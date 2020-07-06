import discord, json
from discord.ext import commands

with open("data/translations.json", "r", encoding="utf-8", errors="ignore") as file:
    translations = json.loads(file.read(), strict=False)

class HelpInfos(commands.Cog):
    def __init__(self, client):
        self.client = client

    def emo(self, text):
        return str(discord.utils.get(self.client.emojis, name=text))

    @commands.command(
        name="help",
        aliases=translations["help"]["fr"]["aliases"].split("/"),
        pass_context=True,
        no_pm=False
    )
    async def help_cmd(self, ctx, args=None):
        prefix_server = "-"
        lang_server = "en"

        if not ctx.message.author.bot == True:
            commands = [c for c in translations.keys() if not c == "GLOBAL"]
            embed = discord.Embed(color=0x11ff11)
            if args == None:
                embed.url = translations["GLOBAL"]["website_url"]
                embed.title = translations["help"][lang_server]["msg_list_commands"]
                commands_value = ""
                for command in commands:
                    data = translations[command][lang_server]
                    if translations[commands[0]]["type"] == translations[command]["type"]:
                        commands_value += f"- **`{prefix_server}{command} {data['usage']}` >** {data['description']}\n"
                        latest_command = command
                    else:
                        embed.add_field(name=self.emo(translations[latest_command]["type_emoji"]) + translations["help"][lang_server]["help_title_" + translations[latest_command]["type"]],
                                        value=commands_value,
                                        inline=True)
                        commands_value = f"- **`{prefix_server}{command} {data['usage']}` >** {data['description']}\n"
                embed.add_field(name=self.emo(translations[command]["type_emoji"]) + translations["help"][lang_server]["help_title_" + translations[command]["type"]],
                                value=commands_value,
                                inline=True)
            return await ctx.send(embed=embed)

def setup(client):
    client.add_cog(HelpInfos(client))
