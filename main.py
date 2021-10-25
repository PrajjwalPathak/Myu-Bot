import os
import discord
import random as rand
import youtube_dl
from googleapiclient.discovery import build
from discord.ext import commands

TOKEN = os.environ['DISCORD_TOKEN']
API_KEY = os.environ['API_KEY']
intents = discord.Intents.default()
intents.members = True
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
    ydl_options = {'--skip-download' '--audio-format': 'mp3', '--audio-quality': '0'}

    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(url, download=False)
        url_play = info['formats'][0]['url']
        source = discord.FFmpegOpusAudio.from_probe(url_play, **ffmpeg_options)
    return source


global ids, titles


def search_songs(keyword):
    request = youtube.search().list(
        part="snippet",
        q=keyword,
        fields="items(id,snippet(title))"
    )
    res = request.execute()
    global ids
    global titles
    ids = []
    titles = []
    for item in res['items']:
        ids.append(item['id']['videoId'])
        titles.append(item['snippet']['title'])
    return [ids, titles]


@bot.command()
async def play_link(ctx, url):
    voice = ctx.voice_client
    if voice:
        voice.stop()
        source = await play_song(url)
        voice.play(source)
    else:
        await ctx.send("Myu-Bot is not connected to the voice channel.")
        await ctx.send("Use the command: !join")


@bot.command()
async def search(ctx, *, keyword):
    global ids, titles
    ids, titles = search_songs(keyword)
    i = 1
    embed = Embed(colour=discord.Color.red())
    for title in titles:
        embed.add_field(name=str(i), value=title, inline=False)
        i += 1
    await ctx.send(embed=embed)


@bot.command()
async def play(ctx, song_id):
    voice = ctx.voice_client
    if voice:
        id_play = ids[int(song_id)]
        song_id = int(song_id) - 1
        url = "https://www.youtube.com/watch?v=" + str(id_play)
        voice.stop()
        source = await play_song(url)
        voice.play(source)
        await ctx.send("Playing: " + str(titles[int(song_id)]))
    else:
        await ctx.send("Myu-Bot is not connected to the voice channel.")
        await ctx.send("Use the command: !join")


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
