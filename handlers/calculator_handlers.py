from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from config import CALCULATOR_FROM, CALCULATOR_TO, CALCULATOR_AMOUNT
from utils.helpers import get_user_language, tr
from services.data_service import fetch_currency_data

# Kalkulyator - boshlash
async def calculator_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data = fetch_currency_data()
    
    if not data:
        await update.message.reply_text(tr(user_id, 'error'))
        return ConversationHandler.END
    
    context.user_data['currencies'] = data
    
    keyboard = []
    row = []
    main_currencies = ['USD', 'EUR', 'RUB', 'GBP', 'CNY', 'JPY']
    
    for curr in data:
        if curr['Ccy'] in main_currencies:
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

# Kalkulyator - dan valyuta
async def calculator_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    context.user_data['from_currency'] = update.message
    
    keyboard = []
    row = []
    main_currencies = ['USD', 'EUR', 'RUB', 'GBP', 'CNY', 'JPY', 'UZS']
    
    for curr in context.user_data['currencies']:
        if curr['Ccy'] in main_currencies:
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

# Kalkulyator - ga valyuta
async def calculator_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    context.user_data['to_currency'] = update.message.text
    
    keyboard = [[KeyboardButton(tr(user_id, 'cancel'))]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        tr(user_id, 'enter_amount').format(context.user_data['from_currency'], context.user_data['to_currency']),
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return CALCULATOR_AMOUNT

# Kalkulyator - miqdor va hisoblash
async def calculator_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    try:
        amount = float(update.message.text.replace(',', ''))
    except ValueError:
        await update.message.reply_text(tr(user_id, 'wrong_format'))
        return CALCULATOR_AMOUNT
    
    from_curr = context.user_data['from_currency']
    to_curr = context.user_data['to_currency']
    
    from_rate = 1 if from_curr == 'UZS' else None
    to_rate = 1 if to_curr == 'UZS' else None
    
    for curr in context.user_data['currencies']:
        if curr['Ccy'] == from_curr:
            from_rate = float(curr['Rate'])
        if curr['Ccy'] == to_curr:
            to_rate = float(curr['Rate'])
    
    if from_rate is None or to_rate is None:
        await update.message.reply_text(tr(user_id, 'currency_not_found'))
        return ConversationHandler.END
    
    uzs_amount = amount * from_rate
    result = uzs_amount / to_rate
    
    keyboard = [
        [KeyboardButton(tr(user_id, 'statistics')), KeyboardButton(tr(user_id, 'calculator'))],
        [KeyboardButton(tr(user_id, 'monthly_stats')), KeyboardButton(tr(user_id, 'yearly_stats'))],
        [KeyboardButton(tr(user_id, 'all_currencies'))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    text = f"{tr(user_id, 'conversion_result')}\n\n"
    text += f"<b>{amount:,.2f}</b> {from_curr} = <b>{result:,.2f}</b> {to_curr}\n\n"
    text += f"{tr(user_id, 'rates')}:\n"
    text += f"• {from_curr}: {from_rate:,.2f} UZS\n"
    text += f"• {to_curr}: {to_rate:,.2f} UZS"
    
    await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    
    return ConversationHandler.END

from handlers.start_handlers import cancel