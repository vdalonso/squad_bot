from asyncio.queues import Queue
import discord
import asyncio
from discord.colour import Color
import youtube_dl
from discord.ext import commands
from youtube_dl.utils import UnsupportedError
from youtube_search import YoutubeSearch


#queue = []

class music(commands.Cog):
    #queue = []

    def __init__(self, client):
        self.client = client
        self.queue = []

    @commands.command(brief='Joins VC the user is in')
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("***You aren't in a voice channel!***")
            return
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await ctx.send("***Hoppin' on VC!***")
            await voice_channel.connect()
        else:
            #await ctx.voice_client.move_to(voice_channel)
            await ctx.send("***I'm already in a VC :(((***")
    
    @commands.command(brief='Leaves VC the bot is in')
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            await ctx.send("***Cya!***")
            await ctx.voice_client.disconnect()
            self.queue = []
        else: 
            return await ctx.send("***I'm not in a VC, silly***")

    @commands.command(brief='Stops music playing and clears the entire queue.')
    async def clear(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            self.queue = []
        else:
            self.queue = []
        return await ctx.send("***Music queue cleared!***")

    @commands.command(brief='Displays the music queue')
    async def queue(self, ctx):
        embed=discord.Embed(title="Da Queue", color=discord.Color.dark_magenta())
        if len(self.queue) == 0:
            embed.add_field(name="Empty Queue :(", value="no songs")
            await ctx.send(embed=embed)
            return
        embed.add_field(name="song #1 (now playing)", value=self.queue[0]['title'], inline=False)
        for idx, val in enumerate(self.queue[1:]):
            embed.add_field(name="song #"+str(idx + 2), value=val['title'], inline=False)
        await ctx.send(embed=embed)
        return

    @commands.command(brief="[args] Plays or queues song requested by user")
    async def play(self, ctx, *, arg):
        if ctx.author.voice is None:
            await ctx.send("***You aren't in a voice channel!***")
            return
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
                    self.queue.append(song) # append song to queue regardless

            else: # it is a single song
                url2 = info['formats'][0]['url'] # playlist cause error here
                #print(info)
                song = {
                    "source": await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS),
                    "title": info['title']
                }
                #source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                self.queue.append(song)
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
            #queue.append(song)
            self.queue.append(song) # append song to queue regardless
            
        if vc.is_playing(): 
            reply = "***Queued: " + info['title'] + "***"

        else: # if nothing is playing: dequeue and play
            song = self.queue[0]
            #song = self.queue.pop(0)
            vc.play(song['source'], after=lambda e: music.play_next(self, ctx))
            #vc.play(source)
            reply = "***Now Playing: " + info['title'] + "***"
        await ctx.send( reply)
        return

    def play_next(self, ctx):
        #self.queue.pop(0) # this raises an error bc callback is called on 'voice_client.stop()' calls
        if len(self.queue) == 0:
            self.queue.clear()
            ctx.voice_client.stop()
        elif len(self.queue) == 1:
            self.queue.pop()
        else:
            self.queue.pop(0)
            song = self.queue[0]
            vc = ctx.voice_client
            vc.play(song['source'], after=lambda e: music.play_next(self, ctx))
            reply = "***Now Playing: " + song['title'] + "***"
            asyncio.run_coroutine_threadsafe(ctx.send(reply), self.client.loop)
        return

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

    @commands.command(brief='[args] Removes a song from the queue specified by a number')
    async def remove(self, ctx, arg):
        if len(self.queue) == 0: # case where queue is empty
            await ctx.send("***Queue is empty :(***")
            return
        track_num = int(arg) 
        if track_num <= 0 or track_num >= len(self.queue) + 1: # case where given int is out of queue range
            return await ctx.send("***Number is not within the queue's range. Use '-queue' command to see song numbers***")
        if track_num == 1:
            return await ctx.invoke(self.client.get_command('skip'))
        song = self.queue.pop(track_num - 1)
        reply = "***Removed: " + song['title'] + "***"
        return await ctx.send(reply)


def setup(client):
    client.add_cog(music(client))

