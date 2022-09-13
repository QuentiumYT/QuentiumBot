import nextcord, requests
from nextcord.ext import commands
from datetime import datetime
from QuentiumBot import storage, get_translations, get_config

# Basic command configs
cmd_name = "weather"
tran = get_translations()
aliases = [] if not tran[cmd_name]["fr"]["aliases"] else tran[cmd_name]["fr"]["aliases"].split("/")

class WeatherUtilities(commands.Cog):
    """Weather command in Utilities section"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name=cmd_name,
        aliases=aliases,
        pass_context=True
    )
    async def weather_cmd(self, ctx, *, city=None):
        # Get specific server data
        if isinstance(ctx.channel, nextcord.TextChannel):
            data = await storage.retrieve_data(ctx.message.guild)
            lang_server = data[0]
        else:
            lang_server = "en"
        cmd_tran = tran[cmd_name][lang_server]

        # Doesn't respond to bots
        if not ctx.message.author.bot == True:
            # Global embed
            embed = nextcord.Embed(color=0x11FFFF)

            # No city given
            if not city:
                embed.title = cmd_tran["msg_specify_city"]
                return await ctx.send(embed=embed)

            # Using HTML escaping
            city = city.replace(" ", "%20")
            url = "https://api.openweathermap.org/data/2.5/weather?q=" + city

            # Weather token
            token_w = get_config("GLOBAL", "token_weather")
            # Get weather data
            data_weather = requests.get(url + f"&appid={token_w}&lang={lang_server}").json()
            if "city not found" in str(data_weather) or not data_weather["coord"]:
                embed.title = cmd_tran["msg_city_not_found"]
                return await ctx.send(embed=embed)

            lat, lon = str(data_weather["coord"]["lat"]), str(data_weather["coord"]["lon"])
            # Timezone token
            token_tz = get_config("GLOBAL", "token_timezone")
            # Get timezone of location for time
            url = f"https://api.timezonedb.com/v2/get-time-zone?key={token_tz}&format=json&by=position&lat={lat}&lng={lon}"
            # Use timezone time or weather time
            try:
                current_time = requests.get(url).json()["formatted"]
            except:
                current_time = data_weather["dt"]
            # Get weather emojis for embed icon
            emoji = nextcord.utils.get(self.client.emojis, name=data_weather["weather"][0]["icon"])

            condition = data_weather["weather"][0]["main"]
            # Get translations for weather status
            if lang_server != "en":
                condition = cmd_tran[condition]

            # Get other weather data
            desc = data_weather["weather"][0]["description"]
            content = f"{emoji} {cmd_tran['msg_condition']} {condition} - \"{desc.title()}\"\n"
            if "clouds" in data_weather:
                content += cmd_tran["msg_cloudy"] + str(data_weather["clouds"]["all"]) + "%\n"
            if "rain" in data_weather:
                first_key = list(data_weather["rain"].keys())[0]
                content += cmd_tran["msg_rainy"].format(first_key) + str(data_weather["rain"][first_key]) + "L/m²\n"
            if "snow" in data_weather:
                first_key = list(data_weather["snow"].keys())[0]
                content += cmd_tran["msg_snowy"].format(first_key) + str(data_weather["snow"][first_key]) + "L/m²\n"
            # Calculates temperatures with Kelvin
            temp_celsius = str(round(data_weather["main"]["temp"] - 273.15, 1))
            temp_fahrenheit = str(round(data_weather["main"]["temp"] * 9 / 5 - 459.67, 1))
            # Add celsius if english lang
            if lang_server != "en":
                content += f"{cmd_tran['msg_temperature']} {temp_celsius}°C\n"
            else:
                content += f"{cmd_tran['msg_temperature']} {temp_celsius}°C - {temp_fahrenheit}°F\n"
            content += f"{cmd_tran['msg_humidity']} {data_weather['main']['humidity']}%\n"
            content += f"{cmd_tran['msg_wind_speed']} {float(data_weather['wind']['speed'])}m/s - {round(float(data_weather['wind']['speed']) * 3.6, 1)}km/h\n\n"
            sunrise_time = datetime.fromtimestamp(int(data_weather["sys"]["sunrise"])).strftime("%H:%M:%S")
            sunset_time = datetime.fromtimestamp(int(data_weather["sys"]["sunset"])).strftime("%H:%M:%S")
            content += cmd_tran["msg_sun"].format(sunrise_time, sunset_time)
            embed.title = cmd_tran["msg_weather_loc"].format(data_weather["name"], data_weather["sys"]["country"].lower())
            embed.description = content
            # Weather status emoji
            embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emoji.id}.png")
            embed.set_footer(text=cmd_tran["msg_local_date"] + current_time,
                             icon_url="https://cdn.discordapp.com/emojis/475328334557872129.png")
            await ctx.send(embed=embed)

def setup(client):
    client.add_cog(WeatherUtilities(client))
