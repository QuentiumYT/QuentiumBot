import discord, json, random
from discord.ext import commands

with open("data/config.json", "r", encoding="utf-8", errors="ignore") as file:
    config = json.loads(file.read(), strict=False)

cogs_folder = "cogs."
startup_cogs = ["help", "kick"]

def get_prefix(client, message):
    server_prefix = "-"

    if not message.guild:
        return "-"

    return commands.when_mentioned_or(server_prefix)(client, message)

client = commands.Bot(command_prefix=get_prefix,
                      description="Quentium's Public Bot",
                      owner_id=246943045105221633,
                      pm_help=True,
                      help_command=None,
                      case_insensitive=True)

@client.event
async def on_ready():
    """Bot ready event"""
    print("\n+--------------------------------------------+"
          "\n|              QuentiumBot ready!            |"
          "\n|           © 2017 - 2020 QuentiumYT         |"
          "\n+--------------------------------------------+\n")
    print("Logged in as %s#%s" % (client.user.name, client.user.discriminator))
    print("ID: " + str(client.user.id))
    return await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            name="Oh, a QuentiumBot rewite!?",
            type=discord.ActivityType.playing)
    )

@client.command()
async def load(ctx, extension):
    """Loads an extension."""
    try:
        client.load_extension(cogs_folder + extension)
    except Exception as e:
        return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
    return await ctx.send("{} loaded.".format(extension))

@client.command()
async def unload(ctx, extension):
    """Unloads an extension."""
    try:
        client.unload_extension(cogs_folder + extension)
    except Exception as e:
        return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
    return await ctx.send("{} unloaded.".format(extension))

@client.command()
async def reload(ctx, extension):
    """Reloads an extension."""
    client.unload_extension(cogs_folder + extension)
    try:
        client.load_extension(cogs_folder + extension)
    except Exception as e:
        return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
    return await ctx.send("{} reloaded.".format(extension))

if __name__ == "__main__":
    for extension in startup_cogs:
        try:
            client.load_extension(cogs_folder + extension)
        except Exception as e:
            print(f"Failed to load extension {extension}\n{type(e).__name__}: {e}.")

    client.run(config["TEST"]["token"])
