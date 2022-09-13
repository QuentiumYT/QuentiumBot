import nextcord, asyncio, random
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

# Basic command configs
cmd_name = "move"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class MoveAdminRights(commands.Cog):
    """Move command in Administration Rights section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.guild_only()
    async def move_cmd(self, ctx, *, number=None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Check user perms
            if not ctx.message.author.guild_permissions.move_members:
                return await ctx.send(cmd_tran["msg_perm_move_user"].format(ctx.message.author.name))
            # Check bot perms
            if not ctx.message.guild.me.guild_permissions.move_members:
                return await ctx.send(cmd_tran["msg_perm_move_bot"])

            # Get a lit with all server channels
            channel_list = [x for x in ctx.message.guild.channels if isinstance(x, nextcord.VoiceChannel)]
            # Argument is random, move in random channel 5 or more times
            if number and "random" in number:
                if number == "random":
                    nb_times = 5
                else:
                    nb_times = int(number.split("random ")[1])
                nb_times = nb_times if nb_times < 20 else 20
                random_numbers = []
                list_members = []
                temp = 0
                while len(random_numbers) < nb_times:
                    random_numbers.append(random.randint(1, len(channel_list)))
                    if random_numbers[-1] == 2 or temp == random_numbers[-1]:
                        random_numbers = random_numbers[:-1]
                    if len(random_numbers) >= 1:
                        temp = random_numbers[-1]
                for member in ctx.message.author.voice.channel.members:
                    list_members.append(member)
                for channel_number in random_numbers:
                    for member in list_members:
                        await member.edit(voice_channel=channel_list[channel_number - 1])
                        await asyncio.sleep(0.1)
                await ctx.message.delete()
            # Move into a specific channel (using it's position)
            elif number and number.isdigit():
                if not len(channel_list) == 0:
                    if not int(number) > len(channel_list):
                        channel = channel_list[int(number[0]) - 1]
                        if not ctx.message.author.voice == None:
                            if channel.id != ctx.message.author.voice.channel.id:
                                await ctx.send(cmd_tran["msg_moving_into"].format(channel))
                                list_members = []
                                for member in ctx.message.author.voice.channel.members:
                                    list_members.append(member)
                                for member in list_members:
                                    await member.edit(voice_channel=channel)
                            else:
                                await ctx.send(cmd_tran["msg_same_channel"])
                        else:
                            await ctx.send(cmd_tran["msg_not_in_channel"])
                    else:
                        await ctx.send(cmd_tran["msg_number_no_channel"])
                else:
                    await ctx.send(cmd_tran["msg_no_voice_channel"])
            # List the channel list position
            else:
                embed = nextcord.Embed(color=0x3498DB)
                embed.title = cmd_tran["msg_voice_channels"]
                embed.description = cmd_tran["msg_specify_channel"]
                channel_no = 0
                for channel in channel_list:
                    channel_no += 1
                    embed.description += "{}. {}\n".format(channel_no, channel)
                await ctx.send(embed=embed)

def setup(client):
    client.add_cog(MoveAdminRights(client))
