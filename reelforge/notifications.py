import logging
import os
import requests
from reelforge.config import settings

logger = logging.getLogger("ReelForge.Notifications")

class NotificationManager:
    """
    Sends automated SMS / WhatsApp / Telegram notifications to the user upon Reel upload.
    Target Phone: 9550869459 (+91 9550869459)
    """

    def __init__(self):
        self.target_phone = os.getenv("NOTIFICATION_PHONE_NUMBER", "9550869459")

    def send_upload_notification(self, topic_title: str, reel_url: str, media_id: str = ""):
        msg = f"🚀 ReelForge AI Alert!\n\nReel published live to @flow.tech.0306!\n📌 Topic: {topic_title}\n🔗 Link: {reel_url}\n🆔 ID: {media_id}"
        
        logger.info(f"[NotificationManager] Sending Reel upload alert for '{topic_title}' to phone {self.target_phone}...")

        # 1. Twilio SMS (if credentials present)
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_from = os.getenv("TWILIO_PHONE_NUMBER")

        if twilio_sid and twilio_token and twilio_from:
            try:
                phone_formatted = self.target_phone if self.target_phone.startswith("+") else f"+91{self.target_phone}"
                url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
                res = requests.post(url, data={
                    "To": phone_formatted,
                    "From": twilio_from,
                    "Body": msg
                }, auth=(twilio_sid, twilio_token), timeout=10)
                if res.status_code in (200, 201):
                    logger.info(f"SMS notification sent successfully via Twilio to {phone_formatted}!")
            except Exception as e:
                logger.error(f"Twilio SMS delivery failed: {str(e)}")

        # 2. Fast2SMS / Indian SMS API (if API key present)
        fast2sms_key = os.getenv("FAST2SMS_API_KEY")
        if fast2sms_key:
            try:
                url = "https://www.fast2sms.com/dev/bulkV2"
                payload = {
                    "route": "q",
                    "message": f"Reel published to @flow.tech.0306: {topic_title} - {reel_url}",
                    "language": "english",
                    "flash": 0,
                    "numbers": self.target_phone
                }
                headers = {"authorization": fast2sms_key}
                requests.post(url, data=payload, headers=headers, timeout=10)
                logger.info(f"Fast2SMS alert sent to {self.target_phone}!")
            except Exception as e:
                logger.error(f"Fast2SMS delivery error: {str(e)}")

        # 3. CallMeBot Free WhatsApp API (if enabled)
        callmebot_apikey = os.getenv("CALLMEBOT_API_KEY")
        if callmebot_apikey:
            try:
                wa_url = f"https://api.callmebot.com/whatsapp.php?phone=+91{self.target_phone}&text={requests.utils.quote(msg)}&apikey={callmebot_apikey}"
                requests.get(wa_url, timeout=10)
                logger.info(f"WhatsApp notification sent to {self.target_phone}!")
            except Exception as e:
                logger.error(f"WhatsApp delivery error: {str(e)}")

        # 4. Telegram Bot (if bot token & chat id present)
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if telegram_token and telegram_chat_id:
            try:
                tg_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                requests.post(tg_url, data={"chat_id": telegram_chat_id, "text": msg}, timeout=10)
                logger.info(f"Telegram notification sent successfully!")
            except Exception as e:
                logger.error(f"Telegram alert error: {str(e)}")

        logger.info(f"Notification log recorded for target {self.target_phone}.")
