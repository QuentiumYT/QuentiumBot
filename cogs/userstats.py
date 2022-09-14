import nextcord
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

# Basic command configs
cmd_name = "userstats"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class UserstatsInfos(commands.Cog):
    """User stats command in Statistics section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def userstats_cmd(self, ctx, *, member: nextcord.Member = None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # No member, using the author
            if not member:
                member = ctx.message.author
            # Get some informations
            user_name = member.name
            user_nickname = cmd_tran["msg_any"] if member.nick == None else member.nick
            user_id = member.id
            user_tag = member.name + "#" + member.discriminator
            user_mention = member.mention
            user_is_bot = cmd_tran["msg_yes"] if member.bot == True else cmd_tran["msg_no"]
            user_status = cmd_tran["msg_" + str(member.status)]
            user_game = cmd_tran["msg_any"] if member.activity == None else member.activity.name
            user_joinserv = member.joined_at.strftime("%d.%m.%Y - %H:%M:%S")
            user_joindiscord = member.created_at.strftime("%d.%m.%Y - %H:%M:%S")
            user_best_role = str(member.top_role)
            user_roles = len(member.roles)
            user_roles_list = ", ".join([x.name for x in member.roles])

            # Send an embed with details
            embed = nextcord.Embed(color=0x1126FF)
            icon = str(member.avatar)
            icon1 = icon.split(".")
            icon2 = "".join(icon1[len(icon1) - 1])
            icon3 = icon.replace(icon2, "")
            avatar = icon3 + "png?size=1024"
            # If member avatar is not found use the default avatar
            if member.avatar:
                embed.set_thumbnail(url=avatar)
            else:
                embed.set_thumbnail(url=member.default_avatar)
             # Using translation list and append data
            content = "".join(cmd_tran["msg_content"]) % (user_name, user_nickname, user_id, user_tag, user_mention,
                                                          user_is_bot, user_status, user_game, user_joinserv,
                                                          user_joindiscord, user_best_role, user_roles, user_roles_list)
            embed.add_field(name=cmd_tran["msg_stats"].format(user_name),
                            value=content + cmd_tran["msg_link_icon"].format(avatar),
                            inline=True)
            embed.set_footer(text=tran["GLOBAL"][lang_server]["requested_by"].format(user_name),
                             icon_url=ctx.message.author.avatar)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(UserstatsInfos(client))
