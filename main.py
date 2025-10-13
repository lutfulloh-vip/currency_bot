"""
Markaziy Bank Valyuta Boti - Asosiy fayl
"""

from telegram import Update
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ContextTypes,
    ConversationHandler
)

from config.settings import (
    BOT_TOKEN, 
    CALCULATOR_FROM, 
    CALCULATOR_TO, 
    CALCULATOR_AMOUNT,
    LANGUAGE_SELECTION
)
from services.data_service import ensure_data_folder
from handlers.start_handler import language_selection, set_language_handler, start
from handlers.statistics_handler import statistics
from handlers.currency_handler import all_currencies
from handlers.calculator_handler import (
    calculator_start,
    calculator_from,
    calculator_to,
    calculator_amount,
    cancel
)
from utils.helpers import tr


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Oddiy xabarlarni qayta ishlash"""
    user_id = update.message.from_user.id
    text = update.message.text
    
    if text == tr(user_id, 'statistics'):
        await statistics(update, context)
    elif text == tr(user_id, 'all_currencies'):
        await all_currencies(update, context)


def main():
    """Botni ishga tushirish"""
    print("🚀 Bot ishga tushirilmoqda...")
    
    # Ma'lumotlar papkasini yaratish
    ensure_data_folder()
    
    # Application yaratish
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Til tanlash conversation handler
    lang_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", language_selection)],
        states={
            LANGUAGE_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, set_language_handler)
            ],
        },
        fallbacks=[],
    )
    
    # Kalkulyator conversation handler
    calc_conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^🧮 Valyuta Kalkulyatori$|^🧮 Валютный калькулятор$|^🧮 Currency Calculator$"), 
                calculator_start
            )
        ],
        states={
            CALCULATOR_FROM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_from)
            ],
            CALCULATOR_TO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_to)
            ],
            CALCULATOR_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, calculator_amount)
            ],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^❌.*$"), cancel)
        ],
    )
    
    # Handlerlarni qo'shish
    application.add_handler(lang_conv_handler)
    application.add_handler(calc_conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Bot muvaffaqiyatli ishga tushdi!")
    print(f"📝 Bot username: @your_bot_username")
    print(f"💾 Ma'lumotlar saqlash: currency_data/")
    print("⏳ Botni to'xtatish uchun Ctrl+C bosing")
    
    # Botni ishga tushirish
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot to'xtatildi. Xayr!")
    except Exception as e:
        print(f"\n❌ Xatolik yuz berdi: {e}")