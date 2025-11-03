"""
Staff Panel for DROP billing application
Features: Create bills, View billing history, View inventory
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import db
from billing_module import BillingModule

class StaffPanel:
    """Staff dashboard with billing capabilities"""
    
    def __init__(self, root, user, theme_manager, login_root):
        self.root = root
        self.user = user
        self.theme_manager = theme_manager
        self.login_root = login_root
        
        self.root.title(f"DROP - Staff Panel ({user['name']})")
        self.root.geometry("1200x700")
        self.root.resizable(True, True)
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self._create_menu_bar()
        self._create_main_interface()
        self._center_window()
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Logout", command=self._logout)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._on_closing)
        
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Toggle Theme", command=self._toggle_theme)
    
    def _create_main_interface(self):
        """Create main interface with notebook tabs"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Billing Tab
        self.billing_frame = tk.Frame(self.notebook, bg=self.theme_manager.get_color('bg'))
        self.notebook.add(self.billing_frame, text="Create Bill")
        self._create_billing_tab()
        
        # Billing History Tab
        self.history_frame = tk.Frame(self.notebook, bg=self.theme_manager.get_color('bg'))
        self.notebook.add(self.history_frame, text="Billing History")
        self._create_history_tab()
        
        # Inventory View Tab
        self.inventory_frame = tk.Frame(self.notebook, bg=self.theme_manager.get_color('bg'))
        self.notebook.add(self.inventory_frame, text="Inventory")
        self._create_inventory_tab()
    
    def _create_billing_tab(self):
        """Create billing interface"""
        # Initialize billing module
        self.billing_module = BillingModule(self.billing_frame, self.user, self.theme_manager, self._on_bill_created)
    
    def _create_history_tab(self):
        """Create billing history interface"""
        # Top frame for filter
        top_frame = tk.Frame(self.history_frame, bg=self.theme_manager.get_color('bg'))
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            top_frame,
            text="Your Billing History",
            font=('Arial', 14, 'bold'),
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg')
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            top_frame,
            text="Refresh",
            command=self._refresh_history,
            bg=self.theme_manager.get_color('secondary_bg'),
            fg=self.theme_manager.get_color('fg'),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT, padx=5)
        
        # Treeview for bills
        tree_frame = tk.Frame(self.history_frame, bg=self.theme_manager.get_color('bg'))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Date', 'Items', 'Total', 'Payment'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.history_tree.yview)
        
        self.history_tree.heading('ID', text='Bill ID')
        self.history_tree.heading('Date', text='Date & Time')
        self.history_tree.heading('Items', text='Items Count')
        self.history_tree.heading('Total', text='Total (₹)')
        self.history_tree.heading('Payment', text='Payment Method')
        
        self.history_tree.column('ID', width=80, anchor='center')
        self.history_tree.column('Date', width=180)
        self.history_tree.column('Items', width=100, anchor='center')
        self.history_tree.column('Total', width=120, anchor='center')
        self.history_tree.column('Payment', width=120)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_tree.bind('<Double-1>', lambda e: self._view_bill_details())
        
        # Bottom frame
        bottom_frame = tk.Frame(self.history_frame, bg=self.theme_manager.get_color('bg'))
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            bottom_frame,
            text="View Details",
            command=self._view_bill_details,
            bg=self.theme_manager.get_color('accent'),
            fg=self.theme_manager.get_color('button_fg'),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            bottom_frame,
            text="Print Receipt",
            command=self._print_receipt,
            bg=self.theme_manager.get_color('success'),
            fg=self.theme_manager.get_color('button_fg'),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        self._refresh_history()
    
    def _create_inventory_tab(self):
        """Create inventory view interface"""
        top_frame = tk.Frame(self.inventory_frame, bg=self.theme_manager.get_color('bg'))
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            top_frame,
            text="Inventory Items (View Only)",
            font=('Arial', 14, 'bold'),
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg')
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            top_frame,
            text="Refresh",
            command=self._refresh_inventory,
            bg=self.theme_manager.get_color('secondary_bg'),
            fg=self.theme_manager.get_color('fg'),
            relief=tk.FLAT,
            padx=15,
            pady=8
        ).pack(side=tk.RIGHT, padx=5)
        
        # Treeview for inventory
        tree_frame = tk.Frame(self.inventory_frame, bg=self.theme_manager.get_color('bg'))
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.inventory_tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Name', 'Category', 'Price'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.inventory_tree.yview)
        
        self.inventory_tree.heading('ID', text='ID')
        self.inventory_tree.heading('Name', text='Item Name')
        self.inventory_tree.heading('Category', text='Category')
        self.inventory_tree.heading('Price', text='Price (₹)')
        
        self.inventory_tree.column('ID', width=50, anchor='center')
        self.inventory_tree.column('Name', width=200)
        self.inventory_tree.column('Category', width=150)
        self.inventory_tree.column('Price', width=100, anchor='center')
        
        self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self._refresh_inventory()
    
    def _refresh_history(self):
        """Refresh billing history"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        bills = db.get_bills_by_user(self.user['id'])
        bills.sort(key=lambda x: x['date'], reverse=True)
        
        for bill in bills:
            date_str = datetime.fromisoformat(bill['date']).strftime("%Y-%m-%d %H:%M")
            self.history_tree.insert('', 'end', values=(
                bill['id'],
                date_str,
                len(bill['items']),
                f"₹{bill['total']:.2f}",
                bill['payment_method']
            ))
    
    def _refresh_inventory(self):
        """Refresh inventory list"""
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)
        
        inventory = db.get_all_inventory()
        for item in inventory:
            self.inventory_tree.insert('', 'end', values=(
                item['id'],
                item['name'],
                item['category'],
                f"₹{item['price']:.2f}"
            ))
    
    def _view_bill_details(self):
        """View details of selected bill"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a bill to view")
            return
        
        bill_id = int(self.history_tree.item(selection[0])['values'][0])
        bill = db.get_bill(bill_id)
        
        if not bill:
            return
        
        # Create details window
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Bill #{bill_id} Details")
        details_window.geometry("500x600")
        
        main_frame = tk.Frame(details_window, bg=self.theme_manager.get_color('bg'), padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text=f"Bill #{bill_id}", font=('Arial', 18, 'bold'), bg=self.theme_manager.get_color('bg'), fg=self.theme_manager.get_color('fg')).pack(pady=10)
        
        date_str = datetime.fromisoformat(bill['date']).strftime("%Y-%m-%d %H:%M:%S")
        info_text = f"Date: {date_str}\nPayment: {bill['payment_method']}"
        tk.Label(main_frame, text=info_text, bg=self.theme_manager.get_color('bg'), fg=self.theme_manager.get_color('fg'), justify=tk.LEFT).pack(pady=10)
        
        tk.Label(main_frame, text="Items:", font=('Arial', 12, 'bold'), bg=self.theme_manager.get_color('bg'), fg=self.theme_manager.get_color('fg')).pack(pady=(20, 10))
        
        items_frame = tk.Frame(main_frame, bg=self.theme_manager.get_color('secondary_bg'), relief=tk.SOLID, borderwidth=1)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for item in bill['items']:
            item_text = f"{item['name']} x{item['quantity']} @ ₹{item['price']:.2f} = ₹{item['total']:.2f}"
            tk.Label(items_frame, text=item_text, bg=self.theme_manager.get_color('secondary_bg'), fg=self.theme_manager.get_color('fg'), anchor='w', padx=10, pady=5).pack(fill=tk.X)
        
        total_frame = tk.Frame(main_frame, bg=self.theme_manager.get_color('bg'))
        total_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(total_frame, text=f"Total: ₹{bill['total']:.2f}", font=('Arial', 16, 'bold'), bg=self.theme_manager.get_color('bg'), fg=self.theme_manager.get_color('accent')).pack()
        
        tk.Button(main_frame, text="Close", command=details_window.destroy, bg=self.theme_manager.get_color('accent'), fg='white', padx=20, pady=5).pack(pady=10)
    
    def _print_receipt(self):
        """Print receipt for selected bill"""
        selection = self.history_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a bill to print")
            return
        
        bill_id = int(self.history_tree.item(selection[0])['values'][0])
        bill = db.get_bill(bill_id)
        
        if not bill:
            return
        
        from receipt_generator import generate_receipt
        receipt_path = generate_receipt(bill, db.get_user(bill['user_id']))
        messagebox.showinfo("Success", f"Receipt generated successfully!\nSaved to: {receipt_path}")
    
    def _on_bill_created(self):
        """Callback when a new bill is created"""
        self._refresh_history()
        messagebox.showinfo("Success", "Bill created successfully!")
    
    def _toggle_theme(self):
        """Toggle theme"""
        self.theme_manager.toggle_theme()
        messagebox.showinfo("Theme", f"Theme changed to {self.theme_manager.current_theme} mode")
    
    def _logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            self.login_root.deiconify()
    
    def _on_closing(self):
        """Handle window closing"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()
            self.login_root.destroy()

