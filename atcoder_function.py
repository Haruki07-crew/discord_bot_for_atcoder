import requests
from datetime import datetime, timezone, timedelta
import time

#現在のレートを取得
def get_latest_rating(atcoder_name):
  url = f"https://atcoder.jp/users/{atcoder_name}/history/json"
  response = requests.get(url)
  data = response.json()
  if len(data) == 0:
    return f"{atcoder_name}は存在しません"
  latest_contenst = data[-1]
  latest_rating = latest_contenst["NewRating"]
  return f"{atcoder_name}の現在のレートは{latest_rating}です"

#出力用にfstringしないバージョン
def get_latest_rating_nofstring(atcoder_name):
  url = f"https://atcoder.jp/users/{atcoder_name}/history/json"
  response = requests.get(url)
  data = response.json()
  if len(data) == 0:
    return f"{atcoder_name}は存在しません"
  latest_contenst = data[-1]
  latest_rating = latest_contenst["NewRating"]
  return latest_rating
#これまでのAC数を取得
def get_ac_count(atcoder_name):
  url_ac_sum = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/ac_rank?user={atcoder_name}"
  response_ac_sum = requests.get(url_ac_sum)
  data_ac_sum = response_ac_sum.json()
  ac_sum = data_ac_sum["count"]
  return ac_sum

#今日のAC数を取得
def count_period_ac(atcoder_name, day):
  time_difference = timezone(timedelta(hours=9))
  now = datetime.now(time_difference)
  if day == 1:
    start_time = datetime(now.year, now.month, now.day, tzinfo=time_difference)
  else:
    start_time = datetime(now.year, now.month, now.day, tzinfo=time_difference) - timedelta(days=day)
  unix_time = int(start_time.timestamp())
  url= f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={atcoder_name}&from_second={unix_time}"
  response = requests.get(url)
  data = response.json()
  s = set()
  ac_point_sum = 0
  for submission in data:
    if submission["result"] == "AC":
      s.add(submission["id"])
      ac_point_sum += submission["point"]
  return [len(s), ac_point_sum]

#これまで・今日のAC数をまとめて返す
def AC_print(atcoder_name):
  ac_sum = get_ac_count(atcoder_name)
  daily_ac_sum, daily_ac_point_sum = count_period_ac(atcoder_name,1)
  if daily_ac_sum == 0:
    result = f"{atcoder_name}さんの今までのAC数は{ac_sum}\n今日のAC数は{daily_ac_sum}です。精進せんかい"
  else:
    result = f"{atcoder_name}さんの今までのAC数は{ac_sum}\n今日のAC数は{daily_ac_sum}で{daily_ac_point_sum}点取得しました"
  return result

#登録されたユーザー間で期間を指定してのAC数の比較
def AC_fight(user_name_dict, day):
  result = []
  for atcoder_name, discord_name in user_name_dict.items():
    time.sleep(1)
    ac_count = count_period_ac(atcoder_name, day)
    result.append({"discord_name":discord_name, "ac": ac_count})
  sorted_result = sorted(result, key = lambda x: (x["ac"][0], x["ac"][1]), reverse=True)
  return sorted_result


#AC数からランキング作成
def make_ranking(user_name_dict, day):
  result = AC_fight(user_name_dict, day)
  if not result:
    return []
  ranking = []
  cur_place = 0
  prev_ac = -1
  for i, d in enumerate(result):
    ac_num = d["ac"][0]
    ac_point = d["ac"][1]
    if ac_num != prev_ac:
      cur_place = i + 1
    if cur_place == 1:
      figure = " 🥇 "
    elif cur_place == 2:
      figure = " 🥈 "
    elif cur_place == 3:
      figure = " 🥉 "
    else:
      figure = " 👤 "
    ranking.append({
      "place" : cur_place,
      "figure" : figure,
      "discord_name" : d["discord_name"],
      "ac" : ac_num,
      "point" : ac_point
    })
    prev_ac = ac_num
  return ranking