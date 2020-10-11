import discord, asyncio, json, os, requests, psutil
from discord.ext import commands
from datetime import datetime, date, timedelta
from ftplib import FTP
from subprocess import check_output

__version__ = 1.0
__author__ = "QuentiumYT"
__filename__ = "QuentiumBot"

debug = True
windows = os.name == "nt"

startup_cogs = {**{"": [c.replace(".py", "") for c in os.listdir("cogs") if os.path.isfile(os.path.join("cogs", c))]}, # Public cogs
                **{cat + ".": [c.replace(".py", "") for c in os.listdir("cogs/" + cat) if c != "__pycache__"]
                   for cat in os.listdir("cogs") if os.path.isdir("cogs/" + cat) and cat != "__pycache__"}} # Other cogs
start_time = datetime.now()

# TYPE Data classes and functions

def get_config(section, key):
    """Get the configuration for tokens and credentials"""

    with open("data/config.json", "r", encoding="utf-8", errors="ignore") as file:
        config = json.loads(file.read(), strict=False)
    return config[section][key]

def get_translations(*args):
    """Get all translations from the file with subkeys"""

    with open("data/translations.json", "r", encoding="utf-8", errors="ignore") as file:
        translations = json.loads(file.read(), strict=False)
    if args:
        for subkey in args:
            translations = translations[subkey]
    return translations

def match_id(dis_id):
    """Match a discord id depending on mention or raw ID"""

    # ID is user mention or role mention
    if any(x in dis_id for x in ["<@!", "<@&"]):
        if len(dis_id) == 22:
            return int(dis_id[3:-1])
    # Simple mention
    elif "<@" in dis_id:
        if len(dis_id) == 21:
            return int(dis_id[2:-1])
    # No mention, just ID
    elif dis_id.isdigit():
        if len(dis_id) == 18:
            return int(dis_id)
    else:
        return False

def is_owner(ctx, user_id=False):
    """Check if the user ID is one of the owner acccount"""

    # Quentium's user IDs
    if user_id:
        return any(x == user_id for x in client.owner_ids)
    return any(x == ctx.message.author.id for x in client.owner_ids)

class HandleData:
    """Handle global data storage file"""

    async def get_data(self, file):
        """Loads data from the json file"""

        self.file = file

        with open(f"data/{self.file}.json", "r", encoding="utf-8", errors="ignore") as file:
            self.data = json.loads(file.read(), strict=False)

        # Return the json file content
        return self.data

    async def dump_data(self, file):
        """Dumps data in the json file"""

        self.file = file

        with open(f"data/{self.file}.json", "w", encoding="utf-8", errors="ignore") as file:
            json.dump(self.data, file, indent=4)

    async def retrieve_data(self, server):
        """Get all parameters from the server or create new entry"""

        self.server_id = str(server.id)
        self.data = await HandleData.get_data(self, "data")

        # Check if server id exists
        if any(x == self.server_id for x in self.data.keys()):
            self.lang_server = self.data[self.server_id]["lang_server"]
            self.commands_server = self.data[self.server_id]["commands_server"]
            self.autorole_server = self.data[self.server_id]["autorole_server"]
            self.prefix_server = self.data[self.server_id]["prefix_server"]
        else:
            # Create default config for the server
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

        # Dump the parameters / stats of the server
        if not isinstance(self, discord.ext.commands.bot.Bot):
            self.commands_server += 1
            self.data[self.server_id]["name_server"] = server.name
            self.data[self.server_id]["commands_server"] = self.commands_server

            await HandleData.dump_data(self, "data")

        # Return the server information
        return self.lang_server, self.commands_server, self.autorole_server, self.prefix_server

    async def change_prefix(self, ctx, new_prefix):
        """Change the prefix of the server"""

        self.server_id = str(ctx.message.guild.id)
        self.new_prefix = new_prefix
        self.data = await HandleData.get_data(self, "data")

        self.data[self.server_id]["prefix_server"] = self.new_prefix

        # Dump the prefix
        await HandleData.dump_data(self, "data")

        client.command_prefix = get_prefix(client, ctx.message)

    async def change_lang(self, ctx, new_lang):
        """Change the language of the server"""

        self.server_id = str(ctx.message.guild.id)
        self.new_lang = new_lang
        self.data = await HandleData.get_data(self, "data")

        self.data[self.server_id]["lang_server"] = self.new_lang

        # Dump the language
        await HandleData.dump_data(self, "data")

    async def change_autorole(self, ctx, new_role):
        """Change the language of the server"""

        self.server_id = str(ctx.message.guild.id)
        self.new_role = new_role
        self.data = await HandleData.get_data(self, "data")

        self.data[self.server_id]["autorole_server"] = self.new_role

        # Dump the autorole
        await HandleData.dump_data(self, "data")

