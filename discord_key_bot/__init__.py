import os
from typing import Any

import discord
from discord.ext.commands import Bot

from .commands.direct import DirectCommands
from .commands.guild import GuildCommands


class Client(Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    async def setup_hook(self) -> None:
        await self.add_cog(GuildCommands(bot))
        await self.add_cog(DirectCommands(bot))


intents = discord.Intents.default()
intents.message_content = True

bot = Client(command_prefix=os.environ.get("BANG", "!"), intents=intents)
