import discord
from discord.ext import commands
from QuentiumBot import HandleData, get_translations

# Basic command configs
cmd_name = "listservers"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class ListserversInfos(commands.Cog):
    """List servers command in Information section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def listservers_cmd(self, ctx):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if not ctx.message.guild.id == 264445053596991498: # DBL ID
                # Get the raw data
                data = await HandleData.get_data(self, "data")
                # Get all the servers the bot is in
                serv_id = [str(server.id) for server in self.client.guilds]
                serv_id_exist = []
                serv_pos = []

                # For each server, get the server and it's position
                for serv in data.keys():
                    for server in serv_id:
                        if server == serv:
                            serv_pos.append(list(data).index(serv))
                            serv_id_exist.append(server)

                # 2 embeds needed
                content = content2 = cmd_tran["msg_server_pos"]
                for pos in range(len(serv_id_exist)):
                    # Append the name and the postion to content
                    if len(content) < 2000:
                        content += "\n- " + str(self.client.get_guild(int(serv_id_exist[pos]))) + " | " + str(serv_pos[pos])
                    else:
                        content2 += "\n- " + str(self.client.get_guild(int(serv_id_exist[pos]))) + " | " + str(serv_pos[pos])

                embed = discord.Embed(color=0xFF9111)
                embed.title = cmd_tran["msg_servers"].format(len(self.client.guilds))
                embed.description = content
                await ctx.send(embed=embed)
                # Second embed empty
                if content2 != cmd_tran["msg_server_pos"]:
                    embed2 = discord.Embed(color=0xFF9111)
                    embed2.title = None
                    embed2.description = content2
                    await ctx.send(embed=embed2)

def setup(client):
    client.add_cog(ListserversInfos(client))
