"""Ma'lumotlarni saqlash va yuklash"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from config.settings import DATA_FOLDER


def ensure_data_folder() -> None:
    """Ma'lumotlar papkasini yaratish"""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        print(f"✅ '{DATA_FOLDER}' papkasi yaratildi")


def save_data(data: List[Dict]) -> bool:
    """
    Ma'lumotlarni kunlik faylga saqlash
    
    Args:
        data: Saqlash uchun ma'lumotlar
    
    Returns:
        Muvaffaqiyatli saqlandi yoki yo'q
    """
    try:
        ensure_data_folder()
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(DATA_FOLDER, f"{today}.json")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Ma'lumotlar saqlandi: {file_path}")
        return True
    
    except Exception as e:
        print(f"❌ Ma'lumotlarni saqlashda xatolik: {e}")
        return False


def load_today_data() -> Optional[List[Dict]]:
    """
    Bugungi ma'lumotni yuklash
    
    Returns:
        Bugungi ma'lumot yoki None
    """
    try:
        ensure_data_folder()
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join(DATA_FOLDER, f"{today}.json")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"✅ Bugungi ma'lumot yuklandi: {file_path}")
                return data
        
        print(f"⚠️ Bugungi ma'lumot fayli topilmadi: {file_path}")
        return None
    
    except Exception as e:
        print(f"❌ Bugungi ma'lumotni yuklashda xatolik: {e}")
        return None


def load_all_data() -> Dict[str, List[Dict]]:
    """
    Barcha kunlik ma'lumotlarni yuklash
    
    Returns:
        Sana bo'yicha ma'lumotlar lug'ati
    """
    try:
        ensure_data_folder()
        all_data = {}
        
        if not os.path.exists(DATA_FOLDER):
            return {}
        
        for filename in os.listdir(DATA_FOLDER):
            if filename.endswith('.json'):
                date_str = filename.replace('.json', '')
                file_path = os.path.join(DATA_FOLDER, filename)
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    all_data[date_str] = json.load(f)
        
        print(f"✅ {len(all_data)} kunlik ma'lumot yuklandi")
        return all_data
    
    except Exception as e:
        print(f"❌ Ma'lumotlarni yuklashda xatolik: {e}")
        return {}


def get_or_fetch_data() -> Optional[List[Dict]]:
    """
    Bugungi ma'lumotni yuklash yoki API dan olish
    
    Returns:
        Valyuta ma'lumotlari yoki None
    """
    # Avval keshdan yuklashga harakat qilish
    data = load_today_data()
    
    if data:
        return data
    
    # Keshda bo'lmasa, API dan olish
    from services.api_service import fetch_currency_data
    data = fetch_currency_data()
    
    if data:
        save_data(data)
    
    return data