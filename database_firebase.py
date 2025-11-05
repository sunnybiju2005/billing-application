"""
Firebase Firestore database for storing users, inventory, and bills
Replaces the JSON-based database with Firebase Firestore
"""

import os
from datetime import datetime, timedelta
from config import DEFAULT_CREDENTIALS
from firebase_config import get_firebase_config

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

class FirebaseDatabase:
    """Firebase Firestore database implementation"""
    
    def __init__(self):
        if not FIREBASE_AVAILABLE:
            raise ImportError(
                "firebase-admin is not installed. "
                "Please install it by running: pip install firebase-admin"
            )
        
        self.db = None
        self._initialize_firebase()
        self._initialize_default_data()
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK - ensures only one initialization"""
        config = get_firebase_config()
        credentials_path = config['credentials_path']
        
        # Check if Firebase is already initialized using get_app()
        try:
            firebase_admin.get_app()
            # Firebase is already initialized, just get the client
            self.db = firestore.client()
            return
        except ValueError:
            # Firebase is not initialized yet, proceed with initialization
            pass
        
        # Initialize Firebase Admin SDK (only if not already initialized)
        if os.path.exists(credentials_path):
            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
        elif config.get('project_id'):
            # Initialize without credentials (uses Application Default Credentials)
            firebase_admin.initialize_app()
        else:
            raise FileNotFoundError(
                f"Firebase credentials file not found: {credentials_path}\n"
                "Please download your Firebase service account JSON file and place it in the project root,\n"
                "or set FIREBASE_CREDENTIALS_PATH environment variable.\n"
                "Alternatively, set FIREBASE_PROJECT_ID to use Application Default Credentials."
            )
        
        self.db = firestore.client()
    
    def _get_collection(self, collection_name):
        """Get a Firestore collection reference"""
        return self.db.collection(collection_name)
    
    def _initialize_default_data(self):
        """Initialize with default data if collections are empty"""
        # Check and initialize users
        users_ref = self._get_collection('users')
        admin_users = users_ref.where('role', '==', 'admin').stream()
        
        admin_exists = False
        admin_doc_id = None
        for user_doc in admin_users:
            admin_exists = True
            admin_doc_id = user_doc.id
            break
        
        if admin_exists and admin_doc_id:
            # Update existing admin credentials
            users_ref.document(admin_doc_id).update({
                'username': DEFAULT_CREDENTIALS['admin']['username'],
                'password': DEFAULT_CREDENTIALS['admin']['password'],
                'name': DEFAULT_CREDENTIALS['admin']['name']
            })
        else:
            # Add admin user
            admin_data = {
                'id': 1,
                'username': DEFAULT_CREDENTIALS['admin']['username'],
                'password': DEFAULT_CREDENTIALS['admin']['password'],
                'role': 'admin',
                'name': DEFAULT_CREDENTIALS['admin']['name']
            }
            users_ref.add(admin_data)
        
        # Check and initialize staff user
        staff_users = users_ref.where('role', '==', 'staff').where('username', '==', DEFAULT_CREDENTIALS['staff']['username']).stream()
        staff_exists = any(True for _ in staff_users)
        
        if not staff_exists:
            # Get max user ID
            all_users = users_ref.stream()
            max_id = 0
            for user_doc in all_users:
                user_data = user_doc.to_dict()
                if user_data.get('id', 0) > max_id:
                    max_id = user_data.get('id', 0)
            
            # Add default staff user
            staff_data = {
                'id': max_id + 1,
                'username': DEFAULT_CREDENTIALS['staff']['username'],
                'password': DEFAULT_CREDENTIALS['staff']['password'],
                'role': 'staff',
                'name': DEFAULT_CREDENTIALS['staff']['name']
            }
            users_ref.add(staff_data)
        
        # Initialize sample inventory if empty
        inventory_ref = self._get_collection('inventory')
        inventory_docs = inventory_ref.stream()
        
        if not any(inventory_docs):
            sample_items = [
                {'id': 1, 'name': 'T-Shirt', 'category': 'Tops', 'price': 29.99, 'stock': 50},
                {'id': 2, 'name': 'Jeans', 'category': 'Bottoms', 'price': 79.99, 'stock': 30},
                {'id': 3, 'name': 'Jacket', 'category': 'Outerwear', 'price': 129.99, 'stock': 20},
                {'id': 4, 'name': 'Dress', 'category': 'Dresses', 'price': 59.99, 'stock': 25},
                {'id': 5, 'name': 'Sneakers', 'category': 'Footwear', 'price': 89.99, 'stock': 40},
                {'id': 6, 'name': 'Cap', 'category': 'Accessories', 'price': 19.99, 'stock': 60},
            ]
            
            for item in sample_items:
                inventory_ref.add(item)
    
    # User management
    def authenticate_user(self, username, password, role):
        """Authenticate user by username, password, and role"""
        users_ref = self._get_collection('users')
        query = users_ref.where('username', '==', username).where('role', '==', role).stream()
        
        for user_doc in query:
            user_data = user_doc.to_dict()
            if user_data.get('password') == password:
                return user_data
        return None
    
    def get_user(self, user_id):
        """Get user by ID"""
        users_ref = self._get_collection('users')
        query = users_ref.where('id', '==', user_id).stream()
        
        for user_doc in query:
            return user_doc.to_dict()
        return None
    
    def add_user(self, username, password, role, name):
        """Add a new user"""
        users_ref = self._get_collection('users')
        
        # Get max user ID
        all_users = users_ref.stream()
        max_id = 0
        for user_doc in all_users:
            user_data = user_doc.to_dict()
            if user_data.get('id', 0) > max_id:
                max_id = user_data.get('id', 0)
        
        new_id = max_id + 1
        user_data = {
            'id': new_id,
            'username': username,
            'password': password,
            'role': role,
            'name': name
        }
        
        doc_ref = users_ref.add(user_data)
        return user_data
    
    def get_all_users(self, role=None):
        """Get all users, optionally filtered by role"""
        users_ref = self._get_collection('users')
        
        if role:
            query = users_ref.where('role', '==', role).stream()
        else:
            query = users_ref.stream()
        
        return [doc.to_dict() for doc in query]
    
    # Inventory management
    def get_all_inventory(self):
        """Get all inventory items"""
        inventory_ref = self._get_collection('inventory')
        return [doc.to_dict() for doc in inventory_ref.stream()]
    
    def get_inventory_item(self, item_id):
        """Get inventory item by ID"""
        inventory_ref = self._get_collection('inventory')
        query = inventory_ref.where('id', '==', item_id).stream()
        
        for item_doc in query:
            return item_doc.to_dict()
        return None
    
    def add_inventory_item(self, name, category, price, stock):
        """Add new inventory item"""
        inventory_ref = self._get_collection('inventory')
        
        # Get max item ID
        all_items = inventory_ref.stream()
        max_id = 0
        for item_doc in all_items:
            item_data = item_doc.to_dict()
            if item_data.get('id', 0) > max_id:
                max_id = item_data.get('id', 0)
        
        new_id = max_id + 1
        item_data = {
            'id': new_id,
            'name': name,
            'category': category,
            'price': float(price),
            'stock': int(stock)
        }
        
        inventory_ref.add(item_data)
        return item_data
    
    def update_inventory_item(self, item_id, **kwargs):
        """Update inventory item"""
        inventory_ref = self._get_collection('inventory')
        query = inventory_ref.where('id', '==', item_id).stream()
        
        for item_doc in query:
            item_doc.reference.update(kwargs)
            # Return updated data
            updated_data = item_doc.to_dict()
            updated_data.update(kwargs)
            return updated_data
        return None
    
    def delete_inventory_item(self, item_id):
        """Delete inventory item"""
        inventory_ref = self._get_collection('inventory')
        query = inventory_ref.where('id', '==', item_id).stream()
        
        for item_doc in query:
            item_doc.reference.delete()
            return True
        return False
    
    def update_stock(self, item_id, quantity_change):
        """Update stock quantity for an item"""
        item = self.get_inventory_item(item_id)
        if item:
            new_stock = max(0, item['stock'] + quantity_change)
            self.update_inventory_item(item_id, stock=new_stock)
            return True
        return False
    
    # Bill management
    def create_bill(self, user_id, items, total, payment_method='Cash'):
        """Create a new bill"""
        bills_ref = self._get_collection('bills')
        
        # Get max numeric ID from all bills
        all_bills = bills_ref.stream()
        max_numeric_id = 0
        for bill_doc in all_bills:
            bill_data = bill_doc.to_dict()
            # Check for numeric_id first, then fall back to extracting from id
            numeric_id = bill_data.get('numeric_id', 0)
            if numeric_id == 0 and isinstance(bill_data.get('id'), str):
                # Extract number from format like DR0201
                try:
                    numeric_id = int(bill_data.get('id', '0').replace('DR', ''))
                except (ValueError, AttributeError):
                    numeric_id = 0
            if numeric_id > max_numeric_id:
                max_numeric_id = numeric_id
        
        new_numeric_id = max_numeric_id + 1
        # Format as DR0201 (DR + 4-digit number with leading zeros)
        new_id = f"DR{str(new_numeric_id).zfill(4)}"
        bill_data = {
            'id': new_id,  # Formatted ID like DR0201
            'numeric_id': new_numeric_id,  # Keep numeric ID for sorting/searching
            'user_id': user_id,
            'date': datetime.now().isoformat(),
            'items': items,
            'total': float(total),
            'payment_method': payment_method
        }
        
        bills_ref.add(bill_data)
        
        # Update monthly sales for items
        self._update_monthly_sales(items)
        
        return bill_data
    
    def _update_monthly_sales(self, items):
        """Update monthly sales quantity for items"""
        current_month = datetime.now().strftime('%Y-%m')
        monthly_sales_ref = self._get_collection('monthly_sales')
        
        # Get or create month document
        month_doc_ref = monthly_sales_ref.document(current_month)
        month_doc = month_doc_ref.get()
        
        if not month_doc.exists:
            month_data = {}
        else:
            month_data = month_doc.to_dict() or {}
        
        for item in items:
            item_id = item.get('inventory_id')
            if item_id:
                item_key = str(item_id)
                current_qty = month_data.get(item_key, 0)
                month_data[item_key] = current_qty + item['quantity']
        
        month_doc_ref.set(month_data)
    
    def get_item_monthly_sales(self, item_id, month=None):
        """Get monthly sales quantity for an item"""
        if month is None:
            month = datetime.now().strftime('%Y-%m')
        
        monthly_sales_ref = self._get_collection('monthly_sales')
        month_doc = monthly_sales_ref.document(month).get()
        
        if not month_doc.exists:
            return 0
        
        month_data = month_doc.to_dict() or {}
        item_key = str(item_id)
        return month_data.get(item_key, 0)
    
    def get_item_sales_in_range(self, item_id, start_date, end_date):
        """Get item sales quantity in a date range"""
        start = datetime.fromisoformat(start_date) if isinstance(start_date, str) else start_date
        end = datetime.fromisoformat(end_date) if isinstance(end_date, str) else end_date
        
        bills_ref = self._get_collection('bills')
        # Note: Firestore requires a composite index for range queries on 'date'
        # If index doesn't exist, filter in memory (slower but works)
        try:
            query = bills_ref.where('date', '>=', start.isoformat()).where('date', '<=', end.isoformat()).stream()
        except Exception:
            # If query fails (no index), get all bills and filter in memory
            query = bills_ref.stream()
        
        total_quantity = 0
        for bill_doc in query:
            bill_data = bill_doc.to_dict()
            bill_date = datetime.fromisoformat(bill_data.get('date', ''))
            if start <= bill_date <= end:
                for item in bill_data.get('items', []):
                    if item.get('inventory_id') == item_id:
                        total_quantity += item['quantity']
        
        return total_quantity
    
    def reset_monthly_sales(self):
        """Reset monthly sales (called at start of new month)"""
        current_month = datetime.now().strftime('%Y-%m')
        prev_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        
        monthly_sales_ref = self._get_collection('monthly_sales')
        all_months = monthly_sales_ref.stream()
        
        for month_doc in all_months:
            month_id = month_doc.id
            if month_id not in [current_month, prev_month]:
                month_doc.reference.delete()
    
    def get_all_bills(self):
        """Get all bills"""
        bills_ref = self._get_collection('bills')
        return [doc.to_dict() for doc in bills_ref.stream()]
    
    def get_bill(self, bill_id):
        """Get bill by ID (supports both DR0201 format and numeric)"""
        bills_ref = self._get_collection('bills')
        # Try exact match first
        query = bills_ref.where('id', '==', bill_id).stream()
        for bill_doc in query:
            return bill_doc.to_dict()
        # Try numeric_id if bill_id is numeric
        if isinstance(bill_id, (int, float)):
            query = bills_ref.where('numeric_id', '==', int(bill_id)).stream()
            for bill_doc in query:
                return bill_doc.to_dict()
        return None
    
    def get_bills_by_user(self, user_id):
        """Get all bills created by a specific user"""
        bills_ref = self._get_collection('bills')
        query = bills_ref.where('user_id', '==', user_id).stream()
        
        return [doc.to_dict() for doc in query]
    
    def delete_bill(self, bill_id):
        """Delete a bill by ID (supports both DR0201 format and numeric)"""
        bills_ref = self._get_collection('bills')
        # Try exact match first
        query = bills_ref.where('id', '==', bill_id).stream()
        for bill_doc in query:
            bill_doc.reference.delete()
            return True
        # Try numeric_id if bill_id is numeric
        if isinstance(bill_id, (int, float)):
            query = bills_ref.where('numeric_id', '==', int(bill_id)).stream()
            for bill_doc in query:
                bill_doc.reference.delete()
                return True
        return False

# This file exports db only if Firebase is successfully initialized
# The main database.py file will import from here if available, otherwise use JSON
DATABASE_TYPE = None
db = None

try:
    db = FirebaseDatabase()
    DATABASE_TYPE = 'firebase'
except (ImportError, FileNotFoundError, Exception) as e:
    # Firebase not available - let database.py handle the fallback
    DATABASE_TYPE = None
    db = None
    # Don't print here - let database.py handle the messaging

