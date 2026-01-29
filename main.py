import pysrt
import requests
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ===== TOKENS =====
GEMINI_API_KEY = "AIzaSyDQltNUp1HN8WQ3yVIRmmNNUHTRNLf5z9Y"
TELEGRAM_BOT_TOKEN = "8314365372:AAFp5ojNibetOFQO79Hd4Ko3IuKYQOBadfc"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

PROMPT_TEMPLATE = """
You are a professional subtitle translator for Indian audience.

Translate into natural Hinglish (Hindi written in English + simple English).

Rules:
- Short, subtitle-friendly
- Casual Hinglish
- Not formal Hindi
- Keep emotion and meaning
- No extra explanation

Subtitle:
{text}
"""

def translate_text(text):
    prompt = PROMPT_TEMPLATE.format(text=text)

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    r = requests.post(GEMINI_URL, json=data)
    r.raise_for_status()
    result = r.json()

    return result["candidates"][0]["content"]["parts"][0]["text"].strip()

def translate_srt_file(input_path, output_path):
    subs = pysrt.open(input_path, encoding='utf-8')

    for i, sub in enumerate(subs):
        print(f"Translating {i+1}/{len(subs)}")
        try:
            translated = translate_text(sub.text)
            sub.text = translated
            time.sleep(1)  # rate limit safe
        except Exception as e:
            print("Error:", e)

    subs.save(output_path, encoding='utf-8')

# ===== TELEGRAM HANDLERS =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! SRT file bhejo, main usko Hinglish me translate karke wapas de dunga 🔥 (Gemini Powered)"
    )

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document

    if not doc.file_name.endswith(".srt"):
        await update.message.reply_text("Sirf .srt file bhejo bhai 🙏")
        return

    file = await doc.get_file()
    input_path = f"input_{doc.file_name}"
    output_path = f"hinglish_{doc.file_name}"

    await file.download_to_drive(input_path)
    await update.message.reply_text("Gemini translate kar raha hai... wait karo ⏳")

    try:
        translate_srt_file(input_path, output_path)
        await update.message.reply_document(document=open(output_path, "rb"))
    except Exception as e:
        await update.message.reply_text(f"Error aaya: {e}")

# ===== MAIN =====

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("Gemini SRT Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()
