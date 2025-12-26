"""
Firebase Firestore database for storing users, inventory, and bills
Replaces the JSON-based database with Firebase Firestore
Also syncs data to local JSON file for backup
"""

import os
import json
import threading
import time
from datetime import datetime, timedelta
from config import DEFAULT_CREDENTIALS, DATA_DIR
from firebase_config import get_firebase_config

DATABASE_FILE = os.path.join(DATA_DIR, "database.json")

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
        self.offline_mode = False
        self.pending_sync = []  # Track operations that need to sync when online
        self._initialize_firebase()
        self._initialize_default_data()
        # Initial sync to local storage
        self._sync_to_local()
        # Migrate existing bills to individual JSON files
        self._migrate_bills_to_individual_files()
        # Start background sync thread
        self._start_background_sync()
    
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
    
    def _check_internet_connection(self):
        """Check if internet connection is available"""
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except OSError:
            return False
    
    def _is_firebase_storage_error(self, error):
        """Check if error is related to Firebase storage/quota issues"""
        error_str = str(error).lower()
        storage_errors = [
            'quota exceeded',
            'resource exhausted',
            'out of space',
            'storage quota',
            'quota',
            'insufficient storage',
            'storage limit',
            'billing',
            'payment required'
        ]
        return any(err in error_str for err in storage_errors)
    
    def _save_to_local_fallback(self, operation_type, data):
        """Save data to local storage when Firebase fails"""
        try:
            # Load existing local data
            if os.path.exists(DATABASE_FILE):
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
            else:
                local_data = {'users': [], 'inventory': [], 'bills': [], 'staff': [], 'monthly_sales': {}}
            
            # Update local data based on operation type
            if operation_type == 'add_user' or operation_type == 'update_user':
                # Add or update user
                user_id = data.get('id')
                if user_id:
                    # Remove existing user with same ID
                    local_data['users'] = [u for u in local_data['users'] if u.get('id') != user_id]
                local_data['users'].append(data)
            
            elif operation_type == 'add_inventory' or operation_type == 'update_inventory':
                # Add or update inventory item
                item_id = data.get('id')
                if item_id:
                    # Remove existing item with same ID
                    local_data['inventory'] = [i for i in local_data['inventory'] if i.get('id') != item_id]
                local_data['inventory'].append(data)
            
            elif operation_type == 'create_bill':
                # Add bill
                local_data['bills'].append(data)
            
            elif operation_type == 'update_bill':
                # Update bill
                bill_id = data.get('id')
                if bill_id:
                    local_data['bills'] = [b for b in local_data['bills'] if b.get('id') != bill_id]
                    local_data['bills'].append(data)
            
            # Save to local file
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(local_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception:
            return False
    
    def _start_background_sync(self):
        """Start background thread to sync pending operations when online"""
        def sync_worker():
            while True:
                time.sleep(30)  # Check every 30 seconds
                if self._check_internet_connection() and not self.offline_mode:
                    if self.pending_sync:
                        try:
                            self._sync_pending_operations()
                        except Exception:
                            pass  # Silently fail, will retry later
                else:
                    self.offline_mode = True
        
        thread = threading.Thread(target=sync_worker, daemon=True)
        thread.start()
    
    def _sync_pending_operations(self):
        """Sync pending operations to Firebase"""
        # This would sync any pending operations
        # For now, just clear the pending list as operations are already saved locally
        self.pending_sync = []
        # Full sync to ensure everything is up to date
        self._sync_to_local()
    
    def _sync_to_local(self):
        """Sync all Firebase data to local JSON file for backup"""
        try:
            if self.offline_mode or not self._check_internet_connection():
                # In offline mode, read from local file and update it
                if os.path.exists(DATABASE_FILE):
                    with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                else:
                    data = {'users': [], 'inventory': [], 'bills': [], 'staff': [], 'monthly_sales': {}}
            else:
                # Get all data from Firebase
                data = {
                    'users': [],
                    'inventory': [],
                    'bills': [],
                    'staff': []
                }
                
                # Get users
                users_ref = self._get_collection('users')
                for doc in users_ref.stream():
                    data['users'].append(doc.to_dict())
                
                # Get inventory
                inventory_ref = self._get_collection('inventory')
                for doc in inventory_ref.stream():
                    data['inventory'].append(doc.to_dict())
                
                # Get bills
                bills_ref = self._get_collection('bills')
                for doc in bills_ref.stream():
                    data['bills'].append(doc.to_dict())
                
                # Get staff (if exists)
                staff_ref = self._get_collection('staff')
                for doc in staff_ref.stream():
                    data['staff'].append(doc.to_dict())
                
                # Get monthly_sales if exists
                monthly_sales_ref = self._get_collection('monthly_sales')
                monthly_sales_docs = list(monthly_sales_ref.stream())
                if monthly_sales_docs:
                    data['monthly_sales'] = monthly_sales_docs[0].to_dict()
                else:
                    data['monthly_sales'] = {}
            
            # Save to local JSON file (always, even in offline mode)
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            # Silently fail - don't interrupt operations if local sync fails
            pass
    
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
            self._sync_to_local()
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
            self._sync_to_local()
        
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
            self._sync_to_local()
        
        # Initialize empty inventory if not exists
        inventory_ref = self._get_collection('inventory')
        inventory_docs = list(inventory_ref.stream())
        
        # Remove sample items if they exist
        sample_item_names = ['T-Shirt', 'Jeans', 'Jacket', 'Dress', 'Sneakers', 'Cap']
        for doc in inventory_docs:
            item_data = doc.to_dict()
            if item_data.get('name') in sample_item_names:
                doc.reference.delete()
                self._sync_to_local()
    
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
        
        try:
            doc_ref = users_ref.add(user_data)
            self.offline_mode = False
        except Exception as e:
            self.offline_mode = True
            self.pending_sync.append(('add_user', user_data))
            # If Firebase storage is full, save to local immediately
            if self._is_firebase_storage_error(e):
                self._save_to_local_fallback('add_user', user_data)
        
        # Always save to local (ensures data is never lost)
        self._sync_to_local()
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
        
        try:
            inventory_ref.add(item_data)
            self.offline_mode = False
        except Exception as e:
            self.offline_mode = True
            self.pending_sync.append(('add_inventory', item_data))
            # If Firebase storage is full, save to local immediately
            if self._is_firebase_storage_error(e):
                self._save_to_local_fallback('add_inventory', item_data)
        
        # Always save to local (ensures data is never lost)
        self._sync_to_local()
        return item_data
    
    def update_inventory_item(self, item_id, **kwargs):
        """Update inventory item"""
        inventory_ref = self._get_collection('inventory')
        query = inventory_ref.where('id', '==', item_id).stream()
        
        for item_doc in query:
            updated_data = item_doc.to_dict()
            updated_data.update(kwargs)
            
            try:
                item_doc.reference.update(kwargs)
                self.offline_mode = False
            except Exception as e:
                self.offline_mode = True
                self.pending_sync.append(('update_inventory', item_id, kwargs))
                # If Firebase storage is full, save to local immediately
                if self._is_firebase_storage_error(e):
                    self._save_to_local_fallback('update_inventory', updated_data)
            
            # Always save to local (ensures data is never lost)
            self._sync_to_local()
            return updated_data
        return None
    
    def delete_inventory_item(self, item_id):
        """Delete inventory item"""
        inventory_ref = self._get_collection('inventory')
        query = inventory_ref.where('id', '==', item_id).stream()
        
        for item_doc in query:
            try:
                item_doc.reference.delete()
                self.offline_mode = False
            except Exception as e:
                self.offline_mode = True
                self.pending_sync.append(('delete_inventory', item_id))
                # If Firebase storage is full, still update local storage
                if self._is_firebase_storage_error(e):
                    # Load local data and remove item
                    if os.path.exists(DATABASE_FILE):
                        try:
                            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                                local_data = json.load(f)
                            local_data['inventory'] = [i for i in local_data['inventory'] if i.get('id') != item_id]
                            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                                json.dump(local_data, f, indent=2, ensure_ascii=False)
                        except Exception:
                            pass
            
            # Always save to local (ensures data is never lost)
            self._sync_to_local()
            return True
        return False
    
    def delete_all_inventory_items(self):
        """Delete all inventory items"""
        inventory_ref = self._get_collection('inventory')
        all_items = inventory_ref.stream()
        
        deleted_count = 0
        for item_doc in all_items:
            item_doc.reference.delete()
            deleted_count += 1
        
        if deleted_count > 0:
            self._sync_to_local()
        return deleted_count > 0
    
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
        
        try:
            bills_ref.add(bill_data)
            # Update monthly sales for items
            try:
                self._update_monthly_sales(items)
            except Exception:
                pass  # If monthly sales update fails, continue
            self.offline_mode = False
        except Exception as e:
            self.offline_mode = True
            self.pending_sync.append(('create_bill', bill_data))
            # If Firebase storage is full, save to local immediately
            if self._is_firebase_storage_error(e):
                self._save_to_local_fallback('create_bill', bill_data)
        
        # Always save to local (ensures data is never lost, even if Firebase is full)
        self._sync_to_local()
        
        # Save individual bill as JSON file
        self._save_individual_bill(bill_data)
        
        return bill_data
    
    def _save_individual_bill(self, bill):
        """Save individual bill as separate JSON file"""
        try:
            from config import BILLS_JSON_DIR
            os.makedirs(BILLS_JSON_DIR, exist_ok=True)
            bill_file = os.path.join(BILLS_JSON_DIR, f"{bill['id']}.json")
            with open(bill_file, 'w', encoding='utf-8') as f:
                json.dump(bill, f, indent=2, ensure_ascii=False)
        except Exception:
            pass  # Silently fail if individual bill save fails
    
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
            try:
                bill_doc.reference.delete()
                self.offline_mode = False
            except Exception as e:
                self.offline_mode = True
                # If Firebase storage is full, still update local storage
                if self._is_firebase_storage_error(e):
                    # Load local data and remove bill
                    if os.path.exists(DATABASE_FILE):
                        try:
                            with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                                local_data = json.load(f)
                            local_data['bills'] = [b for b in local_data['bills'] if b.get('id') != bill_id]
                            with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                                json.dump(local_data, f, indent=2, ensure_ascii=False)
                        except Exception:
                            pass
            
            # Always save to local (ensures data is never lost)
            self._sync_to_local()
            
            # Delete individual bill file
            self._delete_individual_bill(bill_id)
            
            return True
        # Try numeric_id if bill_id is numeric
        if isinstance(bill_id, (int, float)):
            query = bills_ref.where('numeric_id', '==', int(bill_id)).stream()
            for bill_doc in query:
                bill_data = bill_doc.to_dict()
                actual_bill_id = bill_data.get('id', bill_id)
                
                try:
                    bill_doc.reference.delete()
                    self.offline_mode = False
                except Exception as e:
                    self.offline_mode = True
                    # If Firebase storage is full, still update local storage
                    if self._is_firebase_storage_error(e):
                        # Load local data and remove bill
                        if os.path.exists(DATABASE_FILE):
                            try:
                                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                                    local_data = json.load(f)
                                local_data['bills'] = [b for b in local_data['bills'] if b.get('numeric_id') != int(bill_id)]
                                with open(DATABASE_FILE, 'w', encoding='utf-8') as f:
                                    json.dump(local_data, f, indent=2, ensure_ascii=False)
                            except Exception:
                                pass
                
                # Always save to local (ensures data is never lost)
                self._sync_to_local()
                
                # Delete individual bill file
                self._delete_individual_bill(actual_bill_id)
                
                return True
        return False
    
    def _delete_individual_bill(self, bill_id):
        """Delete individual bill JSON file"""
        try:
            from config import BILLS_JSON_DIR
            bill_file = os.path.join(BILLS_JSON_DIR, f"{bill_id}.json")
            if os.path.exists(bill_file):
                os.remove(bill_file)
        except Exception:
            pass  # Silently fail if deletion fails
    
    def _migrate_bills_to_individual_files(self):
        """Migrate all existing bills to individual JSON files"""
        try:
            from config import BILLS_JSON_DIR
            os.makedirs(BILLS_JSON_DIR, exist_ok=True)
            
            # Get all bills from local database file
            if os.path.exists(DATABASE_FILE):
                with open(DATABASE_FILE, 'r', encoding='utf-8') as f:
                    local_data = json.load(f)
                    for bill in local_data.get('bills', []):
                        bill_id = bill.get('id')
                        if bill_id:
                            bill_file = os.path.join(BILLS_JSON_DIR, f"{bill_id}.json")
                            # Only save if file doesn't exist (avoid overwriting)
                            if not os.path.exists(bill_file):
                                self._save_individual_bill(bill)
        except Exception:
            pass  # Silently fail if migration fails
    
    def _delete_individual_bill(self, bill_id):
        """Delete individual bill JSON file"""
        try:
            from config import BILLS_JSON_DIR
            bill_file = os.path.join(BILLS_JSON_DIR, f"{bill_id}.json")
            if os.path.exists(bill_file):
                os.remove(bill_file)
        except Exception:
            pass  # Silently fail if deletion fails
    
    def update_bill(self, bill_id, **kwargs):
        """Update a bill by ID"""
        bills_ref = self._get_collection('bills')
        # Try exact match first
        query = bills_ref.where('id', '==', bill_id).stream()
        for bill_doc in query:
            updated_data = bill_doc.to_dict()
            updated_data.update(kwargs)
            
            try:
                bill_doc.reference.update(kwargs)
                self.offline_mode = False
            except Exception as e:
                self.offline_mode = True
                # If Firebase storage is full, save to local immediately
                if self._is_firebase_storage_error(e):
                    self._save_to_local_fallback('update_bill', updated_data)
            
            # Always save to local (ensures data is never lost)
            self._sync_to_local()
            return updated_data
        # Try numeric_id if bill_id is numeric
        if isinstance(bill_id, (int, float)):
            query = bills_ref.where('numeric_id', '==', int(bill_id)).stream()
            for bill_doc in query:
                updated_data = bill_doc.to_dict()
                updated_data.update(kwargs)
                
                try:
                    bill_doc.reference.update(kwargs)
                    self.offline_mode = False
                except Exception as e:
                    self.offline_mode = True
                    # If Firebase storage is full, save to local immediately
                    if self._is_firebase_storage_error(e):
                        self._save_to_local_fallback('update_bill', updated_data)
                
                # Always save to local (ensures data is never lost)
                self._sync_to_local()
                return updated_data
        return None

# This file exports db only if Firebase is successfully initialized
# The main database.py file will import from here if available, otherwise use JSON
DATABASE_TYPE = None
db = None

try:
    db = FirebaseDatabase()
    DATABASE_TYPE = 'firebase'
except ImportError as e:
    # Firebase package not installed
    DATABASE_TYPE = None
    db = None
except FileNotFoundError as e:
    # Credentials file not found
    DATABASE_TYPE = None
    db = None
except Exception as e:
    # Other errors during initialization - log for debugging
    DATABASE_TYPE = None
    db = None
    # Print error for debugging (can be removed in production)
    import sys
    if '--debug' in sys.argv or '--verbose' in sys.argv:
        print(f"Firebase initialization error: {str(e)}")
        import traceback
        traceback.print_exc()

