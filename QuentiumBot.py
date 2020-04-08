# NOTE Public QuentiumBot Source code

import discord, asyncio, psutil, requests, urllib.request
import time, calendar, json, random, subprocess, inspect, re, os, difflib

from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageFile, ImageFilter
from datetime import datetime, timedelta, date
from icalendar import Calendar
from bs4 import BeautifulSoup
from ftplib import FTP

data = translations = glob_translations = lang_server = commands_server = autorole_server = ""
prefix_server = start_time = embed = server_id = server_name = url = headers = ""
debug = False

# TYPE JSON files

with open("translations.json", "r", encoding="utf-8", errors="ignore") as file:
    translations = json.loads(file.read(), strict=False)

with open("extra/CONFIG.json", "r", encoding="utf-8", errors="ignore") as file:
    config = json.loads(file.read(), strict=False)

with open("extra/data.json", "r", encoding="utf-8", errors="ignore") as file:
    data = json.loads(file.read(), strict=False)

with open("extra/triggers.json", "r", encoding="utf-8", errors="ignore") as file:
    triggers = json.loads(file.read(), strict=False)

with open("extra/letters_dict.json", "r", encoding="utf-8", errors="ignore") as file:
    letters = json.loads(file.read(), strict=False)

with open("extra/dt_aliases.json", "r", encoding="utf-8", errors="ignore") as file:
    aliases_dt = json.loads(file.read(), strict=False)

with open("extra/dt_mines.json", "r", encoding="utf-8", errors="ignore") as file:
    mines = json.loads(file.read(), strict=False)

with open("extra/embed_colors.json", encoding="utf-8", errors="ignore") as file:
    colors_embed = json.loads(file.read(), strict=False)

def emo(text):
    return str(discord.utils.get(client.emojis, name=text))

def get_prefix(client, message):
    global data
    if not message.guild:
        return "+"
    if data.get(str(message.guild.id)) == None:
        prefixes_list = "+"
    else:
        prefixes_list = data.get(str(message.guild.id))["prefix_server"]
    return commands.when_mentioned_or(prefixes_list)(client, message)

token_genius = config["GLOBAL"]["token_genius"]
token_weather = config["GLOBAL"]["token_weather"]
token_timezone = config["GLOBAL"]["token_timezone"]
client = commands.Bot(command_prefix=get_prefix,
                      description="Quentium's Public Bot",
                      owner_id=246943045105221633,
                      pm_help=True, help_command=None,
                      case_insensitive=True)

@client.event
async def on_ready():
    global start_time
    print("\n+--------------------------------------------+"
          "\n|              QuentiumBot ready!            |"
          "\n|           © 2017 - 2020 QuentiumYT         |"
          "\n+--------------------------------------------+\n")
    print("Logged in as %s#%s" % (client.user.name, client.user.discriminator))
    print("ID: " + str(client.user.id))
    start_time = datetime.now()
    url = "https://discordbots.org/api/bots/" + str(client.user.id) + "/stats"
    headers = {"Authorization": config["GLOBAL"]["token_dbl"]}
    print("\nStarting at: " + start_time.strftime("%d.%m.%Y - %H:%M:%S"))
    try:
        payload = {"server_count": len(client.guilds)}
        requests.post(url, data=payload, headers=headers)
    except:
        pass
    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            name="+help | quentium.fr",
            type=discord.ActivityType.playing)
    )

# TYPE GLOBAL function

#----------------------------- SETUP GLOBAL FUNCTIONS AND GLOBAL EVENTS -----------------------------#

async def async_data(server_id, server_name, message_received):
    global data, translations, lang_server, commands_server, autorole_server, prefix_server
    with open("extra/data.json", "r", encoding="utf-8", errors="ignore") as file:
        data = json.loads(file.read(), strict=False)
    with open("translations.json", "r", encoding="utf-8", errors="ignore") as file:
        translations = json.loads(file.read(), strict=False)
    if any(x == str(server_id) for x in data.keys()):
        lang_server = data[server_id]["lang_server"]
        commands_server = data[server_id]["commands_server"] + 1
        data[server_id]["commands_server"] = commands_server
        autorole_server = data[server_id]["autorole_server"]
        prefix_server = data[server_id]["prefix_server"]
    else:
        lang_server = "fr"
        commands_server = 1
        autorole_server = None
        prefix_server = "+"
        data[server_id] = {"name_server": server_name}
        data[server_id]["lang_server"] = lang_server
        data[server_id]["commands_server"] = commands_server
        data[server_id]["autorole_server"] = autorole_server
        data[server_id]["prefix_server"] = prefix_server
    with open("extra/data.json", "w", encoding="utf-8", errors="ignore") as file:
        json.dump(data, file, indent=4)
    # cmd_received = str(message_received.content).replace(prefix_server, "").split()[0]
    # FIXME replace help with cmd_received
    translations = translations[lang_server]["help"]
    return data, translations, lang_server, commands_server, autorole_server, prefix_server

async def async_do_task():
    global start_time, commands_server
    if int(datetime.today().weekday()) == 6:
        await async_command("python3 extra/menu4tte.py", None)
    # if not int(datetime.today().weekday()) == 5 and not int(datetime.today().weekday()) == 6:
        # await async_command("python3 extra/data4tte.py 130", None)

    serv = client.get_guild(391272643229384705)  # Insoumis server ID
    kick_list = [x for x in [x for x in serv.members if not x.bot] if len(x.roles) <= 1]
    kick_list_name = [x.name for x in [x for x in serv.members if not x.bot] if len(x.roles) <= 1]
    for member in kick_list:
        await member.kick()
    if kick_list_name:
        content = "- " + "\n- ".join(kick_list_name)
    else:
        content = "Personne :sweat:"
    embed = discord.Embed(title=f"Membres expulsés : {len(kick_list_name)}", description=content, color=0xFF0000)
    embed.set_footer(text=str(datetime.now().strftime("%d.%m.%Y - %H:%M:%S")))  # Insoumis channel ID
    await serv.get_channel(485168827580284948).send(embed=embed)

    await get_bot_stats()

async def get_bot_stats():
    stats = {}
    stats["hosted"] = "Raspberry Pi 3"
    stats["owner"] = "QuentiumYT#0207"
    stats["helper"] = "Microsoft Visual Studio#1943"
    stats["linux"] = "Debian 8.0 (Raspbian)"
    time = round((datetime.now() - start_time).total_seconds())
    m, s = divmod(int(time), 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    stats["uptime"] = f"{d} Days, {h} Hours, {m} Minutes, {s} Seconds"
    stats["creation_date"] = "16/08/2017 | 17h46"
    date_crea = date(2017, 8, 16)
    date_now = date.today()
    stats["creation_days"] = (date_now - date_crea).days
    stats["lines_count"] = sum(1 for line in open("QuentiumBot.py"))
    stats["memory"] = int(psutil.virtual_memory().used >> 20)
    stats["storage"] = int((os.stat("QuentiumBot.py").st_size >> 10) + (os.stat("Quentium67Bot.py").st_size >> 10))
    bot_commands_get_total = 0
    for serv in data.keys():
        bot_commands_get_total += data[serv]["commands_server"]
    stats["cmd_total"] = int(bot_commands_get_total)
    users = 0
    for serv in client.guilds:
        users += len(serv.members)
    stats["users_total"] = int(users)
    stats["emojis_total"] = len(client.emojis)
    stats["servers_total"] = int(len(client.guilds))
    bot_lang_fr = bot_lang_en = bot_lang_de = 0
    for serv in data.keys():
        if "fr" in data[serv]["lang_server"]:
            bot_lang_fr += 1
        elif "en" in data[serv]["lang_server"]:
            bot_lang_en += 1
        elif "de" in data[serv]["lang_server"]:
            bot_lang_de += 1
    stats["registered_fr"] = int(bot_lang_fr)
    stats["registered_en"] = int(bot_lang_en)
    stats["registered_de"] = int(bot_lang_de)
    with open("extra/botstats.json", "w", encoding="utf-8", errors="ignore") as file:
        json.dump(stats, file, indent=4)
    ftp = FTP(config["GLOBAL"]["ftp_host"], config["GLOBAL"]["ftp_login"], config["GLOBAL"]["ftp_passwd"])
    file = open("extra/botstats.json", "rb")
    ftp.storbinary("STOR /bot/json/botstats.json", file)
    file.close()

async def async_command(args, msg):
    global emo
    if "data4tte" in args or "menu4tte" in args:
        return subprocess.Popen(["sudo"] + args.split())
    msg_channel = discord.utils.get(msg.author.guild.channels, id=msg.channel.id)
    if args == "runpc":
        try:
            await msg.delete()
        except:
            pass
        content = emo("pc1") + " Quentium PC\n" + emo("pc2") + " Office PC\n" + emo("pc3") + " Space PC"
        embed = discord.Embed(title=emo("vote") + " Choisissez un ordinateur à démarrer :", description=content, color=0x000000)
        msg = await msg_channel.send(embed=embed)
        for item in ["pc1", "pc2", "pc3"]:
            emo = discord.utils.get(client.emojis, name=item)
            await msg.add_reaction(emo)
        return
    elif args == "setco":
        try:
            await msg.delete()
        except:
            pass
        content = emo("co1") + " ON 19H\n" + emo("co2") + " ON 22H\n" + emo("co3") + " OFF 19H\n" + emo("co4") + " OFF 22H"
        embed = discord.Embed(title=emo("vote") + " Choisissez une action à réaliser pour la connexion :", description=content, color=0x000000)
        msg = await msg_channel.send(embed=embed)
        for item in ["co1", "co2", "co3", "co4"]:
            emo = discord.utils.get(client.emojis, name=item)
            await msg.add_reaction(emo)
        return
    elif "ping" in args:
        try:
            return await msg.delete()
        except:
            pass
    try:
        result = subprocess.check_output("sudo " + args, shell=True, stderr=subprocess.STDOUT)
    except Exception as e:
        result = type(e).__name__ + ": " + str(e)
    print(repr(result))
    if not "etherwake" in args:
        try:
            return await msg_channel.send("```autohotkey\n{}\n```".format(result.decode("cp1252")))
        except:
            try:
                return await msg_channel.send("```autohotkey\n{}\n```".format(result.decode("ISO-8859-1")))
            except:
                return await msg_channel.send("```autohotkey\n{}\n```".format(str(result)))

@client.listen()
async def on_message(message):
    global triggers, lang_server
    try:
        server_id = message.guild.id
    except:
        server_id = None

    lang_server = "fr"

    try:
        with open("extra/data.json", "r", encoding="utf-8", errors="ignore") as file:
            data = json.loads(file.read(), strict=False)
        lang_server = data[str(server_id)]["lang_server"]
        server_prefix = data[str(server_id)]["prefix_server"]
    except:
        pass

    if client.user.mention == message.content.replace("!", ""):
        if lang_server == "fr":
            return await message.channel.send(f"Le préfixe du bot est `{server_prefix}`. Utilisez la commande `{server_prefix}help` pour la liste des commandes.")
        elif lang_server == "en":
            return await message.channel.send(f"The prefix of the bot is `{server_prefix}`. Use the `{server_prefix}help` command for the list of commands.")
        elif lang_server == "de":
            return await message.channel.send(f"Das Präfix des Bots ist `{server_prefix}`. Verwenden Sie den Befehl `{server_prefix}help` für die Liste der Befehle.")

    if server_id == 199189022894063627:  # TheSweMaster server ID
        if len([x.name for x in message.author.roles]) == 1:
            if any(x in message.content.lower() for x in ["oauth2", "discord.gg"]):
                return await message.delete()

    if not message.author.bot == True:
        if any(x == str(server_id) for x in triggers.keys()):
            with open("extra/triggers.json", "r", encoding="utf-8", errors="ignore") as file:
                triggers = json.loads(file.read(), strict=False)
            if any(x == message.content.lower() for x in triggers[str(server_id)].keys()):
                response = triggers[str(server_id)].get(message.content.lower())
                return await message.channel.send(response)

async def on_server_join(server):
    try:
        payload = {"server_count": len(client.guilds)}
        requests.post(url, data=payload, headers=headers)
    except:
        pass

async def on_server_remove(server):
    try:
        payload = {"server_count": len(client.guilds)}
        requests.post(url, data=payload, headers=headers)
    except:
        pass

async def loop_repeat():
    await client.wait_until_ready()
    now = datetime.today().replace(microsecond=0)
    num_days_month = calendar.monthrange(int(now.strftime("%y")), int(now.strftime("%m")))[1]
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
            await async_do_task()
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
    client.loop.create_task(loop_repeat())
except:
    loop.run_forever()

@client.event
async def on_member_join(member):
    global autorole_server
    server_id = member.guild.id

    autorole_server = None
    try:
        with open("extra/data.json", "r", encoding="utf-8", errors="ignore") as file:
            data = json.loads(file.read(), strict=False)
        autorole_server = data[str(server_id)]["autorole_server"]
    except:
        pass

    if not autorole_server == None:
        role = discord.utils.get(member.guild.roles, id=int(autorole_server))
        if not role == None:
            try:
                await member.add_roles(role)
            except:
                pass

    if server_id == 199189022894063627: # TheSweMaster server ID
        if any(x in member.name for x in ["discord.gg", "twitter.com"]):
            await member.ban()
            msg = "A bot has been banned because we don't like them :ok_hand:"
            return await discord.utils.get(member.guild.channels, id=290905147826110464).send(msg)
        else:
            msg = f"Hey {member.mention} ! Welcome on ***{member.guild.name}***! Feel free to ask for a cookie :cookie:"
            return await discord.utils.get(member.guild.channels, id=199189022894063627).send(msg)

    elif server_id == 392676649365274626: # Speakerino server ID
        embed = discord.Embed(title="Welkom " + member.name, url="https://bot.quentium.fr/", description="Ey kut. Jij bent nu mijn bitch <3. Groetjes <@326821148782231553>", color=0x2769e1)
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text="By QuentiumBot")
        return await discord.utils.get(member.guild.channels, id=392676649365274629).send(embed=embed)

