from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
import os

from config import MONTHLY_CURRENCY, YEARLY_PERIOD, YEARLY_CURRENCY
from utils.helpers import get_user_language, tr
from services.data_service import fetch_currency_data, update_daily_cache, update_monthly_cache_for_currency, get_yearly_currency_data_from_cache
from services.chart_service import create_chart, create_yearly_chart
from handlers.start_handlers import cancel

# Asosiy valyuta statistikasi (30 kunlik)
async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(tr(user_id, 'loading'))
    
    # Kunlik keshni yangilash
    update_daily_cache()
    
    data = fetch_currency_data()
    
    if not data:
        await update.message.reply_text(tr(user_id, 'error'))
        return
    
    main_currencies = ['USD', 'EUR', 'RUB', 'GBP']
    
    for currency_code in main_currencies:
        # Keshdan foydalanib grafik chizish
        chart_file = create_chart(currency_code, days=30, use_cache=True)
        
        if chart_file:
            current_rate = None
            currency_name = None
            
            for curr in data:
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

# Oylik statistika - valyuta tanlash
async def monthly_stats_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(tr(user_id, 'loading'))
    
    data = fetch_currency_data()
    
    if not data:
        await update.message.reply_text(tr(user_id, 'error'))
        return ConversationHandler.END
    
    context.user_data['all_currencies'] = data
    
    # Barcha valyutalarni ko'rsatish
    keyboard = []
    row = []
    
    for curr in data:
        row.append(KeyboardButton(curr['Ccy']))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([KeyboardButton(tr(user_id, 'cancel'))])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        tr(user_id, 'select_currency'),
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return MONTHLY_CURRENCY

# Oylik statistika - tanlangan valyuta uchun grafik
async def monthly_stats_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    currency_code = update.message.text.upper()
    
    await update.message.reply_text(tr(user_id, 'updating_cache'))
    
    # Oylik keshni yangilash
    update_monthly_cache_for_currency(currency_code)
    
    await update.message.reply_text(tr(user_id, 'loading'))
    
    # Grafik chizish (keshdan)
    chart_file = create_chart(currency_code, days=30, use_cache=True)
    
    if chart_file:
        currency_name = None
        current_rate = None
        
        for curr in context.user_data['all_currencies']:
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
        
        keyboard = [
            [KeyboardButton(tr(user_id, 'statistics')), KeyboardButton(tr(user_id, 'calculator'))],
            [KeyboardButton(tr(user_id, 'monthly_stats')), KeyboardButton(tr(user_id, 'yearly_stats'))],
            [KeyboardButton(tr(user_id, 'all_currencies'))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(tr(user_id, 'cache_updated'), reply_markup=reply_markup)
    else:
        await update.message.reply_text(tr(user_id, 'currency_not_found'))
    
    return ConversationHandler.END

# Yillik statistika - faqat 1 yillik
async def yearly_stats_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    # Faqat 1 yillik tugmasi
    keyboard = [
        [KeyboardButton(tr(user_id, 'one_year'))],
        [KeyboardButton(tr(user_id, 'cancel'))]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        tr(user_id, 'select_period'),
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return YEARLY_PERIOD

# Yillik statistika - faqat 1 yilni qabul qilish
async def yearly_period_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    # Faqat 1 yilni qabul qilamiz
    context.user_data['years'] = 1
    
    await update.message.reply_text(tr(user_id, 'loading'))
    
    data = fetch_currency_data()
    
    if not data:
        await update.message.reply_text(tr(user_id, 'error'))
        return ConversationHandler.END
    
    context.user_data['all_currencies'] = data
    
    # Barcha valyutalarni ko'rsatish
    keyboard = []
    row = []
    
    for curr in data:
        row.append(KeyboardButton(curr['Ccy']))
        if len(row) == 4:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    keyboard.append([KeyboardButton(tr(user_id, 'cancel'))])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        tr(user_id, 'select_currency_yearly'),
        parse_mode='HTML',
        reply_markup=reply_markup
    )
    
    return YEARLY_CURRENCY

# Yillik statistika - grafik ko'rsatish (faqat keshdan)
async def yearly_stats_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    currency_code = update.message.text.upper()
    years = context.user_data.get('years', 1)
    
    await update.message.reply_text(tr(user_id, 'loading'))
    
    # Faqat keshdan ma'lumot olish, yangilamaymiz
    data = get_yearly_currency_data_from_cache(currency_code, years=years)
    
    if not data:
        await update.message.reply_text(f"❌ {currency_code} uchun {years} yillik ma'lumot topilmadi. Iltimos, keyinroq urinib ko'ring.")
        return ConversationHandler.END
    
    # Yillik grafik chizish
    chart_file = create_yearly_chart(currency_code, years=years)
    
    if chart_file:
        currency_name = None
        current_rate = None
        
        for curr in context.user_data['all_currencies']:
            if curr['Ccy'] == currency_code:
                current_rate = float(curr['Rate'])
                currency_name = curr['CcyNm_UZ']
                break
        
        caption = f"<b>{currency_code} - {currency_name}</b>\n\n"
        caption += f"{tr(user_id, 'current_rate')}: <b>{current_rate:,.2f}</b> UZS\n"
        caption += f"{tr(user_id, 'date')}: {datetime.now().strftime('%d.%m.%Y')}\n"
        caption += f"📊 {years} yillik dinamika"
        
        with open(chart_file, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption=caption, parse_mode='HTML')
        
        os.remove(chart_file)
        
        keyboard = [
            [KeyboardButton(tr(user_id, 'statistics')), KeyboardButton(tr(user_id, 'calculator'))],
            [KeyboardButton(tr(user_id, 'monthly_stats')), KeyboardButton(tr(user_id, 'yearly_stats'))],
            [KeyboardButton(tr(user_id, 'all_currencies'))]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text("✅ Ma'lumotlar keshdan olindi", reply_markup=reply_markup)
    else:
        await update.message.reply_text(tr(user_id, 'currency_not_found'))
    
    return ConversationHandler.END

from datetime import datetime