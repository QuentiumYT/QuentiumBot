import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations, is_owner

# Basic command configs
cmd_name = "help"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class HelpInfos(commands.Cog):
    """Help command in Information section"""

    def __init__(self, client):
        self.client = client

    # Function to turn a text emoji into its object
    def emo(self, text):
        return str(nextcord.utils.get(self.client.emojis, name=text))

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def help_cmd(self, ctx, *, args=None):
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
            def allow_type(cmd):
                if any(tran[cmd]["type"] == x for x in ["flc", "ism", "theswe", "sparse", "quentium"]):
                    if tran[cmd]["type"] == "flc" and ctx.guild.id == 371687157817016331: # France Les Cités server ID
                        return False
                    if tran[cmd]["type"] == "ism" and ctx.guild.id == 391272643229384705: # Insoumis server ID
                        return False
                    if tran[cmd]["type"] == "sparse" and ctx.guild.id == 798518855529005076: # SparseSneakers server ID
                        return False
                    if tran[cmd]["type"] == "theswe" and ctx.guild.id == 199189022894063627: # TheSweMaster server ID
                        return False
                    if tran[cmd]["type"] == "quentium" and is_owner(ctx):
                        return False
                    return True
            # Create a list of all commands
            commands = [c for c in tran.keys() if not c.isupper() if not allow_type(c)]
            # Create a dict of commands with subcommands
            commands_aliases = [{x: tran[x]["fr"]["aliases"]} for x in commands]
            # List all commands if no arguments
            if not args:
                embed = nextcord.Embed(color=0x11FF11)
                embed.url = tran["GLOBAL"]["website_url"]
                embed.title = cmd_tran["msg_list_commands"]
                embed.description = cmd_tran["msg_details"].format(prefix_server)
                commands_value = ""
                latest_command = commands[0]
                # Loop existing commands
                for command in commands:
                    data = tran[command][lang_server]
                    # Check if category is ended for embed fields
                    if tran[latest_command]["type"] != tran[command]["type"]:
                        first_section_cmd = command
                        # Create a field for each category
                        embed.add_field(name=self.emo(tran[latest_command]["type_emoji"]) + cmd_tran["msg_title_" + tran[latest_command]["type"]],
                                        value=commands_value,
                                        inline=True)
                        # Initialise the value to the first command of type
                        if data["usage"]:
                            commands_value = f"- **`{prefix_server}{command} {data['usage']}` >** {data['description']}\n"
                        else:
                            commands_value = f"- **`{prefix_server}{command}` >** {data['description']}\n"
                    else:
                        if data["usage"]:
                            commands_value += f"- **`{prefix_server}{command} {data['usage']}` >** {data['description']}\n"
                        else:
                            commands_value += f"- **`{prefix_server}{command}` >** {data['description']}\n"

                    # Last command, adding last field
                    if command == commands[-1]:
                        embed.add_field(name=self.emo(tran[first_section_cmd]["type_emoji"]) + cmd_tran["msg_title_" + tran[command]["type"]],
                                        value=commands_value,
                                        inline=True)
                    latest_command = command

                # Add the caption field
                embed.add_field(name=cmd_tran["msg_caption"],
                                value=cmd_tran["msg_caption_desc"],
                                inline=True)
                # Format the link to allow discord markdown
                donation = cmd_tran["msg_donation"].format("https://www.paypal.me/QuentiumYT/1")
                # Add the warning field
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
                embed = nextcord.Embed(color=0x03A678)
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
                # Add a field with usage if exists
                if args_tran["usage"]:
                    desc_text += f"**{cmd_tran['msg_format']}** `{prefix_server}{args} {args_tran['usage']}`\n\n"
                else:
                    desc_text += f"**{cmd_tran['msg_format']}** `{prefix_server}{args}`\n\n"
                # Adds an example if provided
                if args_tran["example"]:
                    desc_text += f"**{cmd_tran['msg_example']}** `{prefix_server}{args} {args_tran['example']}`"
                embed.description = desc_text
            embed.set_footer(text=cmd_tran["msg_more_infos"],
                             icon_url=tran["GLOBAL"]["logo_bot"])
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(HelpInfos(client))