# TYPE Bot init

async def get_prefix(client, message):
    if message.guild:
        # Get the server custom prefix
        data = await HandleData.retrieve_data(client, message.guild)
        prefix_server = data[3]
    else:
        prefix_server = "+"

    return commands.when_mentioned_or(prefix_server)(client, message)

# Create a bot instance
client = commands.Bot(command_prefix=get_prefix,
                      description="Quentium's Public Bot",
                      owner_ids=[246943045105221633, 324570532324442112],
                      pm_help=True,
                      help_command=None,
                      case_insensitive=True,
                      max_messages=999999)

async def post_topgg_data():
    # URL for top.gg
    top_gg_url = "https://top.gg/api/bots/{" + str(client.user.id) + "}/stats"
    # Token for authorization
    headers = {"Authorization": get_config("GLOBAL", "token_dbl")}
    # Guild count
    payload = {"server_count": len(client.guilds)}
    try:
        requests.post(top_gg_url,
                      data=payload,
                      headers=headers)
    except:
        pass

# TYPE Global bot events

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
    if debug:
        presence = "Oh, a QuentiumBot rewrite!?"
    else:
        presence = "+help | bot.quentium.fr"
        await post_topgg_data()
    # Change the bot presence
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            name=presence,
            type=discord.ActivityType.playing
        )
    )

@client.listen()
async def on_message(message):
    """Bot on message listener"""

    if isinstance(message.channel, discord.TextChannel):
        data = await HandleData.retrieve_data(client, message.guild)
        server_id = message.guild.id
        lang_server = data[0]
        prefix_server = data[3]
    else:
        server_id = None
        lang_server = "en"
        prefix_server = "+"
    tran = get_translations("GLOBAL", lang_server)

    # Reply with prefix on bot mention
    if client.user.mention == message.content.replace("!", ""):
        await message.channel.send(tran["bot_prefix"].format(prefix_server, prefix_server))

    # Doesn't respond to bots
    if not message.author.bot == True:
        # Respond with trigger reply
        triggers = await HandleData.get_data(client, "triggers")
        if server_id and any(x == str(server_id) for x in triggers.keys()):
            if any(x == message.content.lower() for x in triggers[str(server_id)].keys()):
                response = triggers[str(server_id)].get(message.content.lower())
                await message.channel.send(response)

    ### Delete advertising messages on TheSweMaster server
    if server_id == 199189022894063627: # TheSweMaster server ID
        if len([x.name for x in message.author.roles]) == 1:
            if any(x in message.content.lower() for x in ["oauth2", "discord.gg"]):
                await message.delete()

@client.event
async def on_member_join(member):
    """Bot member join a server listener"""

    server_id = member.guild.id
    autorole_server = await HandleData.retrieve_data(client, member.guild)

    # Check if automatic role is set
    if autorole_server[2]:
        role = discord.utils.get(member.guild.roles, id=autorole_server[2])
        if role:
            try:
                # Add the role to the new member
                await member.add_roles(role)
            except:
                pass

    ### Welcome message and ban ads accounts on TheSweMaster server
    if server_id == 199189022894063627: # TheSweMaster server ID
        if any(x in member.name for x in ["discord.gg", "twitter.com"]):
            # Ban the ads account
            await member.ban()
            msg = "A bot has been banned because we don't like them :ok_hand:"
            channel = discord.utils.get(member.guild.channels, id=290905147826110464)
            await channel.send(msg)
        else:
            # Send the welcome message
            msg = f"Hey {member.mention} ! Welcome on ***{member.guild.name}***! Feel free to ask for a cookie :cookie:"
            await discord.utils.get(member.guild.channels, id=199189022894063627).send(msg)

    ### Welcome message on QuentiumBot support server
    elif server_id == 380373195473027074: # Support QB server ID
        embed = discord.Embed(color=0x14F5F5)
        embed.title = "Welcome " + member.name
        embed.url = get_translations("GLOBAL")["website_url"]
        embed.description = "You now have joined the testers of QuentiumBot yikes! <a:happy:751103578957021264> Spend some good time with us!"
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text="By QuentiumBot")
        channel = discord.utils.get(member.guild.channels, id=380373687284793344) # Support QB general channel ID
        await channel.send(embed=embed)

