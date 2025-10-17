"""
Advanced i18n implementation using Python's gettext.
This is the production-ready approach.
"""

import gettext
import os
from pathlib import Path

class GettextTranslationManager:
    """Advanced translation manager using gettext."""
    
    def __init__(self, language: str = 'en', domain: str = 'salary_compare'):
        self.language = language
        self.domain = domain
        self.translations_dir = Path(__file__).parent / 'locale'
        self._setup_gettext()
    
    def _setup_gettext(self):
        """Setup gettext for the specified language."""
        # Create locale directory structure
        locale_dir = self.translations_dir / self.language / 'LC_MESSAGES'
        locale_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up gettext
        self.translator = gettext.translation(
            self.domain,
            localedir=str(self.translations_dir),
            languages=[self.language],
            fallback=True
        )
        self.translator.install()
    
    def _(self, message: str) -> str:
        """Get translated message."""
        return self.translator.gettext(message)
    
    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Get translated message with pluralization."""
        return self.translator.ngettext(singular, plural, n)
    
    def pgettext(self, context: str, message: str) -> str:
        """Get translated message with context."""
        return self.translator.pgettext(context, message)

# Example usage:
# translator = GettextTranslationManager('es')
# print(translator._("Hello"))  # "Hola"
# print(translator.ngettext("1 item", "{} items", 5).format(5))  # "5 elementos"
