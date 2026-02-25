import discord 
from discord import app_commands
import config
import atcoder_function
# 全ての情報を受け取る設定(サーバ情報、メンバー情報etc..)
intents = discord.Intents.all()
# clientはbot全体のオブジェクト(イベント(入室、メッセージの受信)の検知、メッセージの送信)
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
# asyncは非同期型 別の処理の完了を待たずに別の処理をする
@client.event
async def on_ready():
  await tree.sync()
  print("bot起動!")
  
# message はdiscordで送信されたメッセージの情報を全て含んだオブジェクト
user_name_dist={}

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



client.run(config.DISCORD_TOKEN)