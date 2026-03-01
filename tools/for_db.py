import sqlite3
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
    user_dict = {}
    for data in cursor.fetchall():
      atcoder_name = data[0]
      discord_name = data[1]
      user_dict[atcoder_name] = discord_name
    return user_dict
  
def user_resister(atcoder_name, discord_name):
  with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO users (atcoder_name, discord_name) VALUES (?, ?)", (atcoder_name, discord_name))
    conn.commit()

def user_unresister(atcoder_name):
  with sqlite3.connect(DB_FILE) as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE atcoder_name = ?", (atcoder_name,))
    success = cursor.rowcount > 0
    conn.commit()
    return success
  