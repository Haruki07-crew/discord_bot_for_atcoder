import discord 
from discord.ext import commands
import config
from tools import for_db

class mybot(commands.Bot):
  def __init__(self):
    intents = discord.Intents.all()
    super().__init__(command_prefix="!", intents=intents)
  
  async def setup_hook(self):
    for_db.init_db()
    extensions = [
      "function.ranking",
      "function.user_manage"
    ]
    for extension in extensions:
      try:
        await self.load_extension(extension)
        print(f"✅ 読み込み完了: {extension}")
      except Exception as e:
        print(f"⚠️ 読み込み失敗: {extension}: {e}")
    await self.tree.sync()
    print(f"🔄 スラッシュコマンド同期成功")
  
  async def on_ready(self):
    print(f"🚪 {self.user}でログイン! (ID: {self.user.id})")

bot = mybot()
bot.run(config.DISCORD_TOKEN)
