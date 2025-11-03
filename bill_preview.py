
"""
Bill preview window matching the template format
"""

import tkinter as tk
from tkinter import font, messagebox
from datetime import datetime
import os
import json
from config import (
    SHOP_NAME, SHOP_TAGLINE, SHOP_ADDRESS, DEFAULT_BILL_WIDTH_MM, DEFAULT_BILL_HEIGHT_MM,
    DEFAULT_CHARACTER_WIDTH, DEFAULT_ALIGNMENT, DEFAULT_MARGIN_TOP, DEFAULT_MARGIN_BOTTOM,
    DEFAULT_MARGIN_LEFT, DEFAULT_MARGIN_RIGHT
)
from database import db

class BillPreview:
    """Bill preview window with formatted layout matching template"""
    
    def __init__(self, parent, bill_items, total, payment_method, user, bill_id=None):
        self.parent = parent
        self.bill_items = bill_items
        self.total = total
        self.payment_method = payment_method
        self.user = user
        self.bill_id = bill_id
        
        # Load bill settings
        settings = self._load_bill_settings()
        self.bill_width_mm = settings['width_mm']
        self.bill_height_mm = settings['height_mm']
        self.char_width = settings['char_width']
        self.alignment = settings['alignment']
        self.margin_top = settings['margin_top']
        self.margin_bottom = settings['margin_bottom']
        self.margin_left = settings['margin_left']
        self.margin_right = settings['margin_right']
        
        self.preview_window = tk.Toplevel(parent)
        self.preview_window.title(f"Bill Preview - {self.bill_width_mm}mm x {self.bill_height_mm}mm")
        # Calculate screen size from paper dimensions (approximate: 1mm ≈ 3.78 pixels at 96 DPI)
        preview_w = int(self.bill_width_mm * 3.78)
        preview_h = int(self.bill_height_mm * 3.78)
        # Add some padding for better visibility
        preview_w = max(preview_w + 20, 300)
        preview_h = min(preview_h + 20, 900)
        self.preview_window.geometry(f"{preview_w}x{preview_h}")
        self.preview_window.configure(bg='#FFFFFF')
        self.preview_window.resizable(False, False)
        
        # Get bill ID if not provided (should always be provided from billing_module)
        if not self.bill_id:
            # Get next bill ID (should not happen, but handle legacy case)
            bills = db.get_all_bills()
            max_numeric_id = max([b.get('numeric_id', 0) if isinstance(b.get('id'), str) else b.get('id', 0) for b in bills], default=0)
            new_numeric_id = max_numeric_id + 1
            self.bill_id = f"DR{str(new_numeric_id).zfill(4)}"
        
        # Ensure bill_id is in DR0201 format
        if isinstance(self.bill_id, (int, float)):
            self.bill_id = f"DR{str(int(self.bill_id)).zfill(4)}"
        
        self._create_preview()
    
    def _create_preview(self):
        """Create bill preview formatted for 80mm x 210mm thermal paper"""
        # Buttons frame (packed first, will stay at bottom)
        button_frame = tk.Frame(self.preview_window, bg='#FFFFFF')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=10)
        
        # Main container with proper layout (above buttons)
        main_container = tk.Frame(self.preview_window, bg='#FFFFFF')
        main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Scrollable frame for long bills (takes remaining space)
        canvas_frame = tk.Frame(main_container, bg='#FFFFFF')
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        canvas = tk.Canvas(canvas_frame, bg='#FFFFFF', highlightthickness=0, width=350)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#FFFFFF', width=350)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create inner frame for margins (scrollable_frame is the container)
        main_frame = tk.Frame(scrollable_frame, bg='#FFFFFF')
        main_frame.pack(fill=tk.BOTH, expand=False, padx=(self.margin_left, self.margin_right), pady=(self.margin_top, self.margin_bottom), anchor='nw')
        
        # Ensure canvas scrolls to top after content is loaded
        def scroll_to_top():
            canvas.update_idletasks()
            canvas.yview_moveto(0)
        
        # Schedule scroll to top after window is ready
        canvas.after(100, scroll_to_top)
        
        # Header - Company Name "DROP" (left-aligned)
        header_frame = tk.Frame(main_frame, bg='#FFFFFF')
        header_frame.pack(fill=tk.X, pady=(0, 2), anchor='w')
        
        shop_label = tk.Label(
            header_frame,
            text=SHOP_NAME,
            font=('Arial', 20, 'bold'),
            bg='#FFFFFF',
            fg='#000000',
            anchor='w'
        )
        shop_label.pack(anchor='w')
        
        # Tagline "DRESS FOR LESS" (left-aligned, italic, smaller)
        tk.Label(
            header_frame,
            text=SHOP_TAGLINE,
            font=('Arial', 9, 'italic'),
            bg='#FFFFFF',
            fg='#000000',
            anchor='w'
        ).pack(anchor='w', pady=(1, 3))
        
        # Address (left-aligned, smaller font, minimal spacing)
        # Calculate wraplength based on character width (approx 6.5 pixels per character at 8pt font)
        address_wraplength = int(self.char_width * 6.5)
        tk.Label(
            header_frame,
            text=SHOP_ADDRESS,
            font=('Arial', 8),
            bg='#FFFFFF',
            fg='#000000',
            wraplength=address_wraplength,
            justify='left',
            anchor='w'
        ).pack(anchor='w', pady=(0, 5))
        
        # Date and Bill No (both left-aligned, minimal spacing)
        info_frame = tk.Frame(main_frame, bg='#FFFFFF')
        info_frame.pack(fill=tk.X, pady=(0, 5), anchor='w')
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        tk.Label(
            info_frame,
            text=f"DATE: {date_str}",
            font=('Arial', 9),
            bg='#FFFFFF',
            fg='#000000',
            anchor='w'
        ).pack(anchor='w')
        tk.Label(
            info_frame,
            text=f"BILL NO: {self.bill_id}",
            font=('Arial', 9),
            bg='#FFFFFF',
            fg='#000000',
            anchor='w'
        ).pack(anchor='w', pady=(1, 0))
        
        # Separator line
        tk.Frame(main_frame, bg='#000000', height=1).pack(fill=tk.X, pady=(5, 8), anchor='w')
        
        # Items list (horizontal format)
        items_frame = tk.Frame(main_frame, bg='#FFFFFF')
        items_frame.pack(fill=tk.X, pady=(0, 15), anchor='w')
        
        for item in self.bill_items:
            # Item container
            item_container = tk.Frame(items_frame, bg='#FFFFFF')
            item_container.pack(fill=tk.X, pady=(5, 10), anchor='w')
            
            # Product name
            product_wraplength = int(self.char_width * 6.5)
            tk.Label(
                item_container,
                text=f"Product: {item['name']}",
                font=('Arial', 9),
                bg='#FFFFFF',
                fg='#000000',
                anchor='w',
                padx=2,
                wraplength=product_wraplength,
                justify='left'
            ).pack(anchor='w', pady=(0, 2))
            
            # Rate
            tk.Label(
                item_container,
                text=f"Rate: ₹{item['price']:.2f}",
                font=('Arial', 9),
                bg='#FFFFFF',
                fg='#000000',
                anchor='w',
                padx=2
            ).pack(anchor='w', pady=(0, 2))
            
            # Quantity
            tk.Label(
                item_container,
                text=f"Quantity: {item['quantity']}",
                font=('Arial', 9),
                bg='#FFFFFF',
                fg='#000000',
                anchor='w',
                padx=2
            ).pack(anchor='w', pady=(0, 2))
            
            # Total Price
            tk.Label(
                item_container,
                text=f"Total Price: ₹{item['total']:.2f}",
                font=('Arial', 9, 'bold'),
                bg='#FFFFFF',
                fg='#000000',
                anchor='w',
                padx=2
            ).pack(anchor='w', pady=(0, 5))
        
        # Separator line
        tk.Frame(main_frame, bg='#000000', height=1).pack(fill=tk.X, pady=(10, 10), anchor='w')
        
        # Total section (left-aligned for narrow paper)
        total_frame = tk.Frame(main_frame, bg='#FFFFFF')
        total_frame.pack(fill=tk.X, pady=8, anchor='w')
        
        tk.Label(
            total_frame,
            text=f"TOTAL: ₹{self.total:.2f}",
            font=('Arial', 11, 'bold'),
            bg='#FFFFFF',
            fg='#000000',
            anchor='w'
        ).pack(anchor='w')
        
        # Payment method (compact)
        payment_frame = tk.Frame(main_frame, bg='#FFFFFF')
        payment_frame.pack(fill=tk.X, pady=(5, 10), anchor='w')
        
        tk.Label(
            payment_frame,
            text=f"Payment: {self.payment_method}",
            font=('Arial', 9),
            bg='#FFFFFF',
            fg='#000000',
            anchor='w'
        ).pack(anchor='w')
        
        # Print button (primary, larger)
        print_btn = tk.Button(
            button_frame,
            text="🖨️ Print Bill",
            font=('Arial', 11, 'bold'),
            bg='#3498DB',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self._print_bill
        )
        print_btn.pack(fill=tk.X, pady=(0, 8))
        print_btn.bind('<Enter>', lambda e: print_btn.config(bg='#2980B9'))
        print_btn.bind('<Leave>', lambda e: print_btn.config(bg='#3498DB'))
        
        # Close button
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=('Arial', 10),
            bg='#95A5A6',
            fg='#FFFFFF',
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.preview_window.destroy
        )
        close_btn.pack(fill=tk.X)
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#7F8C8D'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg='#95A5A6'))
    
    def _print_bill(self):
        """Print the bill formatted for 80mm x 210mm thermal paper"""
        try:
            import sys
            import tempfile
            import subprocess
            
            # Create printable text version formatted for 80mm paper
            bill_text = self._generate_bill_text()
            
            # Always save the receipt first
            from config import RECEIPTS_DIR
            os.makedirs(RECEIPTS_DIR, exist_ok=True)
            receipt_path = os.path.join(RECEIPTS_DIR, f"bill_{self.bill_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            with open(receipt_path, 'w', encoding='utf-8') as f:
                f.write(bill_text)
            
            # Direct print without dialog
            try:
                if sys.platform == 'win32':
                    # Windows: Use temp file and print directly
                    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                    temp_file.write(bill_text)
                    temp_file.close()
                    
                    # Print using Windows default printer
                    os.startfile(temp_file.name, "print")
                    messagebox.showinfo(
                        "Print Sent",
                        "Bill sent to printer!\n\nPaper size: 80mm x 210mm\nPlease ensure your printer is set to thermal receipt mode.",
                        parent=self.preview_window
                    )
                else:
                    # Linux/Mac: Use lp command
                    subprocess.run(['lp', receipt_path], check=False)
                    messagebox.showinfo(
                        "Print Sent",
                        "Bill sent to default printer!",
                        parent=self.preview_window
                    )
            except Exception as e:
                # Fallback: Show success with file location
                messagebox.showinfo(
                    "Bill Saved",
                    f"Bill saved to:\n{receipt_path}\n\nYou can print it manually using a thermal printer.\n\nError: {str(e)}",
                    parent=self.preview_window
                )
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to print bill: {str(e)}", parent=self.preview_window)
    
    def _load_bill_settings(self):
        """Load bill settings from file or use defaults"""
        settings_file = os.path.join('data', 'bill_settings.json')
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    return {
                        'width_mm': settings.get('width_mm', DEFAULT_BILL_WIDTH_MM),
                        'height_mm': settings.get('height_mm', DEFAULT_BILL_HEIGHT_MM),
                        'char_width': settings.get('char_width', DEFAULT_CHARACTER_WIDTH),
                        'alignment': settings.get('alignment', DEFAULT_ALIGNMENT),
                        'margin_top': settings.get('margin_top', DEFAULT_MARGIN_TOP),
                        'margin_bottom': settings.get('margin_bottom', DEFAULT_MARGIN_BOTTOM),
                        'margin_left': settings.get('margin_left', DEFAULT_MARGIN_LEFT),
                        'margin_right': settings.get('margin_right', DEFAULT_MARGIN_RIGHT)
                    }
            else:
                return {
                    'width_mm': DEFAULT_BILL_WIDTH_MM,
                    'height_mm': DEFAULT_BILL_HEIGHT_MM,
                    'char_width': DEFAULT_CHARACTER_WIDTH,
                    'alignment': DEFAULT_ALIGNMENT,
                    'margin_top': DEFAULT_MARGIN_TOP,
                    'margin_bottom': DEFAULT_MARGIN_BOTTOM,
                    'margin_left': DEFAULT_MARGIN_LEFT,
                    'margin_right': DEFAULT_MARGIN_RIGHT
                }
        except Exception:
            return {
                'width_mm': DEFAULT_BILL_WIDTH_MM,
                'height_mm': DEFAULT_BILL_HEIGHT_MM,
                'char_width': DEFAULT_CHARACTER_WIDTH,
                'alignment': DEFAULT_ALIGNMENT,
                'margin_top': DEFAULT_MARGIN_TOP,
                'margin_bottom': DEFAULT_MARGIN_BOTTOM,
                'margin_left': DEFAULT_MARGIN_LEFT,
                'margin_right': DEFAULT_MARGIN_RIGHT
            }
    
    def _generate_bill_text(self):
        """Generate text representation of bill for thermal paper printing - properly formatted for 80mm"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Use saved character width setting (48 for 80mm paper)
        width = self.char_width
        
        # Initialize bill text - ensure no leading spaces, left-aligned
        bill_text = ""
        
        # Top separator - full width
        bill_text += "=" * width + "\n"
        
        # Shop name - left-aligned
        bill_text += SHOP_NAME + "\n"
        
        # Tagline - left-aligned
        bill_text += SHOP_TAGLINE + "\n"
        
        # Address - wrap if needed, each line left-aligned
        address = SHOP_ADDRESS.strip()
        if len(address) > width:
            # Split address into multiple lines based on commas first, then by width
            # This creates natural breaks at commas
            parts = address.split(',')
            line = ""
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                    
                # Add comma if not the last part
                part_with_comma = part + (',' if i < len(parts) - 1 else '')
                
                # Check if adding this part would exceed width
                if line:
                    test_line = (line + ', ' + part_with_comma).strip()
                else:
                    test_line = part_with_comma
                    
                if len(test_line) <= width:
                    if line:
                        line += ', ' + part_with_comma
                    else:
                        line = part_with_comma
                else:
                    # Output the current line (left-aligned) before starting new line
                    if line.strip():
                        bill_text += line.strip() + "\n"
                    line = part_with_comma
            # Output the last line (left-aligned)
            if line.strip():
                bill_text += line.strip() + "\n"
        else:
            # Left-aligned single address line
            bill_text += address + "\n"
        
        bill_text += "\n"
        
        # DATE and BILL NO - left-aligned, each on separate line
        bill_text += f"DATE: {date_str}\n"
        bill_text += f"BILL NO: {self.bill_id}\n"
        bill_text += "=" * width + "\n"
        bill_text += "\n"
        
        # Items in horizontal format
        for item in self.bill_items:
            product_name = item['name']
            quantity = str(item['quantity'])
            price = f"₹{item['price']:.2f}"
            total = f"₹{item['total']:.2f}"
            
            # Product name - wrap if needed
            product_line = f"Product: {product_name}"
            if len(product_line) > width:
                # Split product name if too long
                words = product_name.split()
                line = "Product: "
                for word in words:
                    if len(line + word) <= width:
                        line += word + " "
                    else:
                        if line.strip() != "Product:":
                            bill_text += line.strip() + "\n"
                        line = "  " + word + " "
                if line.strip():
                    bill_text += line.strip() + "\n"
            else:
                bill_text += product_line + "\n"
            
            # Rate
            bill_text += f"Rate: {price}\n"
            
            # Quantity
            bill_text += f"Quantity: {quantity}\n"
            
            # Total Price
            bill_text += f"Total Price: {total}\n"
            bill_text += "\n"
        
        # Grand Total - left-aligned
        total_str = f"₹{self.total:.2f}"
        bill_text += f"TOTAL: {total_str}\n"
        bill_text += "\n"
        
        # Payment method - left-aligned
        bill_text += f"Payment: {self.payment_method}\n"
        bill_text += "\n"
        
        # Footer
        bill_text += "=" * width + "\n"
        thank_msg = "Thank you for shopping at DROP!"
        thank_padding = (width - len(thank_msg)) // 2
        if thank_padding > 0:
            bill_text += " " * thank_padding + thank_msg + "\n"
        else:
            bill_text += thank_msg + "\n"
        bill_text += "=" * width + "\n"
        
        # Add paper cut command if supported (ESC/POS)
        # For thermal printers that support it
        # bill_text += "\x1D\x56\x00"  # Paper cut command (optional)
        
        return bill_text

