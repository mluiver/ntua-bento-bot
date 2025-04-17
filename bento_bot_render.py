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
        send_telegram("這是測試內容（以後會改成自動抓的）")
        print("✅ 發現便當關鍵字，已發送通知")
    else:
        print("❌ 沒有便當關鍵字")


def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'Markdown'  # 支援格式美化
    }
    requests.post(url, data=data)

def format_message(summary):
    now = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
    return (
        f"🍱 *便當警報！*\n\n"
        f"在 Facebook 社團中發現貼文包含便當相關字詞！\n\n"
        f"🕒 檢查時間：`{now}`\n"
        f"📝 摘要：{summary}\n\n"
        f"[👉 前往社團查看貼文]({GROUP_URL})"

if __name__ == "__main__":
    check_facebook_group()

if __name__ == "__main__":
    summary = "這是一則測試通知。今天有*免費便當*可以吃！"
    message = format_message(summary)
    send_telegram(message)
