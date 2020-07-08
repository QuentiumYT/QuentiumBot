import discord
from discord.ext import commands
from QuentiumBot import GetData as gd

cmd_name = "help"
tran = gd.get_translations(gd)
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class HelpInfos(commands.Cog):
    def __init__(self, client):
        self.client = client

    def emo(self, text):
        return str(discord.utils.get(self.client.emojis, name=text))

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=False
    )
    async def help_cmd(self, ctx, args=None):
        global aliases
        if isinstance(ctx.channel, discord.TextChannel):
            data = await gd.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
            prefix_server = data[3]
        else:
            lang_server = "en"
            prefix_server = "+"
        cmd_tran = tran[cmd_name][lang_server]

        if not ctx.message.author.bot == True:
            commands = [c for c in tran.keys() if not c == "GLOBAL"]
            commands_aliases = [{x: tran[x]["fr"]["aliases"]} for x in commands]
            embed = discord.Embed(color=0x11ff11)
            if args == None:
                embed.url = tran["GLOBAL"]["website_url"]
                embed.title = cmd_tran["msg_list_commands"]
                commands_value = ""
                for command in commands:
                    data = tran[command][lang_server]
                    if tran[commands[0]]["type"] == tran[command]["type"]:
                        commands_value += f"- **`{prefix_server}{command} {data['usage']}` >** {data['description']}\n"
                        latest_command = command
                    else:
                        embed.add_field(name=self.emo(tran[latest_command]["type_emoji"]) + cmd_tran["msg_title_" + tran[latest_command]["type"]],
                                        value=commands_value,
                                        inline=True)
                        commands_value = f"- **`{prefix_server}{command} {data['usage']}` >** {data['description']}\n"
                embed.add_field(name=self.emo(tran[command]["type_emoji"]) + cmd_tran["msg_title_" + tran[command]["type"]],
                                value=commands_value,
                                inline=True)
                donation = cmd_tran["msg_donation"].format("https://www.paypal.me/QuentiumYT/1")
                embed.add_field(name=cmd_tran["msg_caption"],
                                value=cmd_tran["msg_caption_desc"],
                                inline=True)
                embed.add_field(name=cmd_tran["msg_warning"],
                                value=cmd_tran["msg_warning_desc"] + donation,
                                inline=True)
            else:
                if args in commands:
                    args_tran = tran[args][lang_server]
                else:
                    for x in commands_aliases:
                        command = list(x.keys())[0]
                        if x[command] and args in x[command].split("/"):
                            aliases = x[command].split("/")
                            args_tran = tran[command][lang_server]
                            break
                    else:
                        return await ctx.send(cmd_tran["msg_no_command_found"])
                embed = discord.Embed(color=0x03A678)
                embed.title = None
                desc_text = f"```{args}```\n**{args_tran['description']}**\n\n"
                desc_text += f"**{cmd_tran['msg_type']}** `{args_tran['type_name']}`\n\n"
                if args_tran["aliases"]:
                    desc_text += f"**{cmd_tran['msg_aliases']}** `{'`, `'.join(aliases)}`\n\n"
                desc_text += f"**{cmd_tran['msg_format']}** `{prefix_server}{args} {args_tran['usage']}`"
                embed.description = desc_text
            embed.set_footer(text=cmd_tran["msg_more_infos"],
                             icon_url=tran["GLOBAL"]["logo_bot"])
            return await ctx.send(embed=embed)

def setup(client):
    client.add_cog(HelpInfos(client))
