"""
Language Translator Bot - Telegram Bot
Deployed on Railway with GitHub integration
"""

import os
import logging
import asyncio
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
import re

# ===================== CONFIGURATION =====================

# Environment variables
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set!")

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== LANGUAGE DATA =====================

SUPPORTED_LANGUAGES = {
    'en': '🇬🇧 English',
    'es': '🇪🇸 Spanish',
    'fr': '🇫🇷 French',
    'de': '🇩🇪 German',
    'it': '🇮🇹 Italian',
    'pt': '🇵🇹 Portuguese',
    'ru': '🇷🇺 Russian',
    'ja': '🇯🇵 Japanese',
    'ko': '🇰🇷 Korean',
    'zh-CN': '🇨🇳 Chinese (Simplified)',
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
    'ur': '🇵🇰 Urdu',
    'bn': '🇧🇩 Bengali',
    'ta': '🇮🇳 Tamil',
    'te': '🇮🇳 Telugu',
    'mr': '🇮🇳 Marathi',
    'gu': '🇮🇳 Gujarati',
    'kn': '🇮🇳 Kannada',
    'ml': '🇮🇳 Malayalam',
}

# Language code aliases for easier use
LANGUAGE_ALIASES = {
    'zh': 'zh-CN',
    'chinese': 'zh-CN',
    'english': 'en',
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

# ===================== USER DATA STORE =====================

# In-memory storage (resets on bot restart)
# For production, consider using Redis or a database
user_preferences: Dict[int, Dict[str, str]] = {}

def get_user_language(user_id: int) -> str:
    """Get user's preferred target language."""
    return user_preferences.get(user_id, {}).get('target', 'en')

def set_user_language(user_id: int, lang_code: str) -> None:
    """Set user's preferred target language."""
    if user_id not in user_preferences:
        user_preferences[user_id] = {}
    user_preferences[user_id]['target'] = lang_code

# ===================== HELPER FUNCTIONS =====================

def format_language_list() -> str:
    """Format the list of supported languages."""
    lines = []
    for code, name in SUPPORTED_LANGUAGES.items():
        lines.append(f"• `{code}` - {name}")
    return "\n".join(lines)

def create_language_keyboard() -> InlineKeyboardMarkup:
    """Create an inline keyboard with language options."""
    keyboard = []
    row = []
    
    # Sort languages for better UX
    sorted_langs = sorted(SUPPORTED_LANGUAGES.items())
    
    for idx, (code, name) in enumerate(sorted_langs):
        # Add 3 buttons per row
        if idx % 3 == 0 and idx > 0:
            keyboard.append(row)
            row = []
        
        # Shorten name for button
        display_name = name.split(' ')[1] if ' ' in name else name[:10]
        row.append(
            InlineKeyboardButton(
                f"{display_name[:12]}",
                callback_data=f"setlang_{code}"
            )
        )
    
    if row:
        keyboard.append(row)
    
    # Add utility buttons
    keyboard.append([
        InlineKeyboardButton("📖 View All Languages", callback_data="list_langs")
    ])
    
    return InlineKeyboardMarkup(keyboard)

# ===================== BOT HANDLERS =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    user_id = user.id
    
    # Set default language if not set
    if user_id not in user_preferences:
        set_user_language(user_id, 'en')
    
    welcome_text = (
        f"👋 *Hello {user.first_name}!*\n\n"
        "🌍 Welcome to the *Language Translator Bot*\n"
        "I can translate text between 20+ languages instantly!\n\n"
        "📝 *How to use:*\n"
        "• Send any text and I'll translate it\n"
        "• Use /translate <text> for specific translations\n"
        "• Use /setlang <code> to change target language\n"
        "• Use /langs to see all supported languages\n"
        "• Type @languagetranslatorbot in any chat for inline translation\n\n"
        f"🎯 *Current target language:* {SUPPORTED_LANGUAGES.get('en', 'English')}\n\n"
        "👉 *Try it now!* Send me any text to translate."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🌐 Change Language", callback_data="change_lang"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = (
        "🆘 *Help & Commands*\n\n"
        "📌 *Basic Commands:*\n"
        "• /start - Start the bot\n"
        "• /help - Show this help\n"
        "• /translate <text> - Translate text\n"
        "• /setlang <code> - Set target language\n"
        "• /langs - List all languages\n"
        "• /about - About this bot\n\n"
        "💡 *Quick Tips:*\n"
        "• Send any message to translate it\n"
        "• Use @languagetranslatorbot in any chat\n"
        "• Default translation: English\n"
        "• Auto-detects source language\n\n"
        "🌐 *Example:*\n"
        "Send 'Hola mundo' → 'Hello world'\n\n"
        "📚 *Need more help?*\n"
        "Contact @BotSupport for assistance."
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command."""
    about_text = (
        "🤖 *Language Translator Bot v2.0*\n\n"
        "⚡ *Features:*\n"
        "• 25+ languages supported\n"
        "• Auto language detection\n"
        "• Inline translation mode\n"
        "• User preferences saved\n"
        "• Fast & reliable\n\n"
        "🛠 *Technologies:*\n"
        "• Python 3.11+\n"
        "• python-telegram-bot\n"
        "• Google Translate API\n"
        "• Railway Hosting\n\n"
        "🔒 *Privacy:*\n"
        "• No messages stored\n"
        "• No data collected\n"
        "• Secure connection\n\n"
        "👨‍💻 *Open Source:*\n"
        "• GitHub: github.com/yourusername/languagetranslatorbot\n"
        "• MIT License\n\n"
        "❤️ *Made with love for everyone*"
    )
    await update.message.reply_text(about_text, parse_mode='Markdown')

async def list_languages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /langs command."""
    lang_list = format_language_list()
    
    message = (
        "🌍 *Supported Languages*\n\n"
        f"{lang_list}\n\n"
        "📌 *Commands:*\n"
        "• /setlang <code> - Set target language\n"
        "• Example: /setlang es\n\n"
        "🔄 Your current language: "
        f"{SUPPORTED_LANGUAGES.get(get_user_language(update.effective_user.id), 'English')}"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setlang command."""
    user_id = update.effective_user.id
    
    if not context.args:
        # Show language selection menu
        await update.message.reply_text(
            "🌐 *Select your target language:*",
            reply_markup=create_language_keyboard(),
            parse_mode='Markdown'
        )
        return
    
    lang_input = context.args[0].lower()
    
    # Check if it's an alias
    if lang_input in LANGUAGE_ALIASES:
        lang_code = LANGUAGE_ALIASES[lang_input]
    else:
        lang_code = lang_input
    
    if lang_code in SUPPORTED_LANGUAGES:
        set_user_language(user_id, lang_code)
        
        await update.message.reply_text(
            f"✅ *Language updated!*\n\n"
            f"Now translating to: {SUPPORTED_LANGUAGES[lang_code]}\n\n"
            f"Send any text to translate it to {SUPPORTED_LANGUAGES[lang_code].split(' ')[1]}!",
            parse_mode='Markdown'
        )
    else:
        # Check if input is a language name (not code)
        for code, name in SUPPORTED_LANGUAGES.items():
            if lang_input in name.lower():
                set_user_language(user_id, code)
                await update.message.reply_text(
                    f"✅ *Language set!*\n\n"
                    f"Now translating to: {name}\n\n"
                    f"Send any text to translate it to {name.split(' ')[1]}!",
                    parse_mode='Markdown'
                )
                return
        
        await update.message.reply_text(
            f"❌ *Language not found!*\n\n"
            f"'{lang_input}' is not a valid language code or name.\n\n"
            f"📋 *Examples:*\n"
            f"• Code: /setlang es\n"
            f"• Name: /setlang spanish\n"
            f"• Alias: /setlang spanish\n\n"
            f"Use /langs to see all supported languages.",
            parse_mode='Markdown'
        )

async def translate_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Translate text message."""
    user_id = update.effective_user.id
    text_to_translate = update.message.text or ""
    
    if not text_to_translate or len(text_to_translate.strip()) == 0:
        await update.message.reply_text("Please send me some text to translate.")
        return
    
    # Check if it's a command with arguments
    if context.args and update.message.text.startswith('/translate'):
        text_to_translate = ' '.join(context.args)
    
    # Get user's target language
    target_lang = get_user_language(user_id)
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Translate using Google Translate
        translator = GoogleTranslator(source='auto', target=target_lang)
        translated = translator.translate(text_to_translate)
        
        # Get source language name (if possible)
        source_lang = "Auto-detected"
        try:
            # Try to detect source language by translating back
            detector = GoogleTranslator(source='auto', target='en')
            source_detected = detector.translate(text_to_translate)
            source_lang = "Auto-detected"
        except:
            pass
        
        # Create response
        response = (
            f"🔄 *Translation*\n\n"
            f"📝 *Original:*\n{text_to_translate}\n\n"
            f"🌐 *Translated ({SUPPORTED_LANGUAGES.get(target_lang, 'English')}):*\n{translated}\n\n"
            f"🏷️ *Source:* {source_lang}"
        )
        
        # Add action buttons
        keyboard = [
            [
                InlineKeyboardButton("🔄 Swap Language", callback_data=f"swap_{target_lang}"),
                InlineKeyboardButton("📝 Copy", callback_data=f"copy_{translated[:50]}")
            ],
            [
                InlineKeyboardButton("🌐 Change Target", callback_data="change_lang")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Translation error for user {user_id}: {e}")
        await update.message.reply_text(
            "❌ *Translation failed!*\n\n"
            "Please try again with different text or check your target language.\n"
            "Use /setlang to change the target language.",
            parse_mode='Markdown'
        )

async def inline_translate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline queries."""
    query = update.inline_query.query
    
    if not query or len(query.strip()) == 0:
        return
    
    try:
        # Default to English for inline mode
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
                f"🔄 *Translated (English):*\n{translated}",
                parse_mode='Markdown'
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 Translate to other", callback_data="inline_help")]
            ])
        )
        
        await update.inline_query.answer([result], cache_time=300)
        
    except Exception as e:
        logger.error(f"Inline translation error: {e}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    try:
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
                "📌 *Language codes:*\n"
                "en = English, es = Spanish, fr = French\n"
                "de = German, it = Italian, pt = Portuguese\n\n"
                "Type /help for complete guide."
            )
            await query.edit_message_text(help_text, parse_mode='Markdown')
            
        elif query.data.startswith("setlang_"):
            lang_code = query.data.replace("setlang_", "")
            if lang_code in SUPPORTED_LANGUAGES:
                set_user_language(user_id, lang_code)
                
                await query.edit_message_text(
                    f"✅ *Language set!*\n\n"
                    f"Now translating to: {SUPPORTED_LANGUAGES[lang_code]}\n\n"
                    f"Send any text to translate it!",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    "❌ Invalid language code. Please try again.",
                    parse_mode='Markdown'
                )
                
        elif query.data == "list_langs":
            lang_list = format_language_list()
            await query.edit_message_text(
                f"🌍 *All Supported Languages*\n\n{lang_list}\n\n"
                f"Your current language: {SUPPORTED_LANGUAGES.get(get_user_language(user_id), 'English')}",
                parse_mode='Markdown'
            )
            
        elif query.data.startswith("swap_"):
            target_lang = query.data.replace("swap_", "")
            await query.edit_message_text(
                f"🔄 *Swap Feature*\n\n"
                f"Current target language: {SUPPORTED_LANGUAGES.get(target_lang, 'English')}\n\n"
                f"Use /setlang to change to a different language.",
                parse_mode='Markdown'
            )
            
        elif query.data.startswith("copy_"):
            text = query.data.replace("copy_", "")
            await query.edit_message_text(
                f"📝 *Text copied!*\n\n"
                f"'{text[:50]}...'\n\n"
                f"Use /translate to translate more text.",
                parse_mode='Markdown'
            )
            
        elif query.data == "inline_help":
            await query.edit_message_text(
                "💡 *Inline Mode*\n\n"
                "Type @languagetranslatorbot followed by your text\n"
                "Example: @languagetranslatorbot Hello world\n\n"
                "The translation will appear as a result!",
                parse_mode='Markdown'
            )
            
    except Exception as e:
        logger.error(f"Button callback error: {e}")
        await query.edit_message_text(
            "❌ An error occurred. Please try again.",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "⚠️ *Oops! Something went wrong.*\n\n"
            "Please try again later or contact support.",
            parse_mode='Markdown'
        )

# ===================== MAIN FUNCTION =====================

def main() -> None:
    """Start the bot."""
    logger.info("🚀 Starting Language Translator Bot...")
    logger.info(f"🤖 Bot username: @languagetranslatorbot")
    
    try:
        # Create application
        application = Application.builder().token(TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("langs", list_languages))
        application.add_handler(CommandHandler("setlang", set_language))
        application.add_handler(CommandHandler("translate", translate_text))
        
        # Add message handler for text messages (not commands)
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND & ~filters.UpdateType.INLINE_QUERY,
                translate_text
            )
        )
        
        # Add inline query handler
        application.add_handler(MessageHandler(filters.INLINE_QUERY, inline_translate))
        
        # Add callback query handler for buttons
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Add error handler
        application.add_error_handler(error_handler)
        
        # Start the bot
        logger.info("✅ Bot is running and listening for messages...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
