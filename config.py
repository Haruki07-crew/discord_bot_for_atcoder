from dotenv import load_dotenv
#同じディレクトリの.envファイルを読み込み
load_dotenv()
import os
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
ADMIN_ID = os.getenv("ADMIN_ID")