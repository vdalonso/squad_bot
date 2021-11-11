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

    @commands.command(brief='Joins VC the user is in')
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("***you aren't in a voice channel!***")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
            await ctx.send("***Hoppin' on VC!***")
        else:
            #await ctx.voice_client.move_to(voice_channel)
            await ctx.send("***I'm busy in some other VC :(((***")
    
    @commands.command(brief='Leaves VC the bot is in')
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.send("***Cya!***")
        queue.clear()

    @commands.command(brief="Plays or queues song requested by user")
    async def play(self, ctx, *, arg):
        if ctx.voice_client is None: # if bot ins't in VC, make it join
            await ctx.invoke(self.client.get_command('join'))
        #ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format': "bestaudio", 'audio-format': "best", 'audio-quality': 0}
        vc = ctx.voice_client

        try: # assuming args is a url
            ydl = youtube_dl.YoutubeDL(YDL_OPTIONS)
            info = ydl.extract_info(arg, download=False)
            if "_type" in info: # if '_type is a field in the dict, it's a playlist
                for i in info['entries']:   # for every single entry, format the url
                    url2 = i['formats'][0]['url']
                    song = {
                        "source": await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS),
                        "title": i['title'],             #TODO: title is the title of the playlist here.
                    }
                    #source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                    queue.append(song) # append song to queue regardless

            else: # it is a single song
                url2 = info['formats'][0]['url'] # playlist cause error here
                source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                queue.append(source)
        except: # if we get Exception that means user didn't give a URL, search as query instead
            print("Uh Oh!" )
            print("Going to query args instead...")
            res = YoutubeSearch(arg, max_results=1).to_dict()
            url = "https://youtube.com" + res[0]['url_suffix']
            ydl = youtube_dl.YoutubeDL(YDL_OPTIONS)
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            song = {
                "source": await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS),
                "title": info['title'],
            }
            #source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
            queue.append(song) # append song to queue regardless
            
        if vc.is_playing(): 
            reply = "***Queued: " + info['title'] + "***"

        else: # if nothing is playing: dequeue and play
            song = queue.pop(0)
            vc.play(song['source'], after=lambda e: music.play_next(self, ctx))
            #vc.play(source)
            reply = "***Now Playing: " + info['title'] + "***"
        await ctx.send( reply)
        return

    def play_next(self, ctx):
        if len(queue) >= 1:
            song = queue.pop(0)
            vc = ctx.voice_client
            vc.play(song['source'], after=lambda e: music.play_next(self, ctx))
            reply = "***Now Playing: " + song['title'] + "***"
            asyncio.run_coroutine_threadsafe(ctx.send(reply), self.client.loop)
        else:
            queue.clear()
            ctx.voice_client.stop()

    @commands.command(brief='Skips currently playing song')
    async def skip(self, ctx):
        if ctx.voice_client is None: # bot not in VC
            return
        if ctx.author.voice.channel != ctx.voice_client.channel : # if user is not in the same VC as the bot
            await ctx.send("***I'm busy in some other VC :(((***")
            return
        if not ctx.voice_client.is_playing(): # bot isn't playing anything
            return
        ctx.voice_client.pause()
        music.play_next(self, ctx)
        return

    @commands.command(brief='Pauses music currently playing')
    async def pause(self, ctx):
        if ctx.author.voice.channel != ctx.voice_client.channel : # if user is not in the same VC as the bot
            await ctx.send("***I'm busy in some other VC :(((***")
            return
        if ctx.voice_client.is_playing(): # if bot is playing, pause
            ctx.voice_client.pause()
            await ctx.send("***Paused!!!***")
        return
    
    @commands.command(brief='Resumes playing music previously paused')
    async def resume(self, ctx):
        if ctx.author.voice.channel != ctx.voice_client.channel : # if user is not in the same VC as the bot, just ignore
            await ctx.send("***I'm busy in some other VC :(((***")
            return
        if ctx.voice_client.is_paused(): # if bot is paused, resume
            ctx.voice_client.resume()
            await ctx.send("***Resuming!!!***")
        return

def setup(client):
    client.add_cog(music(client))

