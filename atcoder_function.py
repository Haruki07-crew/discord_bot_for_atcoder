import requests
from datetime import datetime, timezone, timedelta

def get_latest_rating(atcoder_name):
  url = f"https://atcoder.jp/users/{atcoder_name}/history/json"
  response = requests.get(url)
  data = response.json()
  if len(data) == 0:
    return f"{atcoder_name}は存在しません"
  latest_contenst = data[-1]
  latest_rating = latest_contenst["NewRating"]
  return f"{atcoder_name}の現在のレートは{latest_rating}です"

def get_ac_count(atcoder_name):
  url_ac_sum = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/ac_rank?user={atcoder_name}"
  response_ac_sum = requests.get(url_ac_sum)
  data_ac_sum = response_ac_sum.json()
  ac_sum = data_ac_sum["count"]
  return ac_sum

def count_today_ac(atcoder_name):
  time_difference = timezone(timedelta(hours=9))
  now = datetime.now(time_difference)
  today_start = datetime(now.year, now.month, now.day, tzinfo=time_difference)
  unix_time = (int)(today_start.timestamp())
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
def AC_print(atcoder_name):
  ac_sum = get_ac_count(atcoder_name)
  daily_ac_sum, daily_ac_point_sum = count_today_ac(atcoder_name)
  if daily_ac_sum == 0:
    result = f"{atcoder_name}さんの今までのAC数は{ac_sum}\n今日のAC数は{daily_ac_sum}です。精進しましょう"
  else:
    result = f"{atcoder_name}さんの今までのAC数は{ac_sum}\n今日のAC数は{daily_ac_sum}で{daily_ac_point_sum}点取得しました"
  return result