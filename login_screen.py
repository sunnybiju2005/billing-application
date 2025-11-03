"""
Login screen for DROP billing application
Features a stylish background with DROP watermark
"""

import tkinter as tk
from tkinter import messagebox
from database import db
from theme_manager import ThemeManager
from config import DEFAULT_THEME, SHOP_NAME

class LoginScreen:
    """Login screen with admin and staff login options"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("DROP - Login")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        
        # Initialize theme
        self.theme_manager = ThemeManager(DEFAULT_THEME)
        
        # Center window on screen
        self._center_window()
        
        # Create main container with watermark background
        self.main_frame = tk.Frame(root, bg=self.theme_manager.get_color('bg'))
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create watermark canvas
        self._create_watermark()
        
        # Create login interface
        self._create_login_interface()
        
        # Bind theme toggle
        self.root.bind('<Control-t>', lambda e: self._toggle_theme())
    
    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_watermark(self):
        """Create watermark canvas with DROP text"""
        self.canvas = tk.Canvas(
            self.main_frame,
            bg=self.theme_manager.get_color('bg'),
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw watermark text
        self.canvas.create_text(
            450, 300,
            text=SHOP_NAME,
            font=('Arial', 120, 'bold'),
            fill=self.theme_manager.get_color('watermark'),
            angle=0,
            anchor='center'
        )
    
    def _create_login_interface(self):
        """Create the login interface overlay"""
        # Create overlay frame
        overlay = tk.Frame(
            self.main_frame,
            bg=self.theme_manager.get_color('secondary_bg'),
            relief=tk.FLAT
        )
        overlay.place(relx=0.5, rely=0.5, anchor='center', width=400, height=400)
        
        # Title
        title_label = tk.Label(
            overlay,
            text=f"{SHOP_NAME}",
            font=('Arial', 32, 'bold'),
            bg=self.theme_manager.get_color('secondary_bg'),
            fg=self.theme_manager.get_color('accent')
        )
        title_label.pack(pady=(30, 10))
        
        subtitle_label = tk.Label(
            overlay,
            text="Billing System",
            font=('Arial', 14),
            bg=self.theme_manager.get_color('secondary_bg'),
            fg=self.theme_manager.get_color('secondary_fg')
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Login buttons frame
        buttons_frame = tk.Frame(overlay, bg=self.theme_manager.get_color('secondary_bg'))
        buttons_frame.pack(pady=20, padx=40, fill=tk.X)
        
        # Admin Login Button
        admin_btn = tk.Button(
            buttons_frame,
            text="Admin Login",
            font=('Arial', 12, 'bold'),
            bg=self.theme_manager.get_color('accent'),
            fg=self.theme_manager.get_color('button_fg'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=15,
            command=self._show_admin_login_dialog
        )
        admin_btn.pack(fill=tk.X, pady=(0, 15))
        admin_btn.bind('<Enter>', lambda e: admin_btn.config(bg=self.theme_manager.get_color('accent_hover')))
        admin_btn.bind('<Leave>', lambda e: admin_btn.config(bg=self.theme_manager.get_color('accent')))
        
        # Staff Login Button (Direct login, no credentials needed)
        staff_btn = tk.Button(
            buttons_frame,
            text="Staff Login",
            font=('Arial', 12, 'bold'),
            bg=self.theme_manager.get_color('success'),
            fg=self.theme_manager.get_color('button_fg'),
            relief=tk.FLAT,
            cursor='hand2',
            padx=20,
            pady=15,
            command=self._handle_staff_login
        )
        staff_btn.pack(fill=tk.X)
        staff_btn.bind('<Enter>', lambda e: staff_btn.config(bg='#218838'))
        staff_btn.bind('<Leave>', lambda e: staff_btn.config(bg=self.theme_manager.get_color('success')))
        
        # Theme toggle hint
        hint_label = tk.Label(
            overlay,
            text="Press Ctrl+T to toggle theme",
            font=('Arial', 8),
            bg=self.theme_manager.get_color('secondary_bg'),
            fg=self.theme_manager.get_color('secondary_fg')
        )
        hint_label.pack(pady=(30, 10))
    
    def _show_admin_login_dialog(self):
        """Show dialog for admin login credentials"""
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Admin Login")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg='#FFFFFF')
        
        # Center dialog on screen
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f'400x300+{x}+{y}')
        
        main_frame = tk.Frame(
            dialog,
            bg='#FFFFFF',
            padx=30,
            pady=30
        )
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            main_frame,
            text="Admin Login",
            font=('Arial', 18, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(pady=(0, 25))
        
        # Username field
        username_frame = tk.Frame(main_frame, bg='#FFFFFF')
        username_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            username_frame,
            text="Username:",
            font=('Arial', 11, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 8))
        
        username_entry = tk.Entry(
            username_frame,
            font=('Arial', 13),
            bg='#FFFFFF',
            fg='#000000',
            relief=tk.SOLID,
            borderwidth=2,
            highlightthickness=2,
            highlightbackground='#BDC3C7',
            highlightcolor='#3498DB',
            insertbackground='#000000',
            selectbackground='#3498DB',
            selectforeground='#FFFFFF'
        )
        username_entry.pack(fill=tk.X, ipady=10)
        
        # Password field
        password_frame = tk.Frame(main_frame, bg='#FFFFFF')
        password_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(
            password_frame,
            text="Password:",
            font=('Arial', 11, 'bold'),
            bg='#FFFFFF',
            fg='#2C3E50'
        ).pack(anchor='w', pady=(0, 8))
        
        password_entry = tk.Entry(
            password_frame,
            font=('Arial', 13),
            show='*',
            bg='#FFFFFF',
            fg='#000000',
            relief=tk.SOLID,
            borderwidth=2,
            highlightthickness=2,
            highlightbackground='#BDC3C7',
            highlightcolor='#3498DB',
            insertbackground='#000000',
            selectbackground='#3498DB',
            selectforeground='#FFFFFF'
        )
        password_entry.pack(fill=tk.X, ipady=10)
        
        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password", parent=dialog)
                return
            
            # Authenticate admin user
            user = db.authenticate_user(username, password, 'admin')
            
            if user:
                dialog.destroy()
                # Hide login window
                self.root.withdraw()
                # Open admin dashboard
                from admin_panel import AdminPanel
                admin_window = tk.Toplevel()
                AdminPanel(admin_window, user, self.theme_manager, self.root)
            else:
                messagebox.showerror("Login Failed", "Invalid admin credentials", parent=dialog)
                password_entry.delete(0, tk.END)
                password_entry.focus_set()
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#FFFFFF')
        buttons_frame.pack(fill=tk.X, pady=(25, 0))
        
        login_btn = tk.Button(
            buttons_frame,
            text="Login",
            font=('Arial', 12, 'bold'),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor='hand2',
            command=login,
            activebackground='#2980B9',
            activeforeground='#FFFFFF'
        )
        login_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        login_btn.bind('<Enter>', lambda e: login_btn.config(bg='#2980B9'))
        login_btn.bind('<Leave>', lambda e: login_btn.config(bg='#3498DB'))
        
        cancel_btn = tk.Button(
            buttons_frame,
            text="Cancel",
            font=('Arial', 12),
            bg='#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=25,
            pady=10,
            cursor='hand2',
            command=dialog.destroy,
            activebackground='#7F8C8D',
            activeforeground='#FFFFFF'
        )
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        cancel_btn.bind('<Enter>', lambda e: cancel_btn.config(bg='#7F8C8D'))
        cancel_btn.bind('<Leave>', lambda e: cancel_btn.config(bg='#95A5A6'))
        
        # Bind Enter key to password field
        password_entry.bind('<Return>', lambda e: login())
        username_entry.bind('<Return>', lambda e: password_entry.focus_set())
        
        # Focus on username entry
        username_entry.focus_set()
    
    def _handle_staff_login(self):
        """Handle staff login - direct login without credentials"""
        # Get the first available staff user (or default staff)
        staff_users = db.get_all_users(role='staff')
        
        if not staff_users:
            messagebox.showerror("Error", "No staff account found. Please contact administrator.")
            return
        
        # Use the first staff user (or default)
        user = staff_users[0]
        
        # Hide login window
        self.root.withdraw()
        
        # Open staff dashboard
        from staff_panel import StaffPanel
        staff_window = tk.Toplevel()
        StaffPanel(staff_window, user, self.theme_manager, self.root)
    
    def _toggle_theme(self):
        """Toggle between light and dark theme"""
        self.theme_manager.toggle_theme()
        # Recreate the login interface with new theme
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self._create_watermark()
        self._create_login_interface()

