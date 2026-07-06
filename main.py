"""
Language Translator Bot - Uses Railway Environment Variables
"""

import os
import sys
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from deep_translator import GoogleTranslator

# ===================== LOGGING =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== TOKEN FROM ENVIRONMENT =====================
# Railway will inject this from Variables tab
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

# If token is not set, use hardcoded one (for testing)
if not TOKEN:
    # ⚠️ REPLACE THIS WITH YOUR TOKEN IF ENV DOESN'T WORK
    TOKEN = "YOUR_BOT_TOKEN_HERE"  
    logger.warning("⚠️ Using hardcoded token. Set TELEGRAM_BOT_TOKEN in Railway variables!")

if TOKEN == "YOUR_BOT_TOKEN_HERE" or not TOKEN:
    logger.error("❌ ERROR: No token found! Add TELEGRAM_BOT_TOKEN to Railway variables")
    logger.error("Or paste your token in the code at line 27")
    sys.exit(1)

logger.info(f"✅ Token loaded successfully")

# ===================== LANGUAGE DATA =====================
LANGUAGES = {
    'en': '🇬🇧 English',
    'es': '🇪🇸 Spanish', 
    'fr': '🇫🇷 French',
    'de': '🇩🇪 German',
    'it': '🇮🇹 Italian',
    'pt': '🇵🇹 Portuguese',
    'ru': '🇷🇺 Russian',
    'ja': '🇯🇵 Japanese',
    'ko': '🇰🇷 Korean',
    'zh-CN': '🇨🇳 Chinese',
    'hi': '🇮🇳 Hindi',
    'ar': '🇸🇦 Arabic',
    'nl': '🇳🇱 Dutch',
    'pl': '🇵🇱 Polish',
    'tr': '🇹🇷 Turkish',
    'vi': '🇻🇳 Vietnamese',
    'th': '🇹🇭 Thai',
    'id': '🇮🇩 Indonesian',
    'ms': '🇲🇾 Malay',
    'sw': '🇰🇪 Swahili',
    'ha': '🇳🇬 Hausa',
    'yo': '🇳🇬 Yoruba',
    'ig': '🇳🇬 Igbo',
}

ALIASES = {
    'chinese': 'zh-CN', 'spanish': 'es', 'french': 'fr',
    'german': 'de', 'italian': 'it', 'portuguese': 'pt',
    'russian': 'ru', 'japanese': 'ja', 'korean': 'ko',
    'hindi': 'hi', 'arabic': 'ar', 'dutch': 'nl',
    'polish': 'pl', 'turkish': 'tr', 'vietnamese': 'vi',
    'thai': 'th', 'indonesian': 'id', 'malay': 'ms',
    'swahili': 'sw', 'hausa': 'ha', 'yoruba': 'yo', 'igbo': 'ig',
}

user_prefs = {}

# ===================== KEYBOARD =====================
def create_language_keyboard():
    keyboard = []
    row = []
    for idx, (code, name) in enumerate(sorted(LANGUAGES.items())):
        if idx % 3 == 0 and idx > 0:
            keyboard.append(row)
            row = []
        display = name.split(' ')[1] if ' ' in name else name[:10]
        row.append(InlineKeyboardButton(
            display[:12], callback_data=f"setlang_{code}"
        ))
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

