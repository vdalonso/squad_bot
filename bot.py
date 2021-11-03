import discord
from discord.ext import commands
#from discord.flags import Intents
import music

cogs = [music]

client = commands.Bot(command_prefix='-', Intents = discord.Intents.all())

for i in range(len(cogs)):
    cogs[i].setup(client)


file1 = open('client_token.txt', 'r')
token = file1.readline()
client.run(token)