"""Yordamchi funksiyalar"""

from config.languages import LANGUAGES
from config.settings import DEFAULT_LANGUAGE

# Foydalanuvchi tilini saqlash
USER_LANGUAGES = {}


def get_user_language(user_id: int) -> str:
    """Foydalanuvchi tilini olish"""
    return USER_LANGUAGES.get(user_id, DEFAULT_LANGUAGE)


def set_user_language(user_id: int, language: str) -> None:
    """Foydalanuvchi tilini o'rnatish"""
    if language in LANGUAGES:
        USER_LANGUAGES[user_id] = language


def tr(user_id: int, key: str) -> str:
    """Tarjima olish"""
    lang = get_user_language(user_id)
    return LANGUAGES[lang].get(key, key)