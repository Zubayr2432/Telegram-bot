import telebot
import os
import time
import requests
from instaloader import Instaloader, Post

TOKEN = "7730701363:AAE4Y94RlZ3AHdzUHG_7hXP4A2hlRny5ns4"
ADMIN_ID = 6588255887  # O'zingizning Telegram ID-ingiz
bot = telebot.TeleBot(TOKEN)
loader = Instaloader()

stats = {"total_downloads": 0}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Assalomu alaykum! Instagram video yuklovchi botga xush kelibsiz!\n\nVideo yuklash uchun Instagram havolasini yuboring.")

@bot.message_handler(commands=['stats'])
def send_stats(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, f"📊 Statistika:\n- Jami yuklangan videolar: {stats['total_downloads']}")
    else:
        bot.send_message(message.chat.id, "⛔ Bu buyruq faqat admin uchun!")

@bot.message_handler(commands=['reklama'])
def send_advertisement(message):
    if message.chat.id == ADMIN_ID:
        bot.send_message(message.chat.id, "📢 Reklama matnini yuboring:")
        bot.register_next_step_handler(message, broadcast_ad)
    else:
        bot.send_message(message.chat.id, "⛔ Bu buyruq faqat admin uchun!")

def broadcast_ad(message):
    ad_text = message.text
    for user_id in stats.get("users", []):
        try:
            bot.send_message(user_id, f"📢 Reklama:\n{ad_text}")
        except:
            continue
    bot.send_message(ADMIN_ID, "✅ Reklama barcha foydalanuvchilarga yuborildi!")

@bot.message_handler(func=lambda message: message.text.startswith("https://www.instagram.com/"))
def download_instagram_video(message):
    url = message.text
    bot.send_message(message.chat.id, "⏳ Videoni yuklab olish jarayoni boshlandi...")
    
    try:
        shortcode = url.split("/")[-2]
        post = Post.from_shortcode(loader.context, shortcode)
        
        video_url = post.video_url
        
        if video_url:
            bot.send_message(message.chat.id, "📥 Video yuklanmoqda...")
            file_name = f"{shortcode}.mp4"
            
            response = requests.get(video_url)
            with open(file_name, "wb") as file:
                file.write(response.content)
                
            with open(file_name, "rb") as video:
                bot.send_video(message.chat.id, video, caption="📌 Video @vide_oyuklabot orqali yuklandi.")
            
            os.remove(file_name)
            stats["total_downloads"] += 1
            bot.send_message(message.chat.id, "✅ Video yuklandi!")
        else:
            bot.send_message(message.chat.id, "❌ Xatolik! Video topilmadi.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Xatolik yuz berdi: {str(e)}")

bot.polling(none_stop=True)
