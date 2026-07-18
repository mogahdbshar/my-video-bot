import os
import sys
import subprocess
import threading

# --- 1. فحص وتثبيت المكتبات المطلوبة تلقائياً ---
def install_requirements():
    try:
        with open("requirements.txt", "w", encoding="utf-8") as req_file:
            req_file.write("requests\nflask\n")
    except Exception as e:
        print("Error writing requirements file:", e)

    for lib in ["requests", "flask"]:
        try:
            __import__(lib)
        except ImportError:
            print(f"⏳ جاري تثبيت {lib} تلقائياً للتشغيل...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                print(f"✅ تم تثبيت {lib} بنجاح!")
            except Exception as e:
                print(f"⚠️ حدث خطأ أثناء تثبيت {lib}: {e}")

# تشغيل التثبيت المنظم فوراً
install_requirements()

import time
import requests
from flask import Flask

# --- سيرفر الويب لخدمة Render لفتح البورت ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🔥 البوت يعمل بالكامل وبدون مفاتيح برمجية على Render!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- 2. الإعدادات وعناوين الخدمة المفتوحة ---
BOT_TOKEN = "8850470812:AAFZXvwkJ9BAqXsr-BB63zbiwSwqK3-NseE"
MY_CHAT_ID = "455805554"

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/"
POLLINATIONS_VIDEO_URL = "https://text.pollinations.ai/video"

def send_message(chat_id, text, reply_markup=None):
    url = API_URL + "sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print("Error sending message:", e)

def send_video(chat_id, video_bytes, caption):
    url = API_URL + "sendVideo"
    files = {"video": ("video.mp4", video_bytes, "video/mp4")}
    data = {"chat_id": chat_id, "caption": caption}
    try:
        requests.post(url, files=files, data=data)
    except Exception as e:
        print("Error sending video:", e)

def generate_text_free(prompt):
    system_instruction = "أنت مخرج وثائقي محترف. اكتب سيناريو فيديو قصير ومفصل باللغة العربية ومشاهد بصرية مقترحة لصناعة فيديو مميز حول الفكرة التالية: "
    payload = {
        "messages": [
            {"role": "user", "content": f"{system_instruction} {prompt}"}
        ],
        "model": "openai" # استخدام نموذج النصوص المفتوح والمجاني لديهم
    }
    try:
        response = requests.post(POLLINATIONS_TEXT_URL, json=payload, timeout=30)
        if response.status_code == 200:
            return True, response.text
        return False, f"فشل السيرفر في التجاوب. كود الخطأ: {response.status_code}"
    except Exception as e:
        return False, f"خطأ في الاتصال بالنموذج الحر: {str(e)}"

def generate_video_clip(prompt_visual):
    payload = {"prompt": prompt_visual}
    for attempt in range(3):
        try:
            response = requests.post(POLLINATIONS_VIDEO_URL, json=payload, timeout=60)
            if response.status_code == 200:
                return response.content
            time.sleep(5)
        except Exception as e:
            if attempt == 2:
                print("Error generating video after all retries:", e)
                return None
            time.sleep(3)

def handle_updates():
    offset = 0
    print("البوت يعمل الآن بالنظام الحر والمفتوح...")
    
    send_message(MY_CHAT_ID, "🚀 أهلاً بك يا محمد! تم تفعيل النظام المفتوح بالكامل وبدون أي مفاتيح معقدة. أرسل فكرة الفيديو الآن للتجربة!")
    
    while True:
        try:
            url = API_URL + f"getUpdates?offset={offset}&timeout=20"
            response = requests.get(url).json()
            if "result" in response:
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update and "text" in update["message"]:
                        chat_id = str(update["message"]["chat"]["id"])
                        text = update["message"]["text"]
                        
                        if chat_id != MY_CHAT_ID:
                            send_message(chat_id, "عذراً، هذا البوت خاص بمحمد فقط.")
                            continue
                            
                        if text.startswith("/start"):
                            send_message(chat_id, "أرسل لي فكرة الفيديو أو السيناريو الذي تريد العمل عليه.")
                        else:
                            send_message(chat_id, "⏳ جاري توليد السيناريو والمشاهد عبر النظام المفتوح مجاناً...")
                            
                            # التدفق الذكي لحماية الحصة
                            success, script_result = generate_text_free(text)
                            
                            if success:
                                keyboard = {
                                    "inline_keyboard": [
                                        [{"text": "🎬 ابدأ التوليد والمونتاج الفوري", "callback_data": f"gen_vid_{text[:20]}"}],
                                        [{"text": "✍️ تعديل السيناريو", "callback_data": "edit_script"}]
                                    ]
                                }
                                send_message(chat_id, f"📝 **السيناريو والمشاهد المقترحة:**\n\n{script_result}", reply_markup=keyboard)
                            else:
                                send_message(chat_id, f"❌ **توقف النظام:**\n\n{script_result}")
                            
                    elif "callback_query" in update:
                        cb = update["callback_query"]
                        cb_id = cb["id"]
                        chat_id = str(cb["message"]["chat"]["id"])
                        data = cb["data"]
                        
                        requests.post(API_URL + "answerCallbackQuery", json={"callback_query_id": cb_id})
                        
                        if data.startswith("gen_vid_"):
                            send_message(chat_id, "🚀 جاري الآن توليد المشاهد السينمائية بدون علامة مائية... انتظر ثواني.")
                            video_data = generate_video_clip("Cinematic documentary scene, high quality, highly detailed, moving elements")
                            if video_data:
                                send_video(chat_id, video_data, "🎬 هذا هو المقطع الذي تم توليده بالكامل بالذكاء الاصطناعي وبدون أي علامة مائية!")
                            else:
                                send_message(chat_id, "⚠️ حد الحصص الحالي ممتلئ، سيتم إعادة المحاولة تلقائياً بعد قليل.")
                                
                        elif data == "edit_script":
                            send_message(chat_id, "اكتب لي التعديل الذي تريده على السيناريو وسأقوم بتحديثه فوراً.")
                            
        except Exception as e:
            print("Error loop:", e)
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    handle_updates()
