import discord, json
from discord.ext import commands
from QuentiumBot import HandleData, get_translations

# Basic command configs
cmd_name = "definition"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

with open("data/definitions_sneakers.json", "r", encoding="utf-8", errors="ignore") as file:
    definitions_sneakers = json.loads(file.read(), strict=False)

class DefinitionSparse(commands.Cog):
    """Definition command in Sparse Sneakers section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.guild_only()
    async def definition_cmd(self, ctx, *, args="list"):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            await HandleData.retrieve_data(self, ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            if ctx.guild.id == 798518855529005076: # Sparse Sneakers server ID
                embed = discord.Embed(color=0x158DEE)

                if any(args == x for x in ["list", "liste", "show"]):
                    content = "- " + "\n- ".join(definitions_sneakers.keys())

                    embed.title = cmd_tran["msg_def_list"]
                    embed.description = content
                    return await ctx.send(embed=embed)

                for word, definition in definitions_sneakers.items():
                    if args.lower() == word.lower():
                        embed.set_author(name=word.title(), icon_url=tran[cmd_name]["logo_url"])
                        embed.title = definition["equivalent"]
                        embed.url = definition["url"]
                        embed.description = definition["definition"]
                        embed.set_footer(text=cmd_tran["msg_footer"])
                        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(DefinitionSparse(client))
