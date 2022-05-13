import discord
import asyncio
import pandas as pd
from discord.ext import commands
from youtube_dl.utils import UnsupportedError
import youtube_dl

BOT_CHANNEL = 799877996311085066
LEADERBOARD_PATH = "../leaderboard.csv"

class testing(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def test_arg(self, ctx, arg):
        #id = ctx.channel.id
        await ctx.send(arg)

    @commands.command()
    async def test_args(self, ctx, *, args):
        await ctx.send(args)
    
    @commands.command()
    async def embed(self, ctx, *, args):
        embed=discord.Embed(title="Sample Embed", 
            url="https://realdrewdata.medium.com/", 
            description="This is an embed that will show how to build an embed and the different components", 
            color=discord.Color.blurple())
        await ctx.send(embed=embed)
    
    @commands.command()
    async def checkYT(self, ctx, arg):
        extractors = youtube_dl.extractor.gen_extractors()
        for e in extractors:
            if e.suitable(arg) and e.IE_NAME != 'generic':
                return await ctx.send("VALID YOUTUBE URL")
        return await ctx.send("INVALID URL")

    @commands.command(brief="Displays Leaderboard of Shame")
    async def leaderboard(self, ctx):
        channel = self.client.get_channel(BOT_CHANNEL)
        try:
            file = open(LEADERBOARD_PATH, mode='r')
            df = pd.read_csv(file)
            file.close()
        except OSError as e:
            channel = self.client.get_channel(BOT_CHANNEL)
            return await channel.send("LEADERBOARD ERROR")
        if(df.empty): #if dataframe is empty, return empty DF
            return await channel.send("__***Leaderboard of SHAME***__\nempty!")

        df.sort_values(by=['points'], ascending=False, inplace=True)
        leaderboard = "__***Leaderboard of SHAME***__\n"
        c = 1
        for index, row in df.iterrows():
            leaderboard+="***#" +str(c)+ " ---------- ***" + row['name'] +" [" + str(row['points']) + " points]\n"
            c+=1
        #799877996311085066: ID for the bot text channel
        await channel.send(leaderboard)

    @commands.command(brief="Cleans up text-channel from bot commands and bot replies. Also updates leaderboard")
    async def clean(self, ctx):
        #check previous [40] messages in textchannel and delete messages
        if(ctx.message.channel.name == 'bot-shit' and "all" not in ctx.message.content):
            return await ctx.send("***Bruh this is the bot channel***")
        try:
            file = open(LEADERBOARD_PATH, mode='r')
            df = pd.read_csv(file)
            file.close()
        except OSError as e:
            print(e)
            print("Creating file...")
            d = { 'name': [] , 'points': [] , 'id':[] }
            df = pd.DataFrame(d)
            df.astype({'name': 'str', 'points': 'int32', 'id': 'int32'}).dtypes
            df.to_csv(LEADERBOARD_PATH, index=False)
        lim = None if ("all" in ctx.message.content) else 40
        async for m in ctx.message.channel.history(limit=lim):
            if m.author.name == self.client.user.name or m.content == "-clean": #if a groovy2 reply or message is the invoking msg , delete
               print("deleting...")
               await m.delete()
            elif m.content.startswith('-') and m.content.split(" ")[0][1:] in [c.name for c in self.client.commands]: #if message is a command, delete and update dataframe
                try: # try updating existing count of user
                    index = df.index[df['name'] == m.author.name].tolist()
                    if (not index): # if there are no indeces with the author's name, add new entry
                        df.loc[len(df.index)] = [m.author.name, 1, m.author.id]
                    else:
                        df.at[index[0], 'points'] += 1 # add 1 to the already existing entry
                    print("deleting...Point Update for: " + m.author.name)
                    df.to_csv(LEADERBOARD_PATH, index=False)
                except KeyError as e: # if user isn't in df, create a new entry for them, start at 1
                    print(e)
                    print("ERROR: Name isnt found on data frame :( ")
                await m.delete()
            elif m.content.startswith('-'):
                print("deleting...")
                await m.delete()

        print("Finished Cleaning")
        return await ctx.invoke(self.client.get_command('leaderboard')) 
    
def setup(client):
    client.add_cog(testing(client))