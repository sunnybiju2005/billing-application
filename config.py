"""
Configuration settings for DROP billing application
"""

import os

# Application settings
APP_NAME = "DROP Billing System"
APP_VERSION = "1.0.0"
SHOP_NAME = "DROP"
SHOP_TAGLINE = "DRESS FOR LESS"
SHOP_ADDRESS = "City center, Naikkanal, Thrissur, Kerala 680001"

# File paths
DATA_DIR = "data"
BILLS_DIR = os.path.join(DATA_DIR, "bills")
RECEIPTS_DIR = os.path.join(DATA_DIR, "receipts")

# Create directories if they don't exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(BILLS_DIR, exist_ok=True)
os.makedirs(RECEIPTS_DIR, exist_ok=True)

# Default theme (can be 'light' or 'dark')
DEFAULT_THEME = 'light'

# Default bill settings (for thermal printer)
DEFAULT_BILL_WIDTH_MM = 80  # 80mm width (standard thermal receipt)
DEFAULT_BILL_HEIGHT_MM = 210  # 210mm height (standard thermal receipt)
DEFAULT_CHARACTER_WIDTH = 48  # Characters per line for thermal printer

# Paper width presets (in mm)
PAPER_WIDTH_PRESETS = {
    '80mm': 80,
    'Full': 100,  # Full width option
    'Custom': None
}

# Default alignment settings
DEFAULT_ALIGNMENT = 'Left'  # Options: 'Left', 'Center', 'Full'

# Default margin settings (in pixels, minimal for thermal printers)
DEFAULT_MARGIN_TOP = 0
DEFAULT_MARGIN_BOTTOM = 0
DEFAULT_MARGIN_LEFT = 0
DEFAULT_MARGIN_RIGHT = 0

# Column width options for 80mm paper
COLUMN_WIDTH_OPTIONS_80MM = [48, 56, 72]

# Default credentials (for demo purposes)
DEFAULT_CREDENTIALS = {
    'admin': {
        'username': 'DROP',
        'password': '072024',
        'role': 'admin',
        'name': 'Administrator'
    },
    'staff': {
        'username': 'staff',
        'password': 'staff123',
        'role': 'staff',
        'name': 'Staff Member'
    }
}

