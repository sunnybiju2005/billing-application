"""
Admin Panel for DROP billing application
Features: Clean professional layout with sidebar navigation
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os
import csv
from database import db
from config import (
    SHOP_NAME, SHOP_TAGLINE, SHOP_ADDRESS, DEFAULT_BILL_WIDTH_MM, DEFAULT_BILL_HEIGHT_MM, 
    DEFAULT_CHARACTER_WIDTH, PAPER_WIDTH_PRESETS, DEFAULT_ALIGNMENT, DEFAULT_MARGIN_TOP,
    DEFAULT_MARGIN_BOTTOM, DEFAULT_MARGIN_LEFT, DEFAULT_MARGIN_RIGHT, COLUMN_WIDTH_OPTIONS_80MM
)

class AdminPanel:
    """Admin dashboard with sidebar navigation and clean UI"""
    
    def __init__(self, root, user, theme_manager, login_root):
        self.root = root
        self.user = user
        self.theme_manager = theme_manager
        self.login_root = login_root
        
        self.root.title(f"{SHOP_NAME} - Admin Dashboard")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        self.root.configure(bg='#F5F5F5')
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Current view
        self.current_view = None
        
        # Initialize UI components (created on demand)
        self.staff_tree = None
        self.bills_tree = None
        self.items_tree = None
        self.products_tree = None
        self.date_filter_var = tk.StringVar(value="All")
        self.item_filter_var = tk.StringVar(value="All Items")
        self.product_date_filter = tk.StringVar(value="Current Month")
        self.bill_id_search_var = tk.StringVar(value="")
        # Date range variables for custom date filter
        self.start_date_var = tk.StringVar(value="")
        self.end_date_var = tk.StringVar(value="")
        # Bill settings variables
        self.bill_width_var = tk.StringVar(value="80")
        self.bill_height_var = tk.StringVar(value="210")
        self.bill_char_width_var = tk.StringVar(value="48")
        self.paper_width_preset_var = tk.StringVar(value="80mm")
        self.alignment_var = tk.StringVar(value="Left")
        self.margin_top_var = tk.StringVar(value="0")
        self.margin_bottom_var = tk.StringVar(value="0")
        self.margin_left_var = tk.StringVar(value="0")
        self.margin_right_var = tk.StringVar(value="0")
        
        # Create UI
        self._create_header()
        self._create_sidebar()
        self._create_main_content()
        
        # Load dashboard by default
        self._show_dashboard()
        
        # Center window
        self._center_window()
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_header(self):
        """Create top header with shop name and logout button"""
        header = tk.Frame(self.root, bg='#FFFFFF', height=70, relief=tk.FLAT, bd=0)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        # Shop name
        shop_label = tk.Label(
            header,
            text=SHOP_NAME,
            font=('Arial', 24, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        )
        shop_label.pack(side=tk.LEFT, padx=30, pady=20)
        
        # Spacer
        tk.Frame(header, bg='#FFFFFF').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Logout button
        logout_btn = tk.Button(
            header,
            text="Logout",
            font=('Arial', 11, 'bold'),
            bg='#E74C3C',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self._logout
        )
        logout_btn.pack(side=tk.RIGHT, padx=30, pady=15)
        logout_btn.bind('<Enter>', lambda e: logout_btn.config(bg='#C0392B'))
        logout_btn.bind('<Leave>', lambda e: logout_btn.config(bg='#E74C3C'))
    
    def _create_sidebar(self):
        """Create left sidebar with navigation buttons"""
        sidebar = tk.Frame(self.root, bg='#2C3E50', width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Navigation buttons with icons
        nav_items = [
            ('📊 Dashboard', 'dashboard'),
            ('📦 Items', 'items'),
            ('🛍️ Products', 'products'),
            ('🧾 Bills', 'bills'),
            ('🖨️ Printer', 'bill'),
            ('👥 Staff', 'staff'),
            ('📈 Reports', 'reports'),
            ('❓ Help', 'help'),
            ('⚙️ Settings', 'settings'),
            ('💾 Database', 'database')
        ]
        
        self.sidebar_buttons = []
        for text, view_name in nav_items:
            btn = tk.Button(
                sidebar,
                text=text,
                font=('Arial', 12),
                bg='#2C3E50',
                fg='#ECF0F1',
                relief=tk.FLAT,
                anchor='w',
                padx=25,
                pady=15,
                cursor='hand2',
                command=lambda v=view_name: self._navigate_to(v)
            )
            btn.pack(fill=tk.X, padx=0, pady=2)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg='#34495E'))
            btn.bind('<Leave>', lambda e, b=btn: b.config(bg='#2C3E50'))
            self.sidebar_buttons.append((btn, view_name))
    
    def _create_main_content(self):
        """Create main content area"""
        self.content_frame = tk.Frame(self.root, bg='#F5F5F5')
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    def _clear_content(self):
        """Clear main content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _navigate_to(self, view_name):
        """Navigate to different views"""
        # Update button states
        for btn, name in self.sidebar_buttons:
            if name == view_name:
                btn.config(bg='#3498DB', fg='#FFFFFF')
            else:
                btn.config(bg='#2C3E50', fg='#ECF0F1')
        
        # Clear and load new view
        self._clear_content()
        
        if view_name == 'dashboard':
            self._show_dashboard()
        elif view_name == 'staff':
            self._show_staff_management()
        elif view_name == 'bills':
            self._show_bills()
        elif view_name == 'bill':
            self._show_bill()
        elif view_name == 'reports':
            self._show_reports()
        elif view_name == 'settings':
            self._show_settings()
        elif view_name == 'database':
            self._show_database()
        elif view_name == 'items':
            self._show_items()
        elif view_name == 'products':
            self._show_products()
        elif view_name == 'help':
            self._show_help()
    
    def _show_dashboard(self):
        """Show dashboard with sales summary and latest bills"""
        self.current_view = 'dashboard'
        
        # Title
        title = tk.Label(
            self.content_frame,
            text="Dashboard",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        )
        title.pack(anchor='w', pady=(0, 20))
        
        # Sales Summary Widgets
        summary_frame = tk.Frame(self.content_frame, bg='#F5F5F5')
        summary_frame.pack(fill=tk.X, pady=(0, 30))
        
        bills = db.get_all_bills()
        total_sales = sum(bill['total'] for bill in bills)
        total_bills = len(bills)
        
        today = datetime.now().date()
        today_bills = [b for b in bills if datetime.fromisoformat(b['date']).date() == today]
        today_sales = sum(b['total'] for b in today_bills)
        
        # Summary cards
        summary_data = [
            ("Total Sales", f"₹{total_sales:,.2f}", "#3498DB"),
            ("Total Bills", str(total_bills), "#2ECC71"),
            ("Today's Sales", f"₹{today_sales:,.2f}", "#E67E22"),
            ("Today's Bills", str(len(today_bills)), "#9B59B6")
        ]
        
        for i, (label, value, color) in enumerate(summary_data):
            card = tk.Frame(summary_frame, bg='#FFFFFF', relief=tk.FLAT, bd=0)
            card.grid(row=0, column=i, padx=10, sticky='ew', ipadx=20, ipady=30)
            
            tk.Label(
                card,
                text=value,
                font=('Arial', 24, 'bold'),
                bg='#FFFFFF',
                fg=color
            ).pack()
            
            tk.Label(
                card,
                text=label,
                font=('Arial', 11),
                bg='#FFFFFF',
                fg='#7F8C8D'
            ).pack(pady=(5, 0))
        
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(2, weight=1)
        summary_frame.columnconfigure(3, weight=1)
        
        # Latest Bills Section
        bills_label = tk.Label(
            self.content_frame,
            text="Latest Bills",
            font=('Arial', 16, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        )
        bills_label.pack(anchor='w', pady=(20, 10))
        
        # Bills list
        bills_container = tk.Frame(self.content_frame, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        bills_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(bills_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        bills_tree = ttk.Treeview(
            bills_container,
            columns=('No', 'ID', 'Date', 'Staff', 'Items', 'Total', 'Payment'),
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )
        scrollbar.config(command=bills_tree.yview)
        
        bills_tree.heading('No', text='No')
        bills_tree.heading('ID', text='Bill ID')
        bills_tree.heading('Date', text='Date & Time')
        bills_tree.heading('Staff', text='Staff Member')
        bills_tree.heading('Items', text='Items')
        bills_tree.heading('Total', text='Total (₹)')
        bills_tree.heading('Payment', text='Payment Method')
        
        bills_tree.column('No', width=50, anchor='center')
        bills_tree.column('ID', width=100, anchor='center')
        bills_tree.column('Date', width=180)
        bills_tree.column('Staff', width=150)
        bills_tree.column('Items', width=250)
        bills_tree.column('Total', width=120, anchor='center')
        bills_tree.column('Payment', width=130)
        
        bills_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load latest bills
        latest_bills = sorted(bills, key=lambda x: x['date'], reverse=True)[:50]
        for index, bill in enumerate(latest_bills, start=1):
            staff_user = db.get_user(bill['user_id'])
            staff_name = staff_user['name'] if staff_user else 'Unknown'
            date_str = datetime.fromisoformat(bill['date']).strftime("%Y-%m-%d %H:%M")
            bill_id = bill.get('id', 'N/A')
            # Ensure bill ID is in DR0201 format
            if isinstance(bill_id, (int, float)):
                bill_id = f"DR{str(int(bill_id)).zfill(4)}"
            
            # Format items list
            items_list = []
            for item in bill.get('items', []):
                item_name = item.get('name', 'Unknown')
                item_qty = item.get('quantity', 1)
                if item_qty > 1:
                    items_list.append(f"{item_name} (x{item_qty})")
                else:
                    items_list.append(item_name)
            items_display = ", ".join(items_list)
            # Truncate if too long
            if len(items_display) > 60:
                items_display = items_display[:57] + "..."
            
            bills_tree.insert('', 'end', values=(
                index,
                bill_id,
                date_str,
                staff_name,
                items_display,
                f"₹{bill['total']:.2f}",
                bill['payment_method']
            ))
    
    def _show_staff_management(self):
        """Show staff management interface"""
        self.current_view = 'staff'
        
        # Title and Add button
        top_frame = tk.Frame(self.content_frame, bg='#F5F5F5')
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            top_frame,
            text="Staff Management",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        ).pack(side=tk.LEFT)
        
        tk.Button(
            top_frame,
            text="+ Add Staff",
            font=('Arial', 11, 'bold'),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self._add_staff_member
        ).pack(side=tk.RIGHT)
        
        # Staff list
        list_frame = tk.Frame(self.content_frame, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.staff_tree = ttk.Treeview(
            list_frame,
            columns=('ID', 'Username', 'Name', 'Role'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.staff_tree.yview)
        
        self.staff_tree.heading('ID', text='ID')
        self.staff_tree.heading('Username', text='Username')
        self.staff_tree.heading('Name', text='Name')
        self.staff_tree.heading('Role', text='Role')
        
        self.staff_tree.column('ID', width=100, anchor='center')
        self.staff_tree.column('Username', width=200)
        self.staff_tree.column('Name', width=300)
        self.staff_tree.column('Role', width=150)
        
        self.staff_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.staff_tree.bind('<Double-1>', lambda e: self._delete_staff())
        
        # Action buttons
        action_frame = tk.Frame(self.content_frame, bg='#F5F5F5')
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            action_frame,
            text="Delete Selected",
            font=('Arial', 11),
            bg='#E74C3C',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self._delete_staff
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Refresh",
            font=('Arial', 11),
            bg='#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self._refresh_staff
        ).pack(side=tk.LEFT, padx=5)
        
        self._refresh_staff()
    
    def _show_bills(self):
        """Show bills management interface"""
        self.current_view = 'bills'
        
        # Title and filters
        top_frame = tk.Frame(self.content_frame, bg='#F5F5F5')
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            top_frame,
            text="Bills Management",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        ).pack(side=tk.LEFT)
        
        filter_frame = tk.Frame(top_frame, bg='#F5F5F5')
        filter_frame.pack(side=tk.RIGHT)
        
        tk.Label(filter_frame, text="Date:", bg='#F5F5F5', fg='#2C3E50').pack(side=tk.LEFT, padx=5)
        
        date_filter = ttk.Combobox(filter_frame, textvariable=self.date_filter_var, 
                                  values=["All", "Today", "This Week", "This Month", "Custom Range"], 
                                  width=12, state='readonly')
        date_filter.pack(side=tk.LEFT, padx=5)
        date_filter.bind('<<ComboboxSelected>>', lambda e: self._on_date_filter_changed())
        
        # Date picker buttons (hidden initially)
        self.start_date_btn = tk.Button(
            filter_frame,
            text="📅 Start Date",
            font=('Arial', 9),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2',
            command=lambda: self._pick_date('start')
        )
        self.start_date_btn.pack(side=tk.LEFT, padx=2)
        self.start_date_btn.pack_forget()
        
        self.end_date_btn = tk.Button(
            filter_frame,
            text="📅 End Date",
            font=('Arial', 9),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=10,
            pady=5,
            cursor='hand2',
            command=lambda: self._pick_date('end')
        )
        self.end_date_btn.pack(side=tk.LEFT, padx=2)
        self.end_date_btn.pack_forget()
        
        # Date labels (show selected dates)
        self.start_date_label = tk.Label(
            filter_frame,
            text="",
            bg='#F5F5F5',
            fg='#2C3E50',
            font=('Arial', 9)
        )
        self.end_date_label = tk.Label(
            filter_frame,
            text="",
            bg='#F5F5F5',
            fg='#2C3E50',
            font=('Arial', 9)
        )
        
        # Function to update date labels display
        def update_date_labels():
            if self.start_date_var.get():
                self.start_date_label.config(text=f"From: {self.start_date_var.get()}")
                self.start_date_label.pack(side=tk.LEFT, padx=2)
            else:
                self.start_date_label.pack_forget()
            
            if self.end_date_var.get():
                self.end_date_label.config(text=f"To: {self.end_date_var.get()}")
                self.end_date_label.pack(side=tk.LEFT, padx=2)
            else:
                self.end_date_label.pack_forget()
        
        # Trace variables to update labels
        self.start_date_var.trace('w', lambda *args: update_date_labels())
        self.end_date_var.trace('w', lambda *args: update_date_labels())
        
        tk.Label(filter_frame, text="Item:", bg='#F5F5F5', fg='#2C3E50').pack(side=tk.LEFT, padx=(10, 5))
        
        item_names = ["All Items"] + [item['name'] for item in db.get_all_inventory()]
        item_filter = ttk.Combobox(filter_frame, textvariable=self.item_filter_var, 
                                  values=item_names, width=15, state='readonly')
        item_filter.pack(side=tk.LEFT, padx=5)
        item_filter.bind('<<ComboboxSelected>>', lambda e: self._refresh_bills())
        
        # Bill ID search
        tk.Label(filter_frame, text="Bill ID:", bg='#F5F5F5', fg='#2C3E50').pack(side=tk.LEFT, padx=(10, 5))
        bill_id_entry = tk.Entry(
            filter_frame,
            textvariable=self.bill_id_search_var,
            width=12,
            font=('Arial', 10)
        )
        bill_id_entry.pack(side=tk.LEFT, padx=5)
        bill_id_entry.bind('<KeyRelease>', lambda e: self._refresh_bills())
        bill_id_entry.bind('<Return>', lambda e: self._refresh_bills())
        
        # Clear search button
        clear_search_btn = tk.Button(
            filter_frame,
            text="✕",
            font=('Arial', 9, 'bold'),
            bg='#E74C3C',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=8,
            pady=4,
            cursor='hand2',
            command=lambda: [self.bill_id_search_var.set(""), self._refresh_bills()]
        )
        clear_search_btn.pack(side=tk.LEFT, padx=2)
        clear_search_btn.bind('<Enter>', lambda e: clear_search_btn.config(bg='#C0392B'))
        clear_search_btn.bind('<Leave>', lambda e: clear_search_btn.config(bg='#E74C3C'))
        
        tk.Button(
            filter_frame,
            text="Refresh",
            font=('Arial', 10),
            bg='#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=15,
            pady=6,
            command=self._refresh_bills
        ).pack(side=tk.LEFT, padx=5)
        
        # Bills list
        list_frame = tk.Frame(self.content_frame, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.bills_tree = ttk.Treeview(
            list_frame,
            columns=('No', 'ID', 'Date', 'Staff', 'Items', 'Total', 'Payment'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.bills_tree.yview)
        
        self.bills_tree.heading('No', text='No')
        self.bills_tree.heading('ID', text='Bill ID')
        self.bills_tree.heading('Date', text='Date')
        self.bills_tree.heading('Staff', text='Staff Member')
        self.bills_tree.heading('Items', text='Items')
        self.bills_tree.heading('Total', text='Total (₹)')
        self.bills_tree.heading('Payment', text='Payment Method')
        
        self.bills_tree.column('No', width=50, anchor='center')
        self.bills_tree.column('ID', width=100, anchor='center')
        self.bills_tree.column('Date', width=150)
        self.bills_tree.column('Staff', width=180)
        self.bills_tree.column('Items', width=280)
        self.bills_tree.column('Total', width=130, anchor='center')
        self.bills_tree.column('Payment', width=130)
        
        self.bills_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.bills_tree.bind('<Double-1>', lambda e: self._view_bill_details())
        
        # Action buttons
        action_frame = tk.Frame(self.content_frame, bg='#F5F5F5')
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            action_frame,
            text="View Details",
            font=('Arial', 11),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self._view_bill_details
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="Delete Bill",
            font=('Arial', 11),
            bg='#E74C3C',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self._delete_bill
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🗑️ Delete All Bills",
            font=('Arial', 11, 'bold'),
            bg='#C0392B',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self._delete_all_bills
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="📥 Export Filtered Data",
            font=('Arial', 11),
            bg='#27AE60',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self._export_filtered_bills
        ).pack(side=tk.LEFT, padx=5)
        
        self._refresh_bills()
    
    def _on_date_filter_changed(self):
        """Handle date filter selection change"""
        filter_value = self.date_filter_var.get()
        if filter_value == "Custom Range":
            # Show date picker buttons
            self.start_date_btn.pack(side=tk.LEFT, padx=2)
            self.end_date_btn.pack(side=tk.LEFT, padx=2)
            # Reset dates if not set
            if not self.start_date_var.get():
                self.start_date_var.set("")
            if not self.end_date_var.get():
                self.end_date_var.set("")
        else:
            # Hide date picker buttons
            self.start_date_btn.pack_forget()
            self.end_date_btn.pack_forget()
            self.start_date_label.pack_forget()
            self.end_date_label.pack_forget()
            self.start_date_var.set("")
            self.end_date_var.set("")
        self._refresh_bills()
    
    def _pick_date(self, date_type):
        """Open date picker dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Date")
        dialog.geometry("350x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg='#FFFFFF')
        
        # Get current date or selected date
        if date_type == 'start' and self.start_date_var.get():
            try:
                current_date = datetime.strptime(self.start_date_var.get(), "%Y-%m-%d")
            except (ValueError, TypeError):
                current_date = datetime.now()
        elif date_type == 'end' and self.end_date_var.get():
            try:
                current_date = datetime.strptime(self.end_date_var.get(), "%Y-%m-%d")
            except (ValueError, TypeError):
                current_date = datetime.now()
        else:
            current_date = datetime.now()
        
        main_frame = tk.Frame(dialog, bg='#FFFFFF', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main_frame,
            text=f"Select {date_type.title()} Date",
            font=('Arial', 14, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(pady=(0, 20))
        
        # Year selection
        year_frame = tk.Frame(main_frame, bg='#FFFFFF')
        year_frame.pack(fill=tk.X, pady=5)
        tk.Label(year_frame, text="Year:", bg='#FFFFFF', fg='#2C3E50', font=('Arial', 10)).pack(side=tk.LEFT)
        year_var = tk.IntVar(value=current_date.year)
        year_spinbox = tk.Spinbox(
            year_frame,
            from_=2020,
            to=2030,
            textvariable=year_var,
            width=10,
            font=('Arial', 10)
        )
        year_spinbox.pack(side=tk.LEFT, padx=10)
        
        # Month selection
        month_frame = tk.Frame(main_frame, bg='#FFFFFF')
        month_frame.pack(fill=tk.X, pady=5)
        tk.Label(month_frame, text="Month:", bg='#FFFFFF', fg='#2C3E50', font=('Arial', 10)).pack(side=tk.LEFT)
        month_var = tk.IntVar(value=current_date.month)
        month_spinbox = tk.Spinbox(
            month_frame,
            from_=1,
            to=12,
            textvariable=month_var,
            width=10,
            font=('Arial', 10)
        )
        month_spinbox.pack(side=tk.LEFT, padx=10)
        
        # Day selection
        day_frame = tk.Frame(main_frame, bg='#FFFFFF')
        day_frame.pack(fill=tk.X, pady=5)
        tk.Label(day_frame, text="Day:", bg='#FFFFFF', fg='#2C3E50', font=('Arial', 10)).pack(side=tk.LEFT)
        day_var = tk.IntVar(value=current_date.day)
        day_spinbox = tk.Spinbox(
            day_frame,
            from_=1,
            to=31,
            textvariable=day_var,
            width=10,
            font=('Arial', 10)
        )
        day_spinbox.pack(side=tk.LEFT, padx=10)
        
        def update_day_max():
            """Update maximum day based on selected month/year"""
            try:
                year = year_var.get()
                month = month_var.get()
                # Get last day of month
                if month == 12:
                    last_day = 31
                elif month in [4, 6, 9, 11]:
                    last_day = 30
                elif month == 2:
                    # Check for leap year
                    if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                        last_day = 29
                    else:
                        last_day = 28
                else:
                    last_day = 31
                day_spinbox.config(to=last_day)
                if day_var.get() > last_day:
                    day_var.set(last_day)
            except (ValueError, AttributeError):
                pass
        
        year_var.trace('w', lambda *args: update_day_max())
        month_var.trace('w', lambda *args: update_day_max())
        update_day_max()
        
        def save_date():
            try:
                year = year_var.get()
                month = month_var.get()
                day = day_var.get()
                selected_date = datetime(year, month, day)
                date_str = selected_date.strftime("%Y-%m-%d")
                
                if date_type == 'start':
                    self.start_date_var.set(date_str)
                else:
                    self.end_date_var.set(date_str)
                
                dialog.destroy()
                # Update date labels display after selection (handled by trace in _show_bills)
                self._refresh_bills()
            except ValueError as e:
                messagebox.showerror("Invalid Date", f"Please select a valid date:\n{str(e)}", parent=dialog)
        
        button_frame = tk.Frame(main_frame, bg='#FFFFFF')
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Select Date",
            command=save_date,
            bg='#3498DB',
            fg='#FFFFFF',
            font=('Arial', 11, 'bold'),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg='#95A5A6',
            fg='#FFFFFF',
            font=('Arial', 11),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2'
        ).pack(side=tk.LEFT, padx=5)
    
    def _show_reports(self):
        """Show reports interface"""
        self.current_view = 'reports'
        
        tk.Label(
            self.content_frame,
            text="Reports",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 20))
        
        # Generate report button
        tk.Button(
            self.content_frame,
            text="Generate Sales Report",
            font=('Arial', 12, 'bold'),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor='hand2',
            command=self._generate_sales_report
        ).pack(anchor='w', pady=20)
        
        # Statistics display
        stats_frame = tk.Frame(self.content_frame, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self._update_reports_stats(stats_frame)
    
    def _show_settings(self):
        """Show settings interface"""
        self.current_view = 'settings'
        
        tk.Label(
            self.content_frame,
            text="Settings",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 20))
        
        settings_frame = tk.Frame(self.content_frame, bg='#FFFFFF', relief=tk.FLAT, bd=1, padx=30, pady=30)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            settings_frame,
            text="Application Settings",
            font=('Arial', 14, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 20))
        
        # Theme toggle
        theme_frame = tk.Frame(settings_frame, bg='#FFFFFF')
        theme_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(theme_frame, text="Theme:", bg='#FFFFFF', fg='#2C3E50', font=('Arial', 11)).pack(side=tk.LEFT)
        tk.Button(
            theme_frame,
            text="Toggle Theme",
            font=('Arial', 10),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=15,
            pady=6,
            command=self._toggle_theme
        ).pack(side=tk.LEFT, padx=20)
    
    def _show_database(self):
        """Show database information and Firebase connection status"""
        self.current_view = 'database'
        
        # Header with sync button
        header_frame = tk.Frame(self.content_frame, bg='#F5F5F5')
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            header_frame,
            text="Database",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        ).pack(side=tk.LEFT)
        
        # Check Firebase status for sync button
        try:
            from database_firebase import DATABASE_TYPE
            is_firebase = (DATABASE_TYPE == 'firebase')
        except (ImportError, AttributeError):
            is_firebase = False
        
        # Sync button (only enabled if Firebase is connected)
        sync_btn = tk.Button(
            header_frame,
            text="🔄 Sync Data from Firebase" if is_firebase else "🔄 Refresh Data",
            font=('Arial', 11, 'bold'),
            bg='#3498DB' if is_firebase else '#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2' if is_firebase else 'arrow',
            command=self._sync_database,
            state=tk.NORMAL if is_firebase else tk.NORMAL  # Always enabled, but shows different behavior
        )
        sync_btn.pack(side=tk.RIGHT, padx=10)
        if is_firebase:
            sync_btn.bind('<Enter>', lambda e: sync_btn.config(bg='#2980B9'))
            sync_btn.bind('<Leave>', lambda e: sync_btn.config(bg='#3498DB'))
        else:
            sync_btn.bind('<Enter>', lambda e: sync_btn.config(bg='#7F8C8D'))
            sync_btn.bind('<Leave>', lambda e: sync_btn.config(bg='#95A5A6'))
        
        info_frame = tk.Frame(self.content_frame, bg='#FFFFFF', relief=tk.FLAT, bd=1, padx=30, pady=30)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            info_frame,
            text="Database Information",
            font=('Arial', 14, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 20))
        
        # Check Firebase connection status
        try:
            from database_firebase import DATABASE_TYPE
            if DATABASE_TYPE == 'firebase':
                connection_status = "✅ Connected to Firebase Firestore"
                status_color = '#27AE60'
                db_type = "Firebase Firestore (Cloud)"
            else:
                connection_status = "❌ Firebase Not Connected"
                status_color = '#E74C3C'
                db_type = "JSON File (Local)"
        except (ImportError, AttributeError):
            connection_status = "❌ Firebase Not Connected"
            status_color = '#E74C3C'
            db_type = "JSON File (Local)"
        
        # Connection status frame
        status_frame = tk.Frame(info_frame, bg='#FFFFFF', relief=tk.SOLID, bd=1, padx=20, pady=15)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            status_frame,
            text="Connection Status:",
            font=('Arial', 11, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(anchor='w')
        
        tk.Label(
            status_frame,
            text=connection_status,
            font=('Arial', 12, 'bold'),
            bg='#FFFFFF',
            fg=status_color
        ).pack(anchor='w', pady=(5, 0))
        
        tk.Label(
            status_frame,
            text=f"Database Type: {db_type}",
            font=('Arial', 10),
            bg='#FFFFFF',
            fg='#7F8C8D'
        ).pack(anchor='w', pady=(5, 0))
        
        # Database stats
        bills = db.get_all_bills()
        users = db.get_all_users()
        inventory = db.get_all_inventory()
        
        # Stats frame
        stats_frame = tk.Frame(info_frame, bg='#F8F9FA', relief=tk.SOLID, bd=1, padx=20, pady=15)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            stats_frame,
            text="Database Statistics",
            font=('Arial', 11, 'bold'),
            bg='#F8F9FA',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 10))
        
        stats_text = f"""Total Users: {len(users)}
Total Bills: {len(bills)}
Total Inventory Items: {len(inventory)}"""
        
        tk.Label(
            stats_frame,
            text=stats_text,
            font=('Arial', 11),
            bg='#F8F9FA',
            fg='#2C3E50',
            justify=tk.LEFT,
            anchor='w'
        ).pack(anchor='w')
        
        # Additional info for Firebase
        if 'firebase' in db_type.lower():
            info_text = """
Firebase Firestore provides:
• Cloud storage - Access data from anywhere
• Real-time synchronization
• Automatic backups
• Scalable infrastructure

Click "Sync Data" to refresh all data from Firebase.
            """
        else:
            info_text = """
JSON Database (Local):
• Data stored locally in data/database.json
• No cloud synchronization
• Manual backup required

To use Firebase, see FIREBASE_SETUP.md
            """
        
        info_text_frame = tk.Frame(info_frame, bg='#FFFFFF')
        info_text_frame.pack(fill=tk.X)
        
        tk.Label(
            info_text_frame,
            text=info_text.strip(),
            font=('Arial', 10),
            bg='#FFFFFF',
            fg='#7F8C8D',
            justify=tk.LEFT,
            anchor='w'
        ).pack(anchor='w', pady=10)
    
    def _sync_database(self):
        """Sync data from Firebase and refresh all views"""
        try:
            # Check if Firebase is connected
            try:
                from database_firebase import DATABASE_TYPE
                if DATABASE_TYPE != 'firebase':
                    messagebox.showinfo(
                        "Sync Not Available",
                        "Firebase is not connected.\n\n"
                        "Sync is only available when using Firebase Firestore.\n"
                        "Currently using JSON database (local storage).\n\n"
                        "See FIREBASE_SETUP.md for setup instructions."
                    )
                    return
            except (ImportError, AttributeError):
                messagebox.showinfo(
                    "Sync Not Available",
                    "Firebase is not connected.\n\n"
                    "Sync is only available when using Firebase Firestore.\n"
                    "Currently using JSON database (local storage)."
                )
                return
            
            # Show syncing message
            sync_dialog = tk.Toplevel(self.root)
            sync_dialog.title("Syncing Data")
            sync_dialog.geometry("350x150")
            sync_dialog.resizable(False, False)
            sync_dialog.grab_set()
            sync_dialog.configure(bg='#FFFFFF')
            
            main_frame = tk.Frame(sync_dialog, bg='#FFFFFF', padx=30, pady=30)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            tk.Label(
                main_frame,
                text="🔄 Syncing data from Firebase...",
                font=('Arial', 12, 'bold'),
                bg='#FFFFFF',
                fg='#2C3E50'
            ).pack(pady=10)
            
            progress_label = tk.Label(
                main_frame,
                text="Please wait...",
                font=('Arial', 10),
                bg='#FFFFFF',
                fg='#7F8C8D'
            )
            progress_label.pack(pady=10)
            
            sync_dialog.update()
            
            try:
                # Refresh all data by querying Firebase
                progress_label.config(text="Syncing users...")
                sync_dialog.update()
                _ = db.get_all_users()  # Force refresh
                
                progress_label.config(text="Syncing inventory...")
                sync_dialog.update()
                _ = db.get_all_inventory()  # Force refresh
                
                progress_label.config(text="Syncing bills...")
                sync_dialog.update()
                _ = db.get_all_bills()  # Force refresh
                
                progress_label.config(text="Updating views...")
                sync_dialog.update()
                
                # Helper function to safely check if widget exists
                def widget_exists(widget):
                    """Check if a widget exists and is still valid"""
                    if not hasattr(self, widget):
                        return False
                    widget_obj = getattr(self, widget, None)
                    if widget_obj is None:
                        return False
                    try:
                        # Try to access widget's winfo_exists to verify it's still valid
                        widget_obj.winfo_exists()
                        return True
                    except (tk.TclError, AttributeError):
                        return False
                
                # Refresh current view only if widgets are accessible
                # Close sync dialog first to avoid widget conflicts
                sync_dialog.destroy()
                
                # Small delay to ensure dialog is fully destroyed
                self.root.update_idletasks()
                
                # Refresh current view
                try:
                    if self.current_view == 'dashboard':
                        self._show_dashboard()
                    elif self.current_view == 'items':
                        self._show_items()
                    elif self.current_view == 'products':
                        self._show_products()
                    elif self.current_view == 'bills':
                        if widget_exists('bills_tree'):
                            self._refresh_bills()
                        else:
                            self._show_bills()
                    elif self.current_view == 'staff':
                        if widget_exists('staff_tree'):
                            self._refresh_staff()
                        else:
                            self._show_staff_management()
                    elif self.current_view == 'database':
                        self._show_database()
                except tk.TclError as e:
                    # Widget was destroyed, recreate the view
                    if self.current_view:
                        if self.current_view == 'dashboard':
                            self._show_dashboard()
                        elif self.current_view == 'items':
                            self._show_items()
                        elif self.current_view == 'products':
                            self._show_products()
                        elif self.current_view == 'bills':
                            self._show_bills()
                        elif self.current_view == 'staff':
                            self._show_staff_management()
                        elif self.current_view == 'database':
                            self._show_database()
                
                messagebox.showinfo(
                    "Sync Complete",
                    "Data successfully synced from Firebase!\n\n"
                    "All views have been refreshed with the latest data."
                )
            except Exception as e:
                # Make sure dialog is destroyed even on error
                try:
                    sync_dialog.destroy()
                except:
                    pass
                
                # Show error message
                error_msg = str(e)
                # Clean up Tkinter widget path errors for user-friendly message
                if "invalid command name" in error_msg:
                    error_msg = "A UI component was not accessible during sync.\n\n" + \
                               "This usually happens when the view changes during sync.\n" + \
                               "The data has been synced successfully.\n\n" + \
                               "Please refresh the view manually if needed."
                
                messagebox.showerror(
                    "Sync Error",
                    f"Failed to sync data from Firebase:\n\n{error_msg}"
                )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to sync database: {str(e)}")
    
    def _show_items(self):
        """Show items interface with barcode support"""
        self.current_view = 'items'
        
        # Title and Add button
        top_frame = tk.Frame(self.content_frame, bg='#F5F5F5')
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            top_frame,
            text="Items Management",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        ).pack(side=tk.LEFT)
        
        button_frame = tk.Frame(top_frame, bg='#F5F5F5')
        button_frame.pack(side=tk.RIGHT)
        
        tk.Button(
            button_frame,
            text="📥 Scan Barcode",
            font=('Arial', 10, 'bold'),
            bg='#27AE60',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._scan_barcode
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="+ Add Item",
            font=('Arial', 11, 'bold'),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self._add_item
        ).pack(side=tk.LEFT, padx=5)
        
        # Items list
        list_frame = tk.Frame(self.content_frame, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.items_tree = ttk.Treeview(
            list_frame,
            columns=('ID', 'Name', 'Category', 'Price', 'Barcode'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.items_tree.yview)
        
        self.items_tree.heading('ID', text='ID')
        self.items_tree.heading('Name', text='Item Name')
        self.items_tree.heading('Category', text='Category')
        self.items_tree.heading('Price', text='Price (₹)')
        self.items_tree.heading('Barcode', text='Barcode')
        
        self.items_tree.column('ID', width=80, anchor='center')
        self.items_tree.column('Name', width=250)
        self.items_tree.column('Category', width=150)
        self.items_tree.column('Price', width=120, anchor='center')
        self.items_tree.column('Barcode', width=150, anchor='center')
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.items_tree.bind('<Double-1>', lambda e: self._download_barcode())
        
        # Action buttons
        action_frame = tk.Frame(self.content_frame, bg='#F5F5F5')
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            action_frame,
            text="📥 Download Barcode",
            font=('Arial', 11),
            bg='#27AE60',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self._download_barcode
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🗑️ Delete Item",
            font=('Arial', 11),
            bg='#E74C3C',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self._delete_item
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🔄 Refresh",
            font=('Arial', 11),
            bg='#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self._refresh_items
        ).pack(side=tk.LEFT, padx=5)
        
        self._refresh_items()
    
    def _show_help(self):
        """Show help section"""
        self.current_view = 'help'
        
        tk.Label(
            self.content_frame,
            text="Help & Documentation",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 20))
        
        help_frame = tk.Frame(self.content_frame, bg='#FFFFFF', relief=tk.FLAT, bd=1, padx=30, pady=30)
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        help_text = """
DROP Billing System - User Guide

Items Management:
• Add items with name, category, and price
• Each item gets an automatic Code 11 barcode
• Scan barcode to quickly find items
• Download barcode images to desktop

Products:
• View all products with monthly sales quantities
• Sales automatically reset each month
• Filter by date range to view historical sales

Bills:
• View all bills with summaries
• Filter by date or specific items
• View detailed bill information

Staff Management:
• Add and manage staff accounts
• View staff activity

Reports:
• Generate sales reports
• View comprehensive statistics

Settings:
• Toggle between light and dark themes

For support, contact your administrator.
        """
        
        tk.Label(
            help_frame,
            text=help_text,
            font=('Arial', 11),
            bg='#FFFFFF',
            fg='#2C3E50',
            justify=tk.LEFT,
            anchor='nw'
        ).pack(fill=tk.BOTH, expand=True)
    
    def _show_bill(self):
        """Show bill customization interface with dimension settings and format preview"""
        self.current_view = 'bill'
        
        # Load saved bill settings
        self._load_bill_settings()
        
        # Title
        tk.Label(
            self.content_frame,
            text="Bill Customization",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 20))
        
        # Main container with two columns
        main_container = tk.Frame(self.content_frame, bg='#F5F5F5')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left column - Configuration
        left_frame = tk.Frame(main_container, bg='#FFFFFF', relief=tk.FLAT, bd=1, padx=20, pady=20)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="📏 Bill Dimensions Configuration",
            font=('Arial', 16, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 20))
        
        # Configuration frame
        config_frame = tk.Frame(left_frame, bg='#F8F9FA', relief=tk.SOLID, bd=1, padx=20, pady=20)
        config_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            config_frame,
            text="Paper Width & Column Settings",
            font=('Arial', 12, 'bold'),
            bg='#F8F9FA',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 15))
        
        # Paper Width Preset
        def on_paper_preset_change(*args):
            preset = self.paper_width_preset_var.get()
            if preset in PAPER_WIDTH_PRESETS and PAPER_WIDTH_PRESETS[preset] is not None:
                self.bill_width_var.set(str(PAPER_WIDTH_PRESETS[preset]))
                if preset == '80mm':
                    # Auto-set common character widths for 80mm
                    self.bill_char_width_var.set("48")
        
        paper_width_frame = tk.Frame(config_frame, bg='#F8F9FA')
        paper_width_frame.pack(fill=tk.X, pady=8)
        tk.Label(paper_width_frame, text="Paper Width:", bg='#F8F9FA', fg='#2C3E50', font=('Arial', 10), width=20, anchor='w').pack(side=tk.LEFT)
        paper_combo = ttk.Combobox(paper_width_frame, textvariable=self.paper_width_preset_var, 
                                   values=list(PAPER_WIDTH_PRESETS.keys()), state='readonly', width=12, font=('Arial', 10))
        paper_combo.pack(side=tk.LEFT, padx=5)
        paper_combo.bind('<<ComboboxSelected>>', on_paper_preset_change)
        self.paper_width_preset_var.trace('w', on_paper_preset_change)
        
        # Bill Width (custom or from preset)
        width_frame = tk.Frame(config_frame, bg='#F8F9FA')
        width_frame.pack(fill=tk.X, pady=8)
        tk.Label(width_frame, text="Receipt Width (mm):", bg='#F8F9FA', fg='#2C3E50', font=('Arial', 10), width=20, anchor='w').pack(side=tk.LEFT)
        width_entry = tk.Entry(width_frame, textvariable=self.bill_width_var, font=('Arial', 10), width=15)
        width_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(width_frame, text="(80mm standard thermal)", bg='#F8F9FA', fg='#7F8C8D', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Column Width / Characters per Line (with presets for 80mm)
        def on_width_change(*args):
            # Auto-suggest column widths when width is 80mm
            try:
                if int(self.bill_width_var.get()) == 80:
                    # Show options for 80mm
                    pass
            except:
                pass
        
        char_frame = tk.Frame(config_frame, bg='#F8F9FA')
        char_frame.pack(fill=tk.X, pady=8)
        tk.Label(char_frame, text="Column Width / Chars per Line:", bg='#F8F9FA', fg='#2C3E50', font=('Arial', 10), width=20, anchor='w').pack(side=tk.LEFT)
        # Dropdown with common options for 80mm
        char_combo_frame = tk.Frame(char_frame, bg='#F8F9FA')
        char_combo_frame.pack(side=tk.LEFT, padx=5)
        char_combo = ttk.Combobox(char_combo_frame, textvariable=self.bill_char_width_var,
                                 values=[str(x) for x in COLUMN_WIDTH_OPTIONS_80MM], width=10, font=('Arial', 10))
        char_combo.pack(side=tk.LEFT)
        char_entry = tk.Entry(char_combo_frame, textvariable=self.bill_char_width_var, font=('Arial', 10), width=8)
        char_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(char_frame, text="(48/56/72 for 80mm)", bg='#F8F9FA', fg='#7F8C8D', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Bill Height/Length
        height_frame = tk.Frame(config_frame, bg='#F8F9FA')
        height_frame.pack(fill=tk.X, pady=8)
        tk.Label(height_frame, text="Bill Height/Length (mm):", bg='#F8F9FA', fg='#2C3E50', font=('Arial', 10), width=20, anchor='w').pack(side=tk.LEFT)
        height_entry = tk.Entry(height_frame, textvariable=self.bill_height_var, font=('Arial', 10), width=15)
        height_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(height_frame, text="(210mm standard)", bg='#F8F9FA', fg='#7F8C8D', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Separator
        tk.Frame(config_frame, bg='#D0D0D0', height=1).pack(fill=tk.X, pady=15)
        
        # Alignment Settings
        tk.Label(
            config_frame,
            text="Text Alignment Settings",
            font=('Arial', 12, 'bold'),
            bg='#F8F9FA',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 15))
        
        alignment_frame = tk.Frame(config_frame, bg='#F8F9FA')
        alignment_frame.pack(fill=tk.X, pady=8)
        tk.Label(alignment_frame, text="Text Alignment:", bg='#F8F9FA', fg='#2C3E50', font=('Arial', 10), width=20, anchor='w').pack(side=tk.LEFT)
        alignment_combo = ttk.Combobox(alignment_frame, textvariable=self.alignment_var,
                                       values=['Left', 'Center', 'Full'], state='readonly', width=12, font=('Arial', 10))
        alignment_combo.pack(side=tk.LEFT, padx=5)
        tk.Label(alignment_frame, text="(Left recommended)", bg='#F8F9FA', fg='#7F8C8D', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Separator
        tk.Frame(config_frame, bg='#D0D0D0', height=1).pack(fill=tk.X, pady=15)
        
        # Margin Settings
        tk.Label(
            config_frame,
            text="Margin Settings (pixels, minimal recommended)",
            font=('Arial', 12, 'bold'),
            bg='#F8F9FA',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 15))
        
        # Top margin
        margin_top_frame = tk.Frame(config_frame, bg='#F8F9FA')
        margin_top_frame.pack(fill=tk.X, pady=5)
        tk.Label(margin_top_frame, text="Top Margin:", bg='#F8F9FA', fg='#2C3E50', font=('Arial', 10), width=20, anchor='w').pack(side=tk.LEFT)
        margin_top_entry = tk.Entry(margin_top_frame, textvariable=self.margin_top_var, font=('Arial', 10), width=15)
        margin_top_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(margin_top_frame, text="(0 recommended)", bg='#F8F9FA', fg='#7F8C8D', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Bottom margin
        margin_bottom_frame = tk.Frame(config_frame, bg='#F8F9FA')
        margin_bottom_frame.pack(fill=tk.X, pady=5)
        tk.Label(margin_bottom_frame, text="Bottom Margin:", bg='#F8F9FA', fg='#2C3E50', font=('Arial', 10), width=20, anchor='w').pack(side=tk.LEFT)
        margin_bottom_entry = tk.Entry(margin_bottom_frame, textvariable=self.margin_bottom_var, font=('Arial', 10), width=15)
        margin_bottom_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(margin_bottom_frame, text="(0 recommended)", bg='#F8F9FA', fg='#7F8C8D', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Left margin
        margin_left_frame = tk.Frame(config_frame, bg='#F8F9FA')
        margin_left_frame.pack(fill=tk.X, pady=5)
        tk.Label(margin_left_frame, text="Left Margin:", bg='#F8F9FA', fg='#2C3E50', font=('Arial', 10), width=20, anchor='w').pack(side=tk.LEFT)
        margin_left_entry = tk.Entry(margin_left_frame, textvariable=self.margin_left_var, font=('Arial', 10), width=15)
        margin_left_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(margin_left_frame, text="(0 recommended)", bg='#F8F9FA', fg='#7F8C8D', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Right margin
        margin_right_frame = tk.Frame(config_frame, bg='#F8F9FA')
        margin_right_frame.pack(fill=tk.X, pady=5)
        tk.Label(margin_right_frame, text="Right Margin:", bg='#F8F9FA', fg='#2C3E50', font=('Arial', 10), width=20, anchor='w').pack(side=tk.LEFT)
        margin_right_entry = tk.Entry(margin_right_frame, textvariable=self.margin_right_var, font=('Arial', 10), width=15)
        margin_right_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(margin_right_frame, text="(0 recommended)", bg='#F8F9FA', fg='#7F8C8D', font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(config_frame, bg='#F8F9FA')
        buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        save_btn = tk.Button(
            buttons_frame,
            text="💾 Save Settings",
            font=('Arial', 11, 'bold'),
            bg='#27AE60',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self._save_bill_settings
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        save_btn.bind('<Enter>', lambda e: save_btn.config(bg='#229954'))
        save_btn.bind('<Leave>', lambda e: save_btn.config(bg='#27AE60'))
        
        reset_btn = tk.Button(
            buttons_frame,
            text="🔄 Reset to Defaults",
            font=('Arial', 10),
            bg='#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=15,
            pady=10,
            cursor='hand2',
            command=self._reset_bill_settings
        )
        reset_btn.pack(side=tk.LEFT)
        reset_btn.bind('<Enter>', lambda e: reset_btn.config(bg='#7F8C8D'))
        reset_btn.bind('<Leave>', lambda e: reset_btn.config(bg='#95A5A6'))
        
        # Test Print Section
        test_print_frame = tk.Frame(left_frame, bg='#E8F5E9', relief=tk.SOLID, bd=1, padx=20, pady=20)
        test_print_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            test_print_frame,
            text="Test Print",
            font=('Arial', 12, 'bold'),
            bg='#E8F5E9',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 15))
        
        tk.Label(
            test_print_frame,
            text="Generate a test bill preview with sample data using current settings",
            font=('Arial', 9),
            bg='#E8F5E9',
            fg='#7F8C8D',
            wraplength=300,
            justify='left'
        ).pack(anchor='w', pady=(0, 15))
        
        test_print_btn = tk.Button(
            test_print_frame,
            text="🖨️ Generate Test Print",
            font=('Arial', 11, 'bold'),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=12,
            cursor='hand2',
            command=self._test_print_bill
        )
        test_print_btn.pack(pady=(0, 5))
        test_print_btn.bind('<Enter>', lambda e: test_print_btn.config(bg='#2980B9'))
        test_print_btn.bind('<Leave>', lambda e: test_print_btn.config(bg='#3498DB'))
        
        # Right column - Preview
        right_frame = tk.Frame(main_container, bg='#FFFFFF', relief=tk.FLAT, bd=1, padx=20, pady=20)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(
            right_frame,
            text="📄 Bill Format Preview",
            font=('Arial', 16, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 15))
        
        # Preview container with scrollbar
        preview_container = tk.Frame(right_frame, bg='#FFFFFF', relief=tk.SOLID, bd=1)
        preview_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        preview_canvas = tk.Canvas(preview_container, bg='#FFFFFF', highlightthickness=1, highlightbackground='#E0E0E0')
        preview_scrollbar = tk.Scrollbar(preview_container, orient="vertical", command=preview_canvas.yview)
        preview_scrollable = tk.Frame(preview_canvas, bg='#FFFFFF')
        
        preview_scrollable.bind(
            "<Configure>",
            lambda e: preview_canvas.configure(scrollregion=preview_canvas.bbox("all"))
        )
        
        preview_canvas.create_window((0, 0), window=preview_scrollable, anchor="nw")
        preview_canvas.configure(yscrollcommand=preview_scrollbar.set)
        
        preview_canvas.pack(side="left", fill="both", expand=True)
        preview_scrollbar.pack(side="right", fill="y")
        
        # Update preview function
        def update_preview():
            """Update the live preview"""
            for widget in preview_scrollable.winfo_children():
                widget.destroy()
            
            try:
                width_mm = int(self.bill_width_var.get())
                height_mm = int(self.bill_height_var.get())
                char_width = int(self.bill_char_width_var.get())
            except ValueError:
                width_mm = DEFAULT_BILL_WIDTH_MM
                height_mm = DEFAULT_BILL_HEIGHT_MM
                char_width = DEFAULT_CHARACTER_WIDTH
            
            # Calculate preview size (approximate: 1mm ≈ 3.78 pixels at 96 DPI)
            preview_w = int(width_mm * 3.78)
            preview_h = min(int(height_mm * 3.78), 600)  # Limit height for display
            
            # Create preview frame with calculated dimensions
            preview_inner = tk.Frame(preview_scrollable, bg='#FFFFFF', width=preview_w, height=preview_h, relief=tk.SOLID, bd=2)
            preview_inner.pack(padx=20, pady=20)
            preview_inner.pack_propagate(False)
            
            # Draw bill preview
            header_frame = tk.Frame(preview_inner, bg='#FFFFFF')
            header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
            
            tk.Label(header_frame, text=SHOP_NAME, font=('Arial', 14, 'bold'), bg='#FFFFFF', fg='#000000').pack()
            tk.Label(header_frame, text=SHOP_TAGLINE, font=('Arial', 8, 'italic'), bg='#FFFFFF', fg='#000000').pack()
            tk.Label(header_frame, text=SHOP_ADDRESS[:char_width-5], font=('Arial', 7), bg='#FFFFFF', fg='#000000', wraplength=char_width*6).pack(pady=(2, 5))
            
            tk.Frame(preview_inner, bg='#000000', height=1).pack(fill=tk.X, padx=10, pady=5)
            
            info_frame = tk.Frame(preview_inner, bg='#FFFFFF')
            info_frame.pack(fill=tk.X, padx=10, pady=2)
            tk.Label(info_frame, text="DATE: 2025-01-15", font=('Arial', 8), bg='#FFFFFF', anchor='w').pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(info_frame, text="BILL NO: DR0001", font=('Arial', 8), bg='#FFFFFF', anchor='e').pack(side=tk.RIGHT)
            
            tk.Frame(preview_inner, bg='#000000', height=1).pack(fill=tk.X, padx=10, pady=5)
            
            # Table
            table_frame = tk.Frame(preview_inner, bg='#FFFFFF')
            table_frame.pack(fill=tk.X, padx=10, pady=5)
            
            header_row = tk.Frame(table_frame, bg='#FFFFFF')
            header_row.pack(fill=tk.X)
            tk.Label(header_row, text="PRODUCT", font=('Arial', 8, 'bold'), bg='#FFFFFF', anchor='w', width=20).pack(side=tk.LEFT)
            tk.Label(header_row, text="QTY", font=('Arial', 8, 'bold'), bg='#FFFFFF', anchor='center', width=5).pack(side=tk.LEFT)
            tk.Label(header_row, text="PRICE", font=('Arial', 8, 'bold'), bg='#FFFFFF', anchor='center', width=8).pack(side=tk.LEFT)
            tk.Label(header_row, text="TOTAL", font=('Arial', 8, 'bold'), bg='#FFFFFF', anchor='center', width=8).pack(side=tk.LEFT)
            
            tk.Frame(preview_inner, bg='#000000', height=1).pack(fill=tk.X, padx=10, pady=2)
            
            # Sample items
            for item in [("Test Item 1", 2, 25.00, 50.00), ("Test Item 2", 1, 40.00, 40.00)]:
                item_row = tk.Frame(table_frame, bg='#FFFFFF')
                item_row.pack(fill=tk.X)
                tk.Label(item_row, text=item[0][:18], font=('Arial', 7), bg='#FFFFFF', anchor='w', width=20).pack(side=tk.LEFT)
                tk.Label(item_row, text=str(item[1]), font=('Arial', 7), bg='#FFFFFF', anchor='center', width=5).pack(side=tk.LEFT)
                tk.Label(item_row, text=f"₹{item[2]:.2f}", font=('Arial', 7), bg='#FFFFFF', anchor='center', width=8).pack(side=tk.LEFT)
                tk.Label(item_row, text=f"₹{item[3]:.2f}", font=('Arial', 7), bg='#FFFFFF', anchor='center', width=8).pack(side=tk.LEFT)
            
            tk.Frame(preview_inner, bg='#000000', height=1).pack(fill=tk.X, padx=10, pady=5)
            
            total_frame = tk.Frame(preview_inner, bg='#FFFFFF')
            total_frame.pack(fill=tk.X, padx=10, pady=5)
            tk.Label(total_frame, text="TOTAL:", font=('Arial', 9, 'bold'), bg='#FFFFFF', anchor='e').pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(total_frame, text="₹90.00", font=('Arial', 9, 'bold'), bg='#FFFFFF', anchor='e').pack(side=tk.RIGHT)
            
            tk.Label(preview_inner, text="Payment: Cash", font=('Arial', 8), bg='#FFFFFF').pack(pady=5)
            tk.Label(preview_inner, text="Thank you!", font=('Arial', 7), bg='#FFFFFF').pack(pady=2)
            
            # Dimensions label
            dim_label = tk.Label(
                preview_scrollable,
                text=f"Dimensions: {width_mm}mm × {height_mm}mm | {char_width} chars/line",
                font=('Arial', 9),
                bg='#FFFFFF',
                fg='#7F8C8D'
            )
            dim_label.pack(pady=(10, 0))
        
        # Bind update on changes
        self.bill_width_var.trace('w', lambda *args: update_preview())
        self.bill_height_var.trace('w', lambda *args: update_preview())
        self.bill_char_width_var.trace('w', lambda *args: update_preview())
        
        # Initial preview
        update_preview()
    
    def _load_bill_settings(self):
        """Load bill settings from file"""
        import json
        settings_file = os.path.join('data', 'bill_settings.json')
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.bill_width_var.set(str(settings.get('width_mm', DEFAULT_BILL_WIDTH_MM)))
                    self.bill_height_var.set(str(settings.get('height_mm', DEFAULT_BILL_HEIGHT_MM)))
                    self.bill_char_width_var.set(str(settings.get('char_width', DEFAULT_CHARACTER_WIDTH)))
                    
                    # Load new settings with defaults
                    paper_preset = settings.get('paper_width_preset', '80mm')
                    if paper_preset in PAPER_WIDTH_PRESETS:
                        self.paper_width_preset_var.set(paper_preset)
                    else:
                        self.paper_width_preset_var.set('80mm')
                    
                    self.alignment_var.set(settings.get('alignment', DEFAULT_ALIGNMENT))
                    self.margin_top_var.set(str(settings.get('margin_top', DEFAULT_MARGIN_TOP)))
                    self.margin_bottom_var.set(str(settings.get('margin_bottom', DEFAULT_MARGIN_BOTTOM)))
                    self.margin_left_var.set(str(settings.get('margin_left', DEFAULT_MARGIN_LEFT)))
                    self.margin_right_var.set(str(settings.get('margin_right', DEFAULT_MARGIN_RIGHT)))
            else:
                # Use defaults
                self.bill_width_var.set(str(DEFAULT_BILL_WIDTH_MM))
                self.bill_height_var.set(str(DEFAULT_BILL_HEIGHT_MM))
                self.bill_char_width_var.set(str(DEFAULT_CHARACTER_WIDTH))
                self.paper_width_preset_var.set('80mm')
                self.alignment_var.set(DEFAULT_ALIGNMENT)
                self.margin_top_var.set(str(DEFAULT_MARGIN_TOP))
                self.margin_bottom_var.set(str(DEFAULT_MARGIN_BOTTOM))
                self.margin_left_var.set(str(DEFAULT_MARGIN_LEFT))
                self.margin_right_var.set(str(DEFAULT_MARGIN_RIGHT))
        except Exception:
            # Use defaults on error
            self.bill_width_var.set(str(DEFAULT_BILL_WIDTH_MM))
            self.bill_height_var.set(str(DEFAULT_BILL_HEIGHT_MM))
            self.bill_char_width_var.set(str(DEFAULT_CHARACTER_WIDTH))
            self.paper_width_preset_var.set('80mm')
            self.alignment_var.set(DEFAULT_ALIGNMENT)
            self.margin_top_var.set(str(DEFAULT_MARGIN_TOP))
            self.margin_bottom_var.set(str(DEFAULT_MARGIN_BOTTOM))
            self.margin_left_var.set(str(DEFAULT_MARGIN_LEFT))
            self.margin_right_var.set(str(DEFAULT_MARGIN_RIGHT))
    
    def _save_bill_settings(self):
        """Save bill settings to file"""
        import json
        
        try:
            width_mm = int(self.bill_width_var.get())
            height_mm = int(self.bill_height_var.get())
            char_width = int(self.bill_char_width_var.get())
            margin_top = int(self.margin_top_var.get())
            margin_bottom = int(self.margin_bottom_var.get())
            margin_left = int(self.margin_left_var.get())
            margin_right = int(self.margin_right_var.get())
            
            # Validate ranges
            if not (50 <= width_mm <= 150):
                messagebox.showerror("Error", "Bill width must be between 50mm and 150mm")
                return
            if not (100 <= height_mm <= 500):
                messagebox.showerror("Error", "Bill height must be between 100mm and 500mm")
                return
            if not (30 <= char_width <= 80):
                messagebox.showerror("Error", "Character width must be between 30 and 80")
                return
            
            # Validate margins (non-negative)
            if margin_top < 0 or margin_bottom < 0 or margin_left < 0 or margin_right < 0:
                messagebox.showerror("Error", "Margins must be non-negative values")
                return
            
            settings = {
                'width_mm': width_mm,
                'height_mm': height_mm,
                'char_width': char_width,
                'paper_width_preset': self.paper_width_preset_var.get(),
                'alignment': self.alignment_var.get(),
                'margin_top': margin_top,
                'margin_bottom': margin_bottom,
                'margin_left': margin_left,
                'margin_right': margin_right
            }
            
            os.makedirs('data', exist_ok=True)
            settings_file = os.path.join('data', 'bill_settings.json')
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            messagebox.showinfo("Success", "Bill settings saved successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all fields")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")
    
    def _reset_bill_settings(self):
        """Reset bill settings to defaults"""
        self.bill_width_var.set(str(DEFAULT_BILL_WIDTH_MM))
        self.bill_height_var.set(str(DEFAULT_BILL_HEIGHT_MM))
        self.bill_char_width_var.set(str(DEFAULT_CHARACTER_WIDTH))
        self.paper_width_preset_var.set('80mm')
        self.alignment_var.set(DEFAULT_ALIGNMENT)
        self.margin_top_var.set(str(DEFAULT_MARGIN_TOP))
        self.margin_bottom_var.set(str(DEFAULT_MARGIN_BOTTOM))
        self.margin_left_var.set(str(DEFAULT_MARGIN_LEFT))
        self.margin_right_var.set(str(DEFAULT_MARGIN_RIGHT))
        messagebox.showinfo("Success", "Bill settings reset to defaults")
    
    def _test_print_bill(self):
        """Generate a test bill preview with current settings"""
        import json
        from bill_preview import BillPreview
        
        try:
            # Get current settings from UI
            width_mm = int(self.bill_width_var.get())
            height_mm = int(self.bill_height_var.get())
            char_width = int(self.bill_char_width_var.get())
            margin_top = int(self.margin_top_var.get())
            margin_bottom = int(self.margin_bottom_var.get())
            margin_left = int(self.margin_left_var.get())
            margin_right = int(self.margin_right_var.get())
            
            # Validate ranges
            if not (50 <= width_mm <= 150):
                messagebox.showerror("Error", "Bill width must be between 50mm and 150mm")
                return
            if not (100 <= height_mm <= 500):
                messagebox.showerror("Error", "Bill height must be between 100mm and 500mm")
                return
            if not (30 <= char_width <= 80):
                messagebox.showerror("Error", "Character width must be between 30 and 80")
                return
            
            # Validate margins (non-negative)
            if margin_top < 0 or margin_bottom < 0 or margin_left < 0 or margin_right < 0:
                messagebox.showerror("Error", "Margins must be non-negative values")
                return
            
            # Temporarily save current settings to file (so BillPreview can use them)
            settings = {
                'width_mm': width_mm,
                'height_mm': height_mm,
                'char_width': char_width,
                'paper_width_preset': self.paper_width_preset_var.get(),
                'alignment': self.alignment_var.get(),
                'margin_top': margin_top,
                'margin_bottom': margin_bottom,
                'margin_left': margin_left,
                'margin_right': margin_right
            }
            
            os.makedirs('data', exist_ok=True)
            settings_file = os.path.join('data', 'bill_settings.json')
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            # Create sample bill items for test
            test_bill_items = [
                {
                    'name': 'Test Item 1',
                    'quantity': 2,
                    'price': 25.00,
                    'total': 50.00
                },
                {
                    'name': 'Test Item 2',
                    'quantity': 1,
                    'price': 40.00,
                    'total': 40.00
                },
                {
                    'name': 'Sample Product Name',
                    'quantity': 3,
                    'price': 15.50,
                    'total': 46.50
                }
            ]
            
            test_total = sum(item['total'] for item in test_bill_items)
            test_payment_method = 'Cash'
            
            # Create a dummy user for test
            test_user = {
                'id': 0,
                'name': 'Test User',
                'role': 'staff'
            }
            
            # Open bill preview with test data
            BillPreview(
                self.root,
                test_bill_items,
                test_total,
                test_payment_method,
                test_user,
                bill_id='TEST01'
            )
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for all fields")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate test print: {str(e)}")
    
    def _show_products(self):
        """Show products interface with monthly sales tracking"""
        self.current_view = 'products'
        
        # Title and filter
        top_frame = tk.Frame(self.content_frame, bg='#F5F5F5')
        top_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            top_frame,
            text="Products",
            font=('Arial', 20, 'bold'),
            bg='#F5F5F5',
            fg='#2C3E50'
        ).pack(side=tk.LEFT)
        
        filter_frame = tk.Frame(top_frame, bg='#F5F5F5')
        filter_frame.pack(side=tk.RIGHT)
        
        tk.Label(filter_frame, text="Date Filter:", bg='#F5F5F5', fg='#2C3E50').pack(side=tk.LEFT, padx=5)
        
        self.product_date_filter = tk.StringVar(value="Current Month")
        date_filter = ttk.Combobox(filter_frame, textvariable=self.product_date_filter, 
                                  values=["Current Month", "Last Month", "All Time", "Custom Range"], 
                                  width=15, state='readonly')
        date_filter.pack(side=tk.LEFT, padx=5)
        date_filter.bind('<<ComboboxSelected>>', lambda e: self._refresh_products())
        
        # Products grid/list
        list_frame = tk.Frame(self.content_frame, bg='#FFFFFF', relief=tk.FLAT, bd=1)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.products_tree = ttk.Treeview(
            list_frame,
            columns=('ID', 'Name', 'Category', 'Price', 'Monthly Sales'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.products_tree.yview)
        
        self.products_tree.heading('ID', text='ID')
        self.products_tree.heading('Name', text='Product Name')
        self.products_tree.heading('Category', text='Category')
        self.products_tree.heading('Price', text='Price (₹)')
        self.products_tree.heading('Monthly Sales', text='Qty Sold (This Month)')
        
        self.products_tree.column('ID', width=80, anchor='center')
        self.products_tree.column('Name', width=250)
        self.products_tree.column('Category', width=150)
        self.products_tree.column('Price', width=120, anchor='center')
        self.products_tree.column('Monthly Sales', width=150, anchor='center')
        
        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Button(
            self.content_frame,
            text="🔄 Refresh",
            font=('Arial', 11),
            bg='#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            command=self._refresh_products
        ).pack(pady=10)
        
        self._refresh_products()
    
    def _refresh_products(self):
        """Refresh products list with monthly sales"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        inventory = db.get_all_inventory()
        filter_value = self.product_date_filter.get()
        
        current_month = datetime.now().strftime('%Y-%m')
        
        for item in inventory:
            if filter_value == "Current Month":
                sales_qty = db.get_item_monthly_sales(item['id'], current_month)
            elif filter_value == "Last Month":
                last_month_date = datetime.now().replace(day=1) - timedelta(days=1)
                last_month = last_month_date.strftime('%Y-%m')
                sales_qty = db.get_item_monthly_sales(item['id'], last_month)
            elif filter_value == "All Time":
                # Calculate total sales from all bills
                sales_qty = 0
                for bill in db.get_all_bills():
                    for bill_item in bill['items']:
                        if bill_item.get('inventory_id') == item['id']:
                            sales_qty += bill_item['quantity']
            else:  # Current Month (default)
                sales_qty = db.get_item_monthly_sales(item['id'], current_month)
            
            self.products_tree.insert('', 'end', values=(
                item['id'],
                item['name'],
                item['category'],
                f"₹{item['price']:.2f}",
                sales_qty
            ))
    
    # Staff Management Methods
    def _refresh_staff(self):
        """Refresh staff list"""
        for item in self.staff_tree.get_children():
            self.staff_tree.delete(item)
        
        staff = db.get_all_users(role='staff')
        for user in staff:
            self.staff_tree.insert('', 'end', values=(
                user['id'],
                user['username'],
                user['name'],
                user['role']
            ))
    
    def _add_staff_member(self):
        """Add new staff member"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Staff")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg='#FFFFFF')
        
        main_frame = tk.Frame(dialog, bg='#FFFFFF', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Username:", bg='#FFFFFF', fg='#2C3E50').grid(row=0, column=0, sticky='w', pady=10)
        username_entry = tk.Entry(main_frame, width=30, font=('Arial', 10))
        username_entry.grid(row=0, column=1, pady=10)
        
        tk.Label(main_frame, text="Password:", bg='#FFFFFF', fg='#2C3E50').grid(row=1, column=0, sticky='w', pady=10)
        password_entry = tk.Entry(main_frame, width=30, font=('Arial', 10), show='*')
        password_entry.grid(row=1, column=1, pady=10)
        
        tk.Label(main_frame, text="Name:", bg='#FFFFFF', fg='#2C3E50').grid(row=2, column=0, sticky='w', pady=10)
        name_entry = tk.Entry(main_frame, width=30, font=('Arial', 10))
        name_entry.grid(row=2, column=1, pady=10)
        
        def save():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            name = name_entry.get().strip()
            
            if not all([username, password, name]):
                messagebox.showerror("Error", "Please fill all fields", parent=dialog)
                return
            
            existing_users = db.get_all_users()
            if any(u['username'] == username for u in existing_users):
                messagebox.showerror("Error", "Username already exists", parent=dialog)
                return
            
            db.add_user(username, password, 'staff', name)
            self._refresh_staff()
            dialog.destroy()
            messagebox.showinfo("Success", "Staff member added successfully")
        
        button_frame = tk.Frame(main_frame, bg='#FFFFFF')
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Save", command=save, bg='#3498DB', fg='#FFFFFF', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg='#95A5A6', fg='#FFFFFF', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        username_entry.focus_set()
    
    def _delete_staff(self):
        """Delete selected staff member"""
        selection = self.staff_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a staff member to delete")
            return
        
        user_id = int(self.staff_tree.item(selection[0])['values'][0])
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this staff member?"):
            db.data['users'] = [u for u in db.data['users'] if u['id'] != user_id]
            db.save()
            self._refresh_staff()
            messagebox.showinfo("Success", "Staff member deleted successfully")
    
    # Bills Management Methods
    def _refresh_bills(self):
        """Refresh bills list with filters"""
        for item in self.bills_tree.get_children():
            self.bills_tree.delete(item)
        
        # Get filtered bills using helper method
        sorted_bills = self._get_filtered_bills()
        
        for index, bill in enumerate(sorted_bills, start=1):
            staff_user = db.get_user(bill['user_id'])
            staff_name = staff_user['name'] if staff_user else 'Unknown'
            date_str = datetime.fromisoformat(bill['date']).strftime("%Y-%m-%d %H:%M")
            bill_id = bill.get('id', 'N/A')
            # Ensure bill ID is in DR0201 format
            if isinstance(bill_id, (int, float)):
                bill_id = f"DR{str(int(bill_id)).zfill(4)}"
            
            # Format items list
            items_list = []
            for item in bill.get('items', []):
                item_name = item.get('name', 'Unknown')
                item_qty = item.get('quantity', 1)
                if item_qty > 1:
                    items_list.append(f"{item_name} (x{item_qty})")
                else:
                    items_list.append(item_name)
            items_display = ", ".join(items_list)
            # Truncate if too long
            if len(items_display) > 70:
                items_display = items_display[:67] + "..."
            
            self.bills_tree.insert('', 'end', values=(
                index,
                bill_id,
                date_str,
                staff_name,
                items_display,
                f"₹{bill['total']:.2f}",
                bill['payment_method']
            ))
    
    def _get_filtered_bills(self):
        """Get filtered bills based on current filter settings"""
        bills = db.get_all_bills()
        date_filter = self.date_filter_var.get()
        item_filter = self.item_filter_var.get()
        bill_id_search = self.bill_id_search_var.get().strip()
        
        # Apply Bill ID search filter (applied first for performance)
        if bill_id_search:
            search_id_lower = bill_id_search.upper().strip()
            filtered_bills = []
            for bill in bills:
                bill_id = bill.get('id', '')
                # Ensure bill_id is in DR0201 format for comparison
                if isinstance(bill_id, (int, float)):
                    bill_id_str = f"DR{str(int(bill_id)).zfill(4)}"
                else:
                    bill_id_str = str(bill_id).upper()
                
                # Check if search matches (supports both DR0201 and numeric input)
                if search_id_lower in bill_id_str:
                    filtered_bills.append(bill)
                else:
                    # Try numeric search (e.g., search "201" matches "DR0201")
                    try:
                        if search_id_lower.isdigit():
                            # Extract number from DR format
                            bill_num = int(bill_id_str.replace('DR', '').strip()) if 'DR' in bill_id_str else 0
                            search_num = int(search_id_lower)
                            if bill_num == search_num:
                                filtered_bills.append(bill)
                    except (ValueError, TypeError):
                        continue
            bills = filtered_bills
        
        # Apply date filter
        if date_filter != "All":
            now = datetime.now()
            filtered_bills = []
            for bill in bills:
                bill_date = datetime.fromisoformat(bill['date'])
                bill_date_only = bill_date.date()
                
                if date_filter == "Today":
                    if bill_date_only == now.date():
                        filtered_bills.append(bill)
                elif date_filter == "This Week":
                    days_diff = (now.date() - bill_date_only).days
                    if 0 <= days_diff <= 7:
                        filtered_bills.append(bill)
                elif date_filter == "This Month":
                    if bill_date.year == now.year and bill_date.month == now.month:
                        filtered_bills.append(bill)
                elif date_filter == "Custom Range":
                    start_date_str = self.start_date_var.get()
                    end_date_str = self.end_date_var.get()
                    
                    if start_date_str or end_date_str:
                        try:
                            if start_date_str:
                                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                            else:
                                start_date = None
                            
                            if end_date_str:
                                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                            else:
                                end_date = None
                            
                            # Check if bill date falls within range
                            if start_date and end_date:
                                if start_date <= bill_date_only <= end_date:
                                    filtered_bills.append(bill)
                            elif start_date:
                                if bill_date_only >= start_date:
                                    filtered_bills.append(bill)
                            elif end_date:
                                if bill_date_only <= end_date:
                                    filtered_bills.append(bill)
                        except ValueError:
                            pass  # Invalid date format, skip this filter
            bills = filtered_bills
        
        # Apply item filter
        if item_filter != "All Items":
            filtered_bills = []
            # Find item ID
            item_id = None
            for item in db.get_all_inventory():
                if item['name'] == item_filter:
                    item_id = item['id']
                    break
            
            if item_id:
                for bill in bills:
                    # Check if bill contains this item
                    for bill_item in bill['items']:
                        if bill_item.get('inventory_id') == item_id:
                            filtered_bills.append(bill)
                            break
            bills = filtered_bills
        
        # Sort bills by date (newest first) for consistent numbering
        sorted_bills = sorted(bills, key=lambda x: x['date'], reverse=True)
        return sorted_bills
    
    def _export_filtered_bills(self):
        """Export filtered bills data to CSV file"""
        try:
            # Get filtered bills
            filtered_bills = self._get_filtered_bills()
            
            if not filtered_bills:
                messagebox.showinfo("No Data", "No bills match the current filters. Nothing to export.")
                return
            
            # Ask user for save location
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Filtered Bills Data",
                initialfile=f"bills_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return  # User cancelled
            
            # Write to CSV
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'No', 'Bill ID', 'Date', 'Time', 'Staff Member', 
                    'Items', 'Item Details', 'Total (₹)', 'Payment Method'
                ])
                
                # Write bill data
                for index, bill in enumerate(filtered_bills, start=1):
                    staff_user = db.get_user(bill['user_id'])
                    staff_name = staff_user['name'] if staff_user else 'Unknown'
                    
                    bill_date = datetime.fromisoformat(bill['date'])
                    date_str = bill_date.strftime("%Y-%m-%d")
                    time_str = bill_date.strftime("%H:%M:%S")
                    
                    bill_id = bill.get('id', 'N/A')
                    # Ensure bill ID is in DR0201 format
                    if isinstance(bill_id, (int, float)):
                        bill_id = f"DR{str(int(bill_id)).zfill(4)}"
                    
                    # Format items list
                    items_list = []
                    items_details = []
                    for item in bill.get('items', []):
                        item_name = item.get('name', 'Unknown')
                        item_qty = item.get('quantity', 1)
                        item_price = item.get('price', 0)
                        item_total = item.get('total', 0)
                        
                        if item_qty > 1:
                            items_list.append(f"{item_name} (x{item_qty})")
                        else:
                            items_list.append(item_name)
                        
                        items_details.append(f"{item_name}: Qty={item_qty}, Price=₹{item_price:.2f}, Total=₹{item_total:.2f}")
                    
                    items_display = ", ".join(items_list)
                    items_details_str = " | ".join(items_details)
                    
                    writer.writerow([
                        index,
                        bill_id,
                        date_str,
                        time_str,
                        staff_name,
                        items_display,
                        items_details_str,
                        f"{bill['total']:.2f}",
                        bill['payment_method']
                    ])
            
            messagebox.showinfo(
                "Export Successful",
                f"Successfully exported {len(filtered_bills)} bill(s) to:\n{filename}"
            )
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export bills: {str(e)}")
    
    def _view_bill_details(self):
        """View details of selected bill"""
        selection = self.bills_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a bill to view")
            return
        
        # Get bill ID from the second column (index 1, after 'No' column)
        bill_id_value = str(self.bills_tree.item(selection[0])['values'][1])
        
        # Find bill by ID (handle both DR0201 format and numeric)
        bills = db.get_all_bills()
        bill = None
        
        # Normalize the search value
        search_value = bill_id_value.upper().strip()
        
        for b in bills:
            bill_id_check = b.get('id', '')
            
            # Normalize bill ID for comparison
            if isinstance(bill_id_check, str):
                bill_id_normalized = bill_id_check.upper().strip()
            elif isinstance(bill_id_check, (int, float)):
                bill_id_normalized = f"DR{str(int(bill_id_check)).zfill(4)}"
            else:
                bill_id_normalized = str(bill_id_check).upper().strip()
            
            # Direct match
            if search_value == bill_id_normalized:
                bill = b
                break
            
            # Try numeric ID match if search value is DR format
            if search_value.startswith('DR'):
                try:
                    search_num = int(search_value.replace('DR', '').strip())
                    bill_num_id = b.get('numeric_id', 0)
                    if bill_num_id == search_num:
                        bill = b
                        break
                except (ValueError, AttributeError):
                    pass
            
            # Try matching numeric_id
            bill_num_id = b.get('numeric_id', 0)
            if bill_num_id == 0 and isinstance(bill_id_check, (int, float)):
                bill_num_id = int(bill_id_check)
            
            if search_value.isdigit():
                try:
                    search_num = int(search_value)
                    if bill_num_id == search_num:
                        bill = b
                        break
                except ValueError:
                    pass
        
        if not bill:
            messagebox.showerror("Error", f"Bill not found: {bill_id_value}")
            return
        
        # Get display ID
        display_bill_id = bill.get('id', bill_id_value)
        if isinstance(display_bill_id, (int, float)):
            display_bill_id = f"DR{str(int(display_bill_id)).zfill(4)}"
        
        details_window = tk.Toplevel(self.root)
        details_window.title(f"Bill #{display_bill_id} Details")
        details_window.geometry("500x600")
        details_window.configure(bg='#FFFFFF')
        
        main_frame = tk.Frame(details_window, bg='#FFFFFF', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text=f"Bill #{display_bill_id}", font=('Arial', 18, 'bold'), bg='#FFFFFF', fg='#2C3E50').pack(pady=10)
        
        staff_user = db.get_user(bill['user_id'])
        date_str = datetime.fromisoformat(bill['date']).strftime("%Y-%m-%d %H:%M:%S")
        
        info_text = f"Date: {date_str}\nStaff: {staff_user['name'] if staff_user else 'Unknown'}\nPayment: {bill['payment_method']}"
        tk.Label(main_frame, text=info_text, bg='#FFFFFF', fg='#2C3E50', justify=tk.LEFT).pack(pady=10)
        
        tk.Label(main_frame, text="Items:", font=('Arial', 12, 'bold'), bg='#FFFFFF', fg='#2C3E50').pack(pady=(20, 10))
        
        items_frame = tk.Frame(main_frame, bg='#F5F5F5', relief=tk.SOLID, borderwidth=1)
        items_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for item in bill['items']:
            item_text = f"{item['name']} x{item['quantity']} @ ₹{item['price']:.2f} = ₹{item['total']:.2f}"
            tk.Label(items_frame, text=item_text, bg='#F5F5F5', fg='#2C3E50', anchor='w', padx=10, pady=5).pack(fill=tk.X)
        
        total_frame = tk.Frame(main_frame, bg='#FFFFFF')
        total_frame.pack(fill=tk.X, pady=20)
        
        tk.Label(total_frame, text=f"Total: ₹{bill['total']:.2f}", font=('Arial', 16, 'bold'), bg='#FFFFFF', fg='#3498DB').pack()
        
        tk.Button(main_frame, text="Close", command=details_window.destroy, bg='#3498DB', fg='#FFFFFF', padx=20, pady=5).pack(pady=10)
    
    def _delete_bill(self):
        """Delete selected bill"""
        selection = self.bills_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a bill to delete")
            return
        
        # Get bill ID from the second column (index 1, after 'No' column)
        bill_id_value = str(self.bills_tree.item(selection[0])['values'][1])
        
        # Find bill and delete it
        bills = db.get_all_bills()
        bill_to_delete = None
        
        # Normalize the search value
        search_value = bill_id_value.upper().strip()
        
        for b in bills:
            bill_id_check = b.get('id', '')
            
            # Normalize bill ID for comparison
            if isinstance(bill_id_check, str):
                bill_id_normalized = bill_id_check.upper().strip()
            elif isinstance(bill_id_check, (int, float)):
                bill_id_normalized = f"DR{str(int(bill_id_check)).zfill(4)}"
            else:
                bill_id_normalized = str(bill_id_check).upper().strip()
            
            # Direct match
            if search_value == bill_id_normalized:
                bill_to_delete = b
                break
            
            # Try numeric ID match if search value is DR format
            if search_value.startswith('DR'):
                try:
                    search_num = int(search_value.replace('DR', '').strip())
                    bill_num_id = b.get('numeric_id', 0)
                    if bill_num_id == search_num:
                        bill_to_delete = b
                        break
                except (ValueError, AttributeError):
                    pass
            
            # Try matching numeric_id
            bill_num_id = b.get('numeric_id', 0)
            if bill_num_id == 0 and isinstance(bill_id_check, (int, float)):
                bill_num_id = int(bill_id_check)
            
            if search_value.isdigit():
                try:
                    search_num = int(search_value)
                    if bill_num_id == search_num:
                        bill_to_delete = b
                        break
                except ValueError:
                    pass
        
        if not bill_to_delete:
            messagebox.showerror("Error", f"Bill not found: {bill_id_value}")
            return
        
        display_bill_id = bill_to_delete.get('id', bill_id_value)
        if isinstance(display_bill_id, (int, float)):
            display_bill_id = f"DR{str(int(display_bill_id)).zfill(4)}"
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete bill {display_bill_id}?"):
            db.delete_bill(bill_to_delete.get('id'))
            self._refresh_bills()
            messagebox.showinfo("Success", f"Bill {display_bill_id} deleted successfully")
    
    def _delete_all_bills(self):
        """Delete all bills with confirmation"""
        bills = db.get_all_bills()
        total_bills = len(bills)
        
        if total_bills == 0:
            messagebox.showinfo("Info", "No bills to delete")
            return
        
        # Strong confirmation dialog
        confirm_message = (
            f"⚠️ WARNING: You are about to delete ALL bills!\n\n"
            f"Total bills to delete: {total_bills}\n\n"
            f"This action CANNOT be undone.\n"
            f"All bill records will be permanently deleted.\n\n"
            f"Are you absolutely sure you want to continue?"
        )
        
        # First confirmation
        if not messagebox.askyesno(
            "Delete All Bills - First Confirmation",
            confirm_message,
            icon='warning'
        ):
            return
        
        # Second confirmation for extra safety
        if not messagebox.askyesno(
            "Delete All Bills - Final Confirmation",
            f"⚠️ FINAL WARNING!\n\n"
            f"You are about to permanently delete {total_bills} bill(s).\n\n"
            f"This action CANNOT be reversed!\n\n"
            f"Type YES to confirm or click No to cancel.",
            icon='error'
        ):
            return
        
        try:
            # Delete all bills one by one
            deleted_count = 0
            for bill in bills:
                bill_id = bill.get('id')
                try:
                    result = db.delete_bill(bill_id)
                    # Some databases return True/False, others return None
                    if result is not False:
                        deleted_count += 1
                except Exception:
                    # Continue with next bill if one fails
                    pass
            
            # Refresh the view
            self._refresh_bills()
            
            if deleted_count == total_bills:
                messagebox.showinfo(
                    "Success",
                    f"All bills deleted successfully!\n\n"
                    f"Deleted: {deleted_count} bill(s)"
                )
            elif deleted_count > 0:
                messagebox.showwarning(
                    "Partial Success",
                    f"Some bills were deleted, but not all.\n\n"
                    f"Deleted: {deleted_count} out of {total_bills} bill(s)"
                )
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to delete any bills.\n\n"
                    "Please check database connection."
                )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to delete all bills:\n\n{str(e)}"
            )
    
    # Reports Methods
    def _update_reports_stats(self, frame):
        """Update reports statistics display"""
        for widget in frame.winfo_children():
            widget.destroy()
        
        bills = db.get_all_bills()
        inventory = db.get_all_inventory()
        
        total_sales = sum(bill['total'] for bill in bills)
        total_bills = len(bills)
        total_items_sold = sum(sum(item['quantity'] for item in bill['items']) for bill in bills)
        avg_bill_value = total_sales / total_bills if total_bills > 0 else 0
        
        today = datetime.now().date()
        today_bills = [b for b in bills if datetime.fromisoformat(b['date']).date() == today]
        today_sales = sum(b['total'] for b in today_bills)
        
        stats = [
            ("Total Sales", f"₹{total_sales:,.2f}"),
            ("Total Bills", str(total_bills)),
            ("Total Items Sold", str(total_items_sold)),
            ("Average Bill Value", f"₹{avg_bill_value:.2f}"),
            ("Today's Sales", f"₹{today_sales:,.2f}"),
            ("Today's Bills", str(len(today_bills))),
            ("Inventory Items", str(len(inventory)))
        ]
        
        for i, (label, value) in enumerate(stats):
            stat_frame = tk.Frame(frame, bg='#F8F9FA', relief=tk.SOLID, borderwidth=1)
            stat_frame.grid(row=i//3, column=i%3, sticky='ew', padx=10, pady=10, ipadx=20, ipady=15)
            
            tk.Label(stat_frame, text=label, font=('Arial', 10), bg='#F8F9FA', fg='#7F8C8D').pack()
            tk.Label(stat_frame, text=value, font=('Arial', 14, 'bold'), bg='#F8F9FA', fg='#2C3E50').pack(pady=(5, 0))
        
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)
    
    def _generate_sales_report(self):
        """Generate and save sales report"""
        from receipt_generator import generate_text_report
        report_path = generate_text_report(db.get_all_bills())
        messagebox.showinfo("Success", f"Sales report generated successfully!\nSaved to: {report_path}")
    
    # Items Methods
    def _refresh_items(self):
        """Refresh items list with barcodes"""
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        inventory = db.get_all_inventory()
        for item in inventory:
            barcode_value = f"DROP{str(item['id']).zfill(6)}"
            self.items_tree.insert('', 'end', values=(
                item['id'],
                item['name'],
                item['category'],
                f"₹{item['price']:.2f}",
                barcode_value
            ))
    
    def _scan_barcode(self):
        """Open barcode scanner dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Scan Barcode")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg='#FFFFFF')
        
        main_frame = tk.Frame(dialog, bg='#FFFFFF', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            main_frame,
            text="Enter or Scan Barcode:",
            font=('Arial', 12, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(pady=(0, 15))
        
        barcode_entry = tk.Entry(
            main_frame,
            font=('Arial', 14),
            bg='#FFFFFF',
            fg='#000000',
            relief=tk.SOLID,
            borderwidth=2,
            highlightthickness=2,
            highlightbackground='#BDC3C7',
            highlightcolor='#3498DB'
        )
        barcode_entry.pack(fill=tk.X, ipady=10, pady=10)
        barcode_entry.focus_set()
        
        def search_by_barcode():
            barcode_value = barcode_entry.get().strip()
            if not barcode_value:
                messagebox.showwarning("Warning", "Please enter a barcode", parent=dialog)
                return
            
            # Extract item ID from barcode (format: DROP000001)
            if barcode_value.startswith('DROP'):
                try:
                    item_id = int(barcode_value[4:])
                    item = db.get_inventory_item(item_id)
                    if item:
                        dialog.destroy()
                        messagebox.showinfo("Item Found", f"Item: {item['name']}\nPrice: ₹{item['price']:.2f}", parent=self.root)
                    else:
                        messagebox.showerror("Error", "Item not found", parent=dialog)
                except ValueError:
                    messagebox.showerror("Error", "Invalid barcode format", parent=dialog)
            else:
                messagebox.showerror("Error", "Invalid barcode format. Expected format: DROP000001", parent=dialog)
        
        button_frame = tk.Frame(main_frame, bg='#FFFFFF')
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        tk.Button(
            button_frame,
            text="Search",
            font=('Arial', 11, 'bold'),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=25,
            pady=8,
            command=search_by_barcode
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        tk.Button(
            button_frame,
            text="Cancel",
            font=('Arial', 11),
            bg='#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=25,
            pady=8,
            command=dialog.destroy
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        barcode_entry.bind('<Return>', lambda e: search_by_barcode())
    
    def _download_barcode(self):
        """Download barcode for selected item to desktop"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to download barcode")
            return
        
        try:
            item_id = int(self.items_tree.item(selection[0])['values'][0])
            item_name = self.items_tree.item(selection[0])['values'][1]
            
            from barcode_util import download_barcode_to_desktop, BARCODE_AVAILABLE
            
            if not BARCODE_AVAILABLE:
                messagebox.showerror(
                    "Barcode Library Missing",
                    "The python-barcode library is not installed.\n\n"
                    "Please install it by running:\n"
                    "pip install python-barcode[images]\n\n"
                    "Then restart the application."
                )
                return
            
            filepath = download_barcode_to_desktop(item_id, item_name)
            
            if filepath and os.path.exists(filepath):
                messagebox.showinfo(
                    "Success", 
                    f"Barcode downloaded successfully!\n\nLocation:\n{filepath}\n\n"
                    f"Item: {item_name}\nBarcode: DROP{str(item_id).zfill(6)}"
                )
            else:
                messagebox.showerror("Error", "Barcode was generated but file was not found.\nPlease check the desktop folder.")
        except ImportError as e:
            messagebox.showerror(
                "Import Error",
                f"Barcode library is not available.\n\nError: {str(e)}\n\n"
                "Please install: pip install python-barcode[images]"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download barcode:\n\n{str(e)}")
    
    def _add_item(self):
        """Add new item"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Item")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(bg='#FFFFFF')
        
        main_frame = tk.Frame(dialog, bg='#FFFFFF', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(main_frame, text="Item Name:", bg='#FFFFFF', fg='#2C3E50').grid(row=0, column=0, sticky='w', pady=10)
        name_entry = tk.Entry(main_frame, width=30, font=('Arial', 10))
        name_entry.grid(row=0, column=1, pady=10)
        
        tk.Label(main_frame, text="Category:", bg='#FFFFFF', fg='#2C3E50').grid(row=1, column=0, sticky='w', pady=10)
        category_entry = tk.Entry(main_frame, width=30, font=('Arial', 10))
        category_entry.grid(row=1, column=1, pady=10)
        
        tk.Label(main_frame, text="Price (₹):", bg='#FFFFFF', fg='#2C3E50').grid(row=2, column=0, sticky='w', pady=10)
        price_entry = tk.Entry(main_frame, width=30, font=('Arial', 10))
        price_entry.grid(row=2, column=1, pady=10)
        
        def save():
            try:
                name = name_entry.get().strip()
                category = category_entry.get().strip()
                price = float(price_entry.get())
                
                if not name or not category:
                    messagebox.showerror("Error", "Please fill all fields", parent=dialog)
                    return
                
                db.add_inventory_item(name, category, price, 0)
                self._refresh_items()
                dialog.destroy()
                messagebox.showinfo("Success", "Item added successfully")
            except ValueError:
                messagebox.showerror("Error", "Invalid price value", parent=dialog)
        
        button_frame = tk.Frame(main_frame, bg='#FFFFFF')
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="Save", command=save, bg='#3498DB', fg='#FFFFFF', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg='#95A5A6', fg='#FFFFFF', padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        name_entry.focus_set()
    
    def _delete_item(self):
        """Delete selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete")
            return
        
        # Get item details
        item_values = self.items_tree.item(selection[0])['values']
        item_id = int(item_values[0])
        item_name = item_values[1]
        
        # Confirm deletion
        if messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete this item?\n\n"
            f"Item: {item_name}\n"
            f"ID: {item_id}\n\n"
            f"This action cannot be undone."
        ):
            try:
                # Check if item is used in any bills
                bills = db.get_all_bills()
                item_used = False
                for bill in bills:
                    for bill_item in bill['items']:
                        if bill_item.get('inventory_id') == item_id:
                            item_used = True
                            break
                    if item_used:
                        break
                
                if item_used:
                    response = messagebox.askyesno(
                        "Item Used in Bills",
                        f"This item has been used in existing bills.\n\n"
                        f"Deleting it will remove it from your inventory,\n"
                        f"but historical bill records will remain.\n\n"
                        f"Do you still want to delete this item?",
                        icon='warning'
                    )
                    if not response:
                        return
                
                # Delete item
                db.delete_inventory_item(item_id)
                self._refresh_items()
                messagebox.showinfo("Success", f"Item '{item_name}' deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete item:\n\n{str(e)}")
    
    # Utility Methods
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
