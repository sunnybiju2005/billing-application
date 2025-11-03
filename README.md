# DROP - Desktop Billing Application

## Database Support

The application supports **two database backends**:
- **Firebase Firestore** (Cloud database) - Recommended for production
- **JSON File** (Local storage) - Default fallback

See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for Firebase configuration instructions.

A comprehensive desktop billing application for a clothing shop named "DROP", built with Python and Tkinter.

## Features

### Core Functionality
- **Login System**: Secure login with separate Admin and Staff roles
- **Admin Panel**: Complete management capabilities including:
  - Inventory management (add, edit, delete items)
  - Bill management (view, delete bills)
  - Staff management (add, delete staff members)
  - Sales reports and statistics
- **Staff Panel**: Billing and viewing capabilities including:
  - Create new bills with easy item entry
  - View own billing history
  - Basic inventory viewing (read-only)
- **Billing Module**: 
  - Add items from inventory or custom items
  - Real-time bill preview
  - Automatic total calculation
  - Receipt generation and printing
- **Theme Support**: Light and dark theme options (Press Ctrl+T to toggle)

## Requirements

- Python 3.7 or higher
- tkinter (usually comes pre-installed with Python)

### Installation on Linux
If tkinter is not available:
```bash
sudo apt-get install python3-tk
```

## Installation

1. Clone or download this repository
2. Ensure Python 3.7+ is installed
3. No additional packages required (uses Python standard library only)

## Usage

### Starting the Application

```bash
python main.py
```

### Default Credentials

**Admin Login:**
- Username: `admin`
- Password: `admin123`

**Staff Login:**
- Username: `staff`
- Password: `staff123`

### Keyboard Shortcuts

- `Ctrl + T`: Toggle between light and dark theme

## Project Structure

```
billing-application/
├── main.py                 # Application entry point
├── config.py               # Configuration settings
├── database.py             # Mock database (JSON-based)
├── theme_manager.py        # Theme management
├── login_screen.py         # Login interface
├── admin_panel.py          # Admin dashboard
├── staff_panel.py          # Staff dashboard
├── billing_module.py       # Billing functionality
├── receipt_generator.py    # Receipt and report generation
├── requirements.txt        # Dependencies (none required)
├── README.md              # This file
└── data/                  # Data directory (created automatically)
    ├── database.json      # JSON database file
    ├── bills/             # Generated reports
    └── receipts/          # Generated receipts
```

## Features in Detail

### Admin Panel

1. **Inventory Management**
   - View all inventory items
   - Add new items with name, category, price, and stock
   - Edit existing items
   - Delete items
   - Real-time stock updates

2. **Bill Management**
   - View all bills with filters (All, Today, This Week, This Month)
   - View detailed bill information
   - Delete bills

3. **Staff Management**
   - View all staff members
   - Add new staff accounts
   - Delete staff accounts

4. **Reports**
   - Sales summary with key statistics
   - Generate detailed sales reports
   - View total sales, bill counts, average values, etc.

### Staff Panel

1. **Create Bill**
   - Select items from inventory dropdown
   - Add custom items manually
   - Real-time bill preview
   - Choose payment method (Cash, Card, Digital Payment)
   - Create bill and optionally print receipt

2. **Billing History**
   - View all bills created by the logged-in staff member
   - View detailed bill information
   - Print receipts for past bills

3. **Inventory View**
   - View all inventory items (read-only)
   - See prices and stock levels

## Data Storage

The application uses a JSON-based database stored in `data/database.json`. This includes:
- User accounts (admin and staff)
- Inventory items
- All bills and transactions

## Receipt Generation

Receipts are generated as text files in the `data/receipts/` directory. Each receipt includes:
- Shop name and bill information
- Itemized list with quantities and prices
- Total amount
- Payment method
- Timestamp

## Printing

Receipts can be printed using the system's default printer:
- Windows: Uses built-in print functionality
- Linux/macOS: Uses standard printing commands

## Customization

### Changing Shop Name
Edit `config.py` and change the `SHOP_NAME` variable.

### Adding Default Inventory
Edit `database.py` in the `_initialize_default_data` method to add more default inventory items.

### Changing Theme Colors
Edit `theme_manager.py` to customize the color schemes for light and dark themes.

## Future Enhancements

Potential improvements:
- Connect to a real database (SQLite, PostgreSQL, etc.)
- Add more detailed reports with charts
- Export reports to PDF/Excel
- Multi-user concurrent access support
- Barcode scanning for items
- Inventory alerts for low stock
- Discount/coupon system
- Tax calculation support

## License

This project is provided as-is for demonstration purposes.

## Support

For issues or questions, please refer to the code comments for implementation details.

---

**Note**: This application uses hardcoded credentials for demonstration purposes. In a production environment, implement proper password hashing and secure authentication.

