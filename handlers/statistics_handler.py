"""Statistika handleri"""

from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from config.settings import MAIN_CURRENCIES
from services.data_service import get_or_fetch_data, load_all_data
from services.chart_service import create_chart, cleanup_chart
from services.api_service import get_currency_by_code
from utils.helpers import tr


async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Asosiy valyutalar statistikasi"""
    user_id = update.message.from_user.id
    await update.message.reply_text(tr(user_id, 'loading'))
    
    # Bugungi ma'lumotlarni olish
    current_data = get_or_fetch_data()
    
    if not current_data:
        await update.message.reply_text(tr(user_id, 'error'))
        return
    
    # Barcha tarixiy ma'lumotlarni yuklash
    all_data = load_all_data()
    
    if not all_data:
        await update.message.reply_text(tr(user_id, 'error'))
        return
    
    # Asosiy valyutalar uchun grafiklar
    for currency_code in MAIN_CURRENCIES:
        chart_file = create_chart(all_data, currency_code, days=30)
        
        if chart_file:
            # Joriy kursni olish
            currency = get_currency_by_code(current_data, currency_code)
            
            if currency:
                current_rate = float(currency['Rate'])
                currency_name = currency['CcyNm_UZ']
                
                caption = f"<b>{currency_code} - {currency_name}</b>\n\n"
                caption += f"{tr(user_id, 'current_rate')}: <b>{current_rate:,.2f}</b> UZS\n"
                caption += f"{tr(user_id, 'date')}: {datetime.now().strftime('%d.%m.%Y')}\n"
                caption += tr(user_id, 'dynamics')
                
                with open(chart_file, 'rb') as photo:
                    await update.message.reply_photo(
                        photo=photo, 
                        caption=caption, 
                        parse_mode='HTML'
                    )
                
                cleanup_chart(chart_file)