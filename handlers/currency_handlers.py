from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
import os

from config import ALL_CURR_SELECTION
from utils.helpers import get_user_language, tr
from services.data_service import fetch_currency_data
from services.chart_service import create_chart
from handlers.start_handlers import cancel

async def all_currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(tr(user_id, 'loading'))
    
    data = fetch_currency_data()
    
    if not data:
        await update.message.reply_text(tr(user_id, 'error'))
        return
    
    # Barcha valyutalar ro'yxati
    text = tr(user_id, 'all_currencies_title')
    for curr in data:
        text += f"<b>{curr['Ccy']}</b> - {curr['CcyNm_UZ']}\n"
        text += f"💰 {float(curr['Rate']):,.2f} UZS\n\n"
    
    await update.message.reply_text(text, parse_mode='HTML')

# Valyuta tafsilotlarini ko'rsatish
async def show_currency_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'back'):
        return await cancel(update, context)
    
    currency_code = update.message.text.upper()
    
    await update.message.reply_text(tr(user_id, 'loading'))
    
    # Valyuta uchun grafik chizish
    chart_file = create_chart(currency_code, days=30, use_cache=True)
    
    if chart_file:
        currency_name = None
        current_rate = None
        
        for curr in context.user_data.get('all_currencies', []):
            if curr['Ccy'] == currency_code:
                current_rate = float(curr['Rate'])
                currency_name = curr['CcyNm_UZ']
                break
        
        caption = f"<b>{currency_code} - {currency_name}</b>\n\n"
        caption += f"{tr(user_id, 'current_rate')}: <b>{current_rate:,.2f}</b> UZS\n"
        caption += f"{tr(user_id, 'date')}: {datetime.now().strftime('%d.%m.%Y')}\n"
        caption += tr(user_id, 'dynamics')
        
        with open(chart_file, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode='HTML')
        
        os.remove(chart_file)
    
    return ConversationHandler.END

# Xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    
    if text == tr(user_id, 'statistics'):
        await statistics(update, context)
    elif text == tr(user_id, 'calculator'):
        await calculator_start(update, context)
    elif text == tr(user_id, 'all_currencies'):
        await all_currencies(update, context)
    elif text == tr(user_id, 'monthly_stats'):
        await monthly_stats_start(update, context)
    elif text == tr(user_id, 'yearly_stats'):
        await yearly_stats_start(update, context)

from handlers.statistics_handlers import statistics, monthly_stats_start, yearly_stats_start
from handlers.calculator_handlers import calculator_start
from datetime import datetime