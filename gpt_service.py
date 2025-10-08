import os
from openai import OpenAI
from telegram.ext import ContextTypes
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)


def gpt(text, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت مکالمه‌ی متنی با مدل GPT"""

    sysprompt = {
        "role": "system",
        "content": "تو یه دستیار هوش مصنوعی فارسی‌زبان هستی که پیام‌ها رو برای Markdown تلگرام تنظیم می‌کنی."
    }

    if "messages" not in context.user_data:
        context.user_data["messages"] = [sysprompt]

    context.user_data["messages"].append({"role": "user", "content": text})

    completion = client.chat.completions.create(
        model="meta-llama/llama-4-maverick:free",
        messages=context.user_data["messages"]
    )

    response = completion.choices[0].message.content
    context.user_data["messages"].append({"role": "assistant", "content": response})

    return response


def gpt_image(text, image_url, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت مکالمه با ورودی تصویر"""

    if not text:
        text = "این عکس چیه؟"

    sysprompt = {
        "role": "system",
        "content": "تو یه دستیار هوش مصنوعی هستی که متن و تصویر رو تحلیل می‌کنی و خروجی سازگار با Markdown تلگرام می‌دی."
    }

    if "messages" not in context.user_data:
        context.user_data["messages"] = [sysprompt]

    context.user_data["messages"].append({
        "role": "user",
        "content": [
            {"type": "text", "text": text},
            {"type": "image_url", "image_url": {"url": image_url}},
        ]
    })

    completion = client.chat.completions.create(
        model="meta-llama/llama-4-maverick:free",
        messages=context.user_data["messages"]
    )

    response = completion.choices[0].message.content
    context.user_data["messages"].append({"role": "assistant", "content": response})

    return response
