import os
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# Bot sozlamalari
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylida topilmadi!")

# API sozlamalari
CBU_API_URL = os.getenv('CBU_API_URL', 'https://cbu.uz/ru/arkhiv-kursov-valyut/json/')

# Ma'lumotlar papkasi
DATA_FOLDER = os.getenv('DATA_FOLDER', 'currency_data')

# Til sozlamalari
DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'uz')

# Conversation states
CALCULATOR_FROM = 0
CALCULATOR_TO = 1
CALCULATOR_AMOUNT = 2
LANGUAGE_SELECTION = 3

# Asosiy valyutalar
MAIN_CURRENCIES = ['USD', 'EUR', 'RUB', 'GBP']
CALCULATOR_CURRENCIES = ['USD', 'EUR', 'RUB', 'GBP', 'CNY', 'JPY']