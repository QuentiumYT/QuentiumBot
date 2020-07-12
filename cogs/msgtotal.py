import discord, asyncio
from discord.ext import commands
from QuentiumBot import GetData, get_translations

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
        pass_context=True,
        no_pm=False
    )
    async def msgtotal_cmd(self, ctx, *args):
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
            # if not ctx.message.channel.guild.me.guild_permissions.administrator:
            # return await ctx.send(cmd_tran["msg_perm_admin_user"])
            if len(args) == 2:
                member = discord.utils.get(client.get_all_members(), id=str(args[1])[2:-1])
                args = args[0]
            elif len(args) == 1:
                args = args[0]
                if str(args)[2:-1].isdigit():
                    member = discord.utils.get(client.get_all_members(), id=str(args)[2:-1])
                    args = "all"
                elif not args == "all" and not args == "channel":
                    return await ctx.send(cmd_tran["msg_invalid_arg"].format(prefix_server))
                else:
                    member = ctx.message.author
            else:
                member = ctx.message.author
                args = "all"

            if not isinstance(ctx.channel, discord.TextChannel):
                args = "channel"
            counter = 0
            embed = discord.Embed(color=0xFFA511)
            embed.title = cmd_tran["msg_calculating"]
            tmp = await ctx.send(embed=embed)

            if args == "":
                args = "all"
            if args == "all":
                msg_total = True
                channel_list = [x for x in ctx.message.guild.channels if isinstance(x, discord.TextChannel)]
                for channel in channel_list:
                    if ctx.message.guild.me.permissions_in(channel).read_messages:
                        async for log in channel.history(limit=999999):
                            if log.author == member:
                                counter += 1
            elif args == "channel":
                msg_total = False
                if ctx.message.guild.me.permissions_in(ctx.message.channel).read_messages:
                    async for log in ctx.message.channel.history(limit=999999):
                        if log.author == member:
                            counter += 1
            else:
                return await ctx.send(cmd_tran["msg_invalid_arg"].format(prefix_server))

            embed = discord.Embed(color=0xFFA511)
            embed.title = cmd_tran["msg_number"]
            if msg_total == True:
                embed.description = cmd_tran["msg_has_sent_total"].format(member, counter)
            else:
                embed.description = cmd_tran["msg_has_sent_channel"].format(member, counter)
            embed.set_footer(text=tran["GLOBAL"][lang_server]["asked_by"].format(ctx.message.author.name),
                             icon_url=ctx.message.author.avatar_url)

            if not isinstance(ctx.channel, discord.TextChannel):
                return await tmp.edit(embed=embed)
            await tmp.edit(embed=embed)

def setup(client):
    client.add_cog(MsgtotalUtilities(client))
