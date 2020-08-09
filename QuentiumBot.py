import discord, json, os
from discord.ext import commands
from datetime import datetime

# Defines if the bot is under debug or not
debug = True
# Folder containing all cogs
cogs_folder = "cogs."
startup_cogs = [f.replace(".py", "") for f in os.listdir(cogs_folder) if os.path.isfile(os.path.join(cogs_folder, f))]
start_time = datetime.now()

# TYPE Data class

# Get the configuration for tokens and credidentials
def get_config(section, key):
    with open("data/config.json", "r", encoding="utf-8", errors="ignore") as file:
        config = json.loads(file.read(), strict=False)
    return config[section][key]

# Get all translations from the file
def get_translations(*args):
    with open("data/translations.json", "r", encoding="utf-8", errors="ignore") as file:
        translations = json.loads(file.read(), strict=False)
    if args:
        for subkey in args:
            translations = translations[subkey]
    return translations

# Match a user id depending on mention or raw ID
def match_user(user_id):
    if "<@!" in user_id:
        if len(user_id) == 22:
            return int(user_id[3:-1])
    elif "<@" in user_id:
        if len(user_id) == 21:
            return int(user_id[2:-1])
    elif user_id.isdigit():
        if len(user_id) == 18:
            return int(user_id)
    else:
        return False

class GetData:
    """Get global data from storage file"""

    # Get all parameters from the server or create new entry
    async def retrieve_data(self, server, raw=False):
        self.server_id = str(server.id)

        with open("data/data.json", "r", encoding="utf-8", errors="ignore") as file:
            self.data = json.loads(file.read(), strict=False)
        if raw:
            return self.data

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
        prefix_server = data[-1]
    else:
        prefix_server = "+"

    return commands.when_mentioned_or(prefix_server)(client, message)

# Create a bot instance
client = commands.Bot(command_prefix=get_prefix,
                      description="Quentium's Public Bot",
                      owner_id=246943045105221633,
                      pm_help=True,
                      help_command=None,
                      case_insensitive=True,
                      max_messages=999999)

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
    print("\nStarting at: " + start_time.strftime("%d.%m.%Y - %H:%M:%S"))
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            name="Oh, a QuentiumBot rewite!?",
            type=discord.ActivityType.playing)
    )

@client.listen()
async def on_message(message):
    if isinstance(message.channel, discord.TextChannel):
        data = await GetData.retrieve_data(client, message.guild)
        server_id = message.guild.id
        lang_server = data[0]
        prefix_server = data[3]
    else:
        server_id = None
        lang_server = "en"
        prefix_server = "+"
    tran = get_translations("GLOBAL", lang_server)

    if client.user.mention == message.content.replace("!", ""):
        await message.channel.send(tran["bot_prefix"].format(prefix_server, prefix_server))

if not debug:
    @client.event
    async def on_command_error(ctx, error):
        if isinstance(ctx.channel, discord.TextChannel):
            data = await GetData.retrieve_data(client, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        tran = get_translations("ERRORS", lang_server)

        if "is not found" in str(error):
            return
        elif "Cannot send an empty message" in str(error):
            return await ctx.message.delete()

        elif "Missing Access" in str(error):
            return await ctx.send(tran["msg_missing_access"])
        elif "Unknown Message" in str(error):
            return await ctx.send(tran["msg_unknown_message"])
        elif "You can only bulk delete messages that are under 14 days old" in str(error):
            return await ctx.send(tran["msg_del_old_message"])
        elif isinstance(error, commands.MissingPermissions):
            return await ctx.send(tran["msg_missing_perms"])
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(tran["msg_argument_missing"])
        elif isinstance(error, commands.NoPrivateMessage):
            return await ctx.send(tran["msg_command_no_pm"])
        elif isinstance(error, commands.DisabledCommand):
            return await ctx.send(tran["msg_command_disabled"])
        elif isinstance(error, commands.BadArgument):
            return await ctx.send(tran["msg_bad_argument"])
        elif isinstance(error, commands.TooManyArguments):
            return await ctx.send(tran["msg_too_many_arguments"])
        elif isinstance(error, commands.CommandOnCooldown):
            time_left = str(error).split("Try again in ", 1)[1].split(".", 1)[0]
            return await ctx.send(tran["msg_command_cooldown"].format(time_left))
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(tran["msg_not_owner"])

        file = open("errors.txt", "a", encoding="utf-8", errors="ignore")
        infos = [ctx.message.author, datetime.now().strftime("%d.%m.%Y - %H:%M:%S"), ctx.message.content, error]
        if isinstance(ctx.channel, discord.TextChannel):
            infos.insert(0, ctx.message.guild.name)
        file.write(" --- ".join(map(str, infos)) + "\n")
        file.close()

# TYPE Global commands

@client.command(hidden=True)
async def load(ctx, extension):
    """Loads an extension"""
    if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
        try:
            client.load_extension(cogs_folder + extension)
        except Exception as e:
            return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
        await ctx.send(f"{extension} loaded.")

@client.command(hidden=True)
async def unload(ctx, extension):
    """Unloads an extension"""
    if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
        try:
            client.unload_extension(cogs_folder + extension)
        except Exception as e:
            return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
        await ctx.send(f"{extension} unloaded.")

@client.command(hidden=True)
async def reload(ctx, extension):
    """Reloads an extension"""
    if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
        client.unload_extension(cogs_folder + extension)
        try:
            client.load_extension(cogs_folder + extension)
        except Exception as e:
            return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
        await ctx.send(f"{extension} reloaded.")

# TYPE Start

if __name__ == "__main__":
    for extension in startup_cogs:
        try:
            client.load_extension(cogs_folder + extension)
        except Exception as e:
            print(f"Failed to load extension {extension}\n{type(e).__name__}: {e}.")

    if debug:
        client.run(get_config("TEST", "token"))
    else:
        client.run(get_config("PUBLIC", "token"))