# ===================== COMMANDS =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    if user_id not in user_prefs:
        user_prefs[user_id] = {'target': 'en'}
    
    welcome = (
        f"👋 *Hello {user.first_name}!*\n\n"
        "🌍 Welcome to *Language Translator Bot*\n\n"
        "📝 *How to use:*\n"
        "• Send any text to translate it\n"
        "• /setlang <code> - Change language\n"
        "• /langs - See all languages\n"
        "• @languagetranslatorbot - Inline mode\n\n"
        "🎯 *Current target:* English\n\n"
        "👉 *Try it now!* Send me any text."
    )
    
    keyboard = [[
        InlineKeyboardButton("🌐 Change Language", callback_data="change_lang"),
        InlineKeyboardButton("❓ Help", callback_data="help")
    ]]
    
    await update.message.reply_text(
        welcome,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🆘 *Commands*\n\n"
        "• /start - Start the bot\n"
        "• /help - Show this help\n"
        "• /setlang <code> - Set language\n"
        "• /langs - List all languages\n"
        "• /about - About this bot\n\n"
        "💡 *Tips:*\n"
        "• Send any message to translate\n"
        "• Use @languagetranslatorbot in any chat\n\n"
        "🌐 *Example:* /setlang es"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about = (
        "🤖 *Language Translator Bot*\n\n"
        "⚡ 20+ languages supported\n"
        "🔍 Auto language detection\n"
        "💬 Inline translation mode\n\n"
        "🛠 *Tech:* Python, Telegram Bot API\n"
        "🚀 Hosted on Railway\n\n"
        "❤️ Made with love"
    )
    await update.message.reply_text(about, parse_mode='Markdown')

async def list_languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_list = "\n".join([f"• `{code}` - {name}" for code, name in LANGUAGES.items()])
    message = (
        "🌍 *Supported Languages*\n\n"
        f"{lang_list}\n\n"
        "📌 Use /setlang <code> to change"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "🌐 *Select your target language:*",
            reply_markup=create_language_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    lang_input = context.args[0].lower()
    lang_code = ALIASES.get(lang_input, lang_input)
    
    if lang_code in LANGUAGES:
        if user_id not in user_prefs:
            user_prefs[user_id] = {}
        user_prefs[user_id]['target'] = lang_code
        
        await update.message.reply_text(
            f"✅ *Language set to:* {LANGUAGES[lang_code]}\n\n"
            "Send any text to translate!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *'{lang_input}' not found*\n\nUse /langs to see all languages.",
            parse_mode='Markdown'
        )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if context.args and update.message.text.startswith('/translate'):
        text = ' '.join(context.args)
    else:
        text = update.message.text or ""
    
    if not text or len(text.strip()) == 0:
        await update.message.reply_text("Please send me some text to translate.")
        return
    
    target = user_prefs.get(user_id, {}).get('target', 'en')
    
    try:
        await update.message.chat.send_action(action="typing")
        translator = GoogleTranslator(source='auto', target=target)
        translated = translator.translate(text)
        
        response = (
            f"🔄 *Translation*\n\n"
            f"📝 *Original:*\n{text}\n\n"
            f"🌐 *Translated ({LANGUAGES.get(target, 'English')}):*\n{translated}"
        )
        
        keyboard = [[InlineKeyboardButton("🌐 Change Language", callback_data="change_lang")]]
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "❌ *Translation failed!*\n\nPlease try again.",
            parse_mode='Markdown'
        )

async def inline_translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query or len(query.strip()) == 0:
        return
    
    try:
        translator = GoogleTranslator(source='auto', target='en')
        translated = translator.translate(query)
        
        from telegram import InlineQueryResultArticle, InputTextMessageContent
        
        result = InlineQueryResultArticle(
            id="1",
            title=f"🌐 {translated[:50]}...",
            description=f"Original: {query[:50]}",
            input_message_content=InputTextMessageContent(
                f"🌐 *Translation*\n\n"
                f"📝 *Original:*\n{query}\n\n"
                f"🔄 *Translated:*\n{translated}",
                parse_mode='Markdown'
            )
        )
        await update.inline_query.answer([result], cache_time=300)
    except Exception as e:
        logger.error(f"Inline error: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "change_lang":
        await query.edit_message_text(
            "🌐 *Select your target language:*",
            reply_markup=create_language_keyboard(),
            parse_mode='Markdown'
        )
    elif query.data == "help":
        await query.edit_message_text(
            "🆘 *Quick Help*\n\n"
            "Send text → translate\n"
            "/setlang <code> → change language\n"
            "/langs → see all languages",
            parse_mode='Markdown'
        )
    elif query.data.startswith("setlang_"):
        lang_code = query.data.replace("setlang_", "")
        if lang_code in LANGUAGES:
            if user_id not in user_prefs:
                user_prefs[user_id] = {}
            user_prefs[user_id]['target'] = lang_code
            await query.edit_message_text(
                f"✅ *Language set to:* {LANGUAGES[lang_code]}\n\n"
                "Send any text to translate!",
                parse_mode='Markdown'
            )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")

# ===================== MAIN =====================
def main():
    logger.info("🚀 Starting Language Translator Bot...")
    
    try:
        application = Application.builder().token(TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("langs", list_languages))
        application.add_handler(CommandHandler("setlang", set_language))
        application.add_handler(CommandHandler("translate", translate_text))
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.INLINE_QUERY,
            translate_text
        ))
        application.add_handler(MessageHandler(filters.INLINE_QUERY, inline_translate))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_error_handler(error_handler)
        
        logger.info("✅ Bot is running and listening for messages...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
