"""
Billing module for creating and managing bills
"""

import tkinter as tk
from tkinter import ttk, messagebox
from database import db
from receipt_generator import generate_receipt

class BillingModule:
    """Module for creating bills with item entry, preview, and receipt generation"""
    
    def __init__(self, parent, user, theme_manager, on_bill_created_callback=None):
        self.parent = parent
        self.user = user
        self.theme_manager = theme_manager
        self.on_bill_created_callback = on_bill_created_callback
        
        # Current bill items
        self.current_bill_items = []
        
        self._create_interface()
        self._load_inventory_dropdown()
    
    def _create_interface(self):
        """Create the billing interface"""
        # Main container with two columns
        main_container = tk.Frame(self.parent, bg=self.theme_manager.get_color('bg'))
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left frame - Item Entry
        left_frame = tk.LabelFrame(
            main_container,
            text="Add Items to Bill",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            font=('Arial', 12, 'bold'),
            padx=15,
            pady=15
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Barcode scanning section
        barcode_frame = tk.LabelFrame(
            left_frame,
            text="📷 Scan Barcode",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            font=('Arial', 10, 'bold'),
            padx=10,
            pady=10
        )
        barcode_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            barcode_frame,
            text="Scan or enter barcode:",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            font=('Arial', 9)
        ).pack(anchor='w', pady=(0, 5))
        
        self.barcode_var = tk.StringVar()
        self.barcode_entry = tk.Entry(
            barcode_frame,
            textvariable=self.barcode_var,
            font=('Arial', 12, 'bold'),
            bg=self.theme_manager.get_color('entry_bg'),
            fg=self.theme_manager.get_color('entry_fg'),
            relief=tk.SOLID,
            borderwidth=2
        )
        self.barcode_entry.pack(fill=tk.X, ipady=8)
        self.barcode_entry.bind('<Return>', lambda e: self._scan_barcode())
        self.barcode_entry.bind('<KeyRelease>', self._on_barcode_typing)
        # Focus on barcode entry by default for quick scanning
        self.barcode_entry.focus_set()
        
        # Item selection
        item_frame = tk.Frame(left_frame, bg=self.theme_manager.get_color('bg'))
        item_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            item_frame,
            text="Select Item:",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 5))
        
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(item_frame, textvariable=self.item_var, state='readonly', width=30)
        self.item_combo.pack(fill=tk.X, ipady=5)
        self.item_combo.bind('<<ComboboxSelected>>', self._on_item_selected)
        
        # Quantity with +/- buttons
        quantity_frame = tk.Frame(left_frame, bg=self.theme_manager.get_color('bg'))
        quantity_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            quantity_frame,
            text="Quantity:",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            font=('Arial', 10)
        ).pack(anchor='w', pady=(0, 5))
        
        qty_control_frame = tk.Frame(quantity_frame, bg=self.theme_manager.get_color('bg'))
        qty_control_frame.pack(fill=tk.X)
        
        self.quantity_var = tk.StringVar(value="1")
        
        # Minus button
        minus_btn = tk.Button(
            qty_control_frame,
            text="−",
            font=('Arial', 16, 'bold'),
            bg='#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            width=3,
            cursor='hand2',
            command=lambda: self._decrease_quantity()
        )
        minus_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Quantity display
        self.quantity_label = tk.Label(
            qty_control_frame,
            textvariable=self.quantity_var,
            font=('Arial', 14, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50',
            relief=tk.SOLID,
            borderwidth=1,
            width=8,
            anchor='center',
            padx=10,
            pady=5
        )
        self.quantity_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Plus button
        plus_btn = tk.Button(
            qty_control_frame,
            text="+",
            font=('Arial', 16, 'bold'),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            width=3,
            cursor='hand2',
            command=lambda: self._increase_quantity()
        )
        plus_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Item details display
        self.item_details_label = tk.Label(
            left_frame,
            text="",
            bg=self.theme_manager.get_color('secondary_bg'),
            fg=self.theme_manager.get_color('fg'),
            font=('Arial', 10),
            relief=tk.SOLID,
            borderwidth=1,
            anchor='w',
            padx=10,
            pady=10
        )
        self.item_details_label.pack(fill=tk.X, pady=10)
        
        # Add item button
        add_button = tk.Button(
            left_frame,
            text="Add to Bill",
            command=self._add_item_to_bill,
            bg=self.theme_manager.get_color('accent'),
            fg=self.theme_manager.get_color('button_fg'),
            font=('Arial', 11, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        add_button.pack(fill=tk.X, pady=10)
        
        # Custom item entry
        custom_frame = tk.LabelFrame(
            left_frame,
            text="Or Add Custom Item",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            font=('Arial', 10),
            padx=10,
            pady=10
        )
        custom_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(
            custom_frame,
            text="Item Name:",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg')
        ).pack(anchor='w', pady=(0, 5))
        
        self.custom_name_var = tk.StringVar()
        custom_name_entry = tk.Entry(
            custom_frame,
            textvariable=self.custom_name_var,
            font=('Arial', 10),
            bg=self.theme_manager.get_color('entry_bg'),
            fg=self.theme_manager.get_color('entry_fg')
        )
        custom_name_entry.pack(fill=tk.X, pady=(0, 10))
        
        price_frame = tk.Frame(custom_frame, bg=self.theme_manager.get_color('bg'))
        price_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            price_frame,
            text="Price: ₹",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg')
        ).pack(side=tk.LEFT)
        
        self.custom_price_var = tk.StringVar()
        custom_price_entry = tk.Entry(
            price_frame,
            textvariable=self.custom_price_var,
            width=15,
            font=('Arial', 10),
            bg=self.theme_manager.get_color('entry_bg'),
            fg=self.theme_manager.get_color('entry_fg')
        )
        custom_price_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        tk.Label(
            price_frame,
            text="Qty:",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg')
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        self.custom_qty_var = tk.StringVar(value="1")
        custom_qty_entry = tk.Entry(
            price_frame,
            textvariable=self.custom_qty_var,
            width=10,
            font=('Arial', 10),
            bg=self.theme_manager.get_color('entry_bg'),
            fg=self.theme_manager.get_color('entry_fg')
        )
        custom_qty_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Button(
            custom_frame,
            text="Add Custom Item",
            command=self._add_custom_item,
            bg=self.theme_manager.get_color('warning'),
            fg=self.theme_manager.get_color('button_fg'),
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(fill=tk.X, pady=(10, 0))
        
        # Right frame - Bill Preview
        right_frame = tk.LabelFrame(
            main_container,
            text="Bill Preview",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            font=('Arial', 12, 'bold'),
            padx=15,
            pady=15
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Bill items list
        items_list_frame = tk.Frame(right_frame, bg=self.theme_manager.get_color('bg'))
        items_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(items_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview for bill items
        self.bill_tree = ttk.Treeview(
            items_list_frame,
            columns=('Item', 'Qty', 'Price', 'Total'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )
        scrollbar.config(command=self.bill_tree.yview)
        
        self.bill_tree.heading('Item', text='Item Name')
        self.bill_tree.heading('Qty', text='Quantity')
        self.bill_tree.heading('Price', text='Unit Price')
        self.bill_tree.heading('Total', text='Total')
        
        self.bill_tree.column('Item', width=200)
        self.bill_tree.column('Qty', width=80, anchor='center')
        self.bill_tree.column('Price', width=100, anchor='center')
        self.bill_tree.column('Total', width=100, anchor='center')
        
        self.bill_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.bill_tree.bind('<Double-1>', lambda e: self._remove_selected_item())
        
        # Total display
        total_frame = tk.Frame(right_frame, bg=self.theme_manager.get_color('secondary_bg'), relief=tk.SOLID, borderwidth=2)
        total_frame.pack(fill=tk.X, pady=10)
        
        self.total_label = tk.Label(
            total_frame,
            text="Total: ₹0.00",
            font=('Arial', 18, 'bold'),
            bg=self.theme_manager.get_color('secondary_bg'),
            fg=self.theme_manager.get_color('accent'),
            pady=15
        )
        self.total_label.pack()
        
        # Payment method buttons
        payment_frame = tk.Frame(right_frame, bg=self.theme_manager.get_color('bg'))
        payment_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            payment_frame,
            text="Payment Method:",
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            font=('Arial', 11, 'bold')
        ).pack(anchor='w', pady=(0, 10))
        
        payment_buttons_frame = tk.Frame(payment_frame, bg=self.theme_manager.get_color('bg'))
        payment_buttons_frame.pack(fill=tk.X)
        
        self.payment_var = tk.StringVar(value="Cash")
        
        payment_methods = [
            ("Cash", "#27AE60"),
            ("UPI", "#3498DB"),
            ("Card", "#9B59B6")
        ]
        
        self.payment_buttons = []
        for method, color in payment_methods:
            btn = tk.Button(
                payment_buttons_frame,
                text=method,
                font=('Arial', 12, 'bold'),
                bg=color if self.payment_var.get() == method else '#ECF0F1',
                fg='#FFFFFF' if self.payment_var.get() == method else '#2C3E50',
                relief=tk.FLAT,
                padx=25,
                pady=12,
                cursor='hand2',
                command=lambda m=method: self._select_payment_method(m)
            )
            btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.payment_buttons.append((btn, method, color))
        
        # Action buttons
        buttons_frame = tk.Frame(right_frame, bg=self.theme_manager.get_color('bg'))
        buttons_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            buttons_frame,
            text="Remove Selected",
            command=self._remove_selected_item,
            bg=self.theme_manager.get_color('danger'),
            fg=self.theme_manager.get_color('button_fg'),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        tk.Button(
            buttons_frame,
            text="Clear Bill",
            command=self._clear_bill,
            bg=self.theme_manager.get_color('warning'),
            fg=self.theme_manager.get_color('button_fg'),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        buttons_frame2 = tk.Frame(right_frame, bg=self.theme_manager.get_color('bg'))
        buttons_frame2.pack(fill=tk.X, pady=10)
        
        # Large prominent Create Bill button
        create_bill_btn = tk.Button(
            buttons_frame2,
            text="CREATE BILL",
            command=self._create_bill,
            bg='#27AE60',
            fg='#FFFFFF',
            font=('Arial', 16, 'bold'),
            relief=tk.FLAT,
            padx=40,
            pady=20,
            cursor='hand2',
            activebackground='#229954',
            activeforeground='#FFFFFF'
        )
        create_bill_btn.pack(fill=tk.X, expand=True)
        create_bill_btn.bind('<Enter>', lambda e: create_bill_btn.config(bg='#229954'))
        create_bill_btn.bind('<Leave>', lambda e: create_bill_btn.config(bg='#27AE60'))
    
    def _load_inventory_dropdown(self):
        """Load inventory items into dropdown"""
        inventory = db.get_all_inventory()
        item_list = [f"{item['name']} - ₹{item['price']:.2f}" for item in inventory]
        self.item_combo['values'] = item_list
        self.selected_inventory_item = None
    
    def _on_item_selected(self, event=None):
        """Handle item selection from dropdown"""
        selection = self.item_var.get()
        if not selection:
            return
        
        # Extract item name
        item_name = selection.split(' - ')[0]
        inventory = db.get_all_inventory()
        
        for item in inventory:
            if item['name'] == item_name:
                self.selected_inventory_item = item
                self.item_details_label.config(
                    text=f"Price: ₹{item['price']:.2f} | Category: {item['category']}"
                )
                break
    
    def _increase_quantity(self):
        """Increase quantity by 1"""
        try:
            current = int(self.quantity_var.get())
            self.quantity_var.set(str(current + 1))
        except ValueError:
            self.quantity_var.set("1")
    
    def _decrease_quantity(self):
        """Decrease quantity by 1 (minimum 1)"""
        try:
            current = int(self.quantity_var.get())
            if current > 1:
                self.quantity_var.set(str(current - 1))
        except ValueError:
            self.quantity_var.set("1")
    
    def _select_payment_method(self, method):
        """Select payment method"""
        self.payment_var.set(method)
        # Update button colors
        for btn, btn_method, color in self.payment_buttons:
            if btn_method == method:
                btn.config(bg=color, fg='#FFFFFF')
            else:
                btn.config(bg='#ECF0F1', fg='#2C3E50')
    
    def _add_item_to_bill(self):
        """Add selected inventory item to bill"""
        if not self.selected_inventory_item:
            messagebox.showwarning("Warning", "Please select an item from inventory")
            return
        
        try:
            quantity = int(self.quantity_var.get())
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            item = {
                'name': self.selected_inventory_item['name'],
                'quantity': quantity,
                'price': self.selected_inventory_item['price'],
                'total': self.selected_inventory_item['price'] * quantity,
                'inventory_id': self.selected_inventory_item['id']
            }
            
            # Check if item already exists in cart
            existing_item = None
            for cart_item in self.current_bill_items:
                if cart_item.get('inventory_id') == item['inventory_id']:
                    existing_item = cart_item
                    break
            
            if existing_item:
                # Update quantity for existing item
                existing_item['quantity'] += quantity
                existing_item['total'] = existing_item['price'] * existing_item['quantity']
            else:
                # Add new item to cart
                self.current_bill_items.append(item)
            
            self._update_bill_preview()
            
            # Reset selection
            self.item_var.set('')
            self.quantity_var.set('1')
            self.selected_inventory_item = None
            self.item_details_label.config(text="")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity")
    
    def _on_barcode_typing(self, event):
        """Handle barcode typing - auto-submit when full barcode is entered"""
        barcode_value = self.barcode_var.get().strip().upper()
        # Auto-submit when barcode reaches 10 characters (DROP + 6 digits)
        # This handles barcode scanners that don't send Enter key
        if len(barcode_value) == 10 and barcode_value.startswith('DROP'):
            # Small delay to ensure all characters are captured
            self.barcode_entry.after(50, self._scan_barcode)
    
    def _scan_barcode(self):
        """Scan barcode and automatically add item to cart"""
        barcode_value = self.barcode_var.get().strip().upper()
        
        if not barcode_value:
            return
        
        # Parse barcode: Format is DROP000001 (DROP + 6 digits)
        if not barcode_value.startswith('DROP') or len(barcode_value) != 10:
            messagebox.showerror("Invalid Barcode", "Invalid barcode format. Expected: DROP000001")
            self.barcode_var.set('')
            self.barcode_entry.focus_set()
            return
        
        try:
            # Extract item ID from barcode (last 6 digits)
            item_id = int(barcode_value[4:])
            
            # Find item in inventory
            inventory_items = db.get_all_inventory()
            item = None
            for inv_item in inventory_items:
                if inv_item['id'] == item_id:
                    item = inv_item
                    break
            
            if not item:
                messagebox.showerror("Item Not Found", f"Item with barcode {barcode_value} not found in inventory")
                self.barcode_var.set('')
                self.barcode_entry.focus_set()
                return
            
            # Check if item already exists in cart
            existing_item = None
            for cart_item in self.current_bill_items:
                if cart_item.get('inventory_id') == item['id']:
                    existing_item = cart_item
                    break
            
            if existing_item:
                # Increase quantity by 1 for existing item
                existing_item['quantity'] += 1
                existing_item['total'] = existing_item['price'] * existing_item['quantity']
            else:
                # Add new item with quantity 1
                new_item = {
                    'name': item['name'],
                    'quantity': 1,
                    'price': item['price'],
                    'total': item['price'],
                    'inventory_id': item['id']
                }
                self.current_bill_items.append(new_item)
            
            # Update bill preview
            self._update_bill_preview()
            
            # Clear barcode field and refocus for next scan
            self.barcode_var.set('')
            self.barcode_entry.focus_set()
            
        except ValueError:
            messagebox.showerror("Invalid Barcode", "Barcode contains invalid characters")
            self.barcode_var.set('')
            self.barcode_entry.focus_set()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to scan barcode: {str(e)}")
            self.barcode_var.set('')
            self.barcode_entry.focus_set()
    
    def _add_custom_item(self):
        """Add custom item to bill"""
        try:
            name = self.custom_name_var.get().strip()
            price = float(self.custom_price_var.get())
            quantity = int(self.custom_qty_var.get())
            
            if not name:
                messagebox.showerror("Error", "Please enter item name")
                return
            
            if price <= 0 or quantity <= 0:
                messagebox.showerror("Error", "Price and quantity must be positive")
                return
            
            item = {
                'name': name,
                'quantity': quantity,
                'price': price,
                'total': price * quantity,
                'inventory_id': None  # Custom item, no inventory ID
            }
            
            self.current_bill_items.append(item)
            self._update_bill_preview()
            
            # Reset custom fields
            self.custom_name_var.set('')
            self.custom_price_var.set('')
            self.custom_qty_var.set('1')
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid price and quantity")
    
    def _update_bill_preview(self):
        """Update the bill preview display"""
        # Clear existing items
        for item in self.bill_tree.get_children():
            self.bill_tree.delete(item)
        
        # Add current items
        for item in self.current_bill_items:
            self.bill_tree.insert('', 'end', values=(
                item['name'],
                item['quantity'],
                f"₹{item['price']:.2f}",
                f"₹{item['total']:.2f}"
            ))
        
        # Update total
        total = sum(item['total'] for item in self.current_bill_items)
        self.total_label.config(text=f"Total: ₹{total:.2f}")
    
    def _remove_selected_item(self):
        """Remove selected item from bill"""
        selection = self.bill_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove")
            return
        
        index = self.bill_tree.index(selection[0])
        if 0 <= index < len(self.current_bill_items):
            self.current_bill_items.pop(index)
            self._update_bill_preview()
    
    def _clear_bill(self):
        """Clear all items from bill"""
        if not self.current_bill_items:
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the bill?"):
            self.current_bill_items = []
            self._update_bill_preview()
    
    def _create_bill(self):
        """Create bill in database and show preview"""
        if not self.current_bill_items:
            messagebox.showwarning("Warning", "Bill is empty. Please add items.")
            return
        
        # Calculate total
        total = sum(item['total'] for item in self.current_bill_items)
        
        # Create bill
        bill = db.create_bill(
            self.user['id'],
            self.current_bill_items,
            total,
            self.payment_var.get()
        )
        
        # Show bill preview with bill ID
        from bill_preview import BillPreview
        preview = BillPreview(
            self.parent,
            self.current_bill_items,
            total,
            self.payment_var.get(),
            self.user,
            bill_id=bill['id']
        )
        
        # Clear bill after creation
        self.current_bill_items = []
        self._update_bill_preview()
        self._load_inventory_dropdown()  # Refresh inventory
        
        # Callback
        if self.on_bill_created_callback:
            self.on_bill_created_callback()