@client.event
async def on_raw_reaction_add(ctx):
    if any(x == ctx.user_id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
        user = client.get_user(ctx.user_id)
        server = client.get_guild(ctx.guild_id)
        channel = server.get_channel(ctx.channel_id)
        message = await channel.fetch_message(ctx.message_id)
        if message.embeds and "<:vote:509442482141003776> Choisissez" in message.embeds[0].title:
            await message.remove_reaction(ctx.emoji, user)
            if "ordinateur" in message.embeds[0].title:
                try:
                    emo = ctx.emoji.name
                except:
                    emo = None
                if emo and emo[:2] == "pc":
                    if emo == "pc1":
                        args = "etherwake -i eth0 40:16:7E:AD:F7:21"
                        tmp = await channel.send(str(ctx.emoji) + " Démarrage de ***PC Quentium***")
                    elif emo == "pc2":
                        args = "etherwake -i eth0 40:61:86:93:B7:C7"
                        tmp = await channel.send(str(ctx.emoji) + " Démarrage de ***PC Bureau***")
                    elif emo == "pc3":
                        args = "etherwake -i eth0 40:16:7E:AD:7B:6C"
                        tmp = await channel.send(str(ctx.emoji) + " Démarrage de ***PC Space***")
                    await async_command(args, message)
                    await asyncio.sleep(10)
                    return await tmp.delete()
            elif "connexion" in message.embeds[0].title:
                try:
                    emo = ctx.emoji.name
                except:
                    emo = None
                if emo and emo[:2] == "co":
                    try:
                        password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
                        password_mgr.add_password(None, "http://192.168.1.100:8080", "admin", config["GLOBAL"]["co_passwd"])
                        handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
                        opener = urllib.request.build_opener(handler)
                        urllib.request.install_opener(opener)
                        if emo == "co1":
                            urllib.request.urlopen("http://192.168.1.100:8080/set.cmd?cmd=setpower+p61=1")
                            tmp = await channel.send(str(ctx.emoji) + " Connexion ajoutée jusqu'à ***19h***")
                        elif emo == "co2":
                            urllib.request.urlopen("http://192.168.1.100:8080/set.cmd?cmd=setpower+p62=1")
                            tmp = await channel.send(str(ctx.emoji) + " Connexion ajoutée jusqu'à ***22h***")
                        elif emo == "co3":
                            urllib.request.urlopen("http://192.168.1.100:8080/set.cmd?cmd=setpower+p61=0")
                            tmp = await channel.send(str(ctx.emoji) + " Connexion enlevée de ***19h***")
                        elif emo == "co4":
                            urllib.request.urlopen("http://192.168.1.100:8080/set.cmd?cmd=setpower+p62=0")
                            tmp = await channel.send(str(ctx.emoji) + " Connexion enlevée de ***22h***")
                        await asyncio.sleep(10)
                        return await tmp.delete()
                    except:
                        return await channel.send("Le site n'a pas pu répondre (No route to host)")

if not debug:
    @client.event
    async def on_command_error(ctx, error):
        global lang_server
        if isinstance(ctx.channel, discord.TextChannel):
            server_id = ctx.message.guild.id
            with open("extra/data.json", "r", encoding="utf-8", errors="ignore") as file:
                data = json.loads(file.read(), strict=False)
            try:
                lang_server = data[str(server_id)]["lang_server"]
            except:
                lang_server = "fr"
        else:
            lang_server = "fr"

        if lang_server == "fr":
            if "is not found" in str(error):
                return
            elif "FORBIDDEN (status code: 403): Missing Permissions" in str(error):
                return await ctx.send(":x: Il manque certaines permissions au bot.")
            elif "FORBIDDEN (error code: 50013): Missing Permissions" in str(error):
                return await ctx.send(":x: Il manque certaines permissions au bot.")
            elif "FORBIDDEN (status code: 403): Missing Access" in str(error):
                return await ctx.send(":x: Il manque certains accès au bot.")
            elif "NotFound: 404 NOT FOUND (error code: 10008): Unknown Message" in str(error):
                return await ctx.send(":x: Discord ne trouve pas l'un des messages.")
            elif "Cannot send an empty message" in str(error):
                return await ctx.message.delete()
            elif "BAD REQUEST (status code: 400): You can only bulk delete messages that are under 14 days old." in str(error):
                return await ctx.send(":x: Vous ne pouvez que supprimer les messages datant de moins de 14 jours :pensive:")
            elif isinstance(error, commands.MissingRequiredArgument):
                return await ctx.send(":x: Un argument requis manque :rolling_eyes:")
            elif isinstance(error, commands.NoPrivateMessage):
                return await ctx.send(":x: Cette commande ne peut pas être utilisée en message privés :confused:")
            elif isinstance(error, commands.DisabledCommand):
                return await ctx.send(":x: Cette commande à été désactivée :confounded:")
            elif isinstance(error, commands.BadArgument):
                return await ctx.send(":x: Un mauvais argument à été donné :slight_frown:")
            elif isinstance(error, commands.TooManyArguments):
                return await ctx.send(":x: Trop d'arguments ont étés donnés :scream:")
            elif isinstance(error, commands.CommandOnCooldown):
                time_left = str(error).split("Try again in ", 1)[1].split(".", 1)[0]
                return await ctx.send(f":x: Doucement, il y a un cooldown sur cette commande, il vous reste {time_left} secondes à attendre :raised_hand:")
        elif lang_server == "en":
            if "is not found" in str(error):
                return
            elif "FORBIDDEN (status code: 403): Missing Permissions" in str(error):
                return await ctx.send(":x: The bot is missing some permissions.")
            elif "FORBIDDEN (error code: 50013): Missing Permissions" in str(error):
                return await ctx.send(":x: The bot is missing some permissions.")
            elif "FORBIDDEN (status code: 403): Missing Access" in str(error):
                return await ctx.send(":x: The bot is missing some access.")
            elif "NotFound: 404 NOT FOUND (error code: 10008): Unknown Message" in str(error):
                return await ctx.send(":x: Discord does not find one of the messages.")
            elif "Cannot send an empty message" in str(error):
                return await ctx.message.delete()
            elif "BAD REQUEST (status code: 400): You can only bulk delete messages that are under 14 days old." in str(error):
                return await ctx.send(":x: You can only delete messages that are under 14 days old :pensive:")
            elif isinstance(error, commands.MissingRequiredArgument):
                return await ctx.send(":x: A required argument is missing :rolling_eyes:")
            elif isinstance(error, commands.NoPrivateMessage):
                return await ctx.send(":x: This command can't be used in private messages :confused:")
            elif isinstance(error, commands.DisabledCommand):
                return await ctx.send(":x: This command has been disabled :confounded:")
            elif isinstance(error, commands.BadArgument):
                return await ctx.send(":x: A wrong argument has been given :slight_frown:")
            elif isinstance(error, commands.TooManyArguments):
                return await ctx.send(":x: Too many arguments has been given :scream:")
            elif isinstance(error, commands.CommandOnCooldown):
                time_left = str(error).split("Try again in ", 1)[1].split(".", 1)[0]
                return await ctx.send(f":x: Slow down, there is a cooldown on that command, you have to wait {time_left} more seconds :raised_hand:")
        elif lang_server == "de":
            if "is not found" in str(error):
                return
            elif "FORBIDDEN (status code: 403): Missing Permissions" in str(error):
                return await ctx.send(":x: Dem Bot fehlen einige Berechtigungen.")
            elif "FORBIDDEN (error code: 50013): Missing Permissions" in str(error):
                return await ctx.send(":x: Dem Bot fehlen einige Berechtigungen.")
            elif "FORBIDDEN (status code: 403): Missing Access" in str(error):
                return await ctx.send(":x: Dem Bot fehlen einige Zugang.")
            elif "NotFound: 404 NOT FOUND (error code: 10008): Unknown Message" in str(error):
                return await ctx.send(":x: Discord findet eine der Nachrichten nicht.")
            elif "Cannot send an empty message" in str(error):
                return await ctx.message.delete()
            elif "BAD REQUEST (status code: 400): You can only bulk delete messages that are under 14 days old." in str(error):
                return await ctx.send(":x: Sie können nur Nachrichten löschen, die weniger als 14 Tage alt sind :pensive:")
            elif isinstance(error, commands.MissingRequiredArgument):
                return await ctx.send(":x: Ein Erfordertes argument fehlt :rolling_eyes:")
            elif isinstance(error, commands.NoPrivateMessage):
                return await ctx.send(":x: Dieser Befehl kann nicht in direkt nachrichten verwendet werden :confused:")
            elif isinstance(error, commands.DisabledCommand):
                return await ctx.send(":x: Dieser Befehl wurde deaktivier :confounded:")
            elif isinstance(error, commands.BadArgument):
                return await ctx.send(":x: Es wurd ein falsches argument gegeben :slight_frown:")
            elif isinstance(error, commands.TooManyArguments):
                return await ctx.send(":x: Es wurden zu viele argumente gegeben :scream:")
            elif isinstance(error, commands.CommandOnCooldown):
                time_left = str(error).split("Try again in ", 1)[1].split(".", 1)[0]
                return await ctx.send(f":x: Langsam, dieser befehl hat einen cool down, Sie haben noch {time_left} sekunden zu warten :raised_hand:")
        file = open("errors.txt", "a", encoding="utf-8", errors="ignore")
        infos = [ctx.message.author, datetime.now().strftime("%d.%m.%Y - %H:%M:%S"), ctx.message.content, str(error)]
        if isinstance(ctx.channel, discord.TextChannel):
            infos.insert(0, ctx.message.guild.name)
        file.write(" --- ".join(map(str, infos)) + "\n")
        file.close()
        return

# TYPE Info cmds

#----------------------------- INFORMATIONS COMMANDS -----------------------------#

@client.command(pass_context=True, aliases=["cmd", "aide"])
async def help(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global translations, server_id, server_name, prefix_server
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)

    if not ctx.message.author.bot == True:
        commands_type = ["infos_", "utilities_", "stats_", "feedback_", "admin_configs_", "admin_rights_"]
        commands_type_special = ["flc_", "theswe_", "ism_"]
        commands_type_special_id = ["371687157817016331", "199189022894063627", "391272643229384705"]
        if not args:
            commands_type_emoji = ["informations", "utilities", "statistics", "feedback", "admin_configs", "admin_rights", "serv_flc", "serv_theswe", "serv_ism"]
            commands_title = [translations[x] for x in translations.keys() if "msg_title_" in x]
            embed = discord.Embed(title=translations["msg_list_commands"], url=translations["url_website_discord"], color=0x00ff00)
            for cmds_type in range(len(commands_type)):
                embed_type = [x for x in translations.keys() if commands_type[cmds_type] in x]
                embed_var = ""
                for command in embed_type:
                    command_desc = translations[command]["description"]
                    command_usage = translations[command]["usage"]
                    embed_var += f"- `{prefix_server}{command.replace(commands_type[cmds_type], '')}{command_usage}` > {command_desc}\n"
                embed.add_field(name=emo(commands_type_emoji[cmds_type]) + commands_title[cmds_type], value=embed_var, inline=True)
            for cmds_type in range(len(commands_type_special)):
                embed_type = [x for x in translations.keys() if commands_type_special[cmds_type] in x]
                embed_var = ""
                if str(ctx.message.guild.id) == commands_type_special_id[cmds_type]:
                    for command in embed_type:
                        command_desc = translations[command]["description"]
                        command_usage = translations[command]["usage"]
                        embed_var += f"- `{prefix_server}{command.replace(commands_type_special[cmds_type], '')}{command_usage}` > {command_desc}\n"
                    index = len(commands_type) + cmds_type
                    embed.add_field(name=emo(commands_type_emoji[index]) + commands_title[index], value=embed_var, inline=True)
            if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
                embed_type = [x for x in translations.keys() if "quentium_" in x]
                embed_var = ""
                for command in embed_type:
                    command_desc = translations[command]["description"]
                    command_usage = translations[command]["usage"]
                    embed_var += f"- `{prefix_server}{command.replace('quentium_', '')}{command_usage}` > {command_desc}\n"
                embed.add_field(name=emo("user_quentium") + commands_title[-1], value=embed_var, inline=True)
            donation = translations["msg_donation"].format("https://www.paypal.me/QLienhardt")
            embed.add_field(name=translations["msg_caption"], value=translations["msg_caption_desc"], inline=True)
            embed.add_field(name=translations["msg_warning"], value=translations["msg_warning_desc"] + donation, inline=True)
            embed.set_footer(text=translations["msg_more_infos"], icon_url=translations["url_logo_bot"])
        else:
            all_commands = []
            commands_type += commands_type_special
            commands_keys = [x for x in translations.keys() if any([y in x for y in commands_type])]
            for types in commands_type:
                all_commands += [x.split(types)[1] for x in translations.keys() if types in x]
            for types_aliases in commands_keys:
                all_commands += [x for x in translations[types_aliases]["aliases"].split(" / ") if not x == ""]

            if any(x.lower() == args.lower() for x in all_commands):
                if any([x for x in commands_keys if args in translations[x]["aliases"]]):
                    command_type = [y for y in commands_keys if any([args in x for x in translations[y]["aliases"].split(" / ")])][0]
                else:
                    command_type = [x for x in commands_keys if args in x][0]
                command_desc = translations[command_type]["description"]
                command_usage = translations[command_type]["usage"]
                command_aliases = [command_type.split("_")[1]] + translations[command_type]["aliases"].split(" / ")
                desc_text = f"```{args}```\n**{command_desc}**\n\n"
                if translations[command_type]["aliases"]:
                    desc_text += f"**{translations['msg_aliases']}** `{'`, `'.join(command_aliases)}`\n\n\n"
                else:
                    desc_text += "\n"
                desc_text += f"{translations['msg_format']} `{prefix_server}{args} {command_usage}`"
                embed = discord.Embed(title=None, description=desc_text, color=0x03A678)
            else:
                return await ctx.send(translations["msg_no_command_found"])
        return await ctx.send(embed=embed)

@client.command(pass_context=True)
async def help_old(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if lang_server == "fr":
            commands_user = """
- `help / cmd` > Affiche la liste des commandes.
- `letter ["texte"]` > Ecris un message avec des émojis.
- `embed [T="titre"] [D="description"] [C="couleur"] [I="image URL"] [F="bas de page"] [U="URL"] [A="auteur"]` > Affiche un embed personnalisé.
- `listbans` > Affiche la liste des personnes bannies.
- `listinvites` > Affiche la liste des liens d'invitation.
- `listservers` > Affiche la liste des serveurs comportant le bot.
- `msgtotal [all / channel] [@membre]` > Calcule le nombre de messages d'un membre au total ou dans le salon.
- `lyrics ["musique"]` > Recherche les paroles d'une musique.
- `weather ["ville"]` > Affiche la météo de la ville spécifiée.
- `serverstats` > Montre les statistiques du serveur.
- `userstats [@membre]` > Montre les statistiques d'un membre.
- `botstats` > Montre les statistiques du bot.
- `shareme` > Invite le bot sur votre serveur.
- `ping` > Calcule le temps de réactivité du bot."""
            commands_dt = """
:warning: Le préfixe pour France Les Cités est `-` :warning:
- `absent ["durée + (raison)"]` > Attribuez vous le rôle Absent si vous devez vous absenter un moment.
- `dtmine ["minerais"]` > Affiche les 10 meilleurs endroits pour miner une ressource (©Fomys :smile:)."""
            commands_admin = """
- `clear ["nombre"]` > Supprime un nombre défini de messages.
- `kick [@membre]` > Expulse la personne mentionnée.
- `ban [@membre]` > Bannis la personne mentionnée.
- `autorole ["nom du role" / show / remove]` > Donne un rôle automatiquement à quelqu'un lorsqu'il rejoins le serveur.
- `lang [fr / en / de]` > Change la langue du bot. (Langue par défaut : fr)"""
            commands_feedback = """
- `idea / bug ["texte"]` > Propose une idée ou reporte un bug pour améliorer le bot.
- `showlogs` > Affiche la liste des mises à jour du bot.

Légende : `[argument]` - `["argument donné"]` (Enlevez les guillemets) - `[@mention]` - `[choix / "mon_choix"]`
:warning: Si vous rencontrez un problème, merci de la soumettre avec la commande `+bug` ou en rejoignant le serveur de test/support : https://discord.gg/5sehgXx\n"""
            end_text = ":euro: Pour une petite donation : [Cliquez ici]({})".format("https://www.paypal.me/QLienhardt")
            embed = discord.Embed(title="----- Liste des Commandes -----", url="https://quentium.fr/discord/", color=0x00ff00)
            embed.add_field(name=":video_game: Commandes **UTILISATEUR** :", value=commands_user, inline=True)
            if server_id == 371687157817016331:  # France Les Cités ID
                embed.add_field(name=":flag_fr: Commandes **Deep Town** :", value=commands_dt, inline=True)
            embed.add_field(name=":cop: Commandes **ADMIN** :", value=commands_admin, inline=True)
            embed.add_field(name=":incoming_envelope: Commandes **SUPPORT / FEEDBACK** :", value=commands_feedback + end_text, inline=True)
            embed.set_footer(text="Pour plus d'informations, veuillez visiter le site : https://quentium.fr/discord/", icon_url="https://quentium.fr/+img/logoBot.png")
            return await ctx.send(embed=embed)

        elif lang_server == "en":
            commands_user = """
- `help / cmd` > Show list of commands available.
- `letter ["text"]` > Write a message with emojis.
- `embed [T="title"] [D="description"] [C="color"] [I="image URL"] [F="footer" / None] [U="URL"] [A="author"]` > Shows a personalized embed.
- `listbans` > Show list of banned members.
- `listinvites` > Show list of invite links.
- `listservers` > Show list of servers with the bot.
- `msgtotal [all / channel] [@member]` > Calculates the number of messages of a member in total or in the current channel.
- `lyrics ["music"]` > Search for lyrics of a song.
- `weather ["city"]` > Shows the weather of the specified city.
- `serverstats` > Show stats of the server.
- `userstats [@member]` > Show stats of a member.
- `botstats` > Show stats of the bot.
- `shareme` > Invite the bot to your server.
- `ping` > Calculate bot's latency."""
            commands_admin = """
- `clear ["number"]` > Clear a specific number of messages.
- `kick [@member]` > Kick the tagged member.
- `ban [@member]` > Ban the tagged member.
- `autorole ["rolename" / show / remove]` > Give a role automatically to someone when he join the server.
- `lang [fr / en / de]` > Change the language of the bot. (Default language : fr)"""
            commands_feedback = """
- `idea / bug ["text"]` > Submit an idea or report a bug to improve the bot.
- `showlogs` > Shows update logs of the bot.

Caption: `[argument]` - `["given argument"]` (Remove quotes) - `[@mention]` - `[choice  / "my_choice"]`
:warning: If you have any problem, please submit it with `+bug` command or join our test/support server: https://discord.gg/5sehgXx\n"""
            end_text = ":dollar: For a small donation: [Click here]({})".format("https://www.paypal.me/QLienhardt")
            embed = discord.Embed(title="----- List of Commands -----", url="https://quentium.fr/en/discord/", color=0x00ff00)
            embed.add_field(name=":video_game: Commands **USER**:", value=commands_user, inline=True)
            embed.add_field(name=":cop: Commands **ADMIN**:", value=commands_admin, inline=True)
            embed.add_field(name=":incoming_envelope: Commands **SUPPORT / FEEDBACK**:", value=commands_feedback + end_text, inline=True)
            embed.set_footer(text="For more informations, please check my website: https://quentium.fr/en/discord/", icon_url="https://quentium.fr/+img/logoBot.png")
            return await ctx.send(embed=embed)

        elif lang_server == "de":
            commands_user = """
- `help / cmd` > Zeigt die Befehlsliste an.
- `letter ["Text"]` > Schreibe eine Nachricht mit emojis.
- `embed [T="Titel"] [D="Beschreibung"] [C="Farbe"] [I="Bild URL"] [F="Fußzeile" / None] [U="URL"] [A="Autor"]` > Zeigt eine personifizierte embed an.
- `listbans` > Zeigt die Liste der verbanten Benutzer.
- `listinvites` > Zeigt die Liste der Einladungslinks.
- `listservers` > Zeigt die Liste des Servers mit dem Bot.
- `msgtotal [all / channel] [@Mitglied]` > Berechnet die Anzahl der Nachrichten eines Mitglieds insgesamt oder im Chatroom.
- `lyrics ["Musik"]`> Durchsucht den Text einer Musik.
- `weather ["Stadt"]` > Zeigt das Wetter der angegebenen Stadt an.
- `serverstats` > Zeigt die Serverstatistiken an.
- `userstats [@Mitglied]` > Zeigt die Statistiken des jeweiligen Mitglieds an.
- `botstats` > Zeigt die Botstatistiken an.
- `shareme` > Lädet den Bot auf Deinen Server ein.
- `ping` > Berechnen Sie die Latenz des Bots."""
            commands_admin = """
- `clear ["Zahl"]` > Löscht eine bestimmte Anzahl von Nachrichten.
- `kick [@Mitglied]` > Kickt das genannte Mitglied.
- `ban [@Mitglied]` > Verbannt das genannte Mitglied.
- `autorole ["Rolename" / show / remove]` > Gibt jemandem automatisch eine Rolle, wenn er dem Server beitritt.
- `lang [fr / en / de]` > Verändert die Sprache des Bots. (Standardsprache : fr)"""
            commands_feedback = """
- `idea / bug ["Text"]` > Schlag eine Idee vor oder melde einen Fehler um den Bot zu verbessern.
- `showlogs` > Zeigt die liste der Neuigkeiten des Bots an.

Beschriftung: `[Argument]` - `["Gegeben Argument"]` (Entfernen Sie Anführungszeichen) - `[@Erwähnung]` - `[wähl / "Meine_Wähle"]`
:warning: Wenn ihr einen Fehler findet, bitte meldet ihn mit `+bug` befehle oder indem Sie dem test/support-Server beitreten: https://discord.gg/5sehgXx\n"""
            end_text = ":euro: Für eine kleine spende: [Hier klicken]({})".format("https://www.paypal.me/QLienhardt")
            embed = discord.Embed(title="----- Liste der Befehle -----", url="https://quentium.fr/de/discord/", color=0x00ff00)
            embed.add_field(name=":video_game: Befehle **BENUTZER**:", value=commands_user, inline=True)
            embed.add_field(name=":cop: Befehle **VERWALTER**:", value=commands_admin, inline=True)
            embed.add_field(name=":incoming_envelope: Befehle **SUPPORT / FEEDBACK**:", value=commands_feedback + end_text, inline=True)
            embed.set_footer(text="Für weitere Informationen, Bitte besuchen Sie meine Website: https://quentium.fr/de/discord/", icon_url="https://quentium.fr/+img/logoBot.png")
            return await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=["listserveurs", "listserver", "listeserveurs", "serverlist", "serverliste", "servlist", "servelist", "listservs"])
async def listservers(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not server_id == 264445053596991498:  # DBL ID
            serv_id = [str(server.id) for server in client.guilds]
            serv_id_exist = []
            serv_pos = []

            for serv in data.keys():
                for server in serv_id:
                    if server == serv:
                        serv_pos.append(list(data).index(serv))
                        serv_id_exist.append(server)

            if lang_server == "fr":
                content = "**__Nom du serveur | Position enregistrée__**"
            elif lang_server == "en":
                content = "**__Server name | Registered position__**"
            elif lang_server == "de":
                content = "**__Servername | Registrierte Position__**"
            content2 = ""
            for pos in range(len(serv_id_exist)):
                if len(content) < 2000:
                    content += "\n- " + str(client.get_guild(int(serv_id_exist[pos]))) + " | " + str(serv_pos[pos])
                else:
                    content2 += "\n- " + str(client.get_guild(int(serv_id_exist[pos]))) + " | " + str(serv_pos[pos])
            if lang_server == "fr":
                embed = discord.Embed(title=f"Serveurs : {len(client.guilds)}", description=content, color=0xFF9000)
            elif lang_server == "en":
                embed = discord.Embed(title=f"Servers: {len(client.guilds)}", description=content, color=0xFF9000)
            elif lang_server == "de":
                embed = discord.Embed(title=f"Server: {len(client.guilds)}", description=content, color=0xFF9000)
            if not content2 == "":
                embed2 = discord.Embed(title=None, description=content2, color=0xFF9000)
                await ctx.send(embed=embed)
                return await ctx.send(embed=embed2)
            else:
                return await ctx.send(embed=embed)

@client.command(pass_context=True, no_pm=True, aliases=["listeinvites", "invitelist"])
async def listinvites(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if lang_server == "fr":
            msg_any = "Aucuns"
        elif lang_server == "en":
            msg_any = "None"
        elif lang_server == "de":
            msg_any = "Keine"

        list_invites = await ctx.guild.invites()
        if list_invites:
            content = "\n- ".join([x.url for x in list_invites])
        else:
            content = msg_any
        if lang_server == "fr":
            embed = discord.Embed(title="Liens d'invitation :", description="- " + content, color=0x00FFFF)
        elif lang_server == "en":
            embed = discord.Embed(title="Invite links:", description="- " + content, color=0x00FFFF)
        elif lang_server == "de":
            embed = discord.Embed(title="Einladungslinks:", description="- " + content, color=0x00FFFF)
        return await ctx.send(embed=embed)

@client.command(pass_context=True, no_pm=True, aliases=["listebans", "banlist"])
async def listbans(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if lang_server == "fr":
            msg_any = "Aucun"
        elif lang_server == "en":
            msg_any = "None"
        elif lang_server == "de":
            msg_any = "Keine"

        list_banned = await ctx.guild.bans()
        if list_banned:
            content = "\n- ".join([x[1].name for x in list_banned])
        else:
            content = msg_any
        if lang_server == "fr":
            embed = discord.Embed(title="Liste des membres bannis :", description="- " + content, color=0xFF0000)
        elif lang_server == "en":
            embed = discord.Embed(title="List of banned members:", description="- " + content, color=0xFF0000)
        elif lang_server == "de":
            embed = discord.Embed(title="Liste der verbotenen Mitglied:", description="- " + content, color=0xFF0000)
        return await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=["sharebot", "share", "invitebot"])
async def shareme(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if lang_server == "fr":
            return await ctx.send("Tu peux partager ce lien pour m'inviter sur d'autres serveurs :\n" + config["PUBLIC"]["invite"])
        elif lang_server == "en":
            return await ctx.send("You can share this link to invite me to other servers:\n" + config["PUBLIC"]["invite"])
        elif lang_server == "de":
            return await ctx.send("Sie können diesen Link teilen, um mich zu anderen Servern einzuladen:\n" + config["PUBLIC"]["invite"])

# TYPE Utilities cmds

#----------------------------- UTILITIES COMMANDS -----------------------------#

@client.command(pass_context=True, aliases=["totalmsg"])
async def msgtotal(ctx, *args):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not ctx.message.channel.guild.me.guild_permissions.administrator:
            if lang_server == "fr":
                return await ctx.send(":x: Il manque la permissions **Administrateur** au bot.")
            elif lang_server == "en":
                return await ctx.send(":x: The bot is missing **Administrator** permissions.")
            elif lang_server == "de":
                return await ctx.send(":x: Dem Bot fehlen **Administrator** Berechtigungen.")
        if len(args) == 2:
            member = discord.utils.get(client.get_all_members(), id=str(args[1])[2:-1])
            args = args[0]
        elif len(args) == 1:
            args = args[0]
            if str(args)[2:-1].isdigit():
                member = discord.utils.get(client.get_all_members(), id=str(args)[2:-1])
                args = "all"
            elif not args == "all" and not args == "channel":
                if lang_server == "fr":
                    return await ctx.send(f"Merci de préciser un argument valide : `{prefix_server}msgtotal [all / channel] [@membre]`.")
                elif lang_server == "en":
                    return await ctx.send(f"Please specify a valid argument: `{prefix_server}msgtotal [all / channel] [@membre]`.")
                elif lang_server == "de":
                    return await ctx.send(f"Bitte geben Sie eine richtiges Argument: `{prefix_server}msgtotal [all / channel] [@membre]`.")
            else:
                member = ctx.message.author
        else:
            member = ctx.message.author
            args = "all"

        if not isinstance(ctx.channel, discord.TextChannel):
            args = "channel"
        counter = 0
        if lang_server == "fr":
            embed = discord.Embed(title="Calcul des messages...", color=0xFFA500)
        elif lang_server == "en":
            embed = discord.Embed(title="Calculating messages...", color=0xFFA500)
        elif lang_server == "de":
            embed = discord.Embed(title="Nachrichten werden berechnet...", color=0xFFA500)
        tmp = await ctx.send(embed=embed)
        if args == "":
            args = "all"
        if args == "all":
            msg_total = True
            channel_list = [x for x in ctx.message.guild.channels if isinstance(x, discord.TextChannel)]
            for channel in channel_list:
                async for log in channel.history(limit=1000000):
                    if log.author == member:
                        counter += 1
        elif args == "channel":
            msg_total = False
            async for log in ctx.message.channel.history(limit=1000000):
                if log.author == member:
                    counter += 1
        else:
            await tmp.delete()
            if lang_server == "fr":
                return await ctx.send(f"Merci de préciser un argument valide : `{prefix_server}msgtotal [all / channel] [@membre]`.")
            elif lang_server == "en":
                return await ctx.send(f"Please specify a valid argument: `{prefix_server}msgtotal [all / channel] [@membre]`.")
            elif lang_server == "de":
                return await ctx.send(f"Bitte geben Sie eine ein richtiges Argument: `{prefix_server}msgtotal [all / channel] [@membre]`.")

        if lang_server == "fr":
            if msg_total == True:
                content = f"**{member}** a envoyé **{counter}** messages au total."
            else:
                content = f"**{member}** a envoyé **{counter}** messages dans ce channel."
            embed = discord.Embed(title="**Nombre de messages :**", description=content, color=0xFFA500)
            embed.set_footer(text=f"Demandé par : {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "en":
            if msg_total == True:
                content = f"**{member}** has sent **{counter}** messages in total."
            else:
                content = f"**{member}** has sent **{counter}** messages in this channel."
            embed = discord.Embed(title="**Number of messages:**", description=content, color=0xFFA500)
            embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "de":
            if msg_total == True:
                content = f"**{member}** hast **{counter}** Nachrichten insgesamt gesendet."
            else:
                content = f"**{member}** hast **{counter}** Nachrichten in diesem Chatroom gesendet."
            embed = discord.Embed(title="**Anzahl der Nachrichten:**", description=content, color=0xFFA500)
            embed.set_footer(text="Angefordert von: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)

        if not isinstance(ctx.channel, discord.TextChannel):
            return await tmp.edit(embed=embed)
        await tmp.edit(embed=embed)
        await asyncio.sleep(5)
        return await ctx.message.delete()

@client.command(name="embed", pass_context=True, aliases=["embeds", "richembed"])
async def _embed(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        def r(): return random.randint(0, 255)
        def random_color(): return int("0x%02X%02X%02X" % (r(), r(), r()), 16)

        if not args:
            if lang_server == "fr":
                return await ctx.send(f"Merci de préciser un argument valide : `{prefix_server}embed T=Titre D=Description C=Couleur I=ImageURL F=Footer U=URL A=Auteur`.")
            elif lang_server == "en":
                return await ctx.send(f"Please specify a valid argument: `{prefix_server}embed T=Title D=Description C=Color I=ImageURL F=Footer U=URL A=Author`.")
            elif lang_server == "de":
                return await ctx.send(f"Bitte geben Sie eine ein richtiges Argument: `{prefix_server}embed T=Titel D=Description C=Color I=ImageURL F=Footer U=URL A=Author`.")

        content = re.split(r".=", args)[1:]
        content = [x.strip() for x in content]
        sep = re.findall(r".=", args)
        title = description = color = thumbnail = footer = url = author = None
        for x in range(len(sep)):
            if "T=" == sep[x]:
                title = content[x]
            if "D=" == sep[x]:
                description = content[x]
            if "C=" == sep[x]:
                color = content[x]
            if "I=" == sep[x]:
                thumbnail = content[x]
            if "F=" == sep[x]:
                footer = content[x]
            if "U=" == sep[x]:
                url = content[x]
            if "A=" == sep[x]:
                author = content[x]
        if all(x is None for x in [title, description, color, thumbnail, footer, url, author]):
            if len(args) <= 255:
                title = args
            else:
                title = None
                description = args
        if not title:
            if description and len(args) <= 255:
                title = description
                description = None
        if color == "random":
            color = random_color()
        elif color is not None:
            if any([x for x in colors_embed.keys() if x == color]):
                color = int(colors_embed[color], 16)
            else:
                if color.isdigit():
                    if int(color) >= 16777215:
                        color = 16777215
                else:
                    try:
                        color = int("0x" + color, 16)
                        if color >= 16777215:
                            color = 16777215
                    except:
                        if lang_server == "fr":
                            return await ctx.send("La couleur mentionnée n'existe pas. Paramètres supportés : `nom couleur`, `valeur hexa`, `valeur nombre entier`, `random`.")
                        elif lang_server == "en":
                            return await ctx.send("The mentionned color does not exists. Supported parameters: `color name`, `hex value`, `int value`, `random`.")
                        elif lang_server == "en":
                            return await ctx.send("Die angegebene Farbe existiert nicht. Unterstützte Parameter: `Farbname`, ` Hex-Wert`, `Nummer-Wert`, `random`.")
        else:
            color = random_color()
        embed = discord.Embed(title=title, description=description, color=color, url=url)
        if thumbnail:
            if not "http" in thumbnail:
                thumbnail = "https://" + thumbnail.split("//")[-1]
            try:
                if "image/" in str(requests.get(thumbnail).headers):
                    embed.set_thumbnail(url=thumbnail)
                else:
                    embed.set_thumbnail(url="https://quentium.fr/+Files/discord/question.png")
            except:
                embed.set_thumbnail(url="https://quentium.fr/+Files/discord/question.png")
        if author:
            embed.set_author(name=author)
        if footer:
            if not footer == "None":
                embed.set_footer(text=footer)
        else:
            if lang_server == "fr":
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            elif lang_server == "en":
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            elif lang_server == "de":
                embed.set_footer(text=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        return await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=["lettre", "emojis", "emoji"])
async def letter(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not args:
            if lang_server == "fr":
                return await ctx.send("Merci de préciser un texte.")
            elif lang_server == "en":
                return await ctx.send("Please specify a text.")
            elif lang_server == "de":
                return await ctx.send("Bitte geben Sie einen text an.")

        lst = []
        emojis_used = re.findall(r"<\w*:\w*:\d*>", args)
        emojis_temp = []
        if emojis_used:
            for emoji in emojis_used:
                if int(emoji.split(":", 2)[2].split(">")[0]) in [x.id for x in client.emojis]:
                    args = args.replace(emoji, "☺")  # Custom emoji
                else:
                    args = args.replace(emoji, "☻")
                    emojis_temp.append(emoji)
        for emojis in emojis_temp:
            emojis_used.remove(emojis)
        is_mention = re.findall(r"<@\d*>", args)
        for mention in is_mention:
            args = args.replace(mention, str(discord.utils.get(client.get_all_members(), id=int(mention[2:-1])).name))
        letter = list(str(args.lower()))
        for char in range(len(letter)):
            if any(x == letter[char] for x in letters.keys()):
                if "emo(" in letters[letter[char]]:
                    lst += emo(letters[letter[char]].replace("emo(", "")[0:-1])
                else:
                    lst += letters[letter[char]]
            elif any(x in letter[char] for x in ["â", "ä", "à", "å"]):
                lst += ":regional_indicator_a:"
            elif any(x in letter[char] for x in ["ê", "ë", "è", "é"]):
                lst += ":regional_indicator_e:"
            elif any(x in letter[char] for x in ["î", "ï", "ì", "í"]):
                lst += ":regional_indicator_i:"
            elif any(x in letter[char] for x in ["ô", "ö", "ò", "ó"]):
                lst += ":regional_indicator_o:"
            elif any(x in letter[char] for x in ["û", "ü", "ù", "ú"]):
                lst += ":regional_indicator_u:"
            elif letter[char].isalpha() == True:
                lst += ":regional_indicator_" + letter[char] + ":"
            elif letter[char] == "☺":
                lst.append(str(emojis_used[0]))
                del emojis_used[0]
            else:
                lst.append(letter[char])
        content = "".join(lst)
        def comb(s, n): return [s[i:i + n] for i in range(0, len(s), n)]
        embeds_temp = comb(content, 2019)
        embeds = []
        cut_end_embed = [""]
        for x in embeds_temp:
            full_embed = re.split(r"(<\w*:\w*:\d*>|:)", x)[:-2]
            embeds.append("".join(cut_end_embed + full_embed))
            cut_end_embed = re.split(r"(<\w*:\w*:\d*>|:)", x)[-2:]
        embeds[-1] = embeds[-1] + "".join(cut_end_embed)
        for content in embeds:
            embed = discord.Embed(title=None, description=content, color=0xFFA952)
            if content == embeds[-1]:
                if lang_server == "fr":
                    embed.set_footer(text=f"Demandé par : {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
                elif lang_server == "en":
                    embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
                elif lang_server == "de":
                    embed.set_footer(text=f"Angefordert von: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
                return await ctx.send(embed=embed)
            await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=["meteo"])
async def weather(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if lang_server == "fr":
            msg_condition = "Condition météo :"
            msg_cloud = ":cloud: Nuageux : "
            msg_rain = ":cloud_rain: Volume de pluie (dernières 3h) : "
            msg_snow = ":cloud_snow: Volume de neige (dernières 3h) : "
            msg_temp = ":thermometer: Température :"
            msg_humidity = ":sweat_drops: Humidité : "
            msg_wind = ":wind_blowing_face: Vitesse du vent :"
            msg_city = "Météo actuelle à "
            msg_local_time = "Date locale :"
            msg_sunrise = "Lever du soleil :"
            msg_sunset = " • Coucher du soleil :"
        elif lang_server == "en":
            msg_condition = "Weather condition:"
            msg_cloud = ":cloud: Cloudiness: "
            msg_rain = ":cloud_rain: Rain volume (last 3h): "
            msg_snow = ":cloud_snow: Snow volume (last 3h): "
            msg_temp = ":thermometer: Temperature:"
            msg_humidity = ":sweat_drops: Humidity: "
            msg_wind = ":wind_blowing_face: Wind speed:"
            msg_city = "Current weather at "
            msg_local_time = "Local date:"
            msg_sunrise = "Sunrise:"
            msg_sunset = " • Sunset:"
        elif lang_server == "de":
            msg_condition = "Wetterlage:"
            msg_cloud = ":cloud: Trübung: "
            msg_rain = ":cloud_rain: Regenvolum (letzte 3h): "
            msg_snow = ":cloud_snow: Schneevolum (letzte 3h): "
            msg_temp = ":thermometer: Temperatur:"
            msg_humidity = ":sweat_drops: Feuchtigkeit: "
            msg_wind = ":wind_blowing_face: Windgeschwindigkeit:"
            msg_city = "Aktuelles Wetter bei "
            msg_local_time = "Lokales Datum:"
            msg_sunrise = "Sonnenaufgang:"
            msg_sunset = " • Sonnenuntergang:"

        if not args:
            if lang_server == "fr":
                embed = discord.Embed(title="Merci de préciser une ville.", color=0x00FFFF)
            elif lang_server == "en":
                embed = discord.Embed(title="Please specify a city.", color=0x00FFFF)
            elif lang_server == "de":
                embed = discord.Embed(title="Bitte geben Sie eine Stadt an.", color=0x00FFFF)
            return await ctx.send(embed=embed)
        args = args.replace(" ", "%20")
        url = "https://api.openweathermap.org/data/2.5/weather?q=" + args
        data_weather = requests.get(url + f"&appid={token_weather}&lang={lang_server}").json()
        if "city not found" in str(data_weather):
            if lang_server == "fr":
                embed = discord.Embed(title="La ville n'a pas été trouvée.", color=0x00FFFF)
            elif lang_server == "en":
                embed = discord.Embed(title="The city was not found.", color=0x00FFFF)
            elif lang_server == "de":
                embed = discord.Embed(title="Die Stadt wurde nicht gefunden.", color=0x00FFFF)
            return await ctx.send(embed=embed)
        if not data_weather["coord"]:
            return
        lat, long = str(data_weather["coord"]["lat"]), str(data_weather["coord"]["lon"])
        url = f"https://api.timezonedb.com/v2/get-time-zone?key={token_timezone}&format=json&by=position&lat={lat}&lng={long}"
        try:
            current_time = requests.get(url).json()["formatted"]
        except:
            current_time = data_weather["dt"]
        emoji = discord.utils.get(client.emojis, name=str(data_weather["weather"][0]["icon"]))
        condition = data_weather["weather"][0]["main"]
        if lang_server == "fr":
            if condition == "Thunderstorm":
                condition = "Orage"
            if condition == "Drizzle":
                condition = "Bruine"
            if condition == "Rain":
                condition = "Pluie"
            if condition == "Snow":
                condition = "Neige"
            if condition == "Mist":
                condition = "Brouillard"
            if condition == "Clear":
                condition = "Clair"
            if condition == "Clouds":
                condition = "Nuages"
            if condition == "Tornado":
                condition = "Tornade"
            if condition == "Haze":
                condition = "Brume"
        elif lang_server == "de":
            if condition == "Thunderstorm":
                condition = "Gewitter"
            if condition == "Drizzle":
                condition = "Nieselregen"
            if condition == "Rain":
                condition = "Regen"
            if condition == "Snow":
                condition = "Schnee"
            if condition == "Mist":
                condition = "Nebel"
            if condition == "Clear":
                condition = "Klar"
            if condition == "Clouds":
                condition = "Wolken"
            if condition == "Haze":
                condition = "Nebel"
        desc = str(data_weather["weather"][0]["description"])
        content = f"{emoji} {msg_condition} {condition} - \"{desc.title()}\"\n"
        try:
            content += msg_cloud + str(data_weather["clouds"]["all"]) + "%\n"
        except:
            pass
        try:
            content += msg_rain + str(data_weather["rain"]["3h"]) + "L/m²\n"
        except:
            pass
        try:
            content += msg_snow + str(data_weather["snow"]["3h"]) + "L/m²\n"
        except:
            pass
        temp_celcius = str(round(data_weather["main"]["temp"] - 273.15, 1))
        temp_farenheit = str(round(data_weather["main"]["temp"] * 9 / 5 - 459.67, 1))
        if lang_server == "fr" or lang_server == "de":
            content += f"{msg_temp} {temp_celcius}°C\n"
        elif lang_server == "en":
            content += f"{msg_temp} {temp_celcius}°C - {temp_farenheit}°F\n"
        content += msg_humidity + str(data_weather["main"]["humidity"]) + "%\n"
        wind_speed = data_weather["wind"]["speed"]
        content += f"{msg_wind} {float(wind_speed)}m/s - {round(float(wind_speed) * 3.6, 1)}km/h\n\n"
        sunrise_time = datetime.fromtimestamp(int(data_weather["sys"]["sunrise"])).strftime("%H:%M:%S")
        sunset_time = datetime.fromtimestamp(int(data_weather["sys"]["sunset"])).strftime("%H:%M:%S")
        content += f"<:time:475328338542592000> {msg_sunrise} {sunrise_time} {msg_sunset} {sunset_time} (DST)"
        embed = discord.Embed(title=msg_city + data_weather["name"] + " :flag_" + str(data_weather["sys"]["country"]).lower() + ":\n", description=content, color=0x00FFFF)
        embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji.id}.png")
        embed.set_footer(text=f"{msg_local_time} {current_time}", icon_url="https://cdn.discordapp.com/emojis/475328334557872129.png")
        return await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=["lyric", "paroles", "parole"])
async def lyrics(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not args:
            if lang_server == "fr":
                return await ctx.send("Merci de préciser une musique.")
            elif lang_server == "en":
                return await ctx.send("Please specify a music.")
            elif lang_server == "de":
                return await ctx.send("Bitte geben Sie eine Musik.")
        request_url = "https://api.genius.com/search/"
        query = {"q": args}
        headers = {"Authorization": "Bearer " + token_genius}
        r = requests.get(request_url, params=query, headers=headers).json()

        if not r["response"]["hits"]:
            if lang_server == "fr":
                return await ctx.send("La musique n'a pas été trouvée ou n'existe pas.")
            elif lang_server == "en":
                return await ctx.send("The music has not been found or does not exist.")
            elif lang_server == "de":
                return await ctx.send("Die Musik wurde nicht gefunden oder existiert nicht.")
        path_lyrics = r["response"]["hits"][0]["result"]["path"]
        URL = "https://genius.com" + path_lyrics
        page = requests.get(URL)
        html = BeautifulSoup(page.text, "html.parser")

        try:
            lyrics = html.find("div", class_="lyrics").get_text()
        except:
            if lang_server == "fr":
                return await ctx.send("La musique demandée ne contient pas de paroles.")
            elif lang_server == "en":
                return await ctx.send("The requested music does not contain lyrics.")
            elif lang_server == "de":
                return await ctx.send("Die angeforderte Musik enthält keinen Text.")
        if len(lyrics) > 5900:
            if lang_server == "fr":
                return await ctx.send("Le résultat est trop long (limite discord). Cela peut être aussi causé par l'absence de lyrics de vôtre recherche.")
            elif lang_server == "en":
                return await ctx.send("The result is too long (discord limit). This can also be caused by the absence of lyrics from your research.")
            elif lang_server == "de":
                return await ctx.send("Das Ergebnis ist zu lang (Discord Limit). Dies kann auch durch das Fehlen von Texten aus Ihrer Forschung verursacht werden.")
        title = r["response"]["hits"][0]["result"]["full_title"]
        image = r["response"]["hits"][0]["result"]["header_image_url"]
        if not any(x.lower() in title.lower() for x in args.split()):
            if lang_server == "fr":
                await ctx.send("La recherche ne correspond pas au titre, assurez vous d'avoir bien entré le nom de la musique.")
                await ctx.send(f"Résultat trouvé avec : **{args}**")
            elif lang_server == "en":
                await ctx.send("The search does not match the title, make sure you have entered the name of the music.")
                await ctx.send(f"Result found with: **{args}**")
            elif lang_server == "de":
                await ctx.send("Die Suche stimmt nicht mit dem Titel überein. Vergewissern Sie sich, dass Sie den Namen der Musik eingegeben haben.")
                await ctx.send(f"Ergebnis gefunden mit: **{args}**")
        if lang_server == "fr":
            embed = discord.Embed(title=f"Paroles de : __**{title}**__", description=None, color=0x00FFFF)
        elif lang_server == "en":
            embed = discord.Embed(title=f"Lyrics of: __**{title}**__", description=None, color=0x00FFFF)
        elif lang_server == "de":
            embed = discord.Embed(title=f"Songtexte von: __**{title}**__", description=None, color=0x00FFFF)
        embed.set_thumbnail(url=image)
        for block in lyrics.split("\n\n")[1:-1]:
            splitted = block.split("\n", 1)
            if splitted[0] != "":
                if not len(splitted) == 1:
                    if len(splitted[1]) >= 1024:
                        embed.add_field(name=splitted[0], value=splitted[1][0:1023])
                    else:
                        embed.add_field(name=splitted[0], value=splitted[1])
                else:
                    embed.add_field(name=splitted[0], value=":notes:" * 6)
        if lang_server == "fr":
            embed.set_footer(text=f"Demandé par : {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "en":
            embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "de":
            embed.set_footer(text=f"Angefordert von: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        return await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=["av", "avatars"])
async def avatar(ctx, *, member: discord.Member = None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not member:
            member = ctx.message.author
        icon = str(member.avatar_url)
        icon1 = icon.split(".", 999)
        icon2 = "".join(icon1[len(icon1) - 1])
        icon3 = icon.replace(icon2, "")
        if "gif" in icon:
            avatar_url = icon3 + "gif?size=1024"
        else:
            avatar_url = icon3 + "png?size=1024"
        title = member.name + "#" + member.discriminator
        content = "[Avatar URL]({})".format(avatar_url)
        embed = discord.Embed(title=f"**{title}**", description=content, color=0x15f2c6)
        embed.set_image(url=avatar_url)
        if lang_server == "fr":
            embed.set_footer(text=f"Demandé par : {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "en":
            embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "de":
            embed.set_footer(text=f"Angefordert von: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        return await ctx.send(embed=embed)

# TYPE Stats cmds

#----------------------------- STATISTICS COMMANDS -----------------------------#

@client.command(pass_context=True, no_pm=True, aliases=["statsuser", "statuser", "userinfo", "userinfos"])
async def userstats(ctx, *, member: discord.Member = None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if lang_server == "fr":
            msg_any = "Aucun"
            msg_yes = "Oui"
            msg_no = "Non"
            msg_online = "En ligne"
            msg_offline = "Hors ligne"
            msg_idle = "Absent"
            msg_dnd = "Ne pas déranger"
            msg_invisible = "Invisible"
        elif lang_server == "en":
            msg_any = "None"
            msg_yes = "Yes"
            msg_no = "No"
            msg_online = "Online"
            msg_offline = "Offline"
            msg_idle = "Absent"
            msg_dnd = "Do not disturb"
            msg_invisible = "Invisible"
        elif lang_server == "de":
            msg_any = "Keine"
            msg_yes = "Ja"
            msg_no = "Nein"
            msg_online = "Online"
            msg_offline = "Offline"
            msg_idle = "Abwesend"
            msg_dnd = "Beschäftigt"
            msg_invisible = "Unsichtbar"

        if not member:
            member = ctx.message.author
        user_name = member.name
        user_nickname = msg_any if member.nick == None else str(member.nick)
        user_id = str(member.id)
        user_tag = member.name + "#" + member.discriminator
        user_mention = member.mention
        user_is_bot = msg_yes if member.bot == True else msg_no
        status = str(member.status).lower()
        if status == "online":
            user_status = msg_online
        elif status == "offline":
            user_status = msg_offline
        elif status == "idle":
            user_status = msg_idle
        elif status == "dnd":
            user_status = msg_dnd
        elif status == "invisible":
            user_status = msg_invisible
        user_game = msg_any if member.activity == None else str(member.activity.name)
        user_joinserv = datetime.strptime(str(member.joined_at)[:-7], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y - %H:%M:%S")
        user_joindiscord = datetime.strptime(str(member.created_at)[
                                             :-7], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y - %H:%M:%S")
        user_best_role = str(member.top_role)
        user_roles = str(len([x.name for x in member.roles]))
        user_roles_list = ", ".join([x.name for x in member.roles])

        embed = discord.Embed(color=0x0026FF)
        icon = str(member.avatar_url)
        icon1 = icon.split(".", 999)
        icon2 = "".join(icon1[len(icon1) - 1])
        icon3 = icon.replace(icon2, "")
        avatar_url = icon3 + "png?size=1024"
        if member.avatar_url is not None:
            embed.set_thumbnail(url=avatar_url)
        else:
            embed.set_thumbnail(url=member.default_avatar_url)

        if lang_server == "fr":
            content = "```autohotkey\n" \
                "Nom:                %s\n" \
                "Surnom:             %s\n" \
                "ID:                 %s\n" \
                "Tag:                %s\n" \
                "Mention:            %s\n" \
                "Bot:                %s\n" \
                "Status:             %s\n" \
                "Jeu:                %s\n" \
                "Rejoins serveur le: %s\n" \
                "Rejoins discord le: %s\n" \
                "Meilleur Rôle:      %s\n" \
                "Rôles:              %s\n" \
                "%s" "```" % (user_name, user_nickname, user_id, user_tag, user_mention, user_is_bot, user_status,
                              user_game, user_joinserv, user_joindiscord, user_best_role, user_roles, user_roles_list)
            embed.add_field(name=f"Statistiques de __***{user_name}***__", value=content + " ***[Lien Icône]({})***".format(avatar_url), inline=True)
            embed.set_footer(text=f"Demandé par : {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "en":
            content = "```autohotkey\n" \
                "Name:               %s\n" \
                "Nickname:           %s\n" \
                "ID:                 %s\n" \
                "Tag:                %s\n" \
                "Mention:            %s\n" \
                "Bot:                %s\n" \
                "Status:             %s\n" \
                "Game:               %s\n" \
                "Join server at:     %s\n" \
                "Join Discord at:    %s\n" \
                "Best Role:          %s\n" \
                "Roles:              %s\n" \
                "%s" "```" % (user_name, user_nickname, user_id, user_tag, user_mention, user_is_bot, user_status,
                              user_game, user_joinserv, user_joindiscord, user_best_role, user_roles, user_roles_list)
            embed.add_field(name=f"Statistics of __***{user_name}***__", value=content +
                            " ***[Icon Link]({})***".format(avatar_url), inline=True)
            embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "de":
            content = "```autohotkey\n" \
                "Name:               %s\n" \
                "Spitzname:          %s\n" \
                "ID:                 %s\n" \
                "Tag:                %s\n" \
                "Erwähnung:          %s\n" \
                "Bot:                %s\n" \
                "Status:             %s\n" \
                "Spielt:             %s\n" \
                "Trat Server bei:    %s\n" \
                "Trat Discord bei:   %s\n" \
                "Primaire Rolle:     %s\n" \
                "Rollen:             %s\n" \
                "%s" "```" % (user_name, user_nickname, user_id, user_tag, user_mention, user_is_bot, user_status,
                              user_game, user_joinserv, user_joindiscord, user_best_role, user_roles, user_roles_list)
            embed.add_field(name=f"__***{user_name}***__'s Statistiken", value=content +
                            " ***[Symbolverbindung]({})***".format(avatar_url), inline=True)
            embed.set_footer(text="Angefordert von : " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        return await ctx.send(embed=embed)

@client.command(pass_context=True, no_pm=True, aliases=["serveurstats", "statsserveur", "statserveur", "statserver", "statsserver", "servstats", "serverinfos", "serverinfo", "servinfo"])
async def serverstats(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if lang_server == "fr":
            msg_any = "Aucun"
            msg_low = "Faible"
            msg_medium = "Moyen"
            msg_high = "Elevé"
            msg_extreme = "Extrême"
            msg_limit = "La longueur de la liste des rôles est supérieure à ce que discord peut envoyer."
        elif lang_server == "en":
            msg_any = "None"
            msg_low = "Low"
            msg_medium = "Medium"
            msg_high = "High"
            msg_extreme = "Extreme"
            msg_limit = "The length of the roles list is greater than what discord can send."
        elif lang_server == "de":
            msg_any = "Keine"
            msg_low = "Niedrig"
            msg_medium = "Mittel"
            msg_high = "Hoch"
            msg_extreme = "Extrem"
            msg_limit = "Die länge der Rollenliste ist Größer als die die Discord senden kann."

        serv = ctx.message.guild
        serv_name = serv.name
        serv_id = str(serv.id)
        serv_owner = serv.owner.name
        serv_owner_dis = "#" + serv.owner.discriminator
        serv_created = datetime.strptime(str(serv.created_at)[:-7], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y - %H:%M:%S")
        serv_region = serv.region
        serv_members = str(len(serv.members))
        serv_members_on = str(len([x for x in serv.members if not x.status == discord.Status.offline]))
        serv_users = str(len([x for x in serv.members if not x.bot]))
        serv_users_on = str(len([x for x in serv.members if not x.bot and not x.status == discord.Status.offline]))
        serv_bots = str(len([x for x in serv.members if x.bot]))
        serv_bots_on = str(len([x for x in serv.members if x.bot and not x.status == discord.Status.offline]))
        serv_channels = str(len([x for x in serv.channels if not isinstance(x, discord.CategoryChannel)]))
        serv_text_channels = str(len([x for x in serv.channels if isinstance(x, discord.TextChannel)]))
        serv_voice_channels = str(len([x for x in serv.channels if isinstance(x, discord.VoiceChannel)]))
        serv_afk_channel = msg_any if serv.afk_channel == None else str(serv.afk_channel)
        serv_afk_time = str(round(int(serv.afk_timeout) / 60))
        verif = str(serv.verification_level)
        if verif == "none":
            serv_verif_lvl = msg_any
        elif verif == "low":
            serv_verif_lvl = msg_low
        elif verif == "medium":
            serv_verif_lvl = msg_medium
        elif verif == "high":
            serv_verif_lvl = msg_high
        elif verif == "extreme":
            serv_verif_lvl = msg_extreme
        serv_roles = str(len([x.name for x in serv.roles]))
        serv_roles_list = ", ".join([x.name for x in serv.roles])
        if len(serv_roles_list) > 450:
            serv_roles_list = msg_limit

        embed = discord.Embed(url="https://quentium.fr/discord/", color=0x0026FF)
        icon = str(serv.icon_url)
        icon1 = icon.split(".", 999)
        icon2 = "".join(icon1[len(icon1) - 1])
        icon3 = icon.replace(icon2, "")
        icon_url = icon3 + "png?size=1024"
        if len(serv.icon_url):
            embed.set_thumbnail(url=icon_url)
        else:
            embed.set_thumbnail(url="https://quentium.fr/+Files/discord/question.png")

        if lang_server == "fr":
            content = "```autohotkey\n" \
                "Nom:                %s\n" \
                "ID:                 %s\n" \
                "Propriétaire:       %s (%s)\n" \
                "Crée le:            %s\n" \
                "Région:             %s\n" \
                "Membres:            %s (%s En ligne)\n" \
                "    Personnes:      %s (%s En ligne)\n" \
                "    Bots:           %s (%s En ligne)\n" \
                "Salons:             %s\n" \
                "    Textuels:       %s\n" \
                "    Vocaux:         %s\n" \
                "Salon AFK:          %s\n" \
                "Temps AFK:          %s min\n" \
                "Niveau vérif:       %s\n" \
                "Rôles:              %s\n" \
                "%s" "```" % (serv_name, serv_id, serv_owner, serv_owner_dis, serv_created, serv_region, serv_members, serv_members_on, serv_users, serv_users_on, serv_bots,
                              serv_bots_on, serv_channels, serv_text_channels, serv_voice_channels, serv_afk_channel, serv_afk_time, serv_verif_lvl, serv_roles, serv_roles_list)
            embed.add_field(name=f"Statistiques du serveur __***{serv_name}***__", value=content + " ***[Lien Icône]({})***".format(icon_url), inline=True)
            embed.set_footer(text=f"Demandé par : {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "en":
            content = "```autohotkey\n" \
                "Name:               %s\n" \
                "ID:                 %s\n" \
                "Owner:              %s (%s)\n" \
                "Created at:         %s\n" \
                "Region:             %s\n" \
                "Members:            %s (%s Online)\n" \
                "    Users:          %s (%s Online)\n" \
                "    Bots:           %s (%s Online)\n" \
                "Channels:           %s\n" \
                "    Text:           %s\n" \
                "    Voice:          %s\n" \
                "AFK Channel:        %s\n" \
                "AFK Time:           %s min\n" \
                "Verify level:       %s\n" \
                "Roles:              %s\n" \
                "%s" "```" % (serv_name, serv_id, serv_owner, serv_owner_dis, serv_created, serv_region, serv_members, serv_members_on, serv_users, serv_users_on, serv_bots,
                              serv_bots_on, serv_channels, serv_text_channels, serv_voice_channels, serv_afk_channel, serv_afk_time, serv_verif_lvl, serv_roles, serv_roles_list)
            embed.add_field(name=f"Statistics of __***{serv_name}***__ Server", value=content + " ***[Icon Link]({})***".format(icon_url), inline=True)
            embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "de":
            content = "```autohotkey\n" \
                "Name:               %s\n" \
                "ID:                 %s\n" \
                "Inhaber:            %s (%s)\n" \
                "Hergestellt in:     %s\n" \
                "Region:             %s\n" \
                "Mitglied:           %s (%s Online)\n" \
                "    Leute:          %s (%s Online)\n" \
                "    Bots:           %s (%s Online)\n" \
                "Kanäle:             %s\n" \
                "    Text:           %s\n" \
                "    Sprach:         %s\n" \
                "AFK Kanäle:         %s\n" \
                "AFK Zeit:           %s min\n" \
                "Verify Stufe:       %s\n" \
                "Rollen:             %s\n" \
                "%s" "```" % (serv_name, serv_id, serv_owner, serv_owner_dis, serv_created, serv_region, serv_members, serv_members_on, serv_users, serv_users_on, serv_bots,
                              serv_bots_on, serv_channels, serv_text_channels, serv_voice_channels, serv_afk_channel, serv_afk_time, serv_verif_lvl, serv_roles, serv_roles_list)
            embed.add_field(name=f"__***{serv_name}***__'s Serverstatistiken", value=content + " ***[Symbolverbindung]({})***".format(icon_url), inline=True)
            embed.set_footer(text=f"Angefordert von: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        return await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=["botstat", "statsbot", "statbot"])
async def botstats(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name, start_time
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if lang_server == "fr":
            msg_day = "Jours"
            msg_hour = "Heures"
            msg_minutes = "Minutes"
            msg_seconds = "Secondes"
        elif lang_server == "en":
            msg_day = "Days"
            msg_hour = "Hours"
            msg_minutes = "Minutes"
            msg_seconds = "Seconds."
        elif lang_server == "de":
            msg_day = "Tage"
            msg_hour = "Stunden"
            msg_minutes = "Minuten"
            msg_seconds = "Sekunden"

        bot_host = "Raspberry Pi 3"
        bot_owner = "QuentiumYT#0207"
        bot_version = "Debian 8.0 (Raspbian)"
        time = round((datetime.now() - start_time).total_seconds())
        m, s = divmod(int(time), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        bot_uptime = f"{d} {msg_day}, {h} {msg_hour}, {m} {msg_minutes}, {s} {msg_seconds}"
        bot_memory = psutil.virtual_memory().used >> 20
        if isinstance(ctx.channel, discord.TextChannel):
            bot_commands_get = commands_server
        else:
            if lang_server == "fr":
                bot_commands_get = "Indisponible en MP"
            elif lang_server == "en":
                bot_commands_get = "Not available in PM"
            elif lang_server == "de":
                bot_commands_get = "In PN nicht verfügbar"

        bot_commands_get_total = 0
        for serv in data.keys():
            bot_commands_get_total += data[serv]["commands_server"]
        users = 0
        for serv in client.guilds:
            users += len(serv.members)
        bot_users_total = str(users)
        bot_servers_total = len(client.guilds)
        bot_lang_fr = bot_lang_en = bot_lang_de = 0
        for serv in data.keys():
            if "fr" in data[serv]["lang_server"]:
                bot_lang_fr += 1
            elif "en" in data[serv]["lang_server"]:
                bot_lang_en += 1
            elif "de" in data[serv]["lang_server"]:
                bot_lang_de += 1

        embed = discord.Embed(url="https://quentium.fr/discord/", color=0x0026FF)
        embed.set_thumbnail(url="https://quentium.fr/+img/logoBot.png")
        if lang_server == "fr":
            content = "```autohotkey\n" \
                "Hébergée sur:         %s\n" \
                "Propriétaire:         %s\n" \
                "Linux version:        %s\n" \
                "Durée fonctionnement: %s\n" \
                "Mémoire utilisée:     %s Mo\n" \
                "Commandes reçues:     %s (serveur)\n" \
                "Commandes reçues:     %s (total)\n" \
                "Statistiques:         %s utilisateurs dans %s serveurs\n" \
                "Serveurs FR:          %s\n" \
                "Serveurs EN:          %s\n" \
                "Serveurs DE:          %s\n" \
                "```" % (bot_host, bot_owner, bot_version, bot_uptime, bot_memory, bot_commands_get, bot_commands_get_total,
                         bot_users_total, bot_servers_total, bot_lang_fr, bot_lang_en, bot_lang_de)
            embed.add_field(name="Statistiques du __***QuentiumBot***__", value=content, inline=True)
            embed.set_footer(text=f"Demandé par : {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "en":
            content = "```autohotkey\n" \
                "Hosted on:            %s\n" \
                "Owner:                %s\n" \
                "Linux version:        %s\n" \
                "Uptime:               %s\n" \
                "Memory usage:         %s MB\n" \
                "Commands received:    %s (server)\n" \
                "Commands received:    %s (total)\n" \
                "Stats:                %s users on %s servers\n" \
                "Servers FR:           %s\n" \
                "Servers EN:           %s\n" \
                "Servers DE:           %s\n" \
                "```" % (bot_host, bot_owner, bot_version, bot_uptime, bot_memory, bot_commands_get, bot_commands_get_total,
                         bot_users_total, bot_servers_total, bot_lang_fr, bot_lang_en, bot_lang_de)
            embed.add_field(name="Statistics of __***QuentiumBot***__", value=content, inline=True)
            embed.set_footer(text=f"Requested by: {ctx.message.author.name}", icon_url=ctx.message.author.avatar_url)
        elif lang_server == "de":
            content = "```autohotkey\n" \
                "Gehostet auf:         %s\n" \
                "Inhaber:              %s\n" \
                "Linux Version:        %s\n" \
                "Betriebszeit:         %s\n" \
                "Arbeitsspeicher:      %s MB\n" \
                "Befehle bekommen:     %s (server)\n" \
                "Befehle bekommen:     %s (insgesammt)\n" \
                "Statistiken:          %s Benutzer in %s Servers\n" \
                "Servers FR:           %s\n" \
                "Servers EN:           %s\n" \
                "Servers DE:           %s\n" \
                "```" % (bot_host, bot_owner, bot_version, bot_uptime, bot_memory, bot_commands_get, bot_commands_get_total,
                         bot_users_total, bot_servers_total, bot_lang_fr, bot_lang_en, bot_lang_de)
            embed.add_field(name="__***QuentiumBot***__'s Statistiken", value=content, inline=True)
            embed.set_footer(text="Angefordert von : " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        return await ctx.send(embed=embed)

@client.command(pass_context=True, aliases=["timeup", "runningtime", "runtime", "timerun"])
async def uptime(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        time = round((datetime.now() - start_time).total_seconds())
        m, s = divmod(int(time), 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        if lang_server == "fr":
            bot_uptime = f"Le bot est en ligne depuis {d} Jours, {h} Heures, {m} Minutes, {s} Secondes."
        elif lang_server == "en":
            bot_uptime = f"The bot is online for {d} Days, {h} Hours, {m} Minutes, {s} Seconds."
        elif lang_server == "de":
            bot_uptime = f"Der Bot ist online seit {d} Tage, {h} Stunden, {m} Minuten, {s} Sekunden."
        return await ctx.send(bot_uptime)

@client.command(pass_context=True, aliases=["pong"])
async def ping(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        before = time.perf_counter()
        await ctx.trigger_typing()
        ping = round((time.perf_counter() - before) * 500)
        before = time.monotonic()
        tmp = await ctx.send("***Ping message***")
        ping1 = round((time.monotonic() - before) * 500)
        await tmp.delete()
        if lang_server == "fr":
            return await ctx.send(f":ping_pong: Pong!\n- Latence du bot : `{ping}ms`\n- Latence d'envoi de message : `{ping1}ms`")
        elif lang_server == "en":
            return await ctx.send(f":ping_pong: Pong!\n- Bot's latency: `{ping}ms`\n- Message sending latency: `{ping1}ms`")
        elif lang_server == "de":
            return await ctx.send(f":ping_pong: Pong!\n- Bot's Latenz: `{ping}ms`\n- Nachrichtensende-Latenz: `{ping1}ms`")

# TYPE Feedback cmds

#----------------------------- FEEDBACK COMMANDS -----------------------------#

@client.command(pass_context=True, aliases=["bug", "bugs", "ideas", "idee"])
@commands.cooldown(2, 30, commands.BucketType.channel)
async def idea(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        cmd_received = str(ctx.message.content).replace("+", "").split()[0]
        if not args:
            if cmd_received == "idea":
                if lang_server == "fr":
                    return await ctx.send("Merci de préciser une idée.")
                elif lang_server == "en":
                    return await ctx.send("Please specify an idea.")
                elif lang_server == "de":
                    return await ctx.send("Bitte geben Sie eine Idee an.")
            elif cmd_received == "bug":
                if lang_server == "fr":
                    return await ctx.send("Merci de préciser un bug.")
                elif lang_server == "en":
                    return await ctx.send("Please specify a bug.")
                elif lang_server == "de":
                    return await ctx.send("Bitte geben Sie eine Bug an.")
        ideas = " --- ".join([ctx.message.author.name, cmd_received, args])
        with open("feedback.txt", "a", encoding="utf-8", errors="ignore") as file:
            file.write(ideas + "\n")
        if lang_server == "fr":
            return await ctx.send("Merci de contribuer à l'amélioration du bot !")
        elif lang_server == "en":
            return await ctx.send("Thank you for contributing to improve the bot!")
        elif lang_server == "de":
            return await ctx.send("Danke, dass Sie zur Verbesserung des Bot beigetragen haben!")

@client.command(pass_context=True, aliases=["logs", "showlog", "changelog", "whatsnew", "whatnew"])
async def showlogs(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if lang_server == "fr":
            embed = discord.Embed(title="Logs de mise à jour du bot :", url="https://quentium.fr/discord/", color=0xFFFF00)
        elif lang_server == "en":
            embed = discord.Embed(title="Changelog of the bot:", url="https://quentium.fr/en/discord/", color=0xFFFF00)
        elif lang_server == "de":
            embed = discord.Embed(title="Bot Update-Protokolle:", url="https://quentium.fr/de/discord/", color=0xFFFF00)
        counter = 1
        with open("extra/logs.txt", "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                line_time = line.split(" --- ", 999)[0]
                line_content = line.split(" --- ", 999)[1]
                embed.add_field(name="#" + str(counter) + " / " + line_time, value=line_content.replace("..", ".\n"), inline=True)
                counter += 1
        if lang_server == "fr":
            embed.set_footer(text="Les logs sont publiées dès qu'une nouvelle mise à jour importante du bot a lieu.", icon_url="https://quentium.fr/+img/logoBot.png")
        elif lang_server == "en":
            embed.set_footer(text="Logs are shared when the bot gets a new important update.", icon_url="https://quentium.fr/+img/logoBot.png")
        elif lang_server == "de":
            embed.set_footer(text="Die Protokolle werden veröffentlicht, sobald eine wichtig neue Update der Bots stattfindet.", icon_url="https://quentium.fr/+img/logoBot.png")
        return await ctx.send(embed=embed)

# TYPE Config cmds

#----------------------------- ADMIN_CONFIGS COMMANDS -----------------------------#

@client.command(pass_context=True, no_pm=True, aliases=["prefixe"])
async def prefix(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not(ctx.message.author.guild_permissions.administrator or any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112])):  # Quentium user IDs
            if lang_server == "fr":
                return await ctx.send(f":x: {ctx.message.author.name}, vous n'avez pas la permission **Administrateur** !")
            elif lang_server == "en":
                return await ctx.send(f":x: {ctx.message.author.name}, you don't have the permission **Administrator**!")
            elif lang_server == "de":
                return await ctx.send(f":x: {ctx.message.author.name}, Sie haben nicht die Berechtigung **Verwalter**!")
        if not args:
            if lang_server == "fr":
                return await ctx.send(f"Merci de préciser un argument valide : `{prefix_server}prefix [\"préfixe\" / reset]`.")
            elif lang_server == "en":
                return await ctx.send(f"Please specify a valid argument: `{prefix_server}prefix [\"prefix\" / reset]`.")
            elif lang_server == "de":
                return await ctx.send(f"Bitte geben Sie ein richtiges Argument an: `{prefix_server}prefix [\"Präfix\" / reset]`.")
        if any(x == args for x in ["delete", "reset", "remove"]):
            if not data.get(str(server_id))["prefix_server"] == "+":
                data[str(server_id)]["prefix_server"] = "+"
                with open("extra/data.json", "w", encoding="utf-8", errors="ignore") as file:
                    json.dump(data, file, indent=4)
                    client.command_prefix = get_prefix(client, ctx.message)
                if lang_server == "fr":
                    return await ctx.send("Le préfixe à été réinitialisé.")
                elif lang_server == "en":
                    return await ctx.send("The prefix has been reset.")
                elif lang_server == "de":
                    return await ctx.send("Das Präfix wurde zurückgesetzt.")
            else:
                if lang_server == "fr":
                    return await ctx.send("Le préfixe n'a pas pu être réinitialisé car il n'a pas été défini.")
                elif lang_server == "en":
                    return await ctx.send("The prefix could not be reset because it was not defined.")
                elif lang_server == "de":
                    return await ctx.send("Das Präfix konnte nicht zurückgesetzt werden, da es nicht definiert wurde.")
        data[str(server_id)]["prefix_server"] = args
        with open("extra/data.json", "w", encoding="utf-8", errors="ignore") as file:
            json.dump(data, file, indent=4)
            client.command_prefix = get_prefix(client, ctx.message)
        if lang_server == "fr":
            return await ctx.send(f"Le préfixe à été changé en `{args}`.")
        elif lang_server == "en":
            return await ctx.send(f"The prefix has been changed to `{args}`.")
        elif lang_server == "de":
            return await ctx.send(f"Das Präfix wurde in `{args}` geändert.")

@client.command(pass_context=True, no_pm=True, aliases=["langs", "language", "languages", "langage"])
async def lang(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not(ctx.message.author.guild_permissions.administrator or any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112])):  # Quentium user IDs
            if lang_server == "fr":
                return await ctx.send(f":x: {ctx.message.author.name}, vous n'avez pas la permission **Administrateur** !")
            elif lang_server == "en":
                return await ctx.send(f":x: {ctx.message.author.name}, you don't have the permission **Administrator**!")
            elif lang_server == "de":
                return await ctx.send(f":x: {ctx.message.author.name}, Sie haben nicht die Berechtigung **Verwalter**!")
        if not args:
            if lang_server == "fr":
                return await ctx.send("Merci de préciser la langue à changer. `(fr / en / de)`")
            elif lang_server == "en":
                return await ctx.send("Please specify the language to change. `(fr / en / de)`")
            elif lang_server == "de":
                return await ctx.send("Bitte geben Sie die gewünschte Sprache ein. `(fr / en / de)`")
        else:
            if any(args == x for x in ["fr", "en", "de"]):
                if any(x == str(server_id) for x in data.keys()):
                    lang_server = data[str(server_id)]["lang_server"]
                    if lang_server == args:
                        if lang_server == "fr":
                            await ctx.send("La langue du bot était déjà définie sur **Français**.")
                        elif lang_server == "en":
                            await ctx.send("Language of the bot is already set to **English**.")
                        elif lang_server == "de":
                            await ctx.send("Die Sprache des Bots ist bereits auf **Deutsch** eingestellt.")
                    else:
                        data[str(server_id)]["lang_server"] = args
                        with open("extra/data.json", "w", encoding="utf-8", errors="ignore") as file:
                            json.dump(data, file, indent=4)
                        if args == "fr":
                            return await ctx.send("La langue du bot a été changée en **Français**.")
                        elif args == "en":
                            return await ctx.send("Language of bot has been changed to **English**.")
                        elif args == "de":
                            return await ctx.send("Die Sprache des Bots wurde auf **Deutsch** geändert.")
            else:
                if lang_server == "fr":
                    return await ctx.send("Cette langue n'existe pas, merci de rentrer une language correcte : `(fr / en / de)`.")
                elif lang_server == "en":
                    return await ctx.send("This language doesn't exist, please enter a correct language : `(fr / en / de)`.")
                elif lang_server == "de":
                    return await ctx.send("Diese Sprache existiert nicht, bitte geben Sie eine korrekte Sprache ein : `(fr / en / de)`.")

@client.command(pass_context=True, no_pm=True, aliases=["autoroles"])
async def autorole(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not(ctx.message.author.guild_permissions.manage_roles or any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112])):  # Quentium user IDs
            if lang_server == "fr":
                return await ctx.send(f":x: {ctx.message.author.name}, vous n'avez pas la permission **Gérer les rôles** !")
            elif lang_server == "en":
                return await ctx.send(f":x: {ctx.message.author.name}, you don't have the permission **Manage roles**!")
            elif lang_server == "de":
                return await ctx.send(f":x: {ctx.message.author.name}, Sie haben nicht die Berechtigung **Rollen verwalten**!")
        if not ctx.message.channel.guild.me.guild_permissions.manage_roles:
            if lang_server == "fr":
                return await ctx.send(":x: Il manque la permissions **Gérer les rôles** au bot.")
            elif lang_server == "en":
                return await ctx.send(":x: The bot is missing **Manage roles** permissions.")
            elif lang_server == "de":
                return await ctx.send(":x: Dem Bot fehlen **Rollen verwalten** Berechtigungen.")
        if not args:
            if lang_server == "fr":
                return await ctx.send(f"Merci de préciser un argument. `{prefix_server}autorole <role>/show/remove`")
            elif lang_server == "en":
                return await ctx.send(f"Please specify an argument. `{prefix_server}autorole <role>/show/remove`")
            elif lang_server == "de":
                return await ctx.send(f"Bitte geben Sie eine argument. `{prefix_server}autorole <role>/show/remove`")
        else:
            rolename = args.split()[0].lower()
            if any(x == rolename for x in ["remove", "delete", "show", "see"]):
                role = rolename
            else:
                for role in ctx.message.guild.roles:
                    if "<@" in rolename:
                        role = discord.utils.get(ctx.message.guild.roles, id=int(rolename[3:-1]))
                        break
                    if rolename.isdigit() and len(rolename) >= 18:
                        role = discord.utils.get(ctx.message.guild.roles, id=int(rolename))
                        break
                    if rolename == role.name.lower():
                        role = discord.utils.get(ctx.message.guild.roles, name=role.name)
                        break
                else:
                    role = None
            if role == None:
                if lang_server == "fr":
                    await ctx.send("Merci d'entrer un rôle valide existant sur ce serveur !")
                elif lang_server == "en":
                    await ctx.send("Please enter a valid role existing on this server!")
                elif lang_server == "de":
                    await ctx.send("Bitte geben Sie eine gültige Rolle ein, die auf diesem Server existiert!")
            else:
                try:
                    if any(x == str(server_id) for x in data.keys()):
                        if role == "remove" or role == "delete":
                            data[str(server_id)]["autorole_server"] = None
                            if lang_server == "fr":
                                return await ctx.send("L'autorole à été correctement supprimé.")
                            elif lang_server == "en":
                                return await ctx.send("Autorole has been correctly deleted.")
                            elif lang_server == "de":
                                return await ctx.send("Die Autorole wurde korrekt gelöscht.")
                        elif role == "show" or role == "see":
                            role_file = data[str(server_id)]["autorole_server"]
                            if role_file == None:
                                if lang_server == "fr":
                                    return await ctx.send("L'autorole n'a pas été défini !")
                                elif lang_server == "en":
                                    return await ctx.send("Autorole is not defined!")
                                elif lang_server == "de":
                                    return await ctx.send("Die Autorole wurde nicht definiert!")
                            else:
                                role = discord.utils.get(ctx.message.guild.roles, id=int(role_file))
                                if role == None:
                                    if lang_server == "fr":
                                        return await ctx.send(f"Le rôle définis à été supprimé ou changé.")
                                    elif lang_server == "en":
                                        return await ctx.send(f"The role defined has been removed or changed.")
                                    elif lang_server == "de":
                                        return await ctx.send(f"Die definierte Rolle wurde entfernt oder geändert.")
                                else:
                                    if lang_server == "fr":
                                        return await ctx.send(f"L'autorole est défini sur `{role.name}`.")
                                    elif lang_server == "en":
                                        return await ctx.send(f"Autorole is set to `{role.name}`.")
                                    elif lang_server == "de":
                                        return await ctx.send(f"Die Autorole ist auf `{role.name}` gesetzt.")
                        # elif role == "multiple":
                        #     clean_line[4] = "272369384520024065/450728369848582167"
                        #     list_roles = []
                        #     for roles in clean_line[4].split("/"):
                        #         role = discord.utils.get(ctx.message.guild.roles, id=int(roles))
                        #         if not role == None:
                        #             list_roles.append(role.name)
                        #     await ctx.send("L'autorole à été définis sur `%s` avec succès." % ", ".join(list_roles))
                        else:
                            data[str(server_id)]["autorole_server"] = str(role.id)
                            if lang_server == "fr":
                                await ctx.send(f"L'autorole à été définis sur `{role.name}` avec succès.")
                            elif lang_server == "en":
                                await ctx.send(f"Successfully set autorole to role `{role.name}`.")
                            elif lang_server == "de":
                                await ctx.send(f"Die Autorolle wurde erfolgreich auf `{role.name}` gesetzt.")
                        with open("extra/data.json", "w", encoding="utf-8", errors="ignore") as file:
                            json.dump(data, file, indent=4)
                except:
                    if lang_server == "fr":
                        return await ctx.send("Un problème est survenu lors de la sauvegarde de l'autorole !")
                    elif lang_server == "en":
                        return await ctx.send("Something went wrong while saving autorole!")
                    elif lang_server == "de":
                        return await ctx.send("Beim Sichern des Autorollers ist ein Problem aufgetreten!")

@client.command(pass_context=True, no_pm=True, aliases=["triggers", "reaction", "customreaction", "customtrigger"])
async def trigger(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        global triggers
        if not(ctx.message.author.guild_permissions.administrator or any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112])):  # Quentium user IDs
            if not args:
                if lang_server == "fr":
                    return await ctx.send(f":x: {ctx.message.author.name}, vous n'avez pas la permission **Administrateur** !")
                elif lang_server == "en":
                    return await ctx.send(f":x: {ctx.message.author.name}, you don't have the permission **Administrator**!")
                elif lang_server == "de":
                    return await ctx.send(f":x: {ctx.message.author.name}, Sie haben nicht die Berechtigung **Verwalter**!")
            else:
                if any(x == args.lower() for x in ["list", "liste"]):
                    if any(x == str(server_id) for x in triggers.keys()) and triggers[str(server_id)]:
                        content = "\n- ".join([x for x in triggers[str(server_id)].keys()])
                        if lang_server == "fr":
                            embed = discord.Embed(title=f"Réactions customisées ({len(triggers[str(server_id)].keys())}) :", description="- " + content, color=0xBFFF00)
                        elif lang_server == "en":
                            embed = discord.Embed(title=f"Customized reactions ({len(triggers[str(server_id)].keys())}) :", description="- " + content, color=0xBFFF00)
                        elif lang_server == "de":
                            embed = discord.Embed(title=f"Kundenspezifische Reaktionen ({len(triggers[str(server_id)].keys())}) :", description="- " + content, color=0xBFFF00)
                    else:
                        if lang_server == "fr":
                            embed = discord.Embed(title="Il n'y a aucunes réactions customisées.", color=0xBFFF00)
                        elif lang_server == "en":
                            embed = discord.Embed(title="There are no custom reactions.", color=0xBFFF00)
                        elif lang_server == "de":
                            embed = discord.Embed(title="Es gibt keine benutzerdefinierten Reaktionen.", color=0xBFFF00)
                    return await ctx.send(embed=embed)
                else:
                    if lang_server == "fr":
                        return await ctx.send(f":x: {ctx.message.author.name}, vous n'avez pas la permission **Administrateur** !")
                    elif lang_server == "en":
                        return await ctx.send(f":x: {ctx.message.author.name}, you don't have the permission **Administrator**!")
                    elif lang_server == "de":
                        return await ctx.send(f":x: {ctx.message.author.name}, Sie haben nicht die Berechtigung **Verwalter**!")

        if not args:
            if lang_server == "fr":
                embed = discord.Embed(title=f"Veuillez préciser un déclencheur et une réponse : `{prefix_server}trigger [\"déclancheur\" / liste / remove] [\"réponse\" / url]`", color=0xBFFF00)
            elif lang_server == "en":
                embed = discord.Embed(title=f"Please specify a trigger and an answer: `{prefix_server}trigger [\"trigger\" / list / remove] [\"answer\" / url]`", color=0xBFFF00)
            elif lang_server == "de":
                embed = discord.Embed(title=f"Bitte geben Sie eine Nachricht und eine Antwort an: `{prefix_server}trigger [\"Nachricht\" / list / remove] [\"Antwort\" / url]`", color=0xBFFF00)
            return await ctx.send(embed=embed)

        with open("extra/triggers.json", "r", encoding="utf-8", errors="ignore") as file:
            triggers = json.loads(file.read(), strict=False)

        if any(x in args.split()[0].lower() for x in ["list", "liste", "remove", "delete"]):
            if any(x == args.split()[0].lower() for x in ["list", "liste"]):
                if any(x == str(server_id) for x in triggers.keys()) and triggers[str(server_id)]:
                    content = "\n- ".join([x for x in triggers[str(server_id)].keys()])
                    if lang_server == "fr":
                        embed = discord.Embed(title=f"Réactions customisées ({len(triggers[str(server_id)].keys())}) :", description="- " + content, color=0xBFFF00)
                    elif lang_server == "en":
                        embed = discord.Embed(title=f"Customized reactions ({len(triggers[str(server_id)].keys())}) :", description="- " + content, color=0xBFFF00)
                    elif lang_server == "de":
                        embed = discord.Embed(title=f"Kundenspezifische Reaktionen ({len(triggers[str(server_id)].keys())}) :", description="- " + content, color=0xBFFF00)
                    return await ctx.send(embed=embed)
                else:
                    if lang_server == "fr":
                        embed = discord.Embed(title="Il n'y a aucunes réactions customisées.", color=0xBFFF00)
                    elif lang_server == "en":
                        embed = discord.Embed(title="There are no custom reactions.", color=0xBFFF00)
                    elif lang_server == "de":
                        embed = discord.Embed(title="Es gibt keine benutzerdefinierten Reaktionen.", color=0xBFFF00)
                    return await ctx.send(embed=embed)
            elif any(x == args.split()[0].lower() for x in ["remove", "delete", "clear"]):
                if len(args.split()) == 1:
                    if lang_server == "fr":
                        embed = discord.Embed(title=f"Veuillez préciser un déclencheur à supprimer : `{prefix_server}trigger [remove / delete] [\"déclancheur\"]`", color=0xBFFF00)
                    elif lang_server == "en":
                        embed = discord.Embed(title=f"Please specify a trigger to delete: `{prefix_server}trigger [remove / delete] [\"trigger\"]`", color=0xBFFF00)
                    elif lang_server == "de":
                        embed = discord.Embed(title=f"Bitte geben Sie einen Reaktion zum Löschen an: `{prefix_server}trigger [remove / delete] [\"déclancheur\"]`", color=0xBFFF00)
                    return await ctx.send(embed=embed)
                if '"' in args or "'" in args:
                    remove = re.findall(r'["\'](.*?)["\']', args)[-1].lower()
                else:
                    remove = args.split()[-1].lower()
                if any(x.lower() == remove for x in triggers[str(server_id)].keys()):
                    del triggers[str(server_id)][remove]
                    with open("extra/triggers.json", "w", encoding="utf-8", errors="ignore") as file:
                        json.dump(triggers, file, indent=4)
                    if lang_server == "fr":
                        embed = discord.Embed(title="Réaction supprimée :", description=f"**{remove}**", color=0xBFFF00)
                    elif lang_server == "en":
                        embed = discord.Embed(title="Reaction deleted:", description=f"**{remove}**", color=0xBFFF00)
                    elif lang_server == "de":
                        embed = discord.Embed(title="Reaktion gelöscht:", description=f"**{remove}**", color=0xBFFF00)
                else:
                    if lang_server == "fr":
                        embed = discord.Embed(title="Aucune réaction ne correspond à celle choisie.", color=0xBFFF00)
                    elif lang_server == "en":
                        embed = discord.Embed(title="No reaction corresponds to that chosen.", color=0xBFFF00)
                    elif lang_server == "de":
                        embed = discord.Embed(title="Keine Reaktion entspricht der gewählten.", color=0xBFFF00)
                return await ctx.send(embed=embed)
            elif any(x == args.split()[0].lower() for x in ["removeall", "deleteall", "clearall"]):
                del triggers[str(server_id)]
                with open("extra/triggers.json", "w", encoding="utf-8", errors="ignore") as file:
                    json.dump(triggers, file, indent=4)
                if lang_server == "fr":
                    embed = discord.Embed(title="Toutes les réactions ont été supprimées.", color=0xBFFF00)
                elif lang_server == "en":
                    embed = discord.Embed(title="All reactions have been removed.", color=0xBFFF00)
                elif lang_server == "de":
                    embed = discord.Embed(title="Alle Reaktionen wurden entfernt.", color=0xBFFF00)
                return await ctx.send(embed=embed)
        if not '"' in args and not "'" in args:
            if len(args.split()) == 2:
                trigger = args.split()[0]
                response = args.split()[1]
            elif len(args.split()) < 2:
                if lang_server == "fr":
                    embed = discord.Embed(title="Il n'y a pas assez d'arguments pour créer la réaction, ajoutez-en entre des guillements pour délimiter votre message.", color=0xBFFF00)
                elif lang_server == "en":
                    embed = discord.Embed(title="There are not enough arguments to create the reaction, add some quotes to delimit your message.", color=0xBFFF00)
                elif lang_server == "de":
                    embed = discord.Embed(title="Es gibt nicht genügend Argumente, um die Reaktion auszulösen. Fügen Sie einige Anführungszeichen hinzu, um Ihre Nachricht einzugrenzen.", color=0xBFFF00)
                return await ctx.send(embed=embed)
            else:
                if lang_server == "fr":
                    embed = discord.Embed(title="Il y a trop d'arguments pour créer la réaction, mettez des guillements pour délimiter votre message.", color=0xBFFF00)
                elif lang_server == "en":
                    embed = discord.Embed(title="There are too many arguments to create the reaction, add some quotes to delimit your message.", color=0xBFFF00)
                elif lang_server == "de":
                    embed = discord.Embed(title="Es gibt zu viele Argumente, um die Reaktion auszulösen. Setzen Sie Anführungszeichen, um Ihre Nachricht einzugrenzen.", color=0xBFFF00)
                return await ctx.send(embed=embed)
        else:
            if len(re.findall(r'["\'](.*?)["\']', args)) == 2:
                trigger = re.findall(r'["\'](.*?)["\']', args)[0]
                if "http://" in args or "https://" in args:
                    response = args.split()[-1].replace('"', "").replace("'", "")
                else:
                    response = re.findall(r'["\'](.*?)["\']', args)[1]
            elif len(re.findall(r'["\'](.*?)["\']', args)) < 2:
                if lang_server == "fr":
                    embed = discord.Embed(title="Il n'y a pas assez d'arguments pour créer la réaction, ajoutez-en entre des guillements pour délimiter votre message.", color=0xBFFF00)
                elif lang_server == "en":
                    embed = discord.Embed(title="There are not enough arguments to create the reaction, add some quotes to delimit your message.", color=0xBFFF00)
                elif lang_server == "de":
                    embed = discord.Embed(title="Es gibt nicht genügend Argumente, um die Reaktion auszulösen. Fügen Sie einige in Anführungszeichen ein, um Ihre Nachricht einzugrenzen.", color=0xBFFF00)
                return await ctx.send(embed=embed)
            else:
                if lang_server == "fr":
                    embed = discord.Embed(title="Il y a trop d'arguments pour créer la réaction, mettez des guillements pour délimiter votre message.", color=0xBFFF00)
                elif lang_server == "en":
                    embed = discord.Embed(title="There are too many arguments to create the reaction, add some quotes to delimit your message.", color=0xBFFF00)
                elif lang_server == "de":
                    embed = discord.Embed(title="Es gibt zu viele Argumente, um die Reaktion auszulösen. Setzen Sie Anführungszeichen, um Ihre Nachricht einzugrenzen.", color=0xBFFF00)
                return await ctx.send(embed=embed)
        if not any(x == str(server_id) for x in triggers.keys()):
            triggers[str(server_id)] = {trigger.lower(): response}
        else:
            if trigger.lower() in triggers[str(server_id)].keys():
                if lang_server == "fr":
                    embed = discord.Embed(title="Il y a déjà un déclencheur pour ce message. Supprimer le puis refaites la commande.", color=0xBFFF00)
                elif lang_server == "en":
                    embed = discord.Embed(title="There is already a trigger for this message. Delete it and redo the command.", color=0xBFFF00)
                elif lang_server == "de":
                    embed = discord.Embed(title="Es gibt bereits einen Auslöser für diese Nachricht. Löschen Sie es und wiederholen Sie den Befehl.", color=0xBFFF00)
                return await ctx.send(embed=embed)
        triggers[str(server_id)][trigger.lower()] = response
        with open("extra/triggers.json", "w", encoding="utf-8", errors="ignore") as file:
            json.dump(triggers, file, indent=4)
        if lang_server == "fr":
            embed = discord.Embed(title="Nouvelle réaction customisée :", color=0xBFFF00)
            embed.add_field(name="Déclencheur", value=trigger, inline=True)
            embed.add_field(name="Réponse", value=response, inline=True)
        elif lang_server == "en":
            embed = discord.Embed(title="New customized reaction:", color=0xBFFF00)
            embed.add_field(name="Trigger", value=trigger, inline=True)
            embed.add_field(name="Reply", value=response, inline=True)
        elif lang_server == "de":
            embed = discord.Embed(title="Neue angepasste Reaktion:", color=0xBFFF00)
            embed.add_field(name="Auslöser", value=trigger, inline=True)
            embed.add_field(name="Antwort", value=response, inline=True)
        return await ctx.send(embed=embed)

# TYPE Rights cmds

#----------------------------- ADMIN_RIGHTS COMMANDS -----------------------------#

@client.command(pass_context=True, no_pm=True, aliases=["clearmsg", "clean"])
async def clear(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not ctx.message.author.permissions_in(ctx.message.channel).manage_messages:
            if lang_server == "fr":
                return await ctx.send(f":x: {ctx.message.author.name}, vous n'avez pas la permission **Gérer les messages** !")
            elif lang_server == "en":
                return await ctx.send(f":x: {ctx.message.author.name}, you don't have the permission **Manage messages**!")
            elif lang_server == "de":
                return await ctx.send(f":x: {ctx.message.author.name}, Sie haben nicht die Berechtigung **Nachrichten verwalten**!")
        if not ctx.message.channel.guild.me.guild_permissions.manage_messages:
            if lang_server == "fr":
                return await ctx.send(":x: Il manque la permissions **Gérer les messages** au bot.")
            elif lang_server == "en":
                return await ctx.send(":x: The bot is missing **Manage messages** permissions.")
            elif lang_server == "de":
                return await ctx.send(":x: Dem Bot fehlen **Nachrichten verwalten** Berechtigungen.")
        if not args:
            if lang_server == "fr":
                return await ctx.send("Merci de préciser un nombre.")
            elif lang_server == "en":
                return await ctx.send("Please specify a number.")
            elif lang_server == "de":
                return await ctx.send("Bitte geben Sie eine Nummer an.")
        else:
            if args.split()[0].isdecimal():
                number = int(args.split()[0])
                if number < 99 and number > 0:
                    limit = number + 1
                    await ctx.message.channel.purge(limit=limit)
                else:
                    if lang_server == "fr":
                        return await ctx.send("Le nombre doit être compris entre 1 et 99 pour limiter les erreurs.")
                    elif lang_server == "en":
                        return await ctx.send("The number must be between 1 and 99 to prevent errors.")
                    elif lang_server == "de":
                        return await ctx.send("Die Nummer muss zwischen 1 und 99 liegen um Fehler zu begrenzen.")
            else:
                if lang_server == "fr":
                    return await ctx.send("Nombre inconnu, merci de rentrer un nombre correct.")
                elif lang_server == "en":
                    return await ctx.send("Unknown number, please enter a valid number.")
                elif lang_server == "de":
                    return await ctx.send("Unbekannte Nummer, bitte geben Sie eine korrekte Nummer ein.")

@client.command(pass_context=True, no_pm=True, aliases=["moves"])
async def move(ctx, *, number=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not ctx.message.author.guild_permissions.move_members:
            if lang_server == "fr":
                return await ctx.send(f":x: {ctx.message.author.name}, vous n'avez pas la permission **Déplacer des membres** !")
            elif lang_server == "en":
                return await ctx.send(f":x: {ctx.message.author.name}, you don't have the permission **Move members**!")
            elif lang_server == "de":
                return await ctx.send(f":x: {ctx.message.author.name}, Sie haben nicht die Berechtigung **Mitglieder verschieben**!")
        channel_list = [x for x in ctx.message.guild.channels if isinstance(x, discord.VoiceChannel)]
        if not number:
            if lang_server == "fr":
                content = "Merci de préciser un salon vocal par son numéro.\n\n"
            elif lang_server == "en":
                content = "Please specify a vocal room by its number.\n\n"
            elif lang_server == "de":
                content = "Bitte geben Sie einen Sprachkanäle anhand seiner Nummer an.\n\n"
            numero = 0
            for channel in channel_list:
                numero += 1
                content += "{}. {}\n".format(numero, channel)
            if lang_server == "fr":
                embed = discord.Embed(title="Salons vocaux :", description=content, color=0x3498DB)
            elif lang_server == "en":
                embed = discord.Embed(title="Voice channels:", description=content, color=0x3498DB)
            elif lang_server == "de":
                embed = discord.Embed(title="Sprachkanäle:", description=content, color=0x3498DB)
            return await ctx.send(embed=embed)
        else:
            if "random" in number:
                if number == "random":
                    nb_times = 5
                else:
                    nb_times = int(number.split("random ")[1])
                nb_times = nb_times if nb_times < 20 else 20
                random_numbers = []
                list_members = []
                temp = 0
                while len(random_numbers) < nb_times:
                    random_numbers.append(random.randint(1, len(channel_list)))
                    if random_numbers[-1] == 2 or temp == random_numbers[-1]:
                        random_numbers = random_numbers[:-1]
                    if len(random_numbers) >= 1:
                        temp = random_numbers[-1]
                for member in ctx.message.author.voice.channel.members:
                    list_members.append(member)
                for channel_number in random_numbers:
                    for member in list_members:
                        await member.edit(voice_channel=channel_list[channel_number - 1])
                        await asyncio.sleep(0.15)
                return await ctx.message.delete()
            elif number.isdigit():
                if not len(channel_list) == 0:
                    if not int(number) > len(channel_list):
                        channel = channel_list[int(number[0]) - 1]
                        if not ctx.message.author.voice == None:
                            if channel.id != ctx.message.author.voice.channel.id:
                                if lang_server == "fr":
                                    await ctx.send("Déplacement dans : " + str(channel))
                                elif lang_server == "en":
                                    await ctx.send("Moving in: " + str(channel))
                                elif lang_server == "de":
                                    await ctx.send("Umzug in: " + str(channel))
                                list_members = []
                                for member in ctx.message.author.voice.channel.members:
                                    list_members.append(member)
                                for member in list_members:
                                    await member.edit(voice_channel=channel)
                            else:
                                if lang_server == "fr":
                                    return await ctx.send("Vous êtes déjà dans le même salon vocal.")
                                elif lang_server == "en":
                                    return await ctx.send("You are already in the same voice channel.")
                                elif lang_server == "de":
                                    return await ctx.send("Sie befinden sich bereits im selben Sprachkanäle.")
                        else:
                            if lang_server == "fr":
                                return await ctx.send("Vous n'êtes pas dans un salon vocal.")
                            elif lang_server == "en":
                                return await ctx.send("You are not in a voice channel.")
                            elif lang_server == "de":
                                return await ctx.send("Sie befinden sich nicht in einer Sprachkanäle.")
                    else:
                        if lang_server == "fr":
                            return await ctx.send("Le numéro de salon ne correspond à aucuns salons vocaux.")
                        elif lang_server == "en":
                            return await ctx.send("The salon number does not correspond to any voice channel.")
                        elif lang_server == "de":
                            return await ctx.send("Die Salonnummer entspricht keinem Sprachkanäle.")
                else:
                    if lang_server == "fr":
                        return await ctx.send("Il n'y a aucuns salons vocaux sur votre serveur.")
                    elif lang_server == "en":
                        return await ctx.send("There are no voice channel on your server.")
                    elif lang_server == "de":
                        return await ctx.send("Auf Ihrem Server sind keine Sprachkanäle vorhanden.")
            else:
                if lang_server == "fr":
                    content = "Merci de préciser un salon vocal par son numéro.\n\n"
                elif lang_server == "en":
                    content = "Please specify a vocal room by its number.\n\n"
                elif lang_server == "de":
                    content = "Bitte geben Sie einen Gesangsraum anhand seiner Nummer an.\n\n"
                numero = 0
                for channel in channel_list:
                    numero += 1
                    content += "{}. {}\n".format(numero, channel)
                if lang_server == "fr":
                    embed = discord.Embed(title="Salons vocaux :", description=content, color=0x3498DB)
                elif lang_server == "en":
                    embed = discord.Embed(title="Voice channels:", description=content, color=0x3498DB)
                elif lang_server == "de":
                    embed = discord.Embed(title="Sprachkanäle:", description=content, color=0x3498DB)
                return await ctx.send(embed=embed)

@client.command(pass_context=True, no_pm=True)
async def kick(ctx, *, member: discord.Member = None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not ctx.message.author.guild_permissions.kick_members:
            if lang_server == "fr":
                return await ctx.send(f":x: {ctx.message.author.name}, vous n'avez pas la permission **Expulser des membres** !")
            elif lang_server == "en":
                return await ctx.send(f":x: {ctx.message.author.name}, you don't have the permission **Kick members**!")
            elif lang_server == "de":
                return await ctx.send(f":x: {ctx.message.author.name}, Sie haben nicht die Berechtigung **Kick-Mitglieder**!")
        if not ctx.message.channel.guild.me.guild_permissions.kick_members:
            if lang_server == "fr":
                return await ctx.send(":x: Il manque la permissions **Expulser des membres** au bot.")
            elif lang_server == "en":
                return await ctx.send(":x: The bot is missing **Kick members** permissions.")
            elif lang_server == "de":
                return await ctx.send(":x: Dem Bot fehlen **Kick-Mitglieder** Berechtigungen.")
        if not member:
            if lang_server == "fr":
                return await ctx.send(f":x: {ctx.message.author.name}, mentionnez la personne à expulser !")
            elif lang_server == "en":
                return await ctx.send(f":x: {ctx.message.author.name}, mention the member to kick!")
            elif lang_server == "de":
                return await ctx.send(f":x: {ctx.message.author.name}, erwähnen Sie das ausgestoßende Mitglied!")
        await member.kick()
        if lang_server == "fr":
            embed = discord.Embed(description=f"**{member.name}** a été kick !", color=0xFF0000)
        elif lang_server == "en":
            embed = discord.Embed(description=f"**{member.name}** has been kicked!", color=0xFF0000)
        elif lang_server == "de":
            embed = discord.Embed(description=f"**{member.name}** wurde rausgeschmissen!", color=0xFF0000)
        return await ctx.send(embed=embed)

@client.command(pass_context=True, no_pm=True)
async def ban(ctx, *, member: discord.Member = None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not ctx.message.author.guild_permissions.ban_members:
            if lang_server == "fr":
                return await ctx.send(f":x: {ctx.message.author.name}, vous n'avez pas la permission **Bannir des membres** !")
            elif lang_server == "en":
                return await ctx.send(f":x: {ctx.message.author.name}, you don't have the permission **Ban members**!")
            elif lang_server == "de":
                return await ctx.send(f":x: {ctx.message.author.name}, Sie haben nicht die Berechtigung **Verbot von Mitgliedern**!")
        if not ctx.message.channel.guild.me.guild_permissions.ban_members:
            if lang_server == "fr":
                return await ctx.send(":x: Il manque la permissions **Bannir des membres** au bot.")
            elif lang_server == "en":
                return await ctx.send(":x: The bot is missing **Ban members** permissions.")
            elif lang_server == "de":
                return await ctx.send(":x: Dem Bot fehlen **Verbot von Mitgliedern** Berechtigungen.")
        if not member:
            if lang_server == "fr":
                return await ctx.send(f":x: {ctx.message.author.name}, mentionnez la personne à bannir !")
            elif lang_server == "en":
                return await ctx.send(f":x: {ctx.message.author.name}, mention the member to ban!")
            elif lang_server == "de":
                return await ctx.send(f":x: {ctx.message.author.name}, erwähnen Sie das zu verbannende Mitglied!")
        await member.ban()
        if lang_server == "fr":
            embed = discord.Embed(description=f"**{member.name}** a été bannis !", color=0xFF0000)
        elif lang_server == "en":
            embed = discord.Embed(description=f"**{member.name}** has been banned!", color=0xFF0000)
        elif lang_server == "de":
            embed = discord.Embed(description=f"**{member.name}** wurde verboten!", color=0xFF0000)
        return await ctx.send(embed=embed)

# TYPE FLC cmds

#----------------------------- FRANCE LES CITES COMMANDS -----------------------------#

@client.command(pass_context=True, aliases=["minedt"])
async def dtmine(ctx, *args):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not args:
            if lang_server == "fr":
                return await ctx.send(f"Merci de préciser au moins un minerais : `{prefix_server}dtmine [\"minerais\"] [\"secteur_max\"]`.")
            elif lang_server == "en":
                return await ctx.send(f"Please specify at least one ore: `{prefix_server}dtmine [\"ore\"] [\"max_sector\"]`.")
            elif lang_server == "de":
                return await ctx.send(f"Bitte geben Sie mindestens ein Erz an: `{prefix_server}dtmine [\"Erz\"] [\"max_sektor\"]`.")
        minerais = args[0].lower()
        if len(args) == 2 and args[1].isdigit():
            max_deep = args[1]
        else:
            max_deep = "120"

        try:
            minerais = aliases_dt[minerais]
        except:
            pass
        ores = mines["0"].keys()
        for area, _ in mines.items():
            for ore in ores:
                if mines[area].get(ore) is None:
                    mines[area].update({ore: 0})

        def best_mines(ore):
            ordered_mines = [(k, v) for k, v in mines.items()]
            ordered_mines.sort(key=lambda x: x[1][ore], reverse=True)
            return ordered_mines
        if minerais not in mines["0"].keys():
            if lang_server == "fr":
                return await ctx.send(f"Le minerais {minerais} n'existe pas :frowning:")
            elif lang_server == "en":
                return await ctx.send(f"The ore {minerais} does not exist :frowning:")
            elif lang_server == "de":
                return await ctx.send(f"Die Erze {minerais} existieren nicht :frowning:")
        if max_deep == "120":
            if lang_server == "fr":
                text = f"Voici les 10 meilleurs emplacements pour le minerais {minerais} :```"
            elif lang_server == "en":
                text = f"Here are the 10 best locations for {minerais} ores :```"
            elif lang_server == "de":
                text = f"Hier sind die 10 besten Standorte für {minerais} Erz :```"
        else:
            if lang_server == "fr":
                text = f"Voici les 10 meilleurs emplacements pour le minerais {minerais} jusqu'au secteur {max_deep} :```"
            elif lang_server == "en":
                text = f"Here are the 10 best locations for {minerais} ores up to sector {max_deep}:```"
            elif lang_server == "de":
                text = f"Hier sind die 10 besten Standorte für {minerais} Erz zu Sektor {max_deep}:```"
        i = 0
        for mine in best_mines(minerais):
            if i >= 10:
                break
            if mine[0] == "0":
                continue
            if mine[1][minerais] == 0:
                continue
            if int(mine[0]) <= int(max_deep):
                if mine[1][minerais] < 0.01 and minerais != "platinum":
                    break
                text += mine[0].center(3, " ")
                text += " : " + str(round(mine[1][minerais] * 100, 2)) + "%\n"
            else:
                continue
            i += 1
        text += "```"
        return await ctx.send(text)

@client.command(pass_context=True, no_pm=True, aliases=["abs"])
async def absent(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if server_id == 371687157817016331:  # France Les Cités server ID
            if ctx.message.channel.id == 552484372251410437:  # France Les Cités channel ID
                if not ctx.message.channel.guild.me.guild_permissions.manage_roles:
                    return await ctx.send(":x: Il manque la permissions **Gérer les rôles** au bot.")
                role = discord.utils.get(ctx.message.guild.roles, name="Absent")
                member_name = ctx.message.author.nick if ctx.message.author.nick is not None else str(ctx.message.author.name)
                if not role in ctx.message.author.roles:
                    if args is None:
                        await ctx.message.delete()
                        return await ctx.message.author.send("Pour vous mettre le statut d'absent, il faut que vous spécifiez une raison et une durée d'absence ! (ex : `-absent Vacances 7 jours`)")
                    await ctx.message.author.add_roles(role)
                    await ctx.send(f"**{member_name}** est désormais absent pour la raison : ***{args}***")
                    await ctx.message.author.send("Vous avez bien rejoint le statut d'absent !")
                    return await ctx.message.delete()
                else:
                    await ctx.message.author.remove_roles(role)
                    await ctx.message.author.send("Vous avez bien quitté le statut d'absent !")
                    await ctx.send(f"**{member_name}** est de retour parmi nous !")
                    return await ctx.message.delete()

@client.command(pass_context=True, no_pm=True, aliases=["votes", "voter", "votemax", "voteresults"])
async def vote(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if server_id == 371687157817016331:  # France Les Cités server ID
            if not os.path.isfile("extra/votes_flc.txt"):
                f = open("extra/votes_flc.txt", "w")
                f.write("0")
                f.close()
            with open("extra/votes_flc.txt", "r", encoding="utf-8", errors="ignore") as file:
                content = file.readlines()

            # Cityzoo / Scant / Quentium user ID
            authorised = [348509601936834561, 358214022115360771, 246943045105221633]
            if any(x == ctx.message.author.id for x in authorised):
                if "votemax" in ctx.message.content:
                    content[0] = f"{args}\n"
                    with open("extra/votes_flc.txt", "w", encoding="utf-8", errors="ignore") as file:
                        file.write("".join(content))
                    await ctx.message.delete()
                    return await ctx.message.author.send(f"Le nombre de votes max à été mis à **{args}**")
                elif "voteresults" in ctx.message.content:
                    embed = discord.Embed(title="Résultats :", color=0x00FF00)
                    final = []
                    with open("extra/votes_flc.txt", "r", encoding="utf-8") as file:
                        results = file.readlines()[1:]
                    for x in results:
                        a = x.strip().split(" --> ")[1]
                        final.append(a)
                    d = {}
                    [d.update({i: d.get(i, 0) + 1}) for i in final]
                    e = sorted(d.items(), key=lambda x: x[1], reverse=True)
                    for y in range(len(e)):
                        embed.add_field(name=f"Place {y + 1} :", value=f"n°{e[y][0]} avec {e[y][1]} votes.", inline=True)
                    return await ctx.send(embed=embed)

            if not args:
                await ctx.message.delete()
                return await ctx.message.author.send("Merci de bien vouloir préciser un vote par son numéro.")
            if not args.isdigit():
                await ctx.message.delete()
                return await ctx.message.author.send("Cet argument ne correspond pas au numéros de la liste des votes.")
            else:
                if int(args) > int(content[0]):
                    await ctx.message.delete()
                    return await ctx.message.author.send("Ce nombre dépasse le nombre de votes dans la liste.")
            with open("extra/votes_flc.txt", "r", encoding="utf-8", errors="ignore") as file:
                for line in file:
                    if str(ctx.message.author.id) in line:
                        await ctx.message.delete()
                        return await ctx.message.author.send("Vous avez déjà voté, il est impossible de changer son vote.")
            with open("extra/votes_flc.txt", "a", encoding="utf-8", errors="ignore") as file:
                file.write(f"{ctx.message.author.id} --> {args}\n")
                await ctx.message.delete()
                return await ctx.message.author.send(f"Vous avez bien voté pour le participant **{args}**.")

# TYPE ISM cmds

#----------------------------- INSOUMIS COMMANDS -----------------------------#

@client.command(pass_context=True, no_pm=True, aliases=["roles", "rol"])
async def role(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if server_id == 391272643229384705:  # Insoumis server ID
            list_roles = ["Payday 2", "Diablo 3", "Gta 5", "The division", "Fortnite", "CS GO", "Farming simulator",
                          "Lol", "Dead by daylight", "Destiny 2", "Quake", "left 4 dead 2", "GRID 2", "Steep", "HL2DM",
                          "Sea of Thieves", "Monster Hunter"]

        elif server_id == 350156033198653441:  # TFI server ID
            list_roles = ["Chauffeur en Test", "Ami"]

        elif server_id == 509028174013923339:  # Solumon server ID
            list_roles = ["Payday 2", "Joueur", "Gmod"]

        elif server_id == 319533759894388736:  # Exos_Team server ID
            if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
                if not args:
                    return await ctx.message.delete()
                role = discord.utils.get(ctx.message.guild.roles, name=args)
                if role in ctx.message.author.roles:
                    return await ctx.message.author.remove_roles(role)
                else:
                    return await ctx.message.author.add_roles(role)

        if not args:
            return await ctx.send("Merci de préciser un rôle à vous attribuer : `{}`".format(", ".join(list_roles)))
        if "list" in args.lower():
            return await ctx.send("Voiçi la liste des rôles : `{}`".format(", ".join(list_roles)))
        lower_match = difflib.get_close_matches(args.lower(), [x.lower() for x in list_roles], n=1, cutoff=0)
        rolename = [x for x in list_roles if x.lower() == lower_match[0]]
        role = discord.utils.get(ctx.message.guild.roles, name=rolename[0])
        if not role:
            return await ctx.send("Ce rôle n'existe pas :frowning:")
        if any(x in role.name for x in list_roles):
            if role in ctx.message.author.roles:
                await ctx.message.author.remove_roles(role)
                result = f"Le rôle {role.name} à bien été enlevé."
            else:
                await ctx.message.author.add_roles(role)
                result = f"Le rôle {role.name} à bien été mis."
            return await ctx.send(result)
        else:
            return await ctx.send("Vous n'avez pas le droit de vous attribuer ce rôle.")

# TYPE TheSwe cmds

#----------------------------- THESWEMASTER COMMANDS -----------------------------#

@client.command(pass_context=True, aliases=["cookies"])
async def cookie(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if server_id == 199189022894063627:  # TheSweMaster server ID
            not_cookie = ["MrCookie"]
            cookies = [x for x in client.emojis if "cookie" in str(x.name).lower() and not any(y == str(x.name) for y in not_cookie)]
            msg_cookies = "".join([str(x) for x in cookies])
            return await ctx.send("Here are your cookies ***" + str(ctx.message.author.name) + "*** :cookie:" + msg_cookies)

# TYPE Quentium cmds

#----------------------------- QUENTIUM COMMANDS -----------------------------#

@client.command(pass_context=True)
async def showideas(ctx):
    if isinstance(ctx.channel, discord.TextChannel):
        global server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)

    if not ctx.message.author.bot == True:
        if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
            if os.path.isfile("feedback.txt") == False:
                tmp = await ctx.send("Le fichier est vide :weary:")
                await asyncio.sleep(5)
                await ctx.message.delete()
                return await tmp.delete()
            content = ""
            if not os.path.isfile("feedback.txt"):
                content += "Aucunes"
            else:
                with open("feedback.txt", "r", encoding="utf-8", errors="ignore") as file:
                    for line in file:
                        content += line
            embed = discord.Embed(title="Idées :", description=content)
            tmp = await ctx.send(embed=embed)
            await asyncio.sleep(5)
            await ctx.message.delete()
            return await tmp.delete()

@client.command(pass_context=True)
async def addlogs(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)

    if not ctx.message.author.bot == True:
        if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
            if not args:
                return await ctx.message.delete()
            else:
                logs = " --- ".join([str(datetime.now().strftime("%d.%m.%Y - %H:%M")), args])
                with open("extra/logs.txt", "a", encoding="utf-8", errors="ignore") as file:
                    file.write(logs + "\n")
                await asyncio.sleep(5)
                return await ctx.message.delete()

@client.command(name="eval", pass_context=True, aliases=["evaluate"])
async def _eval(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)

    if not ctx.message.author.bot == True:
        if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
            if not args:
                return await ctx.message.delete()
            try:
                res = eval(args)
                if inspect.isawaitable(res):
                    await res
                else:
                    await ctx.send(res)
            except Exception as e:
                return await ctx.send(f"```python\n{type(e).__name__}: {e}```")

@client.command(name="exec", pass_context=True, aliases=["execute"])
async def _exec(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if any(x == ctx.message.author.id for x in [246943045105221633, 324570532324442112]):  # Quentium user IDs
            if args:
                return ctx.message.delete()
            await async_command(args, ctx.message)

@client.command(pass_context=True)
async def data4tte(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        authorised = [246943045105221633, 224928390694567936, 272412092248752137]
        # Quentium / vectokse / Jaguar AF user ID
        if any(x == ctx.message.author.id for x in authorised):
            if not args:
                args = "130"
            else:
                if not args.isdecimal():
                    args = "130"

            temp = await ctx.send("Sending requests, it may take long")
            await async_command("python3 extra/data4tte.py " + args, ctx.message)
            await asyncio.sleep(5)
            await ctx.message.delete()
            return await temp.delete()
        else:
            return await ctx.message.delete()

# TYPE Temp cmds

#----------------------------- TEMP COMMANDS -----------------------------#

@client.command(pass_context=True)
async def getbotstats(ctx):
    await get_bot_stats()

@client.command(pass_context=True, aliases=["mc", "omg", "omgserv"])
@commands.cooldown(2, 10, commands.BucketType.channel)
async def minecraft(ctx, *, args=None):
    if isinstance(ctx.channel, discord.TextChannel):
        global lang_server, commands_server, autorole_server, prefix_server, server_id, server_name
        server_id = ctx.message.guild.id
        server_name = ctx.message.guild.name
        await async_data(str(server_id), server_name, ctx.message)
    else:
        lang_server = "fr"

    if not ctx.message.author.bot == True:
        if not args:
            if lang_server == "fr":
                return await ctx.send("Veuillez renseigner l'id de vôtre serveur OMGServ.")
            elif lang_server == "en":
                return await ctx.send("Please enter the id of your OMGServ server.")
            elif lang_server == "de":
                return await ctx.send("Bitte geben Sie die ID Ihres OMGServ-Server ein.")
        if not args.isdigit():
            if lang_server == "fr":
                return await ctx.send("L'id OMGServ n'est pas un nombre.")
            elif lang_server == "en":
                return await ctx.send("The OMGServ id is not a number.")
            elif lang_server == "de":
                return await ctx.send("Die OMGServ-ID ist nicht ein Zahl.")
        data_players = requests.get(f"https://panel.omgserv.com/json/{args}/players").json()
        data_status = requests.get(f"https://panel.omgserv.com/json/{args}/status").json()
        if "Access denied" in str(data_status):
            if lang_server == "fr":
                return await ctx.send("L'id OMGServ n'existe pas.")
            elif lang_server == "en":
                return await ctx.send("The OMGServ id does not exist.")
            elif lang_server == "de":
                return await ctx.send("Die OMGServ-ID existiert nicht!")
        if not "Invalid type" in str(data_players):
            list_players = sorted([x for x in eval(str(data_players["players"]))], key=lambda x: x.casefold())
        else:
            list_players = False

        ImageFile.MAXBLOCK = 2**20
        img = Image.open("extra/background.jpg")
        W, _ = img.size
        font1 = ImageFont.truetype("extra/MikadoUltra.ttf", 120)
        font2 = ImageFont.truetype("extra/MikadoUltra.ttf", 90)
        font3 = ImageFont.truetype("extra/MikadoUltra.ttf", 70)
        draw = ImageDraw.Draw(img)
        if lang_server == "fr":
            msg_title = "Statistiques du Serveur"
        elif lang_server == "en":
            msg_title = "Server Statistics"
        elif lang_server == "de":
            msg_title = "Serverstatistik"
        w, _ = draw.textsize(msg_title, font=font1)
        draw.text(((W - w) / 2, 20), msg_title, font=font1, fill=(0, 255, 0))

        if list_players:
            for x in range(len(list_players)):
                if len(list_players) <= 4:
                    column = 300
                else:
                    column = 40
                    column1 = 640
                if x <= 4:
                    draw.text((column, 80 + (x + 1) * 150), "-  " +
                              list_players[x], font=font3, fill=(0, 0, 255))
                elif x <= 9:
                    draw.text((column1, 80 + (x - 4) * 150), "-  " +
                              list_players[x], font=font3, fill=(0, 0, 255))
                else:
                    pass
        else:
            if lang_server == "fr":
                msg_empty_server = "Serveur vide !"
            elif lang_server == "en":
                msg_empty_server = "Empty server!"
            elif lang_server == "de":
                msg_empty_server = "Leerer Server!"
            draw.text((200, 300), msg_empty_server, font=font1, fill=(0, 0, 255))

        try:
            status = "Online" if str(data_status["status"]["online"]) == "True" else "Offline"
        except:
            status = "Unknown"
        try:
            cpu_percent = str(data_status["status"]["cpu"])
        except:
            cpu_percent = "Ø"
        try:
            ram_number = str(data_status["status"]["ram"])
        except:
            ram_number = "Ø"
        try:
            max_players = str(data_status["status"]["players"]["max"])
        except:
            max_players = "Ø"
        draw.text((1280, 220), "Status : " + status, font=font2, fill=(255, 0, 0))
        draw.text((1280, 400), "Players : {}/{}".format(len(list_players), max_players), font=font2, fill=(255, 0, 0))
        draw.text((1280, 580), "CPU : {}%".format(cpu_percent), font=font2, fill=(255, 0, 0))
        draw.text((1280, 760), "RAM : {} Mo".format(ram_number[:4]), font=font2, fill=(255, 0, 0))
        img.thumbnail((1280, 720), Image.ANTIALIAS)
        img.save("extra/result.jpg", "JPEG", quality=80, optimize=True, progressive=True)
        await ctx.send(file=discord.File("extra/result.jpg", "mc.jpg"))
        await asyncio.sleep(10)
        try:
            subprocess.call("sudo rm extra/result.jpg", shell=True)
        except:
            pass

if debug:
    client.run(config["PRIVATE"]["token"])
else:
    client.run(config["PUBLIC"]["token"])
