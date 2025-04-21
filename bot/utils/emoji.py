import re
import discord


class EmojiManager:
    emojis: dict[str, discord.Emoji] = None
    
    def __new__(cls, message: str):
        return cls.translation_emoji_string(message)
    
    
    @classmethod
    def translation_emoji_string(cls, message: str):
        """Translate the message including emojis"""
        pattern = re.compile(r':[^:]+:')
        
        for t in re.findall(pattern, message):
            t: str
            if cls.emojis is not None and t.strip(":") in cls.emojis:
                message = message.replace(t, cls.emojis[t.strip(":")])
                
        return message
    
        
    @classmethod
    def set_emojis(cls, emojis: dict[str, discord.Emoji]):
        cls.emojis = emojis
        
        
    @classmethod
    def get_emojis(cls):
        return cls.emojis