import discord, re
from discord.ext import commands
from QuentiumBot import HandleData, get_translations, is_owner

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
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
            prefix_server = data[3]
        else:
            lang_server = "en"
            prefix_server = "+"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            triggers = await HandleData.get_data(self, "triggers")
            embed = discord.Embed(color=0xBFFF11)

            if not(ctx.message.author.guild_permissions.administrator or is_owner(ctx)):
                if not any(x in args.lower().split() for x in ["list", "liste"]):
                    return await ctx.send(cmd_tran["msg_perm_admin_user"].format(ctx.message.author.name))
            if not args:
                embed.title = cmd_tran["msg_specify_trigger"].format(prefix_server)
                return await ctx.send(embed=embed)

            if any(x in args.lower().split() for x in ["list", "liste"]):
                if any(x == str(ctx.guild.id) for x in triggers.keys()) and triggers[str(ctx.guild.id)]:
                    content = "\n- ".join([x for x in triggers[str(ctx.guild.id)].keys()])
                    embed.title = cmd_tran["msg_reactions_list"].format(len(triggers[str(ctx.guild.id)].keys()))
                    embed.description = "- " + content
                else:
                    embed.title = cmd_tran["msg_no_reactions"]
                return await ctx.send(embed=embed)

            if any(x in args.lower().split() for x in ["remove", "delete", "clear"]):
                if len(args.split()) == 1:
                    embed.title = cmd_tran["msg_specify_trigger_delete"].format(prefix_server)
                    return await ctx.send(embed=embed)

                if '"' in args or "'" in args:
                    remove = re.findall(r'["\'](.*?)["\']', args)[-1].lower()
                else:
                    remove = args.split()[-1].lower()
                if any(x.lower() == remove for x in triggers[str(ctx.guild.id)].keys()):
                    del triggers[str(ctx.guild.id)][remove]
                    self.data = triggers
                    await HandleData.dump_data(self, "triggers")
                    embed.title = cmd_tran["msg_reaction_deleted"]
                    embed.description = f"**{remove}**"
                else:
                    embed.title = cmd_tran["msg_unknown_reaction"]
                return await ctx.send(embed=embed)

            if any(x in args.lower().split() for x in ["removeall", "deleteall", "clearall"]):
                del triggers[str(ctx.guild.id)]
                self.data = triggers
                await HandleData.dump_data(self, "triggers")
                embed.title = cmd_tran["msg_reaction_all_deleted"]
                return await ctx.send(embed=embed)

            if len(args.split()) == 2 or len(re.findall(r'["\'](.*?)["\']', args)) == 2:
                if args.count("'") > 1 or args.count('"') > 1:
                    trigger = re.findall(r'["\'](.*?)["\']', args)[0]
                    if "http://" in args or "https://" in args:
                        response = args.split()[-1].replace('"', "").replace("'", "")
                    else:
                        response = re.findall(r'["\'](.*?)["\']', args)[1]
                else:
                    trigger = args.split()[0]
                    response = args.split()[1]
            elif len(args.split()) < 2 or len(re.findall(r'["\'](.*?)["\']', args)) < 2:
                embed.title = cmd_tran["msg_not_enough_args"]
                return await ctx.send(embed=embed)
            else:
                embed.title = cmd_tran["msg_too_many_args"]
                return await ctx.send(embed=embed)

            if not any(x == str(ctx.guild.id) for x in triggers.keys()):
                triggers[str(ctx.guild.id)] = {trigger.lower(): response}
            else:
                if trigger.lower() in triggers[str(ctx.guild.id)].keys():
                    embed.title = cmd_tran["msg_trigger_exists"]
                    return await ctx.send(embed=embed)
            triggers[str(ctx.guild.id)][trigger.lower()] = response
            self.data = triggers
            await HandleData.dump_data(self, "triggers")
            embed.title = cmd_tran["msg_new_reaction"]
            embed.add_field(name=cmd_tran["msg_trigger"],
                            value=trigger,
                            inline=True)
            embed.add_field(name=cmd_tran["msg_reply"],
                            value=response,
                            inline=True)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(TriggerAdminConfig(client))
