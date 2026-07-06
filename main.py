"""
Language Translator Bot - Fixed for Railway Deployment
"""

import os
import sys
import logging
from typing import Dict, Optional
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

# ===================== CONFIGURATION =====================

# Environment variables with better error handling
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    print("❌ ERROR: TELEGRAM_BOT_TOKEN environment variable not set!")
    print("Please set it in Railway: Variables → TELEGRAM_BOT_TOKEN")
    sys.exit(1)

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

# Language aliases for easier use
ALIASES = {
    'chinese': 'zh-CN',
    'spanish': 'es',
    'french': 'fr',
    'german': 'de',
    'italian': 'it',
    'portuguese': 'pt',
    'russian': 'ru',
    'japanese': 'ja',
    'korean': 'ko',
    'hindi': 'hi',
    'arabic': 'ar',
    'dutch': 'nl',
    'polish': 'pl',
    'turkish': 'tr',
    'vietnamese': 'vi',
    'thai': 'th',
    'indonesian': 'id',
    'malay': 'ms',
    'swahili': 'sw',
    'hausa': 'ha',
    'yoruba': 'yo',
    'igbo': 'ig',
}

# User preferences storage
user_prefs: Dict[int, Dict[str, str]] = {}

# ===================== BOT HANDLERS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    user_id = user.id
    
    # Initialize user preferences
    if user_id not in user_prefs:
        user_prefs[user_id] = {'target': 'en'}
    
    welcome = (
        f"👋 *Hello {user.first_name}!*\n\n"
        "🌍 Welcome to *Language Translator Bot*\n"
        "I can translate text between 20+ languages instantly!\n\n"
        "📝 *How to use:*\n"
        "• Send any text to translate it\n"
        "• Use /setlang to change target language\n"
        "• Use /langs to see all languages\n"
        "• Use @languagetranslatorbot in any chat\n\n"
        f"🎯 *Current target:* {LANGUAGES.get('en', 'English')}\n\n"
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

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = (
        "🆘 *Available Commands*\n\n"
        "📌 *Commands:*\n"
        "• /start - Start the bot\n"
        "• /help - Show this help\n"
        "• /setlang <code> - Set target language\n"
        "• /langs - List all languages\n"
        "• /about - About this bot\n\n"
        "💡 *Quick Tips:*\n"
        "• Send any message to translate it\n"
        "• Use @languagetranslatorbot in any chat\n"
        "• Auto-detects source language\n\n"
        "🌐 *Example:*\n"
        "Send 'Hello world' → Translated text"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command."""
    about = (
        "🤖 *Language Translator Bot*\n\n"
        "⚡ *Features:*\n"
        "• 20+ languages supported\n"
        "• Auto language detection\n"
        "• Inline translation mode\n"
        "• User preferences saved\n\n"
        "🛠 *Tech Stack:*\n"
        "• Python 3.11+\n"
        "• python-telegram-bot\n"
        "• Google Translate API\n"
        "• Railway Hosting\n\n"
        "🔒 *Privacy:*\n"
        "• No messages stored\n"
        "• No data collected\n\n"
        "❤️ *Made with love*"
    )
    await update.message.reply_text(about, parse_mode='Markdown')

async def list_languages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /langs command."""
    lang_list = "\n".join([f"• `{code}` - {name}" for code, name in LANGUAGES.items()])
    
    message = (
        "🌍 *Supported Languages*\n\n"
        f"{lang_list}\n\n"
        "📌 Use /setlang <code> to change language\n"
        "Example: /setlang es"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setlang command."""
    user_id = update.effective_user.id
    
    if not context.args:
        await update.message.reply_text(
            "🌐 *Select your target language:*",
            reply_markup=create_language_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    lang_input = context.args[0].lower()
    
    # Check alias
    if lang_input in ALIASES:
        lang_code = ALIASES[lang_input]
    else:
        lang_code = lang_input
    
    if lang_code in LANGUAGES:
        if user_id not in user_prefs:
            user_prefs[user_id] = {}
        user_prefs[user_id]['target'] = lang_code
        
        await update.message.reply_text(
            f"✅ *Language set to:* {LANGUAGES[lang_code]}\n\n"
            "Send any text to translate it!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ *Language not found!*\n\n"
            f"'{lang_input}' is not valid.\n"
            "Use /langs to see all supported languages.",
            parse_mode='Markdown'
        )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Translate text message."""
    user_id = update.effective_user.id
    
    # Get text to translate
    if context.args and update.message.text.startswith('/translate'):
        text = ' '.join(context.args)
    else:
        text = update.message.text or ""
    
    if not text or len(text.strip()) == 0:
        await update.message.reply_text("Please send me some text to translate.")
        return
    
    # Get target language
    target = user_prefs.get(user_id, {}).get('target', 'en')
    
    try:
        # Show typing
        await update.message.chat.send_action(action="typing")
        
        # Translate
        translator = GoogleTranslator(source='auto', target=target)
        translated = translator.translate(text)
        
        response = (
            f"🔄 *Translation*\n\n"
            f"📝 *Original:*\n{text}\n\n"
            f"🌐 *Translated ({LANGUAGES.get(target, 'English')}):*\n{translated}"
        )
        
        keyboard = [[
            InlineKeyboardButton("🌐 Change Language", callback_data="change_lang")
        ]]
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "❌ *Translation failed!*\n\n"
            "Please try again or change your target language.",
            parse_mode='Markdown'
        )

async def inline_translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries."""
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

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
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
        help_text = (
            "🆘 *Quick Help*\n\n"
            "• Send any text → translate\n"
            "• /setlang <code> → change language\n"
            "• /langs → see all languages\n"
            "• @languagetranslatorbot → inline mode\n\n"
            "📌 *Examples:*\n"
            "• /setlang es (Spanish)\n"
            "• /setlang fr (French)"
        )
        await query.edit_message_text(help_text, parse_mode='Markdown')
        
    elif query.data.startswith("setlang_"):
        lang_code = query.data.replace("setlang_", "")
        if lang_code in LANGUAGES:
            if user_id not in user_prefs:
                user_prefs[user_id] = {}
            user_prefs[user_id]['target'] = lang_code
            
            await query.edit_message_text(
                f"✅ *Language set to:* {LANGUAGES[lang_code]}\n\n"
                "Send any text to translate it!",
                parse_mode='Markdown'
            )
        else:
            await query.edit_message_text(
                "❌ Invalid language. Please try again.",
                parse_mode='Markdown'
            )

def create_language_keyboard() -> InlineKeyboardMarkup:
    """Create language selection keyboard."""
    keyboard = []
    row = []
    
    for idx, (code, name) in enumerate(sorted(LANGUAGES.items())):
        if idx % 3 == 0 and idx > 0:
            keyboard.append(row)
            row = []
        
        display = name.split(' ')[1] if ' ' in name else name[:10]
        row.append(InlineKeyboardButton(
            f"{display[:12]}",
            callback_data=f"setlang_{code}"
        ))
    
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ *Something went wrong!*\n\n"
            "Please try again later.",
            parse_mode='Markdown'
        )

# ===================== MAIN FUNCTION =====================

def main() -> None:
    """Start the bot."""
    logger.info("🚀 Starting Language Translator Bot...")
    logger.info(f"🤖 Bot Token: {TOKEN[:10]}...")  # Show first 10 chars only
    
    try:
        # Create application
        application = Application.builder().token(TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("langs", list_languages))
        application.add_handler(CommandHandler("setlang", set_language))
        application.add_handler(CommandHandler("translate", translate_text))
        
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.INLINE_QUERY,
                translate_text
            )
        )
        
        application.add_handler(MessageHandler(filters.INLINE_QUERY, inline_translate))
        application.add_handler(CallbackQueryHandler(button_callback))
        application.add_error_handler(error_handler)
        
        # Start polling
        logger.info("✅ Bot is running and listening for messages...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
