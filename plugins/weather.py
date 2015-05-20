from util import hook
import requests, re

@hook.command("w",autohelp=False)
@hook.command(autohelp=False)
def weather(inp, db=None, input=None):
    "Usage: weather [location] -- gets weather information from http://openweathermap.org/"
    db.execute("CREATE TABLE IF NOT EXISTS weather(nick primary key, loc)")
    db.execute("CREATE TABLE IF NOT EXISTS location(chan, nick, loc, lat, lon, primary key(chan, nick))")
    db.commit()
    if not inp:
        loc = db.execute("SELECT loc FROM weather WHERE nick = ?", (input.nick.lower(),)).fetchone()
        if not loc:
            return weather.__doc__
        loc = loc[0]
    else:
        loc = inp
        db.execute("INSERT OR REPLACE INTO weather(nick, loc) VALUES (?,?)", (input.nick.lower(), loc))
        db.commit()
    loc = loc.replace('hell','hull')
    try:
        data = requests.get('http://api.openweathermap.org/data/2.5/find', params={"q":loc,"units":"metric"},headers={"user-agent":"Mozilla/5.0 (X11; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0"}).json()["list"][0]
        lat, lon = data["coord"]["lat"], data["coord"]["lon"]
        db.execute("insert or replace into location(chan, nick, loc, lat, lon) values (?, ?, ?, ?, ?)", (input.chan, input.nick.lower(), inp, lat, lon))
        db.commit()
        city = u"{}, {}".format(data["name"],data["sys"]["country"])
        temp_C = int(data["main"]["temp"])
        temp_F = CtoF(temp_C)
        humidity = data["main"]["humidity"]
        wind_speed_mph = int(data["wind"]["speed"])
        wind_speed_kmh = MPHtoKMH(wind_speed_mph)
        wind_direction = DEGtoDIR(int(data["wind"]["deg"]))
        clouds_description = data["weather"][0]["main"]
        return u"{}: Currently {}C ({}F), humidity: {}%, wind: {} at {}mph ({}km/h), conditions: {}.".format(
            city,temp_C,temp_F,humidity,wind_direction,wind_speed_mph,wind_speed_kmh,clouds_description)
    except:
        return "Location not found"

@hook.command(autohelp=False)
def forecast(inp, db=None, input=None):
    "Usage: forecast [location] -- get tomorrows forecast"
    db.execute("CREATE TABLE IF NOT EXISTS weather(nick primary key, loc)")
    if not inp:
        loc = db.execute("SELECT loc FROM weather WHERE nick = ?", (input.nick.lower(),)).fetchone()
        if not loc:
            return forecast.__doc__
        loc = loc[0]
    else:
        loc = inp
        db.execute("INSERT OR REPLACE INTO weather(nick, loc) VALUES (?,?)", (input.nick.lower(), loc))
        db.commit()
    loc = loc.replace('hell','hull')
    try:
        data = requests.get('http://api.openweathermap.org/data/2.5/forecast?q={0}&type=like&units=metric'.format(
            loc), headers={"user-agent":"Mozilla/5.0 (X11; Linux x86_64; rv:36.0) Gecko/20100101 Firefox/36.0"}).json()
        city = "{}, {}".format(data["city"]["name"],data["city"]["country"])
        data = data["list"][0]
        temp_C = int(data["main"]["temp"])
        temp_F = CtoF(temp_C)
        temp_C_min = int(data["main"]["temp_min"])
        temp_C_max = int(data["main"]["temp_max"])
        temp_F_min = CtoF(temp_C_min)
        temp_F_max = CtoF(temp_C_max)
        humidity = data["main"]["humidity"]
        wind_speed_mph = int(data["wind"]["speed"])
        wind_speed_kmh = MPHtoKMH(wind_speed_mph)
        wind_direction = DEGtoDIR(int(data["wind"]["deg"]))
        clouds_description = data["weather"][0]["main"]
        return "Tomorrows forecast for {}: temperature: min: {}C / {}F, max: {}C / {}F, humidity: {}%, wind: {} at {}mph / {}km/h, conditions: {}.".format(
            city,temp_C_min,temp_F_min,temp_C_max,temp_F_max,humidity,wind_direction,wind_speed_mph,wind_speed_kmh,clouds_description)
    except:
        return "Location not found"

def CtoF(c):
    return int(c * 1.8000 + 32)

def MPHtoKMH(m):
    return int(m * 1.60934)

def DEGtoDIR(d):
    return ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"][int((d + 11.25) / 22.5)]

