import logging

import discord
from discord.ext import bridge, commands

from bot.utils.embed import EmbedMaker
from bot.data import get_data
from bot.utils.button import PageButton


log = logging.getLogger(__name__)


def need_help(command_name: str, error: discord.ApplicationCommandError) -> discord.Embed:
    return EmbedMaker(status=False, description=f'**在執行{command_name}時發生錯誤，錯誤報告如下:**``` * {error}```')

def comming_soon(command_name: str) -> discord.Embed:
    return discord.Embed(title=f"⚙️ 指令 {command_name} 尚未開放", description="敬請關注更新公告!!!", color=discord.Color.lighter_gray())

class HelpCommandSettings:
    
    @classmethod
    def set_command_list(cls, command_list: list[discord.ApplicationCommand]) -> None:
        cls.command_list = command_list
        
    
    @classmethod
    def set_prefix(cls, prefix: str) -> None:
        cls.prefix = prefix

        
    @classmethod
    def set_locale(cls, locale: str) -> None:
        cls.locale = locale
        
        
    @classmethod
    def help(cls) -> PageButton:
        
        prefix_commands_description = get_data("prefix_commands_description")
        embed = discord.Embed(title=f'指令列表⚙️', color=discord.Color.purple())
        
        if cls.command_list is None: 
            embed.add_field(name=f"_**無法取得指令資訊**_", inline=False)
            
        cmd_infor_list = []
        data = []
            
        for cmd in cls.command_list:
            
            if isinstance(cmd, (discord.SlashCommand, bridge.BridgeSlashCommand)):
                
                description = cmd.description or "No description provided"
                
                if cmd.description_localizations and (cls.locale in cmd.description_localizations):
                    description = cmd.description_localizations[cls.locale]
                    
                cmd_infor_list.append({
                    "name": cmd.name,
                    "description": description,
                    "type": "slash",
                    "value": f"{cmd.mention}\n _{description}_",
                })
                
            elif isinstance(cmd, (commands.Command, commands.HelpCommand, bridge.BridgeCommand)):
                
                if cls.prefix is None: 
                    log.error("Prefix is not set")
                    return
                
                if isinstance(cmd, bridge.BridgeExtCommand):
                    description = [c["description"] for c in cmd_infor_list if c["name"] == cmd.name][0]
                                
                elif cmd.name in prefix_commands_description:
                    description = prefix_commands_description[cmd.name]
                         
                else:
                    log.warning(f"Command {cmd.name} has no description")
                    description = "No description provided"

                cmd_infor_list.append({
                    "name": cmd.name,
                    "description": description,
                    "type": "prefix",
                    "value": f"**{cls.prefix}{cmd.name}**\n _{description}_",
                })
            
            else:
                log.warning(f"Command {cmd} is not supported, type: {type(cmd)}")
                
        cmd_infor_list = sorted(cmd_infor_list, key=lambda x: x["type"], reverse=True)
        
        for cmd_infor in cmd_infor_list:
            data.append({
                "name": "", 
                "value": cmd_infor["value"], 
                "inline": False
            })
            
        return PageButton(embed=embed, data=data, limit=5)