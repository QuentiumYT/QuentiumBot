import discord, difflib
from discord.ext import commands
from QuentiumBot import HandleData, get_translations, is_owner

# Basic command configs
cmd_name = "role"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class RoleISM(commands.Cog):
    """Role command in Insoumis section (used in several servers)"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    @commands.guild_only()
    async def role_cmd(self, ctx, *, role=None):
        # Get specific server data
        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(self, ctx.message.guild)
        lang_server = "fr"
        cmd_tran = tran[cmd_name][lang_server]

        if not ctx.message.author.bot == True:
            if ctx.guild.id == 391272643229384705: # Insoumis server ID
                list_roles = ["Payday 2", "Diablo 3", "Gta 5", "The division", "Fortnite", "CS GO", "Farming simulator",
                              "Lol", "Dead by daylight", "Destiny 2", "Quake", "left 4 dead 2", "GRID 2", "Steep", "HL2DM",
                              "Sea of Thieves", "Monster Hunter"]

            elif ctx.guild.id == 350156033198653441: # TFI server ID
                list_roles = ["Chauffeur en Test", "Ami"]

            elif ctx.guild.id == 509028174013923339: # Solumon server ID
                list_roles = ["Payday 2", "Joueur", "Gmod"]

            elif ctx.guild.id == 319533759894388736: # Exos_Team server ID
                if any(x == ctx.message.author.id for x in is_owner(ctx)):
                    if not role:
                        return await ctx.message.delete()
                    role = discord.utils.get(ctx.message.guild.roles, name=role)
                    if role in ctx.message.author.roles:
                        return await ctx.message.author.remove_roles(role)
                    else:
                        return await ctx.message.author.add_roles(role)
            else:
                return await ctx.send(cmd_tran["msg_not_enabled"])

            # No role given
            if not role:
                return await ctx.send(cmd_tran["msg_specify_role"].format(", ".join(list_roles)))

            # List all the roles of the server
            if "list" in role.lower(): # List for english and french
                return await ctx.send(cmd_tran["msg_list_role"].format(", ".join(list_roles)))

            # Find the closest match of the arg compared to all roles
            lower_match = difflib.get_close_matches(role.lower(),
                                                    [x.lower() for x in list_roles],
                                                    n=1,
                                                    cutoff=0)
            # List of close matches
            rolename = [x for x in list_roles if x.lower() == lower_match[0]]
            # Get the role object with the first match
            role = discord.utils.get(ctx.message.guild.roles, name=rolename[0])
            if not role:
                return await ctx.send(cmd_tran["msg_unknown_role"])
            # Role is in the available role list
            if any(x in role.name for x in list_roles):
                # If user already have the role, remove the role
                if role in ctx.message.author.roles:
                    await ctx.message.author.remove_roles(role)
                    await ctx.send(cmd_tran["msg_role_removed"].format(role.name))
                # Add the role
                else:
                    await ctx.message.author.add_roles(role)
                    await ctx.send(cmd_tran["msg_role_added"].format(role.name))
            else:
                await ctx.send(cmd_tran["msg_role_not_allowed"])

def setup(client):
    client.add_cog(RoleISM(client))
