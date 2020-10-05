import discord
import datetime
import json
import pytz
from discord.ext import tasks

# Import files
from ThirdpartyAPI.openweathermap import openweathermap
from ThirdpartyAPI.yahoogeocode import yahoogeocode
from ThirdpartyAPI.heartrails import heartrails
from ThirdpartyAPI.earthquake import earthquake
from embed import createembed
import Config.config as config

# Discord related
(discord_bot_token,
 channel_id_weather,
 channel_id_earthquake) = config.discordconfig()

# Open citylist.json
citylistjson = open('./JSON/citylist.json', 'r')
citylist = json.load(citylistjson)

client = discord.Client()

# Discord Connect


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if '$' in message.content is False:
        return

    messagecontent = None
    weatherinfo = None
    coordinateinfo = None

    # Incorrect Command Error
    if not ('$day' in message.content
            or '$tmr' in message.content
            or '$week' in message.content
            or '$help' in message.content):
        await message.channel.send('コマンドに誤りがあります')
        return

    messagecontent = message.content.split(' ')
    geoinfo = yahoogeocode(messagecontent[1])
    if geoinfo[0] != 0:
        await message.channel.send('エラーが発生しました')
    weatherinfo = openweathermap(geoinfo[1])
    coordinateinfo = heartrails(geoinfo[1])

    # $day command
    if message.content.startswith('$day'):
        embed = createembed(0, message, '', weatherinfo, coordinateinfo, '')
        await message.channel.send(embed=embed)
    # $tmr command
    elif message.content.startswith('$tmr'):
        embed = createembed(1, message, '', weatherinfo, coordinateinfo, '')
        await message.channel.send(embed=embed)
    # $week command
    elif message.content.startswith('$week'):
        embed = createembed(2, message, '', weatherinfo, coordinateinfo, '')
        await message.channel.send(embed=embed)
    # $help command
    elif message.content == '$help':
        embed = createembed(3, message, '', '', '')
        await message.channel.send(embed=embed)
    else:
        await message.channel.send('コマンドに誤りがあります')
        return

# region Daily weather forecast


@ tasks.loop(seconds=60)
async def dailyfc():
    now = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%H:%M')
    channel = client.get_channel(int(channel_id_weather))

    if now == '06:00':
        for i in range(len(citylist['city'])):
            geoinfo = yahoogeocode(citylist['city'][i])
            weatherinfo = openweathermap(geoinfo[1])
            embed = createembed(
                4, '', citylist['city'][i], weatherinfo, '', '')
            await channel.send(embed=embed)
    elif now == '19:00':
        for i in range(len(citylist['city'])):
            geoinfo = yahoogeocode(citylist['city'][i])
            weatherinfo = openweathermap(geoinfo[1])
            embed = createembed(
                5, '', citylist['city'][i], weatherinfo, '', '')
            await channel.send(embed=embed)


# endregion

# region Earthquake Early Warning
@ tasks.loop(seconds=1)
async def earthquakealert():
    earthquakeinfo = earthquake()
    channel = client.get_channel(int(channel_id_weather))
    embed = None

    try:
        if earthquakeinfo['Status']['Code'] != '00':
            print('In')
            return

        if (earthquakeinfo['Title']['String'] == '緊急地震速報（警報）'
                and earthquakeinfo['MaxIntensity']['String'] == ('5弱'
                                                                 or '5強'
                                                                 or '6弱'
                                                                 or '6強'
                                                                 or '7')):
            embed = createembed(6, '', '', '', '', earthquakeinfo)
            await channel.send(embed=embed)
    except Exception as e:
        print('Error: ')
        print(e)
        pass

# endregion

# Loop
dailyfc.start()
earthquakealert.start()

client.run(discord_bot_token)
