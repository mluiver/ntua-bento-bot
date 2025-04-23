import subprocess
import sys
import datetime
import requests

# 自動安裝 BeautifulSoup
try:
    from bs4 import BeautifulSoup
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    from bs4 import BeautifulSoup


# ====== Telegram設定 ======
TELEGRAM_TOKEN = '7677457994:AAFoQL_-Cvj9Rve_JWIVMQOZgl1BOO3VWis'
TELEGRAM_CHAT_ID = '6131239576'
GROUP_URL = "https://www.facebook.com/groups/236323096475589?locale=zh_TW"
KEYWORDS = ["便當", "餐盒", "午餐", "免費", "剩下的"]

# ====== Facebook Cookie ======
COOKIES = {
    "c_user": "100001475421788",
    "xs": "2%3AKuJlZ4HTiA6AKQ%3A2%3A1740847129%3A-1%3A11324%3A%3AAcWrhXXgfwpX5UdyQC6807XIicBPUGuheFARS5zcLA1L"
}
HEADERS = {
    'User-Agent': 'Mozilla/5.0',
}

# ====== 時間判斷（台灣時間 UTC+8）=====
now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
current_hour = now.hour
current_minute = now.minute
now_minutes = current_hour * 60 + current_minute
start_minutes = 10 * 60 + 30
end_minutes = 23 * 60 + 30

if now_minutes < start_minutes or now_minutes > end_minutes:
    print(f"⏰ 跳過：現在是 {now.strftime('%H:%M')}（台灣時間），不在執行時段內。")
    exit(0)

# ====== 功能函式區 ======
def format_message(summary, post_url):
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    now_str = now.strftime("%Y/%m/%d %H:%M")
    return (
        f"🍱 <b>便當警報！</b>\n\n"
        f"在 Facebook 社團中發現貼文包含便當相關字詞！\n\n"
        f"🕒 檢查時間：<code>{now_str}</code>\n"
        f"📝 摘要：{summary}\n\n"
        f'<a href="{post_url}">👉 點我查看貼文</a>'
    )
def send_telegram(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'HTML' 
    }
    response = requests.post(url, data=data)

    print("📤 發送中...")
    print("狀態碼：", response.status_code)
    print("回應內容：", response.text)

def extract_summary(html):
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text()
        if any(kw in text for kw in KEYWORDS):
            return text
    return "（無法擷取貼文內容，但偵測到關鍵字）"
def get_recent_post_urls(html, limit=20):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', href=True)
    post_urls = []
    for link in links:
        href = link['href']
        if '/groups/' in href and '/posts/' in href:
            post_url = "https://www.facebook.com" + href.split('?')[0]
            if post_url not in post_urls:
                post_urls.append(post_url)
        if len(post_urls) >= limit:
            break
    return post_urls
def is_login_page(html):
    start = html.find("<title>")
    end = html.find("</title>")
    if start != -1 and end != -1:
        title_text = html[start+7:end].strip().lower()
        print("📄 偵測到頁面標題：", title_text)
        return any(kw in title_text for kw in [
            "facebook – log in", "登入 facebook", "登錄", "login"
        ])
    return False
def load_fail_count():
    try:
        with open("fail_count.txt", "r") as f:
            return int(f.read())
    except:
        return 0

def save_fail_count(count):
    with open("fail_count.txt", "w") as f:
        f.write(str(count))

def check_facebook_group():
    response = requests.get(GROUP_URL, cookies=COOKIES, headers=HEADERS)
    page = response.text

    print("🔍 嘗試解析頁面 <title> ...")
    start = page.find("<title>")
    end = page.find("</title>")
    if start != -1 and end != -1:
        print("📄 頁面標題：", page[start+7:end].strip())
    else:
        print("⚠️ 無法找到 <title>，可能頁面載入失敗。")

    # === 檢查是否登入頁 ===
    if is_login_page(page):
        fail_count = load_fail_count() + 1
        save_fail_count(fail_count)

        if fail_count >= 3:
            now_str = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
            now_str = now_str.strftime("%Y/%m/%d %H:%M")
            message = (
                f"⚠️ *警告：Facebook Cookie 可能已過期！*\n"
                f"請重新抓取新的 c_user 與 xs。\n\n"
                f"📅 最後檢查時間：{now_str}\n"
                f"🔁 連續失敗次數：{fail_count}"
            )
            send_telegram(message)
            print("⚠️ 偵測登入頁面，已發送 Cookie 過期通知")
        else:
            print(f"⚠️ 第 {fail_count} 次偵測到登入頁面，暫不發送通知")
        return
    else:
        save_fail_count(0)

        # ✅ 額外印出整體頁面關鍵字偵測（只顯示，不發通知）
        if any(kw in page for kw in KEYWORDS):
            print("🧐 本頁面中發現關鍵字（但尚未進入單篇貼文分析）")
        else:
            print("📭 本頁面中沒有發現任何關鍵字")

        # ✅ 讀取已通知過的貼文清單
        try:
            with open("notified_urls.txt", "r") as f:
                notified_urls = set(line.strip() for line in f.readlines())
        except:
            notified_urls = set()

        # ✅ 抓取最新貼文網址（擴增為 10 篇）
        recent_urls = get_recent_post_urls(page, limit=10)

        for post_url in recent_urls:
            if post_url in notified_urls:
                continue

            try:
                post_page = requests.get(post_url, cookies=COOKIES, headers=HEADERS).text
                summary = extract_summary(post_page)
            except Exception as e:
                print("❌ 抓取貼文失敗：", post_url, "錯誤：", e)
                continue

            if any(kw in summary for kw in KEYWORDS):
                msg = format_message(summary, post_url)
                send_telegram(msg)
                print("✅ 發現便當貼文，已通知：", post_url)

                with open("notified_urls.txt", "a") as f:
                    f.write(post_url + "\n")
# ====== 主程式入口點 ======
IS_TEST_MODE = False  # 若想測試通知請改成 True，否則請改成 False

if __name__ == "__main__":
    if IS_TEST_MODE:
        test_summary = "這是一則測試訊息：今天有免費便當在7-11前面！"
        test_post_url = "https://www.facebook.com/groups/236323096475589"
        msg = format_message(test_summary, test_post_url)
        send_telegram(msg)
        print("✅ 測試通知已發送")
    else:
        check_facebook_group()
