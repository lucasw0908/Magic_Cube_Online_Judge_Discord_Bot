import discord
from discord.ext import commands

from bot.utils.help import HelpCommandSettings


class Help(commands.MinimalHelpCommand):
    async def send_bot_help(self, mapping):
        destination: discord.abc.Messageable = self.get_destination()
        view = HelpCommandSettings.help()
        await destination.send(embed=view.get_embed(), view=view)