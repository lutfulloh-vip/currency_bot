from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from config import LANGUAGE_SELECTION, LANGUAGES
from utils.helpers import USER_LANGUAGES, get_user_language, tr

# Tilni tanlash
async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton("🇺🇿 O'zbekcha"), KeyboardButton("🇷🇺 Русский")],
        [KeyboardButton("🇺🇸 English")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "Iltimos, tilni tanlang / Please select a language / Пожалуйста, выберите язык:",
        reply_markup=reply_markup
    )
    
    return LANGUAGE_SELECTION

# Tilni saqlash
async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    
    if "O'zbekcha" in text:
        USER_LANGUAGES[user_id] = 'uz'
    elif "Русский" in text:
        USER_LANGUAGES[user_id] = 'ru'
    elif "English" in text:
        USER_LANGUAGES[user_id] = 'en'
    
    await start(update, context)
    return ConversationHandler.END

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    keyboard = [
        [KeyboardButton(tr(user_id, 'statistics')), KeyboardButton(tr(user_id, 'calculator'))],
        [KeyboardButton(tr(user_id, 'monthly_stats')), KeyboardButton(tr(user_id, 'yearly_stats'))],
        [KeyboardButton(tr(user_id, 'all_currencies'))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        tr(user_id, 'start_message'),
        parse_mode='HTML',
        reply_markup=reply_markup
    )

# Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    keyboard = [
        [KeyboardButton(tr(user_id, 'statistics')), KeyboardButton(tr(user_id, 'calculator'))],
        [KeyboardButton(tr(user_id, 'monthly_stats')), KeyboardButton(tr(user_id, 'yearly_stats'))],
        [KeyboardButton(tr(user_id, 'all_currencies'))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(tr(user_id, 'cancelled'), reply_markup=reply_markup)
    return ConversationHandler.END