import discord
from discord.ext import commands
#from discord.flags import Intents
import music, test, utility

bot_shit_channel = 799877996311085066
cogs = [music, utility, test] # add command groups

client = commands.Bot(command_prefix='-', Intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client) # for each group add commands to client/bot

@client.event #startup
async def on_ready():
    print("-------------------Bot is Online!-------------------")

@client.event #command error handler
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return await ctx.send("***Unknown Command, silly***")
    raise error

file1 = open('../client_token.txt', 'r')
token = file1.readline()
client.run(token)