import json
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import pandas as pd
import time
import os

# ==================== CONFIG ====================
BOT_TOKEN = "8344299678:AAG2e8Lza41NpW4k4N29aT72RC3bHWD0S0U"
CBU_API_URL = "https://cbu.uz/oz/arkhiv-kursov-valyut/json/all/"
DATA_FOLDER = "currency_data"
CACHE_FOLDER = "currency_cache"
DAILY_CACHE_FILE = os.path.join(CACHE_FOLDER, "daily_rates.json")
MONTHLY_CACHE_FILE = os.path.join(CACHE_FOLDER, "monthly_rates.json")
YEARLY_CACHE_FILE = os.path.join(CACHE_FOLDER, "yearly_rates.json")

# Conversation states
(CALCULATOR_FROM, CALCULATOR_TO, CALCULATOR_AMOUNT, 
 LANGUAGE_SELECTION, MONTHLY_CURRENCY, CUSTOM_CURRENCY, 
 YEARLY_PERIOD, YEARLY_CURRENCY, ALL_CURR_SELECTION) = range(9)

# ==================== LANGUAGES ====================
LANGUAGES = {
    'uz': {
        'name': "O'zbekcha",
        'start_message': "🏦 <b>Markaziy Bank Valyuta Boti</b>\n\nSalom! Men sizga valyuta kurslari haqida ma'lumot beraman.\n\n📊 <b>Valyuta Statistikasi</b> - Grafiklar va so'nggi kurslar\n🧮 <b>Valyuta Kalkulyatori</b> - Valyuta konvertatsiyasi\n📈 <b>Barcha Valyutalar</b> - Barcha mavjud valyuta kurslari\n📅 <b>Oylik Statistika</b> - Ixtiyoriy valyuta uchun oylik hisobot\n📆 <b>Yillik Statistika</b> - 1 yillik hisobot",
        'statistics': "📊 Valyuta Statistikasi",
        'calculator': "🧮 Valyuta Kalkulyatori",
        'all_currencies': "📈 Barcha Valyutalar",
        'monthly_stats': "📅 Oylik Statistika",
        'yearly_stats': "📆 Yillik Statistika",
        'loading': "📊 Ma'lumotlar yuklanmoqda...",
        'error': "❌ Ma'lumotlarni olishda xatolik yuz berdi.",
        'cancel': "❌ Bekor qilish",
        'back': "🔙 Orqaga",
        'all_currencies_title': "📋 <b>Barcha valyuta kurslari:</b>\n\n",
        'current_rate': "💰 Joriy kurs",
        'date': "📅 Sana",
        'dynamics': "📊 So'nggi 30 kunlik dinamika",
        'conversion_result': "💱 <b>Konvertatsiya Natijasi</b>",
        'rates': "📊 Kurslar",
        'select_from': "🧮 <b>Valyuta Kalkulyatori</b>\n\nQaysi valyutadan aylantirasiz?",
        'select_to': "Tanlandi: <b>{}</b>\n\nQaysi valyutaga aylantirasiz?",
        'enter_amount': "<b>{}</b> → <b>{}</b>\n\nMiqdorni kiriting:",
        'wrong_format': "❌ Noto'g'ri format! Raqam kiriting.",
        'currency_not_found': "❌ Valyuta kursi topilmadi.",
        'cancelled': "❌ Bekor qilindi.",
        'select_currency': "📅 <b>Oylik Statistika</b>\n\nQaysi valyutani ko'rmoqchisiz?",
        'updating_cache': "🔄 Kesh yangilanmoqda...",
        'cache_updated': "✅ Ma'lumotlar yangilandi!",
        'select_period': "📆 <b>Yillik Statistika</b>\n\nDavrni tanlang:",
        'one_year': "📅 1 Yillik",
        'get_chart': "📊 Grafikni olish",
        'select_currency_yearly': "📆 <b>Yillik Statistika</b>\n\nQaysi valyutani ko'rmoqchisiz?",
        'select_currency_all': "📈 <b>Barcha Valyutalar</b>\n\nQaysi valyutani ko'rmoqchisiz?"
    },
    'ru': {
        'name': "Русский",
        'start_message': "🏦 <b>Бот валют Центрального Банка</b>\n\nПривет! Я предоставлю вам информацию о курсах валют.\n\n📊 <b>Статистика валют</b> - Графики и последние курсы\n🧮 <b>Валютный калькулятор</b> - Конвертация валют\n📈 <b>Все валюты</b> - Все доступные курсы валют\n📅 <b>Месячная статистика</b> - Отчет по выбранной валюте\n📆 <b>Годовая статистика</b> - Отчеты за 1 год",
        'statistics': "📊 Статистика валют",
        'calculator': "🧮 Валютный калькулятор",
        'all_currencies': "📈 Все валюты",
        'monthly_stats': "📅 Месячная статистика",
        'yearly_stats': "📆 Годовая статистика",
        'loading': "📊 Данные загружаются...",
        'error': "❌ Ошибка при получении данных.",
        'cancel': "❌ Отмена",
        'back': "🔙 Назад",
        'all_currencies_title': "📋 <b>Все курсы валют:</b>\n\n",
        'current_rate': "💰 Текущий курс",
        'date': "📅 Дата",
        'dynamics': "📊 Динамика за 30 дней",
        'conversion_result': "💱 <b>Результат конвертации</b>",
        'rates': "📊 Курсы",
        'select_from': "🧮 <b>Валютный калькулятор</b>\n\nИз какой валюты конвертировать?",
        'select_to': "Выбрано: <b>{}</b>\n\nВ какую валюту конвертировать?",
        'enter_amount': "<b>{}</b> → <b>{}</b>\n\nВведите сумму:",
        'wrong_format': "❌ Неверный формат! Введите число.",
        'currency_not_found': "❌ Курс валюты не найден.",
        'cancelled': "❌ Отменено.",
        'select_currency': "📅 <b>Месячная статистика</b>\n\nКакую валюту хотите посмотреть?",
        'updating_cache': "🔄 Обновление кеша...",
        'cache_updated': "✅ Данные обновлены!",
        'select_period': "📆 <b>Годовая статистика</b>\n\nВыберите период:",
        'one_year': "📅 1 Год",
        'get_chart': "📊 Получить график",
        'select_currency_yearly': "📆 <b>Годовая статистика</b>\n\nКакую валюту хотите посмотреть?",
        'select_currency_all': "📈 <b>Все валюты</b>\n\nКакую валюту хотите посмотреть?"
    },
    'en': {
        'name': "English",
        'start_message': "🏦 <b>Central Bank Currency Bot</b>\n\nHello! I will provide you with currency exchange rate information.\n\n📊 <b>Currency Statistics</b> - Charts and latest rates\n🧮 <b>Currency Calculator</b> - Currency conversion\n📈 <b>All Currencies</b> - All available currency rates\n📅 <b>Monthly Statistics</b> - Custom currency monthly report\n📆 <b>Yearly Statistics</b> - 1 year reports",
        'statistics': "📊 Currency Statistics",
        'calculator': "🧮 Currency Calculator",
        'all_currencies': "📈 All Currencies",
        'monthly_stats': "📅 Monthly Statistics",
        'yearly_stats': "📆 Yearly Statistics",
        'loading': "📊 Loading data...",
        'error': "❌ Error fetching data.",
        'cancel': "❌ Cancel",
        'back': "🔙 Back",
        'all_currencies_title': "📋 <b>All currency rates:</b>\n\n",
        'current_rate': "💰 Current rate",
        'date': "📅 Date",
        'dynamics': "📊 30-day dynamics",
        'conversion_result': "💱 <b>Conversion Result</b>",
        'rates': "📊 Rates",
        'select_from': "🧮 <b>Currency Calculator</b>\n\nWhich currency to convert from?",
        'select_to': "Selected: <b>{}</b>\n\nWhich currency to convert to?",
        'enter_amount': "<b>{}</b> → <b>{}</b>\n\nEnter amount:",
        'wrong_format': "❌ Wrong format! Enter a number.",
        'currency_not_found': "❌ Currency rate not found.",
        'cancelled': "❌ Cancelled.",
        'select_currency': "📅 <b>Monthly Statistics</b>\n\nWhich currency do you want to see?",
        'updating_cache': "🔄 Updating cache...",
        'cache_updated': "✅ Data updated!",
        'select_period': "📆 <b>Yearly Statistics</b>\n\nSelect period:",
        'one_year': "📅 1 Year",
        'get_chart': "📊 Get Chart",
        'select_currency_yearly': "📆 <b>Yearly Statistics</b>\n\nWhich currency do you want to see?",
        'select_currency_all': "📈 <b>All Currencies</b>\n\nWhich currency do you want to see?"
    }
}

