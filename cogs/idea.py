import discord
from discord.ext import commands
from datetime import datetime
from QuentiumBot import HandleData, get_translations

# Basic command configs
cmd_name = "idea"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class IdeaFeedback(commands.Cog):
    """Idea command in Feedback section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    # 2 commands every minute
    @commands.cooldown(2, 60, commands.BucketType.channel)
    async def idea_cmd(self, ctx, *, args=None):
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
            cmd_received = ctx.message.content.replace(prefix_server, "").split()[0]
            # No idea or bug given
            if not args:
                if "ide" in cmd_received: # ide for idea and idee (french)
                    return await ctx.send(cmd_tran["msg_specify_idea"])
                elif "bug" in cmd_received:
                    return await ctx.send(cmd_tran["msg_specify_bug"])
            # Join feedback details
            ideas = " --- ".join([datetime.now().strftime("%d.%m.%Y - %H:%M:%S"),
                                  ctx.message.author.name + ctx.message.author.discriminator,
                                  cmd_received,
                                  args])
            with open("feedback.txt", "a", encoding="utf-8", errors="ignore") as file:
                file.write(ideas + "\n")
            await ctx.send(cmd_tran["msg_thanks"])

def setup(client):
    client.add_cog(IdeaFeedback(client))
