import requests
import asyncio
from datetime import datetime, timezone, timedelta

async def count_period_ac(atcoder_name, day):
  time_difference = timezone(timedelta(hours=9))
  now = datetime.now(time_difference)
  today_start = datetime(now.year, now.month, now.day, tzinfo=time_difference)
  start_time = today_start - timedelta(days=day)
  unix_start_time = int(start_time.timestamp())
  unix_end_time = int(today_start.timestamp())

  diff_url = "https://kenkoooo.com/atcoder/resources/problem-models.json"
  diff_response = requests.get(diff_url)
  diff_data = diff_response.json()

  s = set()
  ac_point_sum = 0
  last_submission_id = None
  diff_count = {}
  for i in range(8):
    diff_count[i] = 0
  
  while True:
    url = f"https://kenkoooo.com/atcoder/atcoder-api/v3/user/submissions?user={atcoder_name}&from_second={unix_start_time}"
    if last_submission_id:
      url += f"&from_id={last_submission_id + 1}"
    response = requests.get(url)
    data = response.json()
    if not data:
      break
    for sub in data:
      if sub["epoch_second"] >= unix_end_time:
        continue
      if sub["result"] == "AC":
        problem_id = sub["problem_id"]
        if "ahc" not in problem_id and problem_id not in s:
          s.add(problem_id)
          ac_point_sum += (sub.get("point") or 0)

          problem_diff = diff_data.get(problem_id,{})
          diff_val = problem_diff.get("difficulty")
          if diff_val is not None:
            index = min(7, max(0, diff_val) // 400)
            diff_count[index] += 1
          else:
            diff_count[0] += 1 #難易度がわからんやつは一旦灰diffにしとく
      last_submission_id = sub["id"]
    if len(data) < 500:
      break
    await asyncio.sleep(0.8)
  return {
    "ac_count": len(s),
    "ac_point": int(round(ac_point_sum)),
    "diff": diff_count
  }

async def make_ranking(user_dict, day):
  result = []
  for atcoder_name, discord_name in user_dict.items():
    data = await count_period_ac(atcoder_name, day)
    result.append({"discord_name": discord_name, "data": data})
    await asyncio.sleep(1)
  return sorted(result, key=lambda x: (x["data"]["ac_point"], x["data"]["ac_count"]), reverse=True)

async def get_latest_rating(atcoder_name):
  url = f"https://atcoder.jp/users/{atcoder_name}/history/json"
  response = requests.get(url)
  data = response.json()
  if len(data) == 0:
    return f"{atcoder_name}は存在しません"
  latest_contenst = data[-1]
  latest_rating = latest_contenst["NewRating"]
  return latest_rating