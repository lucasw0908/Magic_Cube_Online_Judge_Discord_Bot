import logging

import discord
from discord.ext import commands

from bot.utils.embed import EmbedMaker
from bot.utils.button import PageButton
from bot.judge import Judge, Status


log = logging.getLogger(__name__)


class Upload(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.running = False
        
    @commands.slash_command(name="upload")
    async def upload(self, ctx: discord.ApplicationContext, file: discord.Attachment, data: discord.Attachment=None):
        """Upload a file to the server."""
        
        if not file.filename.endswith(".py"):
            embed = EmbedMaker(
                title="錯誤 :animation_no:",
                description="請上傳 Python 檔案！",
                color="red",
            )
            await ctx.respond(embed=embed)
            return
        
        if data and (not data.filename.endswith(".json")):
            embed = EmbedMaker(
                title="錯誤 :animation_no:",
                description="請上傳 JSON 檔案！",
                color="red",
            )
            await ctx.respond(embed=embed)
            return
        
        if self.running:
            embed = EmbedMaker(
                title="錯誤 :animation_no:",
                description="目前正在運行中，請稍後再試！",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed)
            return
        
        waiting_resp = await ctx.respond("正在運行中，請稍後...", ephemeral=True)
        
        self.running = True
        status_code, msg = \
            Judge.judge(file=await file.read(), data=await data.read(), data_filename=data.filename) \
            if data else Judge.judge(file=await file.read())
            
        self.running = False
        log.debug(f"status_code: {status_code}, msg: {msg}")
        
        embed = EmbedMaker(
            title="**上傳成功 :animation_yes:**",
            description=f"```{msg}```",
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        
        match status_code:
            case Status.AC: 
                embed.color = discord.Color.green()
                embed.add_field(name="測試結果: ", value="Accept", inline=True)
                Judge.record(ctx.author.name)
                
            case Status.WA: 
                embed.color = discord.Color.red()
                embed.add_field(name="測試結果: ", value="Wrong Answer", inline=True)
                
            case Status.TLE: 
                embed.color = discord.Color.blue()
                embed.add_field(name="測試結果: ", value="Time Limit Exceed", inline=True)
                
            case Status.RE: 
                embed.color = discord.Color.purple()
                embed.add_field(name="測試結果: ", value="Rumtime Error", inline=True)
                
            case Status.CE: 
                embed.color = discord.Color.orange()
                embed.add_field(name="測試結果: ", value="Compile Error", inline=True)

        Judge.reset()
        await ctx.send(embed=embed)
        
        log.debug(f"{ctx.author.name}({ctx.author.id}) used {ctx.command.name}.")
        
        
    @commands.slash_command(name="ranklist")
    async def ranklist(self, ctx: discord.ApplicationContext):
        """Show the ranklist."""
        
        embed = discord.Embed(
            title="**排行榜**",
            description="",
            color=discord.Color.gold()
        )
        page_button = PageButton(
            embed=embed,
            data=[{"name": f"", "value": f"***{str(k)} - Score: {round(v, 2)}***", "inline": False} for k, v in Judge.ranklist.items()],
            limit=5,
            ctx=ctx
        )
        await ctx.respond(embed=page_button.get_embed(), view=page_button)
        
        log.debug(f"{ctx.author.name}({ctx.author.id}) used {ctx.command.name}.")


def setup(bot: commands.Bot):
    bot.add_cog(Upload(bot))