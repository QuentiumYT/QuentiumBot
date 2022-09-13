import nextcord, inspect
from nextcord.ext import commands

# Import more useful modules and every Bot functions
from QuentiumBot import *
import os, psutil, time, datetime

class RootQuentium(commands.Cog):
    """Commands to evalute Python code and execute Windows | Unix commands on the host for QuentiumYT (private)"""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name="eval",
        pass_context=True,
        hidden=True
    )
    @commands.is_owner()
    async def eval_cmd(self, ctx, *, args=None):
        if not args:
            return await ctx.message.delete()

        # Alias for ctx.send for output
        say = ctx.send

        try:
            # Evaluates the args
            res = eval(args)
            # If the command can be awaited
            if inspect.isawaitable(res):
                await res
                await say("Command executed!")
            # Send the simple message
            else:
                await say(res)
        except Exception as e:
            await ctx.send(f"```python\n{type(e).__name__}: {e}```")

    @commands.command(
        name="exec",
        pass_context=True,
        hidden=True
    )
    @commands.is_owner()
    async def exec_cmd(self, ctx, *, args=None):
        if not args:
            return await ctx.message.delete()

        # Run the command using the global function
        await exec_command(args, ctx.message)

def setup(client):
    client.add_cog(RootQuentium(client))
