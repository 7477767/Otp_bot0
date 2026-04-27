import requests
import time
import json
import re
import os

# =========================
# 🔐 API SETTINGS
# =========================
API_URL = "http://51.77.216.195/crapi/lamix/viewstats"
TOKEN = "QlFYRElXQkU0blFEWoNkVYOMlmiHaJmIQ1aIWmeAU2lghYdoRneLdXg="

# =========================
# 🤖 TELEGRAM SETTINGS
# =========================
BOT_TOKEN = "8263307601:AAF0-Y8YZxIMqfEpL4oVdjFsW7eoZukXxng"
CHAT_ID = -1003530245573

# =========================
# 📁 STORAGE FILE
# =========================
FILE = "sent.txt"

# Load old messages
if os.path.exists(FILE):
    with open(FILE, "r") as f:
        sent_messages = set(f.read().splitlines())
else:
    sent_messages = set()

def save_message(uid):
    with open(FILE, "a") as f:
        f.write(uid + "\n")

# =========================
# 📱 MASK NUMBER
# =========================
def mask_number(num):
    if num and len(num) >= 8:
        return num[:4] + "XXXX" + num[-4:]
    return num

# =========================
# 📤 SEND MESSAGE
# =========================
def send(msg, number):
    try:
        otp = re.findall(r"\d{4,6}", msg)
        otp_text = otp[0] if otp else "N/A"

        masked = mask_number(number)

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        text = f"""
📩 <b>NEW OTP</b>

📱 Number: <b>{masked}</b>

🔐 OTP:
<code>{otp_text}</code>
"""

        buttons = {
            "inline_keyboard": [
                [
                    {"text": "📋 Copy OTP", "callback_data": f"copy_{otp_text}"}
                ],
                [
                    {"text": "📢 CHANNEL", "url": "https://t.me/yourchannel"},
                    {"text": "🌐 PANEL", "url": "https://yourpanel.com"}
                ]
            ]
        }

        data = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "reply_markup": json.dumps(buttons)
        }

        requests.post(url, data=data, timeout=10)

    except Exception as e:
        print("Send Error:", e)

# =========================
# 🔘 HANDLE CALLBACK
# =========================
last_update_id = 0

def handle_callbacks():
    global last_update_id

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        params = {"offset": last_update_id + 1, "timeout": 5}

        res = requests.get(url, params=params, timeout=10).json()

        for update in res.get("result", []):
            last_update_id = update["update_id"]

            if "callback_query" in update:
                query = update["callback_query"]
                data = query["data"]
                chat_id = query["message"]["chat"]["id"]

                if data.startswith("copy_"):
                    otp = data.replace("copy_", "")

                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        data={"chat_id": chat_id, "text": otp},
                        timeout=10
                    )

    except Exception as e:
        print("Callback Error:", e)

# =========================
# 🔄 MAIN LOOP
# =========================
while True:
    try:
        params = {
            "token": TOKEN,
            "records": 10
        }

        res = requests.get(API_URL, params=params, timeout=10)
        result = res.json()

        if result.get("status") == "success":
            for sms in result["data"]:
                msg = sms.get("msg")
                number = sms.get("num")
                dt = sms.get("dt")

                unique_id = f"{dt}_{msg}_{number}"

                if unique_id not in sent_messages:
                    send(msg, number)
                    sent_messages.add(unique_id)
                    save_message(unique_id)

        handle_callbacks()

    except Exception as e:
        print("Main Error:", e)

    time.sleep(5)
