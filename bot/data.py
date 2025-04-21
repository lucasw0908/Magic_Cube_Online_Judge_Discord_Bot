import os
import json
import logging
from typing import Any

import discord
from discord.ext import commands


log = logging.getLogger(__name__)


def get_assets(filename: str, folder: str="character") -> discord.File | None:
    
    if not filename.endswith(".png"):
        filename += ".png"
        
    path = os.path.join(os.path.dirname(__file__), "assets", folder, filename)
    
    if not os.path.exists(path):
        
        log.error(f"File not found: {path}")
        return None
    
    image = discord.File(path, filename=filename)
    
    log.debug(f"Loaded {filename}")
    
    return image


def get_data(filename: str) -> Any:
    
    if not filename.endswith(".json"):
        filename += ".json"

    path = os.path.join(os.path.dirname(__file__), "json", filename)
    
    if not os.path.exists(path):
        
        log.error(f"File not found: {path}")
        return {}
    
    with open(path, "r", encoding="utf-8") as f:
    
        log.debug(f"Loaded {filename}")
        return json.load(f)
    
    
def get_skill_func(name: str) -> dict:
    
    try:
        import importlib
        importlib.invalidate_caches()
        
        character = importlib.import_module(f"bot.skills.{name}")
        
        log.debug(character)
        
        log.debug(f"Loaded skill function: {name}")
        return [character.skill, character.skill_2, character.ex_skill]
    
    except ImportError as e:
        log.error(f"Skill function not found: {name}", exc_info=e)
        return {}