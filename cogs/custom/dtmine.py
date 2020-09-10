import discord, json
from discord.ext import commands
from QuentiumBot import HandleData, get_translations

# Basic command configs
cmd_name = "dtmine"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

with open("data/dt_mines.json", "r", encoding="utf-8", errors="ignore") as file:
    dt_mines = json.loads(file.read(), strict=False)

with open("data/dt_aliases.json", "r", encoding="utf-8", errors="ignore") as file:
    dt_aliases = json.loads(file.read(), strict=False)

class DtmineFLC(commands.Cog):
    """DeepTown mine command in France Les Cités section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def dtmine_cmd(self, ctx, *args):
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
            # No args given
            if not args:
                return await ctx.send(cmd_tran["msg_specify_ore"].format(prefix_server))

            ore = args[0].lower()
            if len(args) == 2 and args[1].isdigit():
                max_depth = int(args[1])
            else:
                max_depth = 120

            # Find ore alias
            if ore in dt_aliases.keys():
                ore = dt_aliases[ore]
            # List of all existing ores
            all_ores = dt_mines["0"].keys()
            # Check if ore is in the JSON file
            if ore not in all_ores:
                return await ctx.send(cmd_tran["msg_ore_dont_exist"].format(ore))

            # Area does not contain ore
            for area in dt_mines.keys():
                for ore_name in all_ores:
                    if dt_mines[area].get(ore_name) is None:
                        dt_mines[area].update({ore_name: 0})

            # Max sector, if set
            if max_depth == 120:
                text = cmd_tran["msg_top_10"].format(ore)
            else:
                text = cmd_tran["msg_top_10_sector"].format(ore, max_depth)
            i = 0
            ordered_mines = [(k, v) for k, v in dt_mines.items()]
            ordered_mines.sort(key=lambda x: x[1][ore], reverse=True)
            for mine in ordered_mines:
                # Get only 10 results
                if i >= 10:
                    break
                # Skip the 0 key with ores
                if mine[0] == "0":
                    continue
                # Ore in sector is zero
                if mine[1][ore] == 0:
                    continue
                # Sector is lower than given one
                if int(mine[0]) <= max_depth:
                    # Percentage too low or platinum rate
                    if mine[1][ore] < 0.01 and ore != "platinum":
                        break
                    # Center the sector digits
                    text += mine[0].center(3, " ")
                    # Ore percentage
                    text += " : " + str(round(mine[1][ore] * 100, 2)) + "%\n"
                else:
                    continue
                i += 1
            text += "```"
            await ctx.send(text)

def setup(client):
    client.add_cog(DtmineFLC(client))