# ==================== HELPERS ====================
USER_LANGUAGES = {}

def get_user_language(user_id):
    return USER_LANGUAGES.get(user_id, 'uz')

def tr(user_id, key):
    lang = get_user_language(user_id)
    return LANGUAGES[lang][key]

def ensure_data_folder():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"✅ '{DATA_FOLDER}' papkasi yaratildi")
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)
        print(f"✅ '{CACHE_FOLDER}' papkasi yaratildi")

# ==================== CACHE FUNCTIONS ====================
def load_cache(cache_file):
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"❌ Keshni yuklashda xatolik: {e}")
        return {}

def save_cache(cache_file, data):
    try:
        ensure_data_folder()
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Keshni saqlashda xatolik: {e}")
        return False

def update_daily_cache():
    try:
        print("🔄 Kunlik kesh yangilanmoqda...")
        today = datetime.now().strftime("%Y-%m-%d")
        
        cache = load_cache(DAILY_CACHE_FILE)
        
        if today in cache:
            print(f"✅ Bugungi ma'lumot ({today}) keshda mavjud")
            return cache
        
        url = CBU_API_URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        cache[today] = data
        save_cache(DAILY_CACHE_FILE, cache)
        
        print(f"✅ Kunlik kesh yangilandi: {today}")
        return cache
        
    except Exception as e:
        print(f"❌ Kunlik keshni yangilashda xatolik: {e}")
        return load_cache(DAILY_CACHE_FILE)

