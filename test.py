import discord
import asyncio
from discord.ext import commands

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

    

def setup(client):
    client.add_cog(testing(client))