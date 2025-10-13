"""CBU API bilan ishlash"""

import requests
from typing import Optional, List, Dict
from config.settings import CBU_API_URL


def fetch_currency_data(date: Optional[str] = None) -> Optional[List[Dict]]:
    """
    CBU API dan valyuta ma'lumotlarini olish
    
    Args:
        date: Ma'lum bir sana (format: DD.MM.YYYY)
    
    Returns:
        Valyuta ma'lumotlari ro'yxati yoki None
    """
    try:
        if date:
            url = f"{CBU_API_URL}{date}/"
        else:
            url = CBU_API_URL
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ API dan {len(data)} ta valyuta ma'lumoti olindi")
        return data
    
    except requests.exceptions.RequestException as e:
        print(f"❌ API dan ma'lumot olishda xatolik: {e}")
        return None
    
    except Exception as e:
        print(f"❌ Kutilmagan xatolik: {e}")
        return None


def get_currency_by_code(data: List[Dict], currency_code: str) -> Optional[Dict]:
    """
    Valyuta kodiga qarab ma'lumot topish
    
    Args:
        data: Valyuta ma'lumotlari ro'yxati
        currency_code: Valyuta kodi (masalan: USD, EUR)
    
    Returns:
        Valyuta ma'lumoti yoki None
    """
    for currency in data:
        if currency.get('Ccy') == currency_code:
            return currency
    return None


def get_currency_rate(data: List[Dict], currency_code: str) -> Optional[float]:
    """
    Valyuta kursini olish
    
    Args:
        data: Valyuta ma'lumotlari ro'yxati
        currency_code: Valyuta kodi
    
    Returns:
        Valyuta kursi yoki None
    """
    currency = get_currency_by_code(data, currency_code)
    if currency:
        try:
            return float(currency['Rate'])
        except (ValueError, KeyError):
            return None
    return None