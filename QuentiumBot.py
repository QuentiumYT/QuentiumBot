import discord, json, os
from discord.ext import commands
from datetime import datetime

# Defines if the bot is under debug or not
debug = True
# Folder containing all cogs
cogs_folder = "cogs."
startup_cogs = [f.replace('.py', '') for f in os.listdir(cogs_folder) if os.path.isfile(os.path.join(cogs_folder, f))]

# TYPE Data class

class GetData:
    """Get global data from files"""

    # Get the configuration for tokens and credidentials
    def get_config(self, section, key):
        with open("data/config.json", "r", encoding="utf-8", errors="ignore") as file:
            self.config = json.loads(file.read(), strict=False)
        return self.config[section][key]

    # Get all translations from the file
    def get_translations(self):
        with open("data/translations.json", "r", encoding="utf-8", errors="ignore") as file:
            self.translations = json.loads(file.read(), strict=False)
        return self.translations

    # Get all parameters from the server or create new entry
    async def retrieve_data(self, server):
        self.server_id = str(server.id)

        with open("data/data.json", "r", encoding="utf-8", errors="ignore") as file:
            self.data = json.loads(file.read(), strict=False)

        # Check if server id exists
        if any(x == self.server_id for x in self.data.keys()):
            self.lang_server = self.data[self.server_id]["lang_server"]
            self.commands_server = self.data[self.server_id]["commands_server"] + 1
            self.data[self.server_id]["name_server"] = server.name
            self.data[self.server_id]["commands_server"] = self.commands_server
            self.autorole_server = self.data[self.server_id]["autorole_server"]
            self.prefix_server = self.data[self.server_id]["prefix_server"]
        else:
            self.lang_server = "fr"
            self.commands_server = 1
            self.autorole_server = None
            self.prefix_server = "+"
            self.data[self.server_id] = {}
            self.data[self.server_id]["name_server"] = server.name
            self.data[self.server_id]["lang_server"] = self.lang_server
            self.data[self.server_id]["commands_server"] = self.commands_server
            self.data[self.server_id]["autorole_server"] = self.autorole_server
            self.data[self.server_id]["prefix_server"] = self.prefix_server

        # Dump the parameters / stats
        with open("data/data.json", "w", encoding="utf-8", errors="ignore") as file:
            json.dump(self.data, file, indent=4)
        # Return the server informations
        return self.lang_server, self.commands_server, self.autorole_server, self.prefix_server

# TYPE Bot init

async def get_prefix(client, message):
    if message.guild:
        data = await GetData.retrieve_data(client, message.guild)
        server_prefix = data[-1]
    else:
        server_prefix = "+"

    return commands.when_mentioned_or(server_prefix)(client, message)

# Create a bot instance
client = commands.Bot(command_prefix=get_prefix,
                      description="Quentium's Public Bot",
                      owner_id=246943045105221633,
                      pm_help=True,
                      help_command=None,
                      case_insensitive=True)

# TYPE Global events

@client.event
async def on_ready():
    """Bot ready event"""
    print("\n+--------------------------------------------+"
          "\n|              QuentiumBot ready!            |"
          "\n|           © 2017 - 2020 QuentiumYT         |"
          "\n+--------------------------------------------+\n")
    print("Logged in as %s#%s" % (client.user.name, client.user.discriminator))
    print("ID: " + str(client.user.id))
    start_time = datetime.now()
    print("\nStarting at: " + start_time.strftime("%d.%m.%Y - %H:%M:%S"))
    return await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            name="Oh, a QuentiumBot rewite!?",
            type=discord.ActivityType.playing)
    )

# TYPE Global commands

@client.command(hidden=True)
async def load(ctx, extension):
    """Loads an extension."""
    if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
        try:
            client.load_extension(cogs_folder + extension)
        except Exception as e:
            return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
        return await ctx.send("{} loaded.".format(extension))

@client.command(hidden=True)
async def unload(ctx, extension):
    """Unloads an extension."""
    if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
        try:
            client.unload_extension(cogs_folder + extension)
        except Exception as e:
            return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
        return await ctx.send("{} unloaded.".format(extension))

@client.command(hidden=True)
async def reload(ctx, extension):
    """Reloads an extension."""
    if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
        client.unload_extension(cogs_folder + extension)
        try:
            client.load_extension(cogs_folder + extension)
        except Exception as e:
            return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
        return await ctx.send("{} reloaded.".format(extension))

# TYPE Start

if __name__ == "__main__":
    for extension in startup_cogs:
        try:
            client.load_extension(cogs_folder + extension)
        except Exception as e:
            print(f"Failed to load extension {extension}\n{type(e).__name__}: {e}.")

    if debug:
        client.run(GetData.get_config(client, "TEST", "token"))
    else:
        client.run(GetData.get_config(client, "PUBLIC", "token"))
