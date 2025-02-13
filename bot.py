import os
import requests
import yt_dlp
import instaloader
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Bot tokenini kiriting
TOKEN = "7793304980:AAGU3XARm9CCz70soQp3cSyynabHS6mc0Uo"

# Admin ID (o'zingizning Telegram ID-ingizni kiriting)
ADMIN_ID = 6588255887

# YouTube yuklash sozlamalari
yt_opts = {
    'format': 'best',
    'outtmpl': '%(title)s.%(ext)s',
}

# Instaloader sozlamalari
loader = instaloader.Instaloader()

# Foydalanuvchilar ro‘yxati (statistika uchun)
users = set()

# 🔹 /start komandasi
async def start(update: Update, context: CallbackContext) -> None:
    users.add(update.message.chat_id)  # Foydalanuvchini bazaga qo‘shish
    await update.message.reply_text("👋 Assalomu alaykum! YouTube yoki Instagram linkini yuboring, men videoni yuklab beraman.")

# 🔹 YouTube video yuklash
async def download_youtube_video(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    chat_id = update.message.chat_id

    try:
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = f"{info['title']}.mp4"

        await context.bot.send_video(chat_id=chat_id, video=open(video_file, 'rb'), caption=f"📥 Video @vide_oyuklabot orqali yuklab olindi: {info['title']}")
        os.remove(video_file)

    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

# 🔹 Instagram video yuklash (login va parolsiz)
async def download_instagram_video(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    chat_id = update.message.chat_id

    try:
        shortcode = url.split("/")[-2]  # Postning shortcode'ini olish
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        if post.video_url:
            response = requests.get(post.video_url)
            video_file = "instagram_video.mp4"

            with open(video_file, 'wb') as file:
                file.write(response.content)

            await context.bot.send_video(chat_id=chat_id, video=open(video_file, 'rb'), caption="📥 Video @vide_oyuklabot orqali yuklab olindi:")
            os.remove(video_file)
        else:
            await update.message.reply_text("❌ Bu postda video mavjud emas.")

    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

# 🔹 Admin uchun reklama yuborish
async def admin_broadcast(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id == ADMIN_ID:
        msg = update.message.text.split(' ', 1)[1]
        for user in users:
            try:
                await context.bot.send_message(chat_id=user, text=f"📢 Reklama: {msg}")
            except:
                continue
        await update.message.reply_text("✅ Reklama barcha foydalanuvchilarga yuborildi.")
    else:
        await update.message.reply_text("❌ Siz admin emassiz!")

# 🔹 Admin uchun statistika
async def get_statistics(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id == ADMIN_ID:
        await update.message.reply_text(f"📊 Bot foydalanuvchilari soni: {len(users)} ta")
    else:
        await update.message.reply_text("❌ Siz admin emassiz!")

# 🔹 Xabarni avtomatik tekshirish
async def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text

    if "youtube.com" in text or "youtu.be" in text:
        await download_youtube_video(update, context)
    elif "instagram.com" in text:
        await download_instagram_video(update, context)
    elif text.startswith("/broadcast"):
        await admin_broadcast(update, context)
    else:
        await update.message.reply_text("📌 Iltimos, YouTube yoki Instagram video linkini yuboring.")

# 🔹 Botni ishga tushirish
def main() -> None:
    app = Application.builder().token(TOKEN).build()

    # Komandalarni qo‘shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("statistika", get_statistics))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == '__main__':
    main()
