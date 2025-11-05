"""
Database module for storing users, inventory, and bills
Automatically uses Firebase Firestore if available, otherwise falls back to JSON file storage
"""

import json
import os
from datetime import datetime, timedelta
from config import DATA_DIR, BILLS_DIR, DEFAULT_CREDENTIALS

DATABASE_FILE = os.path.join(DATA_DIR, "database.json")

# Try to use Firebase first, fall back to JSON if not available
db = None
try:
    from database_firebase import db, DATABASE_TYPE
    if DATABASE_TYPE == 'firebase' and db is not None:
        # Firebase is being used
        print("Connected to Firebase Firestore")
    else:
        # Firebase import failed, use JSON
        raise ImportError("Firebase not configured")
except (ImportError, AttributeError, Exception) as e:
    # Fall back to JSON database - define Database class below
    db = None
    # Log error for debugging if verbose mode
    import sys
    if '--debug' in sys.argv or '--verbose' in sys.argv:
        print(f"Firebase import failed, using JSON: {str(e)}")

class Database:
    """Simple JSON-based database for demo purposes"""
    
    def __init__(self):
        self.data = self._load_data()
        self._initialize_default_data()
    
    def _load_data(self):
        """Load data from JSON file"""
        if os.path.exists(DATABASE_FILE):
            try:
                with open(DATABASE_FILE, 'r') as f:
                    return json.load(f)
            except:
                return self._get_default_structure()
        return self._get_default_structure()
    
    def _get_default_structure(self):
        """Return default database structure"""
        return {
            'users': [],
            'inventory': [],
            'bills': [],
            'staff': []
        }
    
    def _initialize_default_data(self):
        """Initialize with default data if empty"""
        # Check if admin user exists and update credentials if needed
        admin_user = None
        for user in self.data['users']:
            if user.get('role') == 'admin':
                admin_user = user
                break
        
        if admin_user:
            # Update existing admin credentials to match config
            admin_user['username'] = DEFAULT_CREDENTIALS['admin']['username']
            admin_user['password'] = DEFAULT_CREDENTIALS['admin']['password']
            admin_user['name'] = DEFAULT_CREDENTIALS['admin']['name']
        else:
            # Add default users if empty
            if not self.data['users']:
                self.data['users'] = []
            
            # Add admin user
            self.data['users'].append({
                'id': 1,
                'username': DEFAULT_CREDENTIALS['admin']['username'],
                'password': DEFAULT_CREDENTIALS['admin']['password'],
                'role': 'admin',
                'name': DEFAULT_CREDENTIALS['admin']['name']
            })
        
        # Check if default staff user exists
        staff_exists = any(user.get('role') == 'staff' and user.get('username') == DEFAULT_CREDENTIALS['staff']['username'] 
                          for user in self.data['users'])
        
        if not staff_exists:
            # Add default staff user
            new_staff_id = max([u['id'] for u in self.data['users']], default=0) + 1
            self.data['users'].append({
                'id': new_staff_id,
                'username': DEFAULT_CREDENTIALS['staff']['username'],
                'password': DEFAULT_CREDENTIALS['staff']['password'],
                'role': 'staff',
                'name': DEFAULT_CREDENTIALS['staff']['name']
            })
        
        # Add sample inventory if empty
        if not self.data['inventory']:
            self.data['inventory'] = [
                {'id': 1, 'name': 'T-Shirt', 'category': 'Tops', 'price': 29.99, 'stock': 50},
                {'id': 2, 'name': 'Jeans', 'category': 'Bottoms', 'price': 79.99, 'stock': 30},
                {'id': 3, 'name': 'Jacket', 'category': 'Outerwear', 'price': 129.99, 'stock': 20},
                {'id': 4, 'name': 'Dress', 'category': 'Dresses', 'price': 59.99, 'stock': 25},
                {'id': 5, 'name': 'Sneakers', 'category': 'Footwear', 'price': 89.99, 'stock': 40},
                {'id': 6, 'name': 'Cap', 'category': 'Accessories', 'price': 19.99, 'stock': 60},
            ]
        
        self.save()
    
    def save(self):
        """Save data to JSON file"""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATABASE_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    # User management
    def authenticate_user(self, username, password, role):
        """Authenticate user by username, password, and role"""
        for user in self.data['users']:
            if (user['username'] == username and 
                user['password'] == password and 
                user['role'] == role):
                return user
        return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        for user in self.data['users']:
            if user['id'] == user_id:
                return user
        return None
    
    def add_user(self, username, password, role, name):
        """Add a new user"""
        new_id = max([u['id'] for u in self.data['users']], default=0) + 1
        user = {
            'id': new_id,
            'username': username,
            'password': password,
            'role': role,
            'name': name
        }
        self.data['users'].append(user)
        self.save()
        return user
    
    def get_all_users(self, role=None):
        """Get all users, optionally filtered by role"""
        if role:
            return [u for u in self.data['users'] if u['role'] == role]
        return self.data['users']
    
    # Inventory management
    def get_all_inventory(self):
        """Get all inventory items"""
        return self.data['inventory']
    
    def get_inventory_item(self, item_id):
        """Get inventory item by ID"""
        for item in self.data['inventory']:
            if item['id'] == item_id:
                return item
        return None
    
    def add_inventory_item(self, name, category, price, stock):
        """Add new inventory item"""
        new_id = max([i['id'] for i in self.data['inventory']], default=0) + 1
        item = {
            'id': new_id,
            'name': name,
            'category': category,
            'price': float(price),
            'stock': int(stock)
        }
        self.data['inventory'].append(item)
        self.save()
        return item
    
    def update_inventory_item(self, item_id, **kwargs):
        """Update inventory item"""
        for item in self.data['inventory']:
            if item['id'] == item_id:
                item.update(kwargs)
                self.save()
                return item
        return None
    
    def delete_inventory_item(self, item_id):
        """Delete inventory item"""
        self.data['inventory'] = [i for i in self.data['inventory'] if i['id'] != item_id]
        self.save()
    
    def update_stock(self, item_id, quantity_change):
        """Update stock quantity for an item"""
        item = self.get_inventory_item(item_id)
        if item:
            item['stock'] = max(0, item['stock'] + quantity_change)
            self.save()
            return True
        return False
    
    # Bill management
    def create_bill(self, user_id, items, total, payment_method='Cash'):
        """Create a new bill"""
        # Get numeric ID (stored internally for compatibility)
        # Handle both old format (numeric id) and new format (DR0201 with numeric_id)
        max_numeric_id = 0
        for b in self.data['bills']:
            if 'numeric_id' in b:
                max_numeric_id = max(max_numeric_id, b['numeric_id'])
            elif isinstance(b.get('id'), (int, float)):
                max_numeric_id = max(max_numeric_id, int(b.get('id', 0)))
            elif isinstance(b.get('id'), str) and b.get('id', '').startswith('DR'):
                try:
                    num_id = int(b.get('id', '0').replace('DR', '').strip())
                    max_numeric_id = max(max_numeric_id, num_id)
                except (ValueError, AttributeError):
                    pass
        new_numeric_id = max_numeric_id + 1
        # Format as DR0201 (DR + 4-digit number with leading zeros)
        new_id = f"DR{str(new_numeric_id).zfill(4)}"
        bill = {
            'id': new_id,  # Formatted ID like DR0201
            'numeric_id': new_numeric_id,  # Keep numeric ID for sorting/searching
            'user_id': user_id,
            'date': datetime.now().isoformat(),
            'items': items,
            'total': float(total),
            'payment_method': payment_method
        }
        self.data['bills'].append(bill)
        
        # Update monthly sales for items
        self._update_monthly_sales(items)
        
        self.save()
        return bill
    
    def _update_monthly_sales(self, items):
        """Update monthly sales quantity for items"""
        current_month = datetime.now().strftime('%Y-%m')
        
        # Initialize monthly_sales if not exists
        if 'monthly_sales' not in self.data:
            self.data['monthly_sales'] = {}
        
        if current_month not in self.data['monthly_sales']:
            self.data['monthly_sales'][current_month] = {}
        
        for item in items:
            item_id = item.get('inventory_id')
            if item_id:
                item_key = str(item_id)
                if item_key not in self.data['monthly_sales'][current_month]:
                    self.data['monthly_sales'][current_month][item_key] = 0
                self.data['monthly_sales'][current_month][item_key] += item['quantity']
    
    def get_item_monthly_sales(self, item_id, month=None):
        """Get monthly sales quantity for an item"""
        if 'monthly_sales' not in self.data:
            return 0
        
        if month is None:
            month = datetime.now().strftime('%Y-%m')
        
        if month not in self.data['monthly_sales']:
            return 0
        
        item_key = str(item_id)
        return self.data['monthly_sales'][month].get(item_key, 0)
    
    def get_item_sales_in_range(self, item_id, start_date, end_date):
        """Get item sales quantity in a date range"""
        start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        end = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date
        
        total_quantity = 0
        for bill in self.data['bills']:
            bill_date = datetime.fromisoformat(bill['date'])
            if start <= bill_date <= end:
                for item in bill['items']:
                    if item.get('inventory_id') == item_id:
                        total_quantity += item['quantity']
        
        return total_quantity
    
    def reset_monthly_sales(self):
        """Reset monthly sales (called at start of new month)"""
        current_month = datetime.now().strftime('%Y-%m')
        if 'monthly_sales' not in self.data:
            self.data['monthly_sales'] = {}
        
        # Keep only current month and previous month
        months_to_keep = [
            current_month,
            (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        ]
        self.data['monthly_sales'] = {
            month: data for month, data in self.data['monthly_sales'].items() 
            if month in months_to_keep
        }
        self.save()
    
    def get_all_bills(self):
        """Get all bills"""
        return self.data['bills']
    
    def get_bill(self, bill_id):
        """Get bill by ID (supports both DR0201 format and numeric)"""
        for bill in self.data['bills']:
            if bill['id'] == bill_id:
                return bill
            # Also check numeric_id for compatibility
            if bill.get('numeric_id') and isinstance(bill_id, (int, float)):
                if bill.get('numeric_id') == int(bill_id):
                    return bill
        return None
    
    def get_bills_by_user(self, user_id):
        """Get all bills created by a specific user"""
        return [b for b in self.data['bills'] if b['user_id'] == user_id]
    
    def delete_bill(self, bill_id):
        """Delete a bill by ID (supports both DR0201 format and numeric)"""
        original_count = len(self.data['bills'])
        self.data['bills'] = [b for b in self.data['bills'] if b['id'] != bill_id and b.get('numeric_id') != bill_id]
        if len(self.data['bills']) < original_count:
            self.save()
            return True
        return False

# Global database instance (will be Firebase if available, otherwise JSON)
if db is None:
    # Create JSON database instance
    db = Database()
    print("Using JSON database (Firebase not configured)")
