"""
Gettext-based translation manager for the Salary Comparison Tool.
"""

import gettext
import os
from pathlib import Path
from typing import Dict, Optional

class TranslationManager:
    """Manages translations using gettext."""
    
    # Available languages
    AVAILABLE_LANGUAGES = {
        'en': 'English',
        'ru': 'Русский',
        'he': 'עברית',
        'ar': 'العربية'
    }
    
    def __init__(self, language: str = 'en', domain: str = 'salary_compare'):
        self.language = language
        self.domain = domain
        self.translations_dir = Path(__file__).parent / 'locale'
        self._translator: Optional[gettext.GNUTranslations] = None
        self._setup_translator()
    
    def _setup_translator(self):
        """Setup gettext translator for the specified language."""
        try:
            # Try to load the translation
            self._translator = gettext.translation(
                self.domain,
                localedir=str(self.translations_dir),
                languages=[self.language],
                fallback=True
            )
            self._translator.install()
        except Exception as e:
            print(f"Warning: Could not load translations for {self.language}: {e}")
            # Fallback to English
            self._translator = gettext.NullTranslations()
            self._translator.install()
    
    def _(self, message: str) -> str:
        """Get translated message."""
        # Avoid passing empty strings to gettext as it returns metadata
        if not message or not message.strip():
            return message
        if self._translator:
            return self._translator.gettext(message)
        return message
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Get translated message with pluralization."""
        if self._translator:
            return self._translator.ngettext(singular, plural, n)
        return singular if n == 1 else plural
    
    def pgettext(self, context: str, message: str) -> str:
        """Get translated message with context."""
        if self._translator:
            return self._translator.pgettext(context, message)
        return message
    
    def get_available_languages(self) -> Dict[str, str]:
        """Get available languages."""
        return self.AVAILABLE_LANGUAGES
    
    def set_language(self, language: str):
        """Change the current language."""
        if language in self.AVAILABLE_LANGUAGES:
            self.language = language
            self._setup_translator()

# Global translation manager
_translation_manager: Optional[TranslationManager] = None

def get_translation_manager() -> TranslationManager:
    """Get the global translation manager."""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager('en')
    return _translation_manager

def set_language(language: str):
    """Set the global language."""
    global _translation_manager
    if _translation_manager is None:
        _translation_manager = TranslationManager(language)
    else:
        _translation_manager.set_language(language)

def _(message: str) -> str:
    """Get translated message (convenience function)."""
    # Avoid passing empty strings to gettext as it returns metadata
    if not message or not message.strip():
        return message
    return get_translation_manager()._(message)
