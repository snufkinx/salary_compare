#!/usr/bin/env python3
"""
Translation management script.
Helps extract translatable strings and manage translations.
"""

import os
import re
from pathlib import Path

def extract_translatable_strings(file_path: str) -> set:
    """Extract all translatable strings from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all _('...') patterns
    pattern = r"_\(['\"]([^'\"]+)['\"]\)"
    matches = re.findall(pattern, content)
    
    return set(matches)

def generate_translation_template():
    """Generate a template for translations."""
    # Extract strings from app.py
    app_strings = extract_translatable_strings('app.py')
    
    # Create template
    template = {
        'en': {string: string for string in app_strings},
        'es': {string: f"[ES] {string}" for string in app_strings},
        'fr': {string: f"[FR] {string}" for string in app_strings},
        'de': {string: f"[DE] {string}" for string in app_strings},
    }
    
    return template

def create_translation_files():
    """Create translation files for different languages."""
    template = generate_translation_template()
    
    for lang, translations in template.items():
        filename = f"translations_{lang}.py"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f'"""Translations for {lang.upper()}"""\n\n')
            f.write('TRANSLATIONS = {\n')
            for key, value in translations.items():
                f.write(f'    "{key}": "{value}",\n')
            f.write('}\n')
        
        print(f"Created {filename}")

if __name__ == "__main__":
    create_translation_files()
