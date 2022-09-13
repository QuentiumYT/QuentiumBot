import nextcord, os
from nextcord.ext import commands

class ManageCogs(commands.Cog):
    """Commands to load, unload, reload cogs for QuentiumYT (private)"""

    def __init__(self, client):
        self.client = client

    async def find_cogs(self):
        self.startup_cogs = {**{"": [c.replace(".py", "") for c in os.listdir("cogs") if os.path.isfile(os.path.join("cogs", c))]}, # Public cogs
                             **{cat + ".": [c.replace(".py", "") for c in os.listdir("cogs/" + cat) if c != "__pycache__"]
                                for cat in os.listdir("cogs") if os.path.isdir("cogs/" + cat) and cat != "__pycache__"}} # Other cogs

    @commands.command(
        pass_context=True,
        hidden=True
    )
    @commands.is_owner()
    async def load(self, ctx, extension=None):
        if extension:
            await self.find_cogs()
            for cat, exts in self.startup_cogs.items():
                if extension in exts:
                    try:
                        self.client.load_extension("cogs." + cat + extension)
                        return await ctx.send(f"`{extension}` successfully loaded.")
                    except Exception as e:
                        return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
            else:
                await ctx.send(f"`{extension}` not found...")

    @commands.command(
        pass_context=True,
        hidden=True
    )
    @commands.is_owner()
    async def unload(self, ctx, extension=None):
        if extension:
            await self.find_cogs()
            for cat, exts in self.startup_cogs.items():
                if extension in exts:
                    try:
                        self.client.unload_extension("cogs." + cat + extension)
                        return await ctx.send(f"`{extension}` successfully unloaded.")
                    except Exception as e:
                        return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
            else:
                await ctx.send(f"`{extension}` not found...")

    @commands.command(
        pass_context=True,
        hidden=True
    )
    @commands.is_owner()
    async def reload(self, ctx, extension=None):
        if extension:
            await self.find_cogs()
            for cat, exts in self.startup_cogs.items():
                if extension in exts:
                    try:
                        self.client.unload_extension("cogs." + cat + extension)
                        self.client.load_extension("cogs." + cat + extension)
                        return await ctx.send(f"`{extension}` successfully reloaded.")
                    except Exception as e:
                        return await ctx.send(f"```py\n{type(e).__name__}: {e}\n```")
            else:
                await ctx.send(f"`{extension}` not found...")


def setup(client):
    client.add_cog(ManageCogs(client))
