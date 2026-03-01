import discord 
from discord import app_commands
from discord.ext import commands
from tools import for_db

class user_manage(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @app_commands.command(name="user_resister", description="ユーザーを登録します")
  async def user_resister(self, interaction: discord.Interaction, atcoder_name: str):
    discord_name = interaction.user.display_name
    for_db.user_resister(atcoder_name, discord_name)
    await interaction.response.send_message(f"✅ {discord_name}さんを{atcoder_name}でDBに登録しました")
  
  @app_commands.command(name="user_unresister", description="登録されているユーザーの登録を解除します")
  async def user_unresister(self, interaction: discord.Interaction, atcoder_name: str):
    success = for_db.user_unresister(atcoder_name)
    if success:
      await interaction.response.send_message(f"🗑️ `{atcoder_name}`さんの登録を解除しました")
    else:
      await interaction.response.send_message(f"⚠️ `{atcoder_name}`さんは登録されていません")
  
  @app_commands.command(name="user_list", description="登録済みユーザーを表示します")
  async def user_list(self, interaction: discord.Interaction):
    user = for_db.get_user_dict()
    if not user:
      await interaction.response.send_message("誰も登録されてないぜ。`/user_register` で登録してくれ！")
      return
    
    text = "📊 **登録メンバー**\n"
    for atcoder_name, discord_name in user.items():
      text += f"・ {discord_name} (AtCoder: `{atcoder_name}`)\n"
    await interaction.response.send_message(text)

async def setup(bot):
  await bot.add_cog(user_manage(bot))

