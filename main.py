import os
import discord
import random as rand
import youtube_dl
from discord import Embed
from googleapiclient.discovery import build
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

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
    await ctx.send("Hello 👋, I am a Music Player Bot. You can call me Myu. 😃")
    await ctx.send("To see all the commands, use the command: !com")


def general_channel():
    all_channels = bot.get_all_channels()
    for channel in all_channels:
        if str(channel) == "general":
            return channel


@bot.event
async def on_member_join(member):
    i = rand.randint(0, 4)
    wishes = ["Welcome on board! 🚀", "Welcome! 😊", "Nice to meet you, 😄", "Congratulations and welcome, 😊",
              "Welcome to the team, 🍰"]
    channel = general_channel()
    await channel.send(wishes[i] + " " + str(member))


@bot.event
async def on_member_remove(member):
    channel = general_channel()
    await channel.send(str(member) + " is no longer a member of this server. 🛸")


@bot.command()
async def com(ctx):
    embed = Embed(colour=discord.Color.red())
    embed.add_field(name="!com", value="List all the commands. 📓", inline=False)
    embed.add_field(name="!hello", value="Myu-Bot introduction. 🕷", inline=False)
    embed.add_field(name="!join", value="Myu-Bot joins the voice channel. 🌎", inline=False)
    embed.add_field(name="!leave", value="Myu-Bot leaves the voice channel. ✈", inline=False)
    embed.add_field(name="!play_link", value="Myu-Bot plays the song linked to the url. (!play_link URL) 🎼",
                    inline=False)
    embed.add_field(name="!search", value="Myu-Bot searches the Youtube database for the songs. (!search QUERY)  🎶",
                    inline=False)
    embed.add_field(name="!play", value="Myu-Bot plays the song selected by the user. (!play SONG_NUMBER) 🎵",
                    inline=False)
    embed.add_field(name="!pause", value="Myu-Bot pauses the song. ⏸", inline=False)
    embed.add_field(name="!resume", value="Myu-Bot resumes the song which was paused earlier. ▶", inline=False)
    embed.add_field(name="!stop", value="Myu-Bot stops the song. ⏹", inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.message.author.voice.channel
        await channel.connect()
        await ctx.send("Connected to the voice channel. 🌎")
    else:
        await ctx.send("You must be in a voice channel to run this command. 🏜")


@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel. ✈")
    else:
        await ctx.send("I am not connected to a voice channel. 🏝")


def play_song(url):
    ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    ydl_options = {'--skip-download' '--audio-format': 'mp3', '--audio-quality': '0'}

    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        info = ydl.extract_info(url, download=False)
        url_play = info['formats'][0]['url']
        source = discord.FFmpegOpusAudio.from_probe(url_play, **ffmpeg_options, method='fallback')
    return source


global ids, titles, song


def search_songs(keyword):
    request = youtube.search().list(
        part="snippet",
        q=keyword,
        fields="items(id,snippet(title))",
        type="video"
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
        await ctx.send("Myu-Bot is not connected to the voice channel. 🏝")
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
        global song
        song = ""
        song = str(titles[int(song_id)])
        voice.play(source)
        await ctx.send("Playing: " + song + " 🎧")
    else:
        await ctx.send("Myu-Bot is not connected to the voice channel. 🏝")
        await ctx.send("Use the command: !join")


@bot.command()
async def pause(ctx):
    global song
    voice = ctx.voice_client
    voice.pause()
    await ctx.send("Paused the song. ⏸")


@bot.command()
async def resume(ctx):
    global song
    voice = ctx.voice_client
    voice.resume()
    await ctx.send("Resumed the song. ▶")


@bot.command()
async def stop(ctx):
    voice = ctx.voice_client
    voice.stop()
    await ctx.send("Stopped the song. ⏹")


bot.run(TOKEN)
