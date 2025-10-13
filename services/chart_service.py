"""Grafiklar yaratish"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def create_chart(
    all_data: Dict[str, List[Dict]], 
    currency_code: str = "USD", 
    days: int = 30
) -> Optional[str]:
    """
    Valyuta kursi grafigini yaratish
    
    Args:
        all_data: Barcha ma'lumotlar (sana: ma'lumotlar)
        currency_code: Valyuta kodi
        days: Necha kunlik grafik
    
    Returns:
        Grafik fayl yo'li yoki None
    """
    try:
        dates = []
        rates = []
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Ma'lumotlarni sana bo'yicha saralash
        sorted_dates = sorted(all_data.items())
        
        for date_str, currencies in sorted_dates:
            try:
                # Sana formatini aniqlash
                if '.' in date_str:
                    date_obj = datetime.strptime(date_str, "%d.%m.%Y")
                else:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                continue
            
            # Belgilangan oraliqda bo'lsa
            if start_date <= date_obj <= end_date:
                for currency in currencies:
                    if currency.get("Ccy") == currency_code:
                        dates.append(date_obj)
                        rates.append(float(currency["Rate"]))
                        break
        
        if not dates or not rates:
            print(f"⚠️ {currency_code} uchun ma'lumot topilmadi.")
            return None
        
        # Grafik chizish
        plt.figure(figsize=(12, 6))
        plt.fill_between(dates, rates, alpha=0.3, color='#4169E1')
        plt.plot(dates, rates, linewidth=2, color='#4169E1', label=f"{currency_code}/UZS")
        
        plt.title(f"{currency_code}/UZS kursi ({days} kunlik)", fontsize=16, fontweight="bold", pad=20)
        plt.xlabel("Sana", fontsize=12)
        plt.ylabel("Kurs (UZS)", fontsize=12)
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
        plt.gca().xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        
        plt.grid(True, alpha=0.3, linestyle="--")
        plt.legend()
        plt.tight_layout()
        
        chart_file = f"chart_{currency_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_file, dpi=300, bbox_inches="tight")
        plt.close()
        
        print(f"✅ Grafik saqlandi: {chart_file}")
        return chart_file
    
    except Exception as e:
        print(f"❌ Grafik chizishda xatolik: {e}")
        return None


def cleanup_chart(chart_file: str) -> None:
    """
    Grafik faylni o'chirish
    
    Args:
        chart_file: Grafik fayl yo'li
    """
    try:
        if os.path.exists(chart_file):
            os.remove(chart_file)
            print(f"✅ Grafik o'chirildi: {chart_file}")
    except Exception as e:
        print(f"❌ Grafik o'chirishda xatolik: {e}")