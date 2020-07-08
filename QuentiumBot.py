import discord, json, random
from discord.ext import commands
from datetime import datetime

debug = True
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
    start_time = datetime.now()
    print("\nStarting at: " + start_time.strftime("%d.%m.%Y - %H:%M:%S"))
    return await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            name="Oh, a QuentiumBot rewite!?",
            type=discord.ActivityType.playing)
    )

class GetData:
    def get_config(self, section, key):
        with open("data/config.json", "r", encoding="utf-8", errors="ignore") as file:
            self.config = json.loads(file.read(), strict=False)
        return self.config[section][key]

    def get_translations(self):
        with open("data/translations.json", "r", encoding="utf-8", errors="ignore") as file:
            self.translations = json.loads(file.read(), strict=False)
        return self.translations

    async def retrieve_data(self, server):
        self.server_id = str(server.id)

        with open("data/data.json", "r", encoding="utf-8", errors="ignore") as file:
            self.data = json.loads(file.read(), strict=False)

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
            self.data[self.server_id]["name_server"] = server.name
            self.data[self.server_id]["lang_server"] = self.lang_server
            self.data[self.server_id]["commands_server"] = self.commands_server
            self.data[self.server_id]["autorole_server"] = self.autorole_server
            self.data[self.server_id]["prefix_server"] = self.prefix_server

        with open("data/data.json", "w", encoding="utf-8", errors="ignore") as file:
            json.dump(self.data, file, indent=4)
        return self.lang_server, self.commands_server, self.autorole_server, self.prefix_server



# TYPE Global commands

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

    client.run(GetData.get_config(client, "TEST", "token"))
