from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
import requests

# Telegram 設定
TOKEN = '7677457994:AAFoQL_-Cvj9Rve_JWIVMQOZgl1BOO3VWis'
CHAT_ID = '6131239576'

# Facebook Cookie
COOKIES = {
    "c_user": "100001475421788",  # 例如：1234567890
    "xs": "2%3AKuJlZ4HTiA6AKQ%3A2%3A1740847129%3A-1%3A11324%3A%3AAcWveBuXP_2YeLXsBETEppIdVRj6tv_04sjKRG_cvVg"           # 例如：abcd:12xy...
}

# 社團網址（請換成你自己的社團）
GROUP_URL = "https://www.facebook.com/groups/236323096475589?locale=zh_TW"

# 要搜尋的關鍵字
KEYWORDS = ["便當", "餐盒", "午餐", "免費", "餐盒", "剩下的"]

# 傳送訊息到 Telegram
def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

# 開始模擬瀏覽器
options = Options()
options.add_argument("--headless")  # 不開視窗 (headless 無頭模式)
options.add_argument("--disable-gpu")  # 停用顯示卡加速
from selenium.webdriver.chrome.service import Service

service = Service("C:/Users/Yunus/Desktop/chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)


# 登入 Facebook
driver.get("https://www.facebook.com/")
for name, value in COOKIES.items():
    driver.add_cookie({"name": name, "value": value, "domain": ".facebook.com"})
driver.get(GROUP_URL)
time.sleep(5)

# 擷取頁面內容並搜尋關鍵字
page = driver.page_source
if any(kw in page for kw in KEYWORDS):
    send_telegram("🍱發現便當！")
    print("✅ 已發出便當通知")
else:
    print("❌ 沒有便當訊息")

driver.quit()
