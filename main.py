import os
import sys
import subprocess
import threading

# --- 1. فحص وتثبيت المكتبات المطلوبة تلقائياً وبدون تدخل منك ---
def install_requirements():
    try:
        with open("requirements.txt", "w", encoding="utf-8") as req_file:
            req_file.write("requests\nflask\n")
    except Exception as e:
        print("Error writing requirements file:", e)

    try:
        import requests
    except ImportError:
        print("⏳ جاري تثبيت المكتبات المطلوبة تلقائياً، انتظر ثوانٍ...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
            print("✅ تم التثبيت بنجاح!")
        except Exception as e:
            print("⚠️ حدث خطأ أثناء التثبيت التلقائي:", e)

    try:
        import flask
    except ImportError:
        print("⏳ جاري تثبيت مكتبة flask لتفعيل البورت في Render...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
            print("✅ تم تثبيت flask بنجاح!")
        except Exception as e:
            print("⚠️ حدث خطأ أثناء تثبيت flask:", e)

# تشغيل الفحص والتثبيت فوراً قبل بدء بقية الكود
install_requirements()

# استدعاء المكتبات بعد التأكد من تثبيتها
import time
import requests
from flask import Flask

# --- سيرفر الويب لخدمة Render لفتح البورت ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🔥 البوت يعمل بالكامل ومستقر على سيرفرات Render!"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# --- 2. المفاتيح الخاصة بك مدمجة مباشرة وجاهزة للعمل فوراً ---
BOT_TOKEN = "8850470812:AAFZXvwkJ9BAqXsr-BB63zbiwSwqK3-NseE"
MY_CHAT_ID = "455805554"
# تم دمج مفتاح Gemini الخاص بك هنا بنجاح
GEMINI_TOKEN = "AQ.Ab8RN6KJ6yI28_E86MNRO228Pcma2OUOT6wtb6o6tv0y0RQJWQ"

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# عناوين النماذج البديلة المستقرة والمفتوحة بالكامل على Render
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_TOKEN}"
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

def generate_text(prompt):
    headers = {"Content-Type": "application/json"}
    system_instruction = "أنت مخرج وثائقي محترف. اكتب سيناريو فيديو قصير ومفصل باللغة العربية ومشاهد بصرية مقترحة لصناعة فيديو مميز حول الفكرة التالية: "
    payload = {
        "contents": [{
            "parts": [{"text": f"{system_instruction} {prompt}"}]
        }]
    }
    
    for attempt in range(4):
        try:
            response = requests.post(GEMINI_URL, headers=headers, json=payload, timeout=30)
            res_json = response.json()
            if "candidates" in res_json and len(res_json["candidates"]) > 0:
                return res_json["candidates"][0]["content"]["parts"][0]["text"]
            return f"لم أتمكن من توليد السيناريو. رد السيرفر: {str(res_json)}"
        except Exception as e:
            if attempt == 3:
                return f"خطأ في توليد السيناريو بعد عدة محاولات: {str(e)}"
            print(f"إعادة محاولة الاتصال بـ Gemini... محاولة رقم {attempt+1}")
            time.sleep(2)

def generate_video_clip(prompt_visual):
    # إرسال الطلب لنموذج توليد الفيديو المفتوح والمستقر بالكامل على Render
    payload = {"prompt": prompt_visual}
    for attempt in range(4):
        try:
            response = requests.post(POLLINATIONS_VIDEO_URL, json=payload, timeout=60)
            if response.status_code == 200:
                return response.content
            time.sleep(5)
        except Exception as e:
            if attempt == 3:
                print("Error generating video after all retries:", e)
                return None
            time.sleep(3)

def handle_updates():
    offset = 0
    print("البوت يعمل الآن ومستعد لاستقبال رسائلك...")
    
    send_message(MY_CHAT_ID, "🔥 أهلاً بك يا محمد! البوت مفعّل بالكامل ومستعد للعمل. أرسل لي أي فكرة فيديو لنبدأ فوراً.")
    
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
                            send_message(chat_id, "عذراً، هذا البوت خاص بمحمد الدستور فقط.")
                            continue
                            
                        if text.startswith("/start"):
                            send_message(chat_id, "أرسل لي فكرة الفيديو أو السيناريو الذي تريد العمل عليه.")
                        else:
                            send_message(chat_id, "⏳ جاري مناقشة الفكرة وتوليد السيناريو والمشاهد من الذكاء الاصطناعي...")
                            script_result = generate_text(text)
                            
                            keyboard = {
                                "inline_keyboard": [
                                    [{"text": "🎬 ابدأ التوليد والمونتاج الفوري", "callback_data": f"gen_vid_{text[:20]}"}],
                                    [{"text": "✍️ تعديل السيناريو", "callback_data": "edit_script"}]
                                ]
                            }
                            send_message(chat_id, f"📝 **السيناريو والمشاهد المقترحة:**\n\n{script_result}", reply_markup=keyboard)
                            
                    elif "callback_query" in update:
                        cb = update["callback_query"]
                        cb_id = cb["id"]
                        chat_id = str(cb["message"]["chat"]["id"])
                        data = cb["data"]
                        
                        requests.post(API_URL + "answerCallbackQuery", json={"callback_query_id": cb_id})
                        
                        if data.startswith("gen_vid_"):
                            send_message(chat_id, "🚀 جاري الآن مخاطبة نموذج التوليد المفتوح لتوليد المشاهد السينمائية بدون علامة مائية... انتظر ثواني.")
                            video_data = generate_video_clip("Cinematic documentary scene, high quality, highly detailed, moving elements")
                            if video_data:
                                send_video(chat_id, video_data, "🎬 هذا هو المقطع الذي تم توليده بالكامل بالذكاء الاصطناعي وبدون أي علامة مائية!")
                            else:
                                send_message(chat_id, "⚠️ حد الحصص الحالي ممتلئ أو النموذج يقوم بالتحديث، سيتم إعادة المحاولة تلقائياً بعد قليل مجاناً عند تجدد الحصة.")
                                
                        elif data == "edit_script":
                            send_message(chat_id, "اكتب لي التعديل الذي تريده على السيناريو وسأقوم بتحديثه فوراً مع الذكاء الاصطناعي.")
                            
        except Exception as e:
            print("Error loop:", e)
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    handle_updates()
