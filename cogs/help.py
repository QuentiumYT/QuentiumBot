import discord
from discord.ext import commands
from QuentiumBot import GetData, get_translations

# Basic command configs
cmd_name = "help"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class HelpInfos(commands.Cog):
    """Help command in Informations section"""

    def __init__(self, client):
        self.client = client

    # Function to turn a text emoji into its object
    def emo(self, text):
        return str(discord.utils.get(self.client.emojis, name=text))

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=False
    )
    async def help_cmd(self, ctx, *, args=None):
        global aliases
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
            # Create a list of all commands
            commands = [c for c in tran.keys() if not c in ["GLOBAL", "ERRORS"]]
            # Create a dict of commands with subcommands
            commands_aliases = [{x: tran[x]["fr"]["aliases"]} for x in commands]
            embed = discord.Embed(color=0x11ff11)
            # List all commands
            if args == None:
                embed.url = tran["GLOBAL"]["website_url"]
                embed.title = cmd_tran["msg_list_commands"]
                embed.description = cmd_tran["msg_details"].format(prefix_server)
                commands_value = ""
                latest_command = commands[0]
                # Loop existing commands
                for command in commands:
                    data = tran[command][lang_server]
                    # Check if category is ended for embed fields
                    if tran[latest_command]["type"] == tran[command]["type"]:
                        commands_value += f"- **`{prefix_server}{command} {data['usage']}` >** {data['description']}\n"
                    else:
                        # Create a field for each category
                        embed.add_field(name=self.emo(tran[latest_command]["type_emoji"]) + cmd_tran["msg_title_" + tran[latest_command]["type"]],
                                        value=commands_value,
                                        inline=True)
                        commands_value = f"- **`{prefix_server}{command} {data['usage']}` >** {data['description']}\n"
                        latest_command = command
                embed.add_field(name=self.emo(tran[command]["type_emoji"]) + cmd_tran["msg_title_" + tran[command]["type"]],
                                value=commands_value,
                                inline=True)
                embed.add_field(name=cmd_tran["msg_caption"],
                                value=cmd_tran["msg_caption_desc"],
                                inline=True)
                # Format the link to allow discord markdown
                donation = cmd_tran["msg_donation"].format("https://www.paypal.me/QuentiumYT/1")
                embed.add_field(name=cmd_tran["msg_warning"],
                                value=cmd_tran["msg_warning_desc"].format(prefix_server) + donation,
                                inline=True)

            # List details of a specific command
            else:
                # Command is the main command
                if args in commands:
                    args_tran = tran[args][lang_server]
                    command = args
                # Find the main command using the alias
                else:
                    for x in commands_aliases:
                        # Get dict key name
                        command = list(x.keys())[0]
                        # If alias exists get main command
                        if x[command] and args in x[command].split("/"):
                            aliases = x[command].split("/")
                            args_tran = tran[command][lang_server]
                            break
                    # Argument is not a command or subcommand
                    else:
                        return await ctx.send(cmd_tran["msg_no_command_found"])
                embed = discord.Embed(color=0x03A678)
                embed.title = cmd_tran["msg_title"]
                embed.url = tran["GLOBAL"]["website_url"]
                desc_text = f"```{args}```\n"
                desc_text += f"{self.emo(tran[command]['type_emoji'])} | **{args_tran['description']}**\n\n"
                desc_text += f"**{cmd_tran['msg_type']}** `{args_tran['type_name']}`\n\n"
                # List command aliases if exists
                if args_tran["aliases"]:
                    aliases = args_tran["aliases"].split("/")
                    if args in aliases:
                        aliases.remove(args)
                        aliases.append(command)
                    desc_text += f"**{cmd_tran['msg_aliases']}** `{'`, `'.join(aliases)}`\n\n"
                desc_text += f"**{cmd_tran['msg_format']}** `{prefix_server}{args} {args_tran['usage']}`\n\n"
                if args_tran["example"]:
                    desc_text += f"**{cmd_tran['msg_example']}** `{prefix_server}{args} {args_tran['example']}`"
                embed.description = desc_text
            embed.set_footer(text=cmd_tran["msg_more_infos"],
                             icon_url=tran["GLOBAL"]["logo_bot"])
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(HelpInfos(client))
