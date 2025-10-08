import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from gpt_service import gpt, gpt_image

# بارگذاری متغیرهای محیطی
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع ربات"""
    await update.message.reply_text(
        f"درود {update.effective_user.first_name} 🌸\n"
        f"به ربات ChatGPT خوش اومدی!\n"
        f"برای شروع مکالمه‌ی جدید از دستور /new_chat استفاده کن."
    )


async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شروع مکالمه جدید"""
    context.user_data.clear()
    await update.message.reply_text("🆕 مکالمه‌ی جدید آغاز شد، از اینجا بنویس 👇🏻")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پاسخ به پیام متنی"""
    text = update.message.text
    timer = await update.message.reply_text("⌛️ در حال فکر کردن...")

    answer = gpt(text, context)
    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=timer.message_id,
        text=answer,
        parse_mode="Markdown"
    )


async def pic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """پردازش عکس"""
    pic = update.message.photo[-1]
    caption = update.message.caption

    try:
        file = await context.bot.get_file(pic.file_id)
        image_url = file.file_path

        timer = await update.message.reply_text("⌛️ در حال بررسی تصویر...")

        answer = gpt_image(caption, image_url, context)
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=timer.message_id,
            text=answer,
            parse_mode="Markdown"
        )
    except Exception:
        await update.message.reply_text("❌ خطا: مطمئن شو حجم عکس کمتر از ۲۰ مگابایت باشه.")


if __name__ == "__main__":
    print("🚀 Bot is starting...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("new_chat", new_chat))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))
    app.add_handler(MessageHandler(filters.PHOTO, pic_handler))

    print("✅ Bot is polling...")
    app.run_polling()
