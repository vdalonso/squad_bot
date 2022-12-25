from turtle import title
import discord
import asyncio
import pandas as pd
import pickle
from discord.ext import commands

BOT_CHANNEL = 799877996311085066
LEADERBOARD_PATH = "../leaderboard.csv"
EVENTS_PATH = "../events.pkl"
EMOJI_LIST = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']


class utility(commands.Cog):
    def __init__(self, client):
        self.client = client
        with open(EVENTS_PATH, 'rb') as input: # load events
            self.events = pickle.load(input)

    @commands.command()
    async def schedule(self, ctx, arg):
        if(arg == 'view'):
            await ctx.send("viewing")
            await utility.scheduleView(self, ctx)
        elif(arg == 'add'):
            await ctx.send("adding new event")
        else:
            await ctx.send("***Invalid arguement. Options are 'view', 'add', 'invite', 'remove'***")

    async def scheduleView(self, ctx):
        res = ""
        for i in self.events:
            res += "___" + i.title + "___\n"
        await ctx.send(embed=discord.Embed(
            title="Events",
            description=res
        ))
        return

    @commands.command(brief="Cast a vote! Enter things to vote on, send 'done' when finished")
    async def vote(self, ctx):
        await ctx.send("***Enter options to vote on (send 'done' when finished)***")
        candidates = []
        channel = ctx.channel
        def check (m):
            return m.channel == channel
        # collect all candidates from text channel
        msg = await self.client.wait_for('message', check=check, timeout=90.0)
        while(msg.content != 'done' or len(candidates) >= 10):
            candidates.append(msg.content)
            msg = await self.client.wait_for('message', check=check, timeout=90.0)
        #string-ify the candidates along with respective emoji's
        list = ""
        for index, c in enumerate(candidates):
            list += EMOJI_LIST[index] +": " + c + "\n"

        vote_msg = await ctx.send(embed=discord.Embed(
            title="Hit the Polling Station, it's time to Vote!",
            color=discord.Color.blurple(),
            description=list)
        )
        #add a reaction to embed for each candidate (the voting mechanism)
        for i in range(list.count('\n')):
            await vote_msg.add_reaction(EMOJI_LIST[i])
        return
        
    @commands.command(brief="Check if the bot is online")
    async def ping(self, ctx):
        return await ctx.send("***Pong!***")

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
    client.add_cog(utility(client))

class Event:
    attendees = []
    def __init__(self, title, time, date, weekly):
        self.title = title
        self.time = time
        self.date = date
        self.weekly = weekly