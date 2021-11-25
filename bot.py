import discord
from discord.ext import commands
#from discord.flags import Intents
import music, test

bot_shit_channel = 799877996311085066
cogs = [music, test] # add command groups

client = commands.Bot(command_prefix='-', Intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client) # for each group add commands to client/bot

@client.event
async def on_ready():
    print("-------------------Bot is Online!-------------------")

file1 = open('client_token.txt', 'r')
token = file1.readline()
client.run(token)