import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations, match_id

# Basic command configs
cmd_name = "msgtotal"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class MsgtotalUtilities(commands.Cog):
    """Msgtotal command in Utilities section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def msgtotal_cmd(self, ctx, *args):
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
            # if not ctx.message.channel.guild.me.guild_permissions.administrator:
            # return await ctx.send(cmd_tran["msg_perm_admin_user"])

            # If two args, first arg is member, second count type
            if len(args) == 2:
                if match_id(args[1]):
                    member = nextcord.utils.get(self.client.get_all_members(), id=match_id(args[1]))
                else:
                    return await ctx.send(cmd_tran["msg_invalid_member"])
                args = args[0]
            # If only one argument is given, check if member or count type
            elif len(args) == 1:
                if match_id(args[0]):
                    member = nextcord.utils.get(self.client.get_all_members(), id=match_id(args[0]))
                    args = "all"
                else:
                    member = ctx.message.author
                    args = args[0]
            # Else count all messages from the author
            else:
                member = ctx.message.author
                args = "all"

            if not isinstance(ctx.channel, nextcord.TextChannel):
                args = "channel"
            # Init the counter
            counter = 0
            embed = nextcord.Embed(color=0xFFA511)
            embed.title = cmd_tran["msg_calculating"]
            tmp = await ctx.send(embed=embed)

            # Loop all channels of the server
            if args == "all":
                msg_total = True
                # Channels accessible by the bot
                channel_list = [x for x in ctx.message.guild.channels if isinstance(x, nextcord.TextChannel)]
                for channel in channel_list:
                    # Count all messages in channels
                    if ctx.message.channel.permissions_for(ctx.message.author).read_messages:
                        async for log in channel.history(limit=999999):
                            if log.author == member:
                                counter += 1
            # Use the current channel
            elif args == "channel":
                msg_total = False
                # Count all messages in channels
                if ctx.message.channel.permissions_for(ctx.message.author).read_messages:
                    async for log in ctx.message.channel.history(limit=999999):
                        if log.author == member:
                            counter += 1
            # Count type is incorrect
            else:
                return await ctx.send(cmd_tran["msg_invalid_arg"].format(prefix_server))

            # Send the number of messages in an embed
            embed.title = cmd_tran["msg_number"]
            # All or Channel count type specified
            if msg_total:
                embed.description = cmd_tran["msg_has_sent_total"].format(member, counter)
            else:
                embed.description = cmd_tran["msg_has_sent_channel"].format(member, counter)
            embed.set_footer(text=tran["GLOBAL"][lang_server]["requested_by"].format(ctx.message.author.name),
                             icon_url=ctx.message.author.avatar)
            # Edit the temp message
            await tmp.edit(embed=embed)

def setup(client):
    client.add_cog(MsgtotalUtilities(client))
