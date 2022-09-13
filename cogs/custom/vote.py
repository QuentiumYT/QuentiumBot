import nextcord, os
from nextcord.ext import commands
from QuentiumBot import storage, get_translations

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
        # Add hidden aliases
        aliases=aliases + ["participants", "voteresults"],
        pass_context=True
    )
    @commands.guild_only()
    async def vote_cmd(self, ctx, *, args=None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if True: # France Les Cités server ID
                # No args given
                if not args and not "voteresults" in ctx.message.content:
                    return await ctx.message.author.send(cmd_tran["msg_no_args"])

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
                    # Using participants command
                    if "participants" in ctx.message.content:
                        if args:
                            # Set the first line to the max number of voting participants
                            content[0] = f"{args}\n"
                            with open(vote_file, "w", encoding="utf-8") as file:
                                file.write("".join(content))
                            return await ctx.message.author.send(cmd_tran["msg_participants_set"].format(args))

                    # Using voteresults command
                    if "voteresults" in ctx.message.content:
                        embed = nextcord.Embed(color=0x11FF11)
                        embed.title = cmd_tran["msg_results"]
                        final = []
                        with open(vote_file, "r", encoding="utf-8") as file:
                            # Get results except first line
                            results = file.readlines()[1:]
                        for x in results:
                            a = x.strip().split(" --► ")[1]
                            final.append(a)
                        # Create a sorted dict of results
                        vote_count = {}
                        [vote_count.update({i: vote_count.get(i, 0) + 1}) for i in final]
                        sorted_vote_count = sorted(vote_count.items(), key=lambda x: x[1], reverse=True)
                        for i in range(len(sorted_vote_count)):
                            # Display the place and the number of votes
                            embed.add_field(name=cmd_tran["msg_place"].format(i + 1),
                                            value=cmd_tran["msg_votes"].format(sorted_vote_count[i][0], sorted_vote_count[i][1]),
                                            inline=True)
                        return await ctx.send(embed=embed)

                # Not a number
                if not args.isdigit():
                    return await ctx.message.author.send(cmd_tran["msg_wrong_arg"])

                # Vote max is not defined
                if int(content[0]) == 0:
                    os.remove(vote_file)
                    return await ctx.message.author.send(cmd_tran["msg_max_not_defined"])

                # Vote is bigger than the number of participants
                if int(args) > int(content[0]):
                    return await ctx.message.author.send(cmd_tran["msg_number_too_high"])

                # Member has already voted
                if any(str(ctx.message.author.id) in x for x in content):
                    return await ctx.message.author.send(cmd_tran["msg_already_voted"])

                # Add the vote to the file
                with open(vote_file, "a", encoding="utf-8") as file:
                    file.write(f"{ctx.message.author.id} --► {args}\n")
                    return await ctx.message.author.send(cmd_tran["msg_voted"].format(args))


def setup(client):
    client.add_cog(VoteFLC(client))
