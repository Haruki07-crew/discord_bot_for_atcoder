import discord 
from discord import app_commands
import config
import atcoder_function
intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

user_name_dist = {}


@client.event
async def on_ready():
  await tree.sync()
  print("bot起動!")

@client.event
async def on_message(message):
  if message.author == client.user:
    return 
  if ":" in message.content:
    sent_message = message.content.split(":")
    atcoder_name, purpose = sent_message
    print(purpose)
    if purpose == "rating":
      result = atcoder_function.get_latest_rating(atcoder_name)
      await message.channel.send(result)
    elif purpose == "AC":
      result = atcoder_function.AC_print(atcoder_name)
      await message.channel.send(result)
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
  user_name_dist[atcoder_name] = discord_name
  await interaction.response.send_message(f"{discord_name}さんを{atcoder_name}で登録しました")
#ユーザー登録の解除
@tree.command(name = "user_unresister", description="登録されているユーザーの登録を解除します")
async def user_unresister(interaction: discord.Interaction, atcoder_name: str):
  if atcoder_name in user_name_dist:
    discor_name = user_name_dist[atcoder_name]
    del user_name_dist[atcoder_name]
    await interaction.response.send_message(f"{discor_name}さんの登録を解除しました")
#登録されているユーザの一覧を表示
@tree.command(name = "user_list", description="登録済みユーザーの一覧を表示します")
async def user_list(interaction: discord.Interaction):
  if user_name_dist:
    for atcoder_name in user_name_dist:
      result = f"{user_name_dist[atcoder_name]}→{atcoder_name}"
      await interaction.response.send_message(result)
  else:
    await interaction.response.send_message("登録されているユーザーがいません")
#ユーザー同士でAC数を比較
@tree.command(name = "ac_fight", description="ユーザー同士でACを比較することができます")
async def ac_fight(interaction: discord.Interaction):
  await interaction.response.send_message("ちょっと待てよ、時間かかるけん")
  result = atcoder_function.AC_fight(user_name_dist)
  if not result:
    await interaction.response.send_message("登録されているユーザーがいません")
    return
  out_response = "🏆 AC fight ランキング🏆\n"

  for i, dist in enumerate(result):
    place = i + 1
    if place == 1:
      figure = "🥇 "
    elif place == 2:
      figure = "🥈 "
    elif place == 3:
      figure = "🥉 "
    else:
      figure = "🫵 "
    award = f"{place}位 {dist["discord_name"]} {dist["ac"]}AC\n"
    tmp_response = figure + award
    out_response += tmp_response
  await interaction.response.send_message(out_response) 


client.run(config.DISCORD_TOKEN)



