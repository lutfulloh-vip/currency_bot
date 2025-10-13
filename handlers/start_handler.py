"""Start va til tanlash handlerlari"""

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from config.settings import LANGUAGE_SELECTION
from utils.helpers import tr, set_user_language


async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Til tanlash ekranini ko'rsatish"""
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


async def set_language_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Tanlangan tilni saqlash"""
    user_id = update.message.from_user.id
    text = update.message.text
    
    if "O'zbekcha" in text:
        set_user_language(user_id, 'uz')
    elif "Русский" in text:
        set_user_language(user_id, 'ru')
    elif "English" in text:
        set_user_language(user_id, 'en')
    
    await start(update, context)
    return ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start komandasi - asosiy menyu"""
    user_id = update.message.from_user.id
    
    keyboard = [
        [KeyboardButton(tr(user_id, 'statistics')), KeyboardButton(tr(user_id, 'calculator'))],
        [KeyboardButton(tr(user_id, 'all_currencies'))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        tr(user_id, 'start_message'),
        parse_mode='HTML',
        reply_markup=reply_markup
    )