import os
import json
import requests
from typing import Optional, Dict, Any


class NotificationService:
    @staticmethod
    def send_telegram_alert(session_id: str, user_input: str, assistant_response: str) -> bool:
        token = os.getenv("TELEGRAM_ALERT_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_ALERT_CHAT_ID") or os.getenv("TELEGRAM_CHAT_ID")

        if not token or not chat_id:
            print("[NOTIFICATION_SERVICE WARNING] Telegram token or chat_id missing. Alert skipped.")
            return False

        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            escaped_input = user_input.replace("<", "&lt;").replace(">", "&gt;")[:800]
            escaped_reply = assistant_response.replace("<", "&lt;").replace(">", "&gt;")[:800]

            text = (
                f"🚨 <b>EVERY CHAT ALERT</b>\n\n"
                f"<b>Session ID:</b> <code>{session_id}</code>\n"
                f"<b>User Input:</b>\n{escaped_input}\n\n"
                f"<b>AI Assistant Response:</b>\n{escaped_reply}"
            )

            res = requests.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            }, timeout=10)

            if res.status_code == 200:
                print(f"[NOTIFICATION_SERVICE] Alert sent to Telegram for session {session_id}.")
                return True
            else:
                print(f"[NOTIFICATION_SERVICE ERROR] HTTP {res.status_code}: {res.text}")
                return False
        except Exception as e:
            print(f"[NOTIFICATION_SERVICE EXCEPTION] Failed to send Telegram alert: {e}")
            return False
