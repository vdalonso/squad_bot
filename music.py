import discord
import asyncio
from discord.ext import commands
from youtube_dl.utils import UnsupportedError
from youtube_search import YoutubeSearch
import youtube_dl

queue = []

class music(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("***you aren't in a voice channel!***")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
        await ctx.send("***Hoppin' on VC!***")
    
    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.send("***Cya!***")

    @commands.command()
    async def play(self, ctx, *, arg):
        #print(arg)
        

        if ctx.voice_client is None: # if bot ins't in VC, make it join
            await ctx.invoke(self.client.get_command('join'))
        #ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio", 'audio-format': "best", 'audio-quality': 0}
        vc = ctx.voice_client

        try: # assuming args is a url
            ydl = youtube_dl.YoutubeDL(YDL_OPTIONS)
            info = ydl.extract_info(arg, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        except: # TODO: we're assuming here that this was a invalid URL error..
            print("Uh Oh!" )
            print("Going to query args instead...")
            res = YoutubeSearch(arg, max_results=1).to_dict()
            #print(res)
            url = "https://youtube.com" + res[0]['url_suffix']
            #print(url)
            ydl = youtube_dl.YoutubeDL(YDL_OPTIONS)
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            
        if vc.is_playing():
            queue.append(source)
            reply = "***Queued: " + info['title'] + "***"

        else:
            vc.play(source, after=lambda e: music.play_next(self, ctx))
            #vc.play(source)
            reply = "***Now Playing: " + info['title'] + "***"
        await ctx.send( reply)
        return

    def play_next(self, ctx):
        if len(queue) >= 1:
            source = queue.pop(0)
            vc = ctx.voice_client
            vc.play(source, after=lambda e: music.play_next(self, ctx))
            asyncio.run_coroutine_threadsafe(ctx.send("No more songs in queue"), self.client.loop)
        return


    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client != None:
            await ctx.voice_client.pause()
            await ctx.send("***Paused!!!***")
            return
        return
    
    @commands.command()
    async def resume(self, ctx):
        await ctx.voice_client.resume()
        await ctx.send("***Resuming!!!***")

    @commands.command()
    async def test(self, ctx, arg):
        await ctx.send(arg)

def setup(client):
    client.add_cog(music(client))

