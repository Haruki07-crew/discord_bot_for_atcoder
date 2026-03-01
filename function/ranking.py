import discord
from datetime import time, timezone, timedelta, datetime
from tools import atcoder_api, for_db
from discord.ext import tasks, commands

time_difference = timezone(timedelta(hours=9))
execution_time = time(hour=0, minute=5, tzinfo=time_difference)

class ranking(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.announce_channel_id = 1475681765661081761
    self.daily_check.start()
  
  def cog_unload(self):
    self.daily_check.cancel()

  @tasks.loop(time=execution_time)
  async def daily_check(self):
    channel = self.bot.get_channel(self.announce_channel_id)
    if not channel:
      return
    user_dict = for_db.get_user_dict()
    if not user_dict:
      return
    now = datetime.now(time_difference)
    yesterday = now - timedelta(days=1)

    daily_title = f'🔥 {yesterday.strftime("%Y/%m/%d")}のACランキング'
    await self.send_ranking(channel, user_dict, 1, daily_title, 0x2ecc71)

    if now.weekday() == 0:
      weekly_title = "🏆 週間ACランキング"
      await self.send_ranking(channel, user_dict, 7, weekly_title, 0xf1c40f)

    if now.day == 1:
      monthly_title = f'👑 {yesterday.strftime("%m月")}のACランキング'
      await self.send_ranking(channel, user_dict, 30, monthly_title, 0xe91e63)

  async def send_ranking(self, channel, user_dict, day, title, color):
    ranking_data = await atcoder_api.make_ranking(user_dict, day)
    embed = discord.Embed(
      title=title,
      color=color,
      timestamp=datetime.now(time_difference)
    )
    diff_emoji = ["⬜️", "🟫", "🟩", "💧", "🟦", "🟨", "🟧", "🟥"]

    for i, user in enumerate(ranking_data):
      d = user["data"]
      diff_dict = d["diff"]

      detail = []
      for index in range(8):
        count = diff_dict.get(index, 0)
        if count > 0:
          detail.append(f"{diff_emoji[index]}`{count}`")
      if detail:
        detail_text = " ".join(detail)
      else:
        detail_text = "ACなし!!!!"

      if i == 0:
        rank_icon = "🥇"
      elif i ==1:
        rank_icon = "🥈"
      elif i ==2:
        rank_icon = "🥉"
      else:
        rank_icon = "👤"
      embed.add_field(
        name=f'{rank_icon} {i+1}位: {user["discord_name"]}',
        value=f'✅ **{d["ac_count"]} AC** / ✨ **{d["ac_point"]} pts**\n└{detail_text}',
        inline=False
      )
    if not ranking_data:
      embed.description = "期間内のACはなかったぜbro"
    
    await channel.send(embed=embed)
  
async def setup(bot):
  await bot.add_cog(ranking(bot))
