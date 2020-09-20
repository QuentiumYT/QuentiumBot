import discord, json, os
from discord.ext import commands
from QuentiumBot import HandleData, get_translations

# Basic command configs
cmd_name = "vote"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class VoteFLC(commands.Cog):
    """Vote command in France Les Cités section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def vote_cmd(self, ctx, *, args=None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if ctx.guild.id == 371687157817016331:  # France Les Cités server ID
                # Delete the message to keep the vote anonym
                await ctx.message.delete()
                vote_file = "data/flc_votes.txt"
                # Init the file with max voting number
                if not os.path.isfile(vote_file):
                    f = open(vote_file, "w")
                    f.write("0")
                    f.close()

                # Get the file content
                with open(vote_file, "r", encoding="utf-8") as file:
                    content = file.readlines()

                # Cityzoo / Scant / Quentium user ID
                authorized = [348509601936834561, 358214022115360771, 246943045105221633]
                if any(x == ctx.message.author.id for x in authorized):
                    # No args given
                    if not args:
                        return await ctx.message.author.send(cmd_tran["msg_no_args"])

                    # Using votemax command
                    if "votemax" in ctx.message.content:
                        if args:
                            # Set the first line to the max number of voting participants
                            content[0] = f"{args}\n"
                            with open(vote_file, "w", encoding="utf-8") as file:
                                file.write("".join(content))
                            return await ctx.message.author.send(cmd_tran["msg_votemax_set"].format(args))

                    # Using voteresults command
                    if "voteresults" in ctx.message.content:
                        embed = discord.Embed(color=0x11FF11)
                        embed.title = cmd_tran["msg_results"]
                        final = []
                        with open(vote_file, "r", encoding="utf-8") as file:
                            # Get results except first line
                            results = file.readlines()[1:]
                        for x in results:
                            a = x.strip().split(" --> ")[1]
                            final.append(a)
                        # Create a sorted dict of results
                        d = {}
                        [d.update({i: d.get(i, 0) + 1}) for i in final]
                        e = sorted(d.items(), key=lambda x: x[1], reverse=True)
                        for y in range(len(e)):
                            # Display the place and the number of votes
                            embed.add_field(name=cmd_tran["msg_place"].format(y + 1),
                                            value=cmd_tran["msg_votes"].format(e[y][0], e[y][1]),
                                            inline=True)
                        return await ctx.send(embed=embed)

                # Not a number
                if not args.isdigit():
                    return await ctx.message.author.send(cmd_tran["msg_wrong_arg"])

                # Vote is bigger than the number of participants
                if int(args) > int(content[0]):
                    return await ctx.message.author.send(cmd_tran["msg_number_too_high"])

                # Member has already voted
                if str(ctx.message.author.id) in content:
                    return await ctx.message.author.send(cmd_tran["msg_already_voted"])

                # Add the vote to the file
                with open(vote_file, "a", encoding="utf-8") as file:
                    file.write(f"{ctx.message.author.id} --► {args}\n")
                    return await ctx.message.author.send(cmd_tran["msg_voted"].format(args))


def setup(client):
    client.add_cog(VoteFLC(client))
