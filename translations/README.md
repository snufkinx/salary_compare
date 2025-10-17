# Translation System for Salary Comparison Tool

This directory contains the internationalization (i18n) system for the Salary Comparison Tool.

## 🌍 Supported Languages

- **English (en)** - Default
- **Spanish (es)** - Español
- **French (fr)** - Français  
- **German (de)** - Deutsch
- **Italian (it)** - Italiano
- **Portuguese (pt)** - Português
- **Czech (cs)** - Čeština
- **Hebrew (he)** - עברית
- **Romanian (ro)** - Română
- **Bulgarian (bg)** - Български

## 🚀 Quick Start

### Simple Dictionary Approach (Current)
```python
from translations.i18n import set_language, _

# Set language
set_language('es')

# Use translations
title = _('app_title')  # "Herramienta de Comparación Salarial"
```

### Advanced Gettext Approach (Production)
```python
from translations.gettext_example import GettextTranslationManager

# Setup translator
translator = GettextTranslationManager('es')

# Use translations
title = translator._('app_title')
```

## 📁 File Structure

```
translations/
├── __init__.py              # Module initialization
├── i18n.py                  # Simple dictionary-based translations
├── gettext_example.py       # Advanced gettext implementation
├── manage_translations.py   # Translation management tools
├── README.md               # This file
└── locale/                 # Gettext locale files (when using gettext)
    ├── en/LC_MESSAGES/
    ├── es/LC_MESSAGES/
    └── ...
```

## 🔧 Implementation Approaches

### 1. Simple Dictionary Approach (Recommended for Start)
- **Pros**: Easy to implement, no external dependencies
- **Cons**: No pluralization, manual key management
- **Best for**: Small projects, quick implementation

### 2. Gettext Approach (Production Ready)
- **Pros**: Industry standard, pluralization support, professional tools
- **Cons**: More complex setup, requires .po files
- **Best for**: Large projects, professional deployment

## 🛠️ Adding New Languages

### For Dictionary Approach:
1. Add language to `AVAILABLE_LANGUAGES` in `i18n.py`
2. Add translation dictionary in `_get_translation_dict()`
3. Test with `set_language('new_lang')`

### For Gettext Approach:
1. Create `.po` files in `locale/new_lang/LC_MESSAGES/`
2. Compile with `msgfmt` command
3. Add language to available languages

## 📝 Adding New Translatable Strings

1. **In your code**: Use `_('your_key')` instead of hardcoded strings
2. **Add to translations**: Add the key to all language dictionaries
3. **Test**: Verify the translation appears correctly

## 🎯 Best Practices

1. **Use descriptive keys**: `'gross_salary'` not `'gs'`
2. **Keep keys consistent**: Use snake_case throughout
3. **Context matters**: Use `pgettext()` for ambiguous strings
4. **Pluralization**: Use `ngettext()` for count-dependent strings
5. **Fallback**: Always provide English fallback

## 🔍 Example Usage in Streamlit

```python
import streamlit as st
from translations.i18n import set_language, _

# Language selector in sidebar
with st.sidebar:
    language = st.selectbox("Language", ["en", "es", "fr"])
    set_language(language)

# Use translations throughout the app
st.title(_('app_title'))
st.markdown(_('app_description'))

# In tables
summary_data = [{
    _('country'): result.country,
    _('gross_annual'): f"€{result.gross_salary:,.0f}",
    # ...
}]
```

## 🚀 Migration Path

1. **Start Simple**: Use dictionary approach for quick implementation
2. **Add Languages**: Gradually add more languages
3. **Scale Up**: Migrate to gettext when needed
4. **Professional**: Use translation services for large-scale deployment

## 📚 External Resources

- [Python gettext documentation](https://docs.python.org/3/library/gettext.html)
- [GNU gettext manual](https://www.gnu.org/software/gettext/manual/)
- [Streamlit internationalization guide](https://docs.streamlit.io/library/advanced-features/configuration)
