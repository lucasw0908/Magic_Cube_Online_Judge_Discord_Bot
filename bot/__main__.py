import logging
import logging.handlers
import os

import discord
from discord.ext import bridge, commands
from setuptools import find_namespace_packages

from bot.config import TOKEN, LOG_FILENAME
from bot.judge import Judge


log = logging.getLogger(os.path.basename(os.path.dirname(__file__)))
        
        
class DiscordBotSync(bridge.Bot):
    """The discord bot object."""
    
    def __init__(self, command_prefix: str=None, **options) -> None:
        super().__init__(self, intents=discord.Intents.all(), **options)
        self.command_prefix = command_prefix if commands.when_mentioned_or(command_prefix) else commands.when_mentioned_or("-")
        
        
    def init_logger(self, debug: bool=False):
        
        formatter = logging.Formatter("[{asctime}] {levelname} {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{")
        
        if debug:
            log.setLevel(logging.DEBUG)
        else:
            log.setLevel(logging.INFO)
            
        file_handler = logging.handlers.RotatingFileHandler(
            filename=LOG_FILENAME,
            encoding="utf-8",
            maxBytes=8**7, 
            backupCount=8
        )
        
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logging.getLogger().addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        
      
    def load(self) -> None:
        """Load all cogs."""

        log.info("Loading packages...")
        
        for cog in find_namespace_packages(include=[f"{os.path.basename(os.path.dirname(__file__))}.cogs.*"]):

            try:
                self.load_extension(cog)
                log.info(f"Loaded package {cog}")
            except Exception:
                log.error(f"Failed to load package {cog}!", exc_info=True)
                
        log.info("Packages loading completed!")
        
      
    def run(self, token: str=TOKEN, debug: bool=False, **kwargs):
        
        self.init_logger(debug=debug)
        log.info("Initializing Judge...")
        Judge.init()
        self.load()
        
        super().run(token, **kwargs)
        

bot = DiscordBotSync("?")


if __name__ == "__main__":
    bot.run(debug=True)