#!/usr/bin/env python3
"""
Compile .po files to .mo files using Python.
"""

import os
import subprocess
import sys
from pathlib import Path

def compile_po_to_mo(po_file: Path, mo_file: Path):
    """Compile a .po file to .mo file using Python's gettext tools."""
    try:
        # Try using msgfmt if available
        result = subprocess.run(['msgfmt', str(po_file), '-o', str(mo_file)], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Compiled {po_file} -> {mo_file}")
            return True
    except FileNotFoundError:
        pass
    
    # Fallback: use Python to compile
    try:
        import polib
        
        # Load .po file
        po = polib.pofile(str(po_file))
        
        # Save as .mo file
        po.save_as_mofile(str(mo_file))
        print(f"✅ Compiled {po_file} -> {mo_file} (using polib)")
        return True
        
    except ImportError:
        print("❌ Neither msgfmt nor polib available. Installing polib...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'polib'], check=True)
        
        # Try again
        import polib
        po = polib.pofile(str(po_file))
        po.save_as_mofile(str(mo_file))
        print(f"✅ Compiled {po_file} -> {mo_file} (using polib)")
        return True

def main():
    """Compile all .po files in the locale directory."""
    locale_dir = Path(__file__).parent / 'locale'
    
    for lang_dir in locale_dir.iterdir():
        if lang_dir.is_dir():
            lc_messages_dir = lang_dir / 'LC_MESSAGES'
            if lc_messages_dir.exists():
                po_file = lc_messages_dir / 'salary_compare.po'
                mo_file = lc_messages_dir / 'salary_compare.mo'
                
                if po_file.exists():
                    compile_po_to_mo(po_file, mo_file)
                else:
                    print(f"⚠️  No .po file found in {lc_messages_dir}")

if __name__ == "__main__":
    main()
