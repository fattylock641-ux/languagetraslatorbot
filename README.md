# 🌍 Language Translator Bot

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/yourusername/languagetranslatorbot)

A powerful Telegram bot that translates text between 25+ languages instantly using Google Translate API.

## ✨ Features

- 🌐 **25+ Languages** - Support for major world languages
- ⚡ **Instant Translation** - Fast and accurate translations
- 🔍 **Auto-Detection** - Automatically detects source language
- 💬 **Inline Mode** - Use `@languagetranslatorbot` in any chat
- 🎯 **Customizable** - Set your preferred target language
- 📱 **User-Friendly** - Interactive buttons and easy commands
- 🔒 **Privacy-Focused** - No messages stored permanently

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and get welcome message |
| `/help` | Show all available commands |
| `/translate <text>` | Translate specific text |
| `/setlang <code>` | Set target language |
| `/langs` | List all supported languages |
| `/about` | About this bot |

## 🚀 Quick Deploy to Railway

1. **Click the "Deploy on Railway" button above**
2. **Add environment variable:**
   - `TELEGRAM_BOT_TOKEN` = Your bot token from @BotFather
3. **Wait for deployment** (2-3 minutes)
4. **Your bot is live!** 🎉

## 🛠️ Manual Deployment

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Railway account

### Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/languagetranslatorbot.git
   cd languagetranslatorbot