def fetch_currency_data(date=None):
    try:
        if not date:
            cache = update_daily_cache()
            today = datetime.now().strftime("%Y-%m-%d")
            if today in cache:
                return cache[today]
        
        if date:
            url = f"{CBU_API_URL}{date}/"
        else:
            url = CBU_API_URL
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Save data
        ensure_data_folder()
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(DATA_FOLDER, f"{today}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return data
    except Exception as e:
        print(f"❌ API dan ma'lumot olishda xatolik: {e}")
        return None

# ==================== CHART FUNCTIONS ====================
def create_chart(currency_code="USD", days=30):
    try:
        # For now, create simple chart without cache
        data = fetch_currency_data()
        if not data:
            return None
            
        currency_data = None
        for curr in data:
            if curr['Ccy'] == currency_code:
                currency_data = curr
                break
                
        if not currency_data:
            return None
            
        # Create simple chart with dummy data
        dates = [datetime.now() - timedelta(days=x) for x in range(days, 0, -1)]
        rates = [float(currency_data['Rate']) * (0.95 + 0.1 * (i/days)) for i in range(days)]
        
        fig, ax = plt.subplots(figsize=(14, 7))
        ax.set_facecolor('#f8f9fa')
        fig.patch.set_facecolor('white')
        
        ax.plot(dates, rates, linewidth=2.5, color='#4169E1', alpha=0.7, label=f"{currency_code}/UZS")
        ax.scatter(dates, rates, color='#4169E1', s=25, alpha=0.8, edgecolors='white', linewidth=1)
        ax.fill_between(dates, rates, alpha=0.2, color='#4169E1')
        
        ax.set_title(f"{currency_code}/UZS kursi ({days} kunlik)", fontsize=18, fontweight="bold", pad=20, color='#2c3e50')
        ax.set_xlabel("Sana", fontsize=13, fontweight='bold', color='#34495e')
        ax.set_ylabel("Kurs (UZS)", fontsize=13, fontweight='bold', color='#34495e')
        
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
        plt.xticks(rotation=45, ha='right')
        
        ax.grid(True, alpha=0.3, linestyle="--", linewidth=0.8, color='#bdc3c7')
        ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
        
        plt.tight_layout()
        
        chart_file = f"chart_{currency_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches="tight", facecolor='white')
        plt.close()
        
        return chart_file
    
    except Exception as e:
        print(f"❌ Grafik chizishda xatolik: {e}")
        return None

# ==================== HANDLERS ====================
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

async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(tr(user_id, 'loading'))
    
    update_daily_cache()
    data = fetch_currency_data()
    
    if not data:
        await update.message.reply_text(tr(user_id, 'error'))
        return
    
    main_currencies = ['USD', 'EUR', 'RUB', 'GBP']
    
    for currency_code in main_currencies:
        chart_file = create_chart(currency_code, days=30)
        
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

async def all_currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    await update.message.reply_text(tr(user_id, 'loading'))
    
    data = fetch_currency_data()
    
    if not data:
        await update.message.reply_text(tr(user_id, 'error'))
        return
    
    text = tr(user_id, 'all_currencies_title')
    for curr in data:
        text += f"<b>{curr['Ccy']}</b> - {curr['CcyNm_UZ']}\n"
        text += f"💰 {float(curr['Rate']):,.2f} UZS\n\n"
    
    await update.message.reply_text(text, parse_mode='HTML')

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

async def calculator_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if update.message.text == tr(user_id, 'cancel'):
        return await cancel(update, context)
    
    context.user_data['from_currency'] = update.message.text
    
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
        await update.message.reply_text("🚧 Tez orada ishga tushadi!")
    elif text == tr(user_id, 'yearly_stats'):
        await update.message.reply_text("🚧 Tez orada ishga tushadi!")

# ==================== MAIN ====================
def main():
    ensure_data_folder()
    
    print("🔄 Boshlang'ich kesh yangilanmoqda...")
    update_daily_cache()
    print("✅ Boshlang'ich kesh tayyor!")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Language selection handler
    lang_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", language_selection)],
        states={
            LANGUAGE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
        },
        fallbacks=[],
    )
    
    # Calculator conversation handler
    calc_conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🧮 Valyuta Kalkulyatori$|^🧮 Валютный калькулятор$|^🧮 Currency Calculator$"), calculator_start)],
        states={
            CALCULATOR_FROM: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_from)],
            CALCULATOR_TO: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_to)],
            CALCULATOR_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_amount)],
        },
        fallbacks=[MessageHandler(filters.Regex("^❌.*$"), cancel)],
    )
    
    # Handlerlar
    application.add_handler(lang_conv_handler)
    application.add_handler(calc_conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot ishga tushdi!")
    print(f"📁 Ma'lumotlar '{DATA_FOLDER}' papkasida saqlanadi")
    print(f"💾 Kesh '{CACHE_FOLDER}' papkasida saqlanadi")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()