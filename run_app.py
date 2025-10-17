#!/usr/bin/env python3
"""
Convenience script to run the Salary Comparison Tool.
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app."""
    print("🚀 Starting Salary Comparison Tool...")
    print("📱 Opening in your default browser...")
    print("🌍 Available languages: English, Русский, עברית, العربية")
    print("💡 Tip: Use Ctrl+C to stop the app")
    print("-" * 50)
    
    try:
        # Run the streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app/main.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running app: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install dependencies:")
        print("   make install")
        sys.exit(1)

if __name__ == "__main__":
    main()
