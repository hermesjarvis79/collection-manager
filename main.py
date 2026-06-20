"""
Collection Manager — Main Entry Point
"""

import sys
import os

# Ensure the project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import main

if __name__ == "__main__":
    main()
