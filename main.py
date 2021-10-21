import discord
from keys import *
import random as rand
import youtube_dl
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print("Bot is online.")


@bot.command()
async def hello(ctx):
    await ctx.send("Hello, I am a Test Bot.")


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


@bot.command()
async def play(ctx, url):
    voice = ctx.voice_client
    voice.stop()
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    YDL_OPTIONS = {'format': 'bestaudio/best'}

    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        urlplay = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(urlplay, **FFMPEG_OPTIONS)
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
