"""Valyuta kalkulyatori handlerlari"""

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from config.settings import CALCULATOR_FROM, CALCULATOR_TO, CALCULATOR_AMOUNT, CALCULATOR_CURRENCIES
from services.data_service import get_or_fetch_data
from services.api_service import get_currency_rate
from utils.helpers import tr


async def calculator_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Kalkulyatorni boshlash - birinchi valyutani tanlash"""
    user_id = update.message.from_user.id
    data = get_or_fetch_data()
    
    if not data:
        await update.message.reply_text(tr(user_id, 'error'))
        return ConversationHandler.END
    
    context.user_data['currencies'] = data
    
    # Asosiy valyutalar tugmalari
    keyboard = []
    row = []
    
    for curr in data:
        if curr['Ccy'] in CALCULATOR_CURRENCIES:
            row.append(KeyboardButton(curr['Ccy']))
            if len(row) == 3:
                keyboard.append(row)
                row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([KeyboardButton(tr(user_id, 'cancel'))])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        tr(user_id, 'select_from'),
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return CALCULATOR_FROM


async def calculator_from(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Birinchi valyutani saqlash va ikkinchi valyutani tanlash"""
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    context.user_data['from_currency'] = update.message.text
    
    # Ikkinchi valyuta uchun tugmalar (UZS qo'shilgan)
    keyboard = []
    row = []
    
    for curr in context.user_data['currencies']:
        if curr['Ccy'] in CALCULATOR_CURRENCIES:
            row.append(KeyboardButton(curr['Ccy']))
            if len(row) == 3:
                keyboard.append(row)
                row = []
    
    row.append(KeyboardButton('UZS'))
    keyboard.append(row)
    keyboard.append([KeyboardButton(tr(user_id, 'cancel'))])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        tr(user_id, 'select_to').format(context.user_data['from_currency']),
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return CALCULATOR_TO


async def calculator_to(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ikkinchi valyutani saqlash va miqdorni so'rash"""
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    context.user_data['to_currency'] = update.message.text
    
    keyboard = [[KeyboardButton(tr(user_id, 'cancel'))]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        tr(user_id, 'enter_amount').format(
            context.user_data['from_currency'], 
            context.user_data['to_currency']
        ),
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return CALCULATOR_AMOUNT


async def calculator_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Miqdorni qabul qilish va konvertatsiya qilish"""
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    # Miqdorni o'qish
    try:
        amount = float(update.message.text.replace(',', '').replace(' ', ''))
    except ValueError:
        await update.message.reply_text(tr(user_id, 'wrong_format'))
        return CALCULATOR_AMOUNT
    
    from_curr = context.user_data['from_currency']
    to_curr = context.user_data['to_currency']
    
    # Kurslarni olish
    from_rate = 1.0 if from_curr == 'UZS' else get_currency_rate(context.user_data['currencies'], from_curr)
    to_rate = 1.0 if to_curr == 'UZS' else get_currency_rate(context.user_data['currencies'], to_curr)
    
    if from_rate is None or to_rate is None:
        await update.message.reply_text(tr(user_id, 'currency_not_found'))
        return ConversationHandler.END
    
    # Konvertatsiya
    uzs_amount = amount * from_rate
    result = uzs_amount / to_rate
    
    # Asosiy menyuga qaytish
    keyboard = [
        [KeyboardButton(tr(user_id, 'statistics')), KeyboardButton(tr(user_id, 'calculator'))],
        [KeyboardButton(tr(user_id, 'all_currencies'))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # Natijani ko'rsatish
    text = f"{tr(user_id, 'conversion_result')}\n\n"
    text += f"<b>{amount:,.2f}</b> {from_curr} = <b>{result:,.2f}</b> {to_curr}\n\n"
    text += f"{tr(user_id, 'rates')}:\n"
    text += f"• {from_curr}: {from_rate:,.2f} UZS\n"
    text += f"• {to_curr}: {to_rate:,.2f} UZS"
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Kalkulyatordan chiqish"""
    user_id = update.message.from_user.id
    
    keyboard = [
        [KeyboardButton(tr(user_id, 'statistics')), KeyboardButton(tr(user_id, 'calculator'))],
        [KeyboardButton(tr(user_id, 'all_currencies'))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(tr(user_id, 'cancelled'), reply_markup=reply_markup)
    return ConversationHandler.END