async def on_server_join(server):
    """Bot added to a new server listener"""

    # Post new server count on top.gg
    if not debug:
        await post_topgg_data()

async def on_server_remove(server):
    """Bot removed from a server listener"""

    # Post new server count on top.gg
    if not debug:
        await post_topgg_data()

@client.event
async def on_raw_reaction_add(ctx):
    """Non-cache reaction listener"""

    # If Quentium react
    if is_owner(ctx, ctx.user_id):
        user = client.get_user(ctx.user_id)
        server = client.get_guild(ctx.guild_id)
        channel = server.get_channel(ctx.channel_id)
        message = await channel.fetch_message(ctx.message_id)
        # Check embed and title
        if message.embeds and "Choisissez un ordinateur à démarrer" in message.embeds[0].title:
            await message.remove_reaction(ctx.emoji, user)
            emo = ctx.emoji.name
            if emo and emo[:2] == "pc":
                if emo == "pc1":
                    args = "etherwake -i eth0 40:16:7E:AD:F7:21"
                    tmp = await channel.send(str(ctx.emoji) + " Démarrage de **PC Quentium**")
                elif emo == "pc2":
                    args = "etherwake -i eth0 04:ED:33:08:C2:35"
                    tmp = await channel.send(str(ctx.emoji) + " Démarrage de **PC portable Quentium**")
                elif emo == "pc3":
                    args = "etherwake -i eth0 40:61:86:93:B7:C7"
                    tmp = await channel.send(str(ctx.emoji) + " Démarrage de **PC Bureau**")
                elif emo == "pc4":
                    args = "etherwake -i eth0 40:16:7E:AD:7B:6C"
                    tmp = await channel.send(str(ctx.emoji) + " Démarrage de **PC Space**")
                # Run the etherwake command
                await exec_command(args, message)
                # Wait 10 seconds and delete the message
                await asyncio.sleep(10)
                await tmp.delete()

