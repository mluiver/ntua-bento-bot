import datetime

# 台灣時間 = UTC+8
now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
current_hour = now.hour
current_minute = now.minute

# 只允許在每天 10:30 - 23:30 之間執行（台灣時間）
start_minutes = 10 * 60 + 30   # 10:30
end_minutes = 23 * 60 + 30     # 23:30
now_minutes = current_hour * 60 + current_minute

if now_minutes < start_minutes or now_minutes > end_minutes:
    print(f"⏰ 跳過：現在是 {now.strftime('%H:%M')}（台灣時間），不在執行時段內。")
    exit(0)

import subprocess
import sys

# 自動安裝 requests
try:
    import requests
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

import requests
import time

# ====== Telegram設定基本設定 ======
TOKEN = '7677457994:AAFoQL_-Cvj9Rve_JWIVMQOZgl1BOO3VWis'
CHAT_ID = '6131239576'
# 社團網址
GROUP_URL = "https://www.facebook.com/groups/236323096475589?locale=zh_TW"
# 要搜尋的關鍵字
KEYWORDS = ["便當", "餐盒", "午餐", "免費", "餐盒", "剩下的"]

# ====== Facebook Cookie ======
COOKIES = {
    "c_user": "100001475421788",
    "xs": "2%3AKuJlZ4HTiA6AKQ%3A2%3A1740847129%3A-1%3A11324%3A%3AAcWveBuXP_2YeLXsBETEppIdVRj6tv_04sjKRG_cvVg"
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
}

# ====== 主要程式邏輯 ======

def check_facebook_group():
    response = requests.get(GROUP_URL, cookies=COOKIES, headers=HEADERS)
    page = response.text

    if any(keyword in page for keyword in KEYWORDS):
        send_telegram("發現便當貼文！快去搶🍱")
        print("✅ 發現便當關鍵字，已發送通知")
    else:
        print("❌ 沒有便當關鍵字")

def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=data)

if __name__ == "__main__":
    check_facebook_group()
