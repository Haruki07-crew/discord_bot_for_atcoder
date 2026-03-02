import discord 
from discord import app_commands
import config
import atcoder_function
import sqlite3
import asyncio
from server import server_thread
import os

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

admin_id = config.ADMIN_ID
DB_FILE = "database.db"

def init_db():
  with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (atcoder_name TEXT PRIMARY KEY, discord_name TEXT)")
    conn.commit()
def get_user_dict():
  with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT atcoder_name, discord_name FROM users")
    row = cursor.fetchall()
  user_dict = {}
  for data in row:
    atcoder_name = data[0]
    discord_name = data[1]
    user_dict[atcoder_name] = discord_name
  return user_dict





@client.event
async def on_ready():
  init_db()
  await tree.sync()
  print("bot起動!")


#現在のレートの取得
@tree.command(name = "syozin", description="Atcoderの精進記録を返します")
async def rating_command(interaction: discord.Interaction, atcoder_name: str):
  await interaction.response.defer()
  try:
    ac_sum = await atcoder_function.get_ac_count(atcoder_name)
    ac_daily = await atcoder_function.count_period_ac(atcoder_name, 1)
    problems_url = f"https://kenkoooo.com/atcoder/#/user/{atcoder_name}?userPageTab=Progress+Charts"
    embed = discord.Embed(
      title = f"{atcoder_name}さんの精進記録",
      color = 0x2ecc71,
      url = problems_url,
      timestamp = interaction.created_at
    )
    embed.add_field(
      name = "これまでのAC数",
      value = f"**{ac_sum}** AC",
      inline = True
    )
    embed.add_field(
      name = "今日のAC数",
      value = f"**{ac_daily[0]}** AC",
      inline = True
    )
    embed.add_field(
      name = "今日の獲得点数",
      value = f"**{round(ac_daily[1])}** 点",
      inline = True
    )
    if ac_daily[0] == 0:
      embed.set_footer(text = "精進せんかい雑魚bro\n")
    else :
      embed.set_footer(text = "偉すぎるぜbro\n")
    await interaction.edit_original_response(embed = embed)
  except Exception as e:
    print(e)
    await interaction.edit_original_response(content=f"⚠️ エラーが発生しました。お手数ですが(<@{admin_id}>)までご連絡ください。")





#ユーザーの登録
@tree.command(name = "user_resister", description="ユーザーを登録します")
async def user_resister(interaction: discord.Interaction, atcoder_name: str):
  discord_name = interaction.user.display_name
  check = await atcoder_function.get_latest_rating_nofstring(atcoder_name)
  if "存在しません" in str(check):
    await interaction.response.send_message(f"エラー : {atcoder_name}は存在しません")
  else:
    with sqlite3.connect(DB_FILE) as conn:
      cursor = conn.cursor()
      cursor.execute("REPLACE INTO users (atcoder_name, discord_name) VALUES (?, ?)", (atcoder_name, discord_name))
      conn.commit()
    await interaction.response.send_message(f"{discord_name}さんを{atcoder_name}でDBに登録しました")



#ユーザー登録の解除
@tree.command(name = "user_unresister", description="登録されているユーザーの登録を解除します")
async def user_unresister(interaction: discord.Interaction, atcoder_name: str):
  conn = sqlite3.connect("database.db")
  cursor = conn.cursor()
  cursor.execute("DELETE FROM users WHERE atcoder_name = ?", (atcoder_name,))
  if cursor.rowcount > 0:
    await interaction.response.send_message(f"{atcoder_name}さんの登録を解除しました")
  else:
    await interaction.response.send_message(f"{atcoder_name}さんは登録されていません")
  conn.commit()
  conn.close()


#登録されているユーザの一覧を表示
@tree.command(name = "user_list", description="登録済みユーザーおよびレートを表示します")
async def user_list(interaction: discord.Interaction):
  user = get_user_dict()
  if not user:
    await interaction.response.send_message("登録されているユーザーがいません")
    return
  await interaction.response.defer()
  embed = discord.Embed(
    title = "登録ユーザー",
    color = 0x3498db,
    timestamp = interaction.created_at
  )
  for atcoder_name, discor_name in user.items():
    latest_rating = await atcoder_function.get_latest_rating_nofstring(atcoder_name)
    atcoder_url = f"https://atcoder.jp/users/{atcoder_name}"
    embed.add_field(
      name = f"{atcoder_function.get_rate_heart(latest_rating)} {discor_name}",
      value = f"Atcoder_ID: [{atcoder_name}]({atcoder_url})\n Rating: **{latest_rating}**",
      inline = False
    )
    await asyncio.sleep(0.5)
  await interaction.edit_original_response(embed = embed)


#ユーザー同士でAC数を比較
@tree.command(name = "ac_fight", description="ユーザー同士でACを比較することができます")
@app_commands.choices(period=[
  app_commands.Choice(name = "1日", value = 1),
  app_commands.Choice(name = "1週間", value = 7),
  app_commands.Choice(name = "1ヶ月", value = 30),
])
async def ac_fight(interaction: discord.Interaction, period: app_commands.Choice[int]):
  await interaction.response.defer()
  try:
    user = get_user_dict()
    day = period.value
    label = period.name
    ranking_data = await atcoder_function.make_ranking(user,day)

    if not ranking_data:
      await interaction.edit_original_response(content="登録されているユーザーがいません")
      return 
    embed = discord.Embed(
      title = f"🏆 AC fight ランキング [{label}]🏆",
      color = 0xFFD700, 
      timestamp = interaction.created_at
    )
    for data in ranking_data:
      embed.add_field(
        name = f"{data["figure"]}{data["place"]}位 : {data["discord_name"]}",
        value = f"AC数 : **{data["ac"]}** AC  点数 : **{data["point"]}** 点",
        inline = False
      )
    await interaction.edit_original_response(content=None, embed=embed) 
  except Exception as e:
    print(e)
    await interaction.edit_original_response(content=f"⚠️ エラーが発生しました。お手数ですが(<@{admin_id}>)までご連絡ください。")



server_thread()
client.run(config.DISCORD_TOKEN)



