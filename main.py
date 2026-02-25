import discord 
from discord import app_commands
import config
import atcoder_function
import sqlite3

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

# def init_db():


user_name_dict = {}


@client.event
async def on_ready():
  await tree.sync()
  print("bot起動!")


#現在のレートの取得
@tree.command(name = "rating", description="Atcoderのレートを取得します")
async def rating_command(interaction: discord.Interaction, atcoder_name: str):
  result = atcoder_function.get_latest_rating(atcoder_name)
  await interaction.response.send_message(result)


#これまでのAC数および今日のAC数
@tree.command(name = "ac_count", description="AC数を取得します")
async def AC_counter(interaction: discord.Interaction, atcoder_name: str):
  result = atcoder_function.AC_print(atcoder_name)
  await interaction.response.send_message(result)


#ユーザーの登録
@tree.command(name = "user_resister", description="ユーザーを登録します")
async def user_resister(interaction: discord.Interaction, atcoder_name: str, discord_name: str):
  check = atcoder_function.get_latest_rating_nofstring(atcoder_name)
  if "存在しません" in str(check):
    await interaction.response.send_message(f"エラー : {atcoder_name}は存在しません")
  else:
    user_name_dict[atcoder_name] = discord_name
    await interaction.response.send_message(f"{discord_name}さんを{atcoder_name}で登録しました")


#ユーザー登録の解除
@tree.command(name = "user_unresister", description="登録されているユーザーの登録を解除します")
async def user_unresister(interaction: discord.Interaction, atcoder_name: str):
  if atcoder_name in user_name_dict:
    discor_name = user_name_dict[atcoder_name]
    del user_name_dict[atcoder_name]
    await interaction.response.send_message(f"{discor_name}さんの登録を解除しました")


#登録されているユーザの一覧を表示
@tree.command(name = "user_list", description="登録済みユーザーおよびレートを表示します")
async def user_list(interaction: discord.Interaction):
  if user_name_dict:
    response_tmp_dict = []
    for atcoder_name, discor_name in user_name_dict.items():
      latest_rating = atcoder_function.get_latest_rating_nofstring(atcoder_name)
      response_tmp_dict.append(f"👤{discor_name} → {atcoder_name} : {latest_rating}")
    response_message = "\n".join(response_tmp_dict)
    await interaction.response.send_message(response_message)
  else:
    await interaction.response.send_message("登録されているユーザーがいません")


#ユーザー同士でAC数を比較
@tree.command(name = "ac_fight", description="ユーザー同士でACを比較することができます")
@app_commands.choices(period=[
  app_commands.Choice(name = "1日", value = 1),
  app_commands.Choice(name = "1週間", value = 7),
  app_commands.Choice(name = "1ヶ月", value = 30),
  app_commands.Choice(name = "3ヶ月", value = 90),
  app_commands.Choice(name = "半年", value = 180),
  app_commands.Choice(name = "1年", value = 365)
])
async def ac_fight(interaction: discord.Interaction, period: app_commands.Choice[int]):
  await interaction.response.defer()
  day = period.value
  label = period.name
  ranking_data = atcoder_function.make_ranking(user_name_dict,day)

  if not ranking_data:
    await interaction.edit_original_response(content = "登録されているユーザーがいません")
    return 
  embed = discord.Embed(
    title = f"🏆 AC fight ランキング [{label}]🏆",
    color = 0xFFD700, 
    timestamp = interaction.created_at
  )
  for data in ranking_data:
    embed.add_field(
      name = f"{data["figure"]}{data["place"]}位 : {data["discord_name"]}",
      value = f"今日のAC数 : **{data["ac"]}** AC  点数 : **{data["point"]}** 点",
      inline = False
    )
  await interaction.edit_original_response(content = None, embed=embed) 




client.run(config.DISCORD_TOKEN)



