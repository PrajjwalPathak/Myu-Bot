import os
import discord
import random as rand
import youtube_dl
from googleapiclient.discovery import build
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix='!', intents=intents)
youtube = build('youtube', 'v3', developerKey=API_KEY)


@bot.event
async def on_ready():
    print("Bot is online.")


@bot.command()
async def hello(ctx):
    await ctx.send("Hello, I am a Music Player Bot. You can call me Myu.")


def general_channel():
    all_channels = bot.get_all_channels()
    for channel in all_channels:
        if str(channel) == "general":
            return channel


@bot.event
async def on_member_join(member):
    i = rand.randint(0, 4)
    wishes = ["Welcome on board! ", "Welcome! ", "Nice to meet you, ", "Congratulations and welcome, ",
              "Welcome to the team, "]
    channel = general_channel()
    await channel.send(wishes[i] + str(member))


@bot.event
async def on_member_remove(member):
    channel = general_channel()
    await channel.send(str(member) + " is no longer a member of this server.")


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You must be in a voice channel to run this command.")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I am not connected to a voice channel.")


def play_song(url):
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    ydl_options = {'format': 'bestaudio/best'}

    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(url, download=False)
        url_play = info['formats'][0]['url']
        source = discord.FFmpegOpusAudio.from_probe(url_play, **ffmpeg_options)
    return source


def search_song_id(keyword):
    request = youtube.search().list(q=keyword, part='snippet', type='video')
    res = request.execute()
    ids = []
    for item in res['items']:
        ids.append(item['id']['videoId'])
    return ids


def search_song_title(keyword):
    request = youtube.search().list(q=keyword, part='snippet', type='video')
    res = request.execute()
    titles = []
    for item in res['items']:
        titles.append(item['snippet']['title'])
    return titles


@bot.command()
async def play_link(ctx, url):
    voice = ctx.voice_client
    voice.stop()
    source = await play_song(url)
    voice.play(source)


@bot.command()
async def search(ctx, *, keyword):
    titles = search_song_title(keyword)
    i = 1
    for title in titles:
        await ctx.send(str(i) + ". " + title)
        i += 1

    @bot.command()
    async def play(ct, song_id):
        ids = search_song_id(keyword)
        id_play = ids[int(song_id)]
        song_id = int(song_id) - 1
        url = "https://www.youtube.com/watch?v=" + str(id_play)
        await ct.send("Playing: " + str(titles[int(song_id)]))
        voice = ctx.voice_client
        voice.stop()
        source = await play_song(url)
        voice.play(source)


@bot.command()
async def pause(ctx):
    voice = ctx.voice_client
    voice.pause()
    await ctx.send("Paused")


@bot.command()
async def resume(ctx):
    voice = ctx.voice_client
    voice.resume()
    await ctx.send("Resumed")


@bot.command()
async def stop(ctx):
    voice = ctx.voice_client
    voice.stop()
    await ctx.send("Stopped")


bot.run(TOKEN)