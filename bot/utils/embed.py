import discord
from .emoji import EmojiManager

class EmbedMaker:
    
    def __new__(cls, status: bool | None=None, description: str | None=None, title: str=None, color: str=None):
        cls.embed = discord.Embed(description=EmojiManager(description))
        
        emojis = EmojiManager.get_emojis()
        yes_emoji = "✅"
        no_emoji = "❌"
        
        if emojis:
            if "animation_yes" in emojis:
                yes_emoji = emojis["animation_yes"]
                
            if "animation_no" in emojis:
                no_emoji = emojis["animation_no"]
        
        if status is None:
            cls.embed.title = EmojiManager(title) if title else None
            cls.embed.color = discord.Color.blue()
            
        elif status:
            cls.embed.title = EmojiManager(title) if title else f'**執行成功{yes_emoji}**'
            cls.embed.color = discord.Color.green()
            
        else:
            cls.embed.title = EmojiManager(title) if title else f'**執行失敗{no_emoji}**'
            cls.embed.color = discord.Color.red()
            
        if color is not None:
            try: cls.embed.color = getattr(discord.Color, color)()
            except AttributeError: pass
            
        return cls.embed