if not debug:
    @client.event
    async def on_command_error(ctx, error):
        """Bot command error handler"""

        if isinstance(ctx.channel, discord.TextChannel):
            data = await HandleData.retrieve_data(client, ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        # Get error translations
        tran = get_translations("ERRORS", lang_server)

        if "is not found" in str(error):
            return
        elif "Missing Access" in str(error):
            return
            # return await ctx.send(tran["msg_missing_access"])
        elif "Cannot send an empty message" in str(error):
            return await ctx.message.delete()

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
            return
            # return await ctx.send(tran["msg_not_owner"])

        # Log other error types to a file
        file = open("errors.txt", "a", encoding="utf-8", errors="ignore")
        infos = [ctx.message.author, datetime.now().strftime("%d.%m.%Y - %H:%M:%S"), ctx.message.content, error]
        if isinstance(ctx.channel, discord.TextChannel):
            infos.insert(0, ctx.message.guild.name)
        file.write(" --- ".join(map(str, infos)) + "\n")
        file.close()

# TYPE Global functions

async def do_tasks():
    """Execute cron tasks actions"""

    # TimeToEat project menu upload
    if datetime.today().weekday() == 6:
        if windows:
            await exec_command("python scripts/menu4tte.py", None)
        else:
            await exec_command("python3 scripts/menu4tte.py", None)
    # TimeToEat project data generation
    if datetime.today().weekday() < 5:
        if windows:
            await exec_command("python scripts/data4tte.py 130", None)
        else:
            await exec_command("python3 scripts/data4tte.py 130", None)

    ### Insoumis server kick inactive members
    serv = client.get_guild(391272643229384705) # Insoumis server ID
    channel = serv.get_channel(485168827580284948) # Insoumis logs channel ID
    kick_list = [x for x in [x for x in serv.members if not x.bot] if len(x.roles) <= 1]
    kick_list_name = [x.name for x in [x for x in serv.members if not x.bot] if len(x.roles) <= 1]
    # Kick the inactive members
    for member in kick_list:
        await member.kick()
    # List the kicked members
    if kick_list_name:
        content = "- " + "\n- ".join(kick_list_name)
    else:
        content = "Personne :smile:"
    embed = discord.Embed(color=0xFF1111)
    embed.title = f"Membres expulsés : {len(kick_list_name)}"
    embed.description = content
    embed.set_footer(text=str(datetime.now().strftime("%d.%m.%Y - %H:%M:%S")))
    await channel.send(embed=embed)

async def push_bot_stats():
    """Send a JSON recap with data to the website"""

    data = await HandleData.get_data(client, "data")

    # Get all stats to show on the website
    stats = {}
    stats["hosted"] = "VPS Oserya.fr"
    stats["owner"] = "QuentiumYT#0207"
    stats["helper"] = "Microsoft Visual Studio#1943"
    stats["linux"] = "Debian GNU/Linux 10 (buster)"
    time = round((datetime.now() - start_time).total_seconds())
    m, s = divmod(int(time), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    stats["uptime"] = f"{d} Days, {h} Hours, {m} Minutes, {s} Seconds"
    stats["creation_date"] = "16/08/2017 | 17h46"
    creation_date = date(2017, 8, 16)
    stats["creation_days"] = (date.today() - creation_date).days
    stats["lines_count"] = sum(1 for line in open("QuentiumBot.py"))
    # Get RAM + size and shift bytes
    stats["memory"] = psutil.virtual_memory().used >> 20
    stats["storage"] = (os.stat("QuentiumBot.py").st_size >> 10) # + (os.stat("Quentium67Bot.py").st_size >> 10)
    bot_commands_get_total = 0
    for serv in data.keys():
        bot_commands_get_total += data[serv]["commands_server"]
    stats["cmd_total"] = bot_commands_get_total
    users = 0
    for serv in client.guilds:
        users += len(serv.members)
    stats["users_total"] = users
    stats["emojis_total"] = len(client.emojis)
    stats["servers_total"] = len(client.guilds)
    bot_lang_fr = bot_lang_en = bot_lang_de = 0
    for serv in data.keys():
        if "fr" in data[serv]["lang_server"]:
            bot_lang_fr += 1
        elif "en" in data[serv]["lang_server"]:
            bot_lang_en += 1
        elif "de" in data[serv]["lang_server"]:
            bot_lang_de += 1
    stats["registered_fr"] = bot_lang_fr
    stats["registered_en"] = bot_lang_en
    stats["registered_de"] = bot_lang_de

    # Dump the data
    with open("data/botstats.json", "w", encoding="utf-8", errors="ignore") as file:
        json.dump(stats, file, indent=4)

    # Connect to the FTP server
    ftp = FTP(get_config("PUBLIC", "ftp_host"),
              get_config("PUBLIC", "ftp_login"),
              get_config("PUBLIC", "ftp_passwd"))
    file = open("data/botstats.json", "rb")
    # Store the file
    ftp.storbinary("STOR /bot/json/botstats.json", file)
    file.close()
    ftp.close()

async def loop_repeat():
    """Loop running for cron task at 7AM"""

    await client.wait_until_ready()
    now = datetime.today().replace(microsecond=0)
    num_days_month = (date(now.year + now.month // 12, now.month % 12 + 1, 1) - timedelta(days=1)).day
    clock = now.replace(day=now.day, hour=7, minute=0, second=0, microsecond=0)
    if now.hour > clock.hour:
        if int(now.strftime("%d")) == num_days_month:
            clock = now.replace(month=now.month + 1, day=1, hour=7, minute=0, second=0, microsecond=0)
        else:
            clock = now.replace(day=now.day + 1, hour=7, minute=0, second=0, microsecond=0)
    elif now.hour == clock.hour:
        clock = now.replace(day=now.day + 1, hour=7, minute=0, second=0, microsecond=0)
    while not client.is_closed():
        time_now = datetime.today().replace(microsecond=0)
        timer_finished = time_now
        sec_time = int(time_now.strftime("%S"))
        min_time = int(time_now.strftime("%M"))
        hour_time = int(time_now.strftime("%H"))
        day_time = int(time_now.strftime("%d"))
        if sec_time > 55 and sec_time <= 59:
            if min_time == 59:
                if hour_time == 23:
                    if day_time == num_days_month:
                        timer_finished = time_now.replace(month=time_now.month + 1, day=1, hour=0, minute=0, second=0)
                    else:
                        timer_finished = time_now.replace(day=time_now.day + 1, hour=0, minute=0, second=0)
                else:
                    timer_finished = time_now.replace(hour=time_now.hour + 1, minute=0, second=0)
            else:
                timer_finished = time_now.replace(minute=time_now.minute + 1, second=0)
        if timer_finished == clock:
            await do_tasks()
            await push_bot_stats()
            now = datetime.today().replace(microsecond=0)
            if day_time == num_days_month:
                if now.month == 12:
                    clock = now.replace(year=now.year + 1, month=1, day=1, hour=7, minute=0, second=0, microsecond=0)
                else:
                    clock = now.replace(month=now.month + 1, day=1, hour=7, minute=0, second=0, microsecond=0)
            else:
                clock = now.replace(day=now.day + 1, hour=7, minute=0, second=0, microsecond=0)
        await asyncio.sleep(5)

loop = asyncio.get_event_loop()
try:
    # Add the function to bot's task
    client.loop.create_task(loop_repeat())
except:
    loop.run_forever()

async def exec_command(args, msg):
    """Execute a command on the hosting server"""

    def emo(text):
        return discord.utils.get(client.emojis, name=text)

    # Personal arguments to start a PC or enable the connection using discord
    if any(args == x for x in ["runpc", "setco"]):
        await msg.delete()
        # Create a reaction selection message
        embed = discord.Embed(color=0x000000)
        if args == "runpc":
            # List of emojis objects
            emojis = list(map(emo, ["pc1", "pc2", "pc3", "pc4"]))
            content = f"{emojis[0]} Quentium PC\n{emojis[1]} Quentium Laptop\n{emojis[2]} Office PC\n{emojis[3]} Space PC"
            embed.title = f"{emo('vote')} Choisissez un ordinateur à démarrer :"
        else:
            emojis = list(map(emo, ["co1", "co2", "co3", "co4"]))
            content = f"{emojis[0]} ON 19H\n{emojis[1]} ON 22H\n{emojis[2]} OFF 19H\n{emojis[3]} OFF 22H"
            embed.title = f"{emo('vote')} Choisissez une action à réaliser pour la connexion :"
        embed.description = content
        msg = await msg.channel.send(embed=embed)
        for emoji in emojis:
            # React with every emoji
            await msg.add_reaction(emoji)
        return

    try:
        # Execute the command and send the result
        result = check_output(args,
                              shell=True,
                              stderr=-2) # -2 is equal to STDOUT
    except Exception as e:
        result = type(e).__name__ + ": " + str(e)

    try:
        # Try to format with linux cp1252 encoding
        await msg.channel.send("```autohotkey\n{}\n```".format(result.decode("cp1252")))
    except:
        try:
            # Try to format with global ISO-8859-1 encoding
            await msg.channel.send("```autohotkey\n{}\n```".format(result.decode("ISO-8859-1")))
        except:
            # Else print string bytes
            await msg.channel.send("```autohotkey\n{}\n```".format(str(result)))

# TYPE Start

if __name__ == "__main__":
    # Load extensions
    for cat, exts in startup_cogs.items():
        for ext in exts:
            try:
                client.load_extension("cogs." + cat + ext)
            except Exception as e:
                print(f"Failed to load extension {ext}\n{type(e).__name__}: {e}.")

    # Run with the private bot or the public one
    if debug:
        client.run(get_config("TEST", "token"))
    else:
        client.run(get_config("PUBLIC", "token"))
