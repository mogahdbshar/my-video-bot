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
    return "⚡ BuzzShorts Engine Supercharged and Ready!"

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
    system_instruction = (
        "أنت مخرج وثائقي محترف وصانع محتوى وثائقي قصير (Shorts). "
        "اكتب سيناريو فيديو شورت قصير جداً ومثير لا يتجاوز 45 ثانية باللغة العربية الفصحى السليمة 100% "
        "وبدون أي كلمات غريبة أو ركيكة. قسم السيناريو إلى لقطات سريعة بالثواني، واكتب نص الراوي العربي، "
        "مع وصف دقيق وشامل للديزاين والمونتاج البصري العمودي لكل لقطة لتبدو احترافية للغاية."
    )
    payload = {
        "messages": [
            {"role": "user", "content": f"{system_instruction}\n\nفكرة الفيديو المطلوبة: {prompt}"}
        ],
        "model": "openai"
    }
    try:
        response = requests.post(POLLINATIONS_TEXT_URL, json=payload, timeout=45)
        if response.status_code == 200:
            return True, response.text
        return False, f"⚠️ خطأ السيرفر المباشر: {response.status_code} - النص المتلقى: {response.text[:200]}"
    except Exception as e:
        return False, f"❌ فشل الاتصال بالشبكة: {str(e)}"

def generate_video_clip(prompt_visual):
    full_prompt = f"{prompt_visual}, cinematic look, 8k resolution, highly detailed, moving elements, 9:16 vertical ratio for shorts, no watermark"
    payload = {"prompt": full_prompt}
    
    # مصفوفة لتخزين سجل تفاصيل الأخطاء الحقيقية لعرضها للمستخدم بدقة
    error_logs = []
    
    for attempt in range(3):
        try:
            # توسيع مهلة الاتصال لـ 180 ثانية (3 دقائق كاملة) لانتظار معالجة السيرفر المفتوح براحة
            response = requests.post(POLLINATIONS_VIDEO_URL, json=payload, timeout=180)
            
            if response.status_code == 200 and response.content:
                return True, response.content
            
            err_msg = f"محاولة {attempt+1}: كود الاستجابة {response.status_code} - نص الرد: {response.text[:150]}"
            error_logs.append(err_msg)
            
            # زيادة فواصل الانتظار لـ 10 ثواني لعدم حرق الطلبات وتهدئة السيرفر المفتوح
            time.sleep(10)
            
        except Exception as e:
            error_logs.append(f"محاولة {attempt+1}: استثناء برميجي (Timeout/Network) -> {str(e)}")
            time.sleep(5)
            
    # إذا فشلت كل المحاولات، يتم دمج وإرجاع الأخطاء الحقيقية بالتفصيل
    return False, "\n".join(error_logs)

def handle_updates():
    offset = 0
    print("البوت الأسطوري المطور والمحدث لحقن وفحص الأخطاء يعمل الآن...")
    
    send_message(MY_CHAT_ID, "🔥 أهلاً بك يا محمد! تم تشغيل البوت بالنظام الأسطوري المطور. قمنا برفع مهلة المعالجة لـ 3 دقائق وتفعيل نظام تتبع وفحص الأخطاء المباشر. أرسل الآن فكرة الشورت للتجربة الحاسمة!")
    
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
                            send_message(chat_id, "أرسل لي فكرة فيديو شورت قصير تريد صياغته فصحى وتوليده.")
                        else:
                            send_message(chat_id, "⏳ جاري هندسة وتوليد سيناريو الشورت عبر محرك النصوص المطور...")
                            
                            success, script_result = generate_text_free(text)
                            
                            if success:
                                keyboard = {
                                    "inline_keyboard": [
                                        [{"text": "🎬 ابدأ التوليد والمونتاج الفوري للديزاين", "callback_data": f"gen_vid_{text[:20]}"}],
                                        [{"text": "✍️ تعديل السيناريو", "callback_data": "edit_script"}]
                                    ]
                                }
                                send_message(chat_id, f"📝 **سيناريو الشورت والديزاين المقترح:**\n\n{script_result}", reply_markup=keyboard)
                            else:
                                send_message(chat_id, f"❌ **خطأ أثناء توليد النص:**\n\n{script_result}")
                            
                    elif "callback_query" in update:
                        cb = update["callback_query"]
                        cb_id = cb["id"]
                        chat_id = str(cb["message"]["chat"]["id"])
                        data = cb["data"]
                        
                        requests.post(API_URL + "answerCallbackQuery", json={"callback_query_id": cb_id})
                        
                        if data.startswith("gen_vid_"):
                            send_message(chat_id, "🚀 جاري الآن توليد ومونتاج المشهد بالمهلة الموسعة الذكية... انتظر ثواني ولا تستعجل.")
                            
                            # استدعاء دالة التوليد الذكية الجديدة التي ترجع حالة النجاح متبوعة بالبيانات أو الأخطاء الحقيقية
                            success_video, result_data = generate_video_clip("Cinematic short video scene, deep ocean secret, detailed view, highly stylized vertical 9:16")
                            
                            if success_video:
                                send_video(chat_id, result_data, "🎬 تم توليد وحقن مقطع الشورت بنجاح وبأعلى دقة بدون أي علامة مائية!")
                            else:
                                # هنا طباعة الأخطاء الحقيقية الصريحة القادمة من السيرفر دون أي رسائل عامة
                                send_message(chat_id, f"❌ **تقرير فشل السيرفر الحقيقي والأخطاء بالتفصيل:**\n\n{result_data}")
                                
                        elif data == "edit_script":
                            send_message(chat_id, "اكتب لي التعديل الذي تريده على السيناريو وسأقوم بتحديثه فوراً.")
                            
        except Exception as e:
            print("Error loop:", e)
            time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=run_web_server, daemon=True).start()
    handle_updates()
