import discord, psutil
from discord.ext import commands
from datetime import datetime
from QuentiumBot import HandleData, get_translations, start_time

# Basic command configs
cmd_name = "botstats"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class BotstatsInfos(commands.Cog):
    """Bot stats command in Statistics section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True,
        no_pm=True
    )
    @commands.guild_only()
    async def botstats_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
            commands_server = data[1]
        else:
            lang_server = "en"
            commands_server = None
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            bot_host = cmd_tran["msg_bot_host"]
            bot_os = cmd_tran["msg_bot_os"]
            bot_owner = discord.utils.get(self.client.get_all_members(), id=self.client.owner_id)
            time = round((datetime.now() - start_time).total_seconds())
            m, s = divmod(int(time), 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            bot_uptime = f"{d} {cmd_tran['msg_day']}, {h} {cmd_tran['msg_hour']}, {m} {cmd_tran['msg_min']}, {s} {cmd_tran['msg_sec']}"
            bot_memory = psutil.virtual_memory().used >> 20
            bot_commands_get = commands_server if not commands_server == None else cmd_tran["msg_not_available"]
            bot_commands_get_total = 0

            data = await HandleData.get_data(self)
            for serv in data.keys():
                bot_commands_get_total += data[serv]["commands_server"]
            users = 0
            for serv in self.client.guilds:
                users += len(serv.members)
            bot_users_total = str(users)
            bot_servers_total = len(self.client.guilds)
            bot_lang_fr = bot_lang_en = bot_lang_de = 0
            for serv in data.keys():
                if "fr" in data[serv]["lang_server"]:
                    bot_lang_fr += 1
                elif "en" in data[serv]["lang_server"]:
                    bot_lang_en += 1
                elif "de" in data[serv]["lang_server"]:
                    bot_lang_de += 1

            embed = discord.Embed(color=0x1126FF)
            embed.url = tran["GLOBAL"]["website_url"]
            embed.set_thumbnail(url=tran["GLOBAL"]["logo_bot"])

            content = "".join(cmd_tran["msg_content"]) % (bot_host, bot_os, bot_owner, bot_uptime, bot_memory,
                                                          bot_commands_get, bot_commands_get_total, bot_users_total,
                                                          bot_servers_total, bot_lang_fr, bot_lang_en, bot_lang_de)

            embed.add_field(name=cmd_tran["msg_stats"],
                            value=content,
                            inline=True)
            embed.set_footer(text=tran["GLOBAL"][lang_server]["requested_by"].format(ctx.message.author.name),
                             icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(BotstatsInfos(client))
