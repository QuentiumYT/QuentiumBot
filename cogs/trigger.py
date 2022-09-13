import nextcord, re
from nextcord.ext import commands
from QuentiumBot import storage, get_translations, is_owner

# Basic command configs
cmd_name = "trigger"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class TriggerAdminConfig(commands.Cog):
    """Trigger message command in Admin Config section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.guild_only()
    async def trigger_cmd(self, ctx, *, args=None):
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
            # Global embed
            embed = nextcord.Embed(color=0xBFFF11)

            # Check user perms or owner
            if not (ctx.message.author.guild_permissions.administrator or is_owner(ctx)):
                # Allow trigger list without any permissions
                if not any(x in args.lower().split() for x in ["list", "liste"]):
                    return await ctx.send(cmd_tran["msg_perm_admin_user"].format(ctx.message.author.name))
            # No args given
            if not args:
                embed.title = cmd_tran["msg_specify_trigger"].format(prefix_server)
                return await ctx.send(embed=embed)

            # Get all triggers
            triggers = await storage.get_data(self, "triggers")

            # List server's triggers
            if any(x in args.lower().split() for x in ["list", "liste"]):
                # Check if server triggers exist and is not empty
                if any(x == str(ctx.guild.id) for x in triggers.keys()) and triggers[str(ctx.guild.id)]:
                    content = "\n- ".join([x for x in triggers[str(ctx.guild.id)].keys()])
                    embed.title = cmd_tran["msg_reactions_list"].format(len(triggers[str(ctx.guild.id)].keys()))
                    embed.description = "- " + content
                else:
                    embed.title = cmd_tran["msg_no_reactions"]
                return await ctx.send(embed=embed)

            # Remove a trigger
            if any(x in args.lower().split() for x in ["remove", "delete", "clear"]):
                # No triggers given
                if len(args.split()) == 1:
                    embed.title = cmd_tran["msg_specify_trigger_delete"].format(prefix_server)
                    return await ctx.send(embed=embed)

                # Find trigger between quotes
                if args.count("'") > 1 or args.count('"') > 1:
                    filter_args = re.findall(r"\"(.+?)\"|\'(.+?)\'", args)
                    raw_args = [x[0] if x[0] != '' else x[1] for x in filter_args]
                    remove = raw_args[-1].lower()
                else:
                    remove = args.split()[-1].lower()
                # Trigger found
                if any(x.lower() == remove for x in triggers[str(ctx.guild.id)].keys()):
                    # Delete the trigger
                    del triggers[str(ctx.guild.id)][remove]
                    self.data = triggers
                    # Save the triggers data
                    await storage.dump_data(self, "triggers")
                    embed.title = cmd_tran["msg_reaction_deleted"]
                    embed.description = f"**{remove}**"
                else:
                    embed.title = cmd_tran["msg_unknown_reaction"]
                return await ctx.send(embed=embed)

            # Delete all trigger from the server
            if any(x in args.lower().split() for x in ["removeall", "deleteall", "clearall"]):
                del triggers[str(ctx.guild.id)]
                self.data = triggers
                await storage.dump_data(self, "triggers")
                embed.title = cmd_tran["msg_reaction_all_deleted"]
                return await ctx.send(embed=embed)

            # Add a trigger with two arguments
            if len(args.split()) == 2:
                if args.count("'") == 0 and args.count('"') == 0:
                    # Both arguments are valid and not between quotes
                    trigger = args.split()[0]
                    response = args.split()[1]
                else:
                    embed.title = cmd_tran["msg_not_enough_args"]
                    return await ctx.send(embed=embed)

            elif len(re.findall(r"\"(.+?)\"|\'(.+?)\'", args)) == 2:
                # If not all quotes required
                if args.count("'") < 4 and args.count('"') < 4:
                    embed.title = cmd_tran["msg_not_enough_args"]
                    return await ctx.send(embed=embed)

                # If one of two args is surrounded with quotes
                if args.count("'") % 2 == 0 or args.count('"') % 2 == 0:
                    filter_args = re.findall(r"\"(.+?)\"|\'(.+?)\'", args)
                    raw_args = [x[0] if x[0] != '' else x[1] for x in filter_args]
                    # Get the trigger
                    trigger = raw_args[0]
                    # Displays all links even images in response (if only 1 image link, displays the preview directly)
                    response = raw_args[1]
                else:
                    embed.title = cmd_tran["msg_too_many_args"]
                    return await ctx.send(embed=embed)

            # Just one arg given
            elif len(args.split()) < 2 or len(re.findall(r"\"(.+?)\"|\'(.+?)\'", args)) < 2:
                embed.title = cmd_tran["msg_not_enough_args"]
                return await ctx.send(embed=embed)
            # Multiple args given or no quotes to delimit
            else:
                embed.title = cmd_tran["msg_too_many_args"]
                return await ctx.send(embed=embed)

            # Is it the first trigger registered
            if any(x == str(ctx.guild.id) for x in triggers.keys()):
                # Trigger does not exist already
                if trigger.lower() in triggers[str(ctx.guild.id)].keys():
                    embed.title = cmd_tran["msg_trigger_exists"]
                    return await ctx.send(embed=embed)
                # Add a key
                triggers[str(ctx.guild.id)][trigger.lower()] = response
            else:
                # Create the key
                triggers[str(ctx.guild.id)] = {trigger.lower(): response}

            # Save the data in the file
            self.data = triggers
            await storage.dump_data(self, "triggers")
            embed.title = cmd_tran["msg_new_reaction"]
            # Send the trigger and the reply
            embed.add_field(name=cmd_tran["msg_trigger"],
                            value=trigger,
                            inline=True)
            embed.add_field(name=cmd_tran["msg_reply"],
                            value=response,
                            inline=True)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(TriggerAdminConfig(client))
