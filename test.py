import discord
import asyncio
import pandas as pd
from discord.ext import commands
from youtube_dl.utils import UnsupportedError
import youtube_dl

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
    
def setup(client):
    client.add_cog(testing(client))