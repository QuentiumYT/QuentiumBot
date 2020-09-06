import discord
from discord.ext import commands
from QuentiumBot import HandleData, get_translations

# Basic command configs
cmd_name = "serverstats"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class ServerstatsInfos(commands.Cog):
    """Server stats command in Statistics section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.guild_only()
    async def serverstats_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            serv = ctx.message.guild
            serv_name = serv.name
            serv_id = serv.id
            serv_owner = serv.owner.name
            serv_owner_dis = "#" + serv.owner.discriminator
            serv_created = serv.created_at.strftime("%d.%m.%Y - %H:%M:%S")
            serv_region = str(serv.region).capitalize()
            serv_members = len(serv.members)
            serv_members_on = len([x for x in serv.members if not x.status == discord.Status.offline])
            serv_users = len([x for x in serv.members if not x.bot])
            serv_users_on = len([x for x in serv.members if not x.bot and not x.status == discord.Status.offline])
            serv_bots = len([x for x in serv.members if x.bot])
            serv_bots_on = len([x for x in serv.members if x.bot and not x.status == discord.Status.offline])
            serv_channels = len([x for x in serv.channels if not isinstance(x, discord.CategoryChannel)])
            serv_text_channels = len([x for x in serv.channels if isinstance(x, discord.TextChannel)])
            serv_voice_channels = len([x for x in serv.channels if isinstance(x, discord.VoiceChannel)])
            serv_afk_channel = cmd_tran["msg_none"] if serv.afk_channel == None else str(serv.afk_channel)
            serv_afk_time = round(serv.afk_timeout / 60)
            serv_verif_lvl = cmd_tran["msg_" + str(serv.verification_level)]
            serv_roles = len(serv.roles)
            serv_roles_list = ", ".join([x.name for x in serv.roles])
            if len(serv_roles_list) > 450:
                serv_roles_list = cmd_tran["msg_limit"]

            embed = discord.Embed(color=0x1126FF)
            embed.url = tran["GLOBAL"]["website_url"]
            icon = str(serv.icon_url)
            icon1 = icon.split(".")
            icon2 = "".join(icon1[len(icon1) - 1])
            icon3 = icon.replace(icon2, "")
            icon_url = icon3 + "png?size=1024"
            if len(serv.icon_url):
                embed.set_thumbnail(url=icon_url)
            else:
                embed.set_thumbnail(url=tran["GLOBAL"]["logo_question"])

            content = "".join(cmd_tran["msg_content"]) % (serv_name, serv_id, serv_owner, serv_owner_dis, serv_created,
                                                          serv_region, serv_members, serv_members_on, serv_users,
                                                          serv_users_on, serv_bots, serv_bots_on, serv_channels,
                                                          serv_text_channels, serv_voice_channels, serv_afk_channel,
                                                          serv_afk_time, serv_verif_lvl, serv_roles, serv_roles_list)

            embed.add_field(name=cmd_tran["msg_stats"].format(serv_name),
                            value=content + cmd_tran["msg_link_icon"].format(icon_url),
                            inline=True)
            embed.set_footer(text=tran["GLOBAL"][lang_server]["requested_by"].format(ctx.message.author.name),
                             icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(ServerstatsInfos(client))
