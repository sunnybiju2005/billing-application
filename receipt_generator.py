"""
Receipt generator for printing bills and generating reports
"""

import os
from datetime import datetime
from config import RECEIPTS_DIR, BILLS_DIR, SHOP_NAME

def generate_receipt(bill, user):
    """
    Generate a printable receipt for a bill
    Returns the file path of the generated receipt
    """
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    
    receipt_path = os.path.join(RECEIPTS_DIR, f"receipt_{bill['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with open(receipt_path, 'w') as f:
        # Header
        f.write("=" * 50 + "\n")
        f.write(f"    {SHOP_NAME} - Clothing Shop\n")
        f.write("=" * 50 + "\n\n")
        
        # Bill info
        f.write(f"Bill ID: #{bill['id']}\n")
        f.write(f"Date: {datetime.fromisoformat(bill['date']).strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Staff: {user['name'] if user else 'Unknown'}\n")
        f.write("-" * 50 + "\n\n")
        
        # Items
        f.write("Items:\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Item':<30} {'Qty':<6} {'Price':<12} {'Total':<12}\n")
        f.write("-" * 50 + "\n")
        
        for item in bill['items']:
            item_name = item['name'][:28] if len(item['name']) <= 28 else item['name'][:25] + "..."
            f.write(f"{item_name:<30} {item['quantity']:<6} ₹{item['price']:<11.2f} ₹{item['total']:<11.2f}\n")
        
        f.write("-" * 50 + "\n")
        
        # Total
        f.write(f"\n{'Subtotal:':<48} ₹{bill['total']:.2f}\n")
        f.write(f"{'Total:':<48} ₹{bill['total']:.2f}\n")
        f.write(f"\nPayment Method: {bill['payment_method']}\n")
        
        # Footer
        f.write("\n" + "=" * 50 + "\n")
        f.write("    Thank you for shopping at DROP!\n")
        f.write("=" * 50 + "\n")
    
    return receipt_path

def generate_text_report(bills):
    """
    Generate a sales report text file
    Returns the file path of the generated report
    """
    os.makedirs(BILLS_DIR, exist_ok=True)
    
    report_path = os.path.join(BILLS_DIR, f"sales_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    
    with open(report_path, 'w') as f:
        # Header
        f.write("=" * 70 + "\n")
        f.write(f"    {SHOP_NAME} - Sales Report\n")
        f.write(f"    Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")
        
        # Summary
        total_sales = sum(bill['total'] for bill in bills)
        total_bills = len(bills)
        total_items = sum(sum(item['quantity'] for item in bill['items']) for bill in bills)
        
        f.write("SUMMARY\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total Sales: ₹{total_sales:.2f}\n")
        f.write(f"Total Bills: {total_bills}\n")
        f.write(f"Total Items Sold: {total_items}\n")
        f.write(f"Average Bill Value: ₹{total_sales / total_bills:.2f}\n" if total_bills > 0 else "Average Bill Value: ₹0.00\n")
        f.write("\n")
        
        # Detailed bill list
        f.write("DETAILED BILL LIST\n")
        f.write("-" * 70 + "\n")
        f.write(f"{'Bill ID':<10} {'Date':<20} {'Items':<8} {'Total':<15} {'Payment':<15}\n")
        f.write("-" * 70 + "\n")
        
        for bill in bills:
            date_str = datetime.fromisoformat(bill['date']).strftime('%Y-%m-%d %H:%M')
            f.write(f"#{bill['id']:<9} {date_str:<20} {len(bill['items']):<8} ₹{bill['total']:<14.2f} {bill['payment_method']:<15}\n")
        
        f.write("\n" + "=" * 70 + "\n")
    
    return report_path

def print_receipt_to_printer(receipt_path):
    """
    Print receipt to default printer (Windows)
    For cross-platform support, this can be extended
    """
    try:
        import subprocess
        import sys
        
        if sys.platform == 'win32':
            # Windows: use notepad to print
            os.startfile(receipt_path, "print")
        elif sys.platform == 'darwin':
            # macOS: use lpr
            subprocess.run(['lpr', receipt_path])
        else:
            # Linux: use lp
            subprocess.run(['lp', receipt_path])
    except Exception as e:
        print(f"Printing error: {str(e)}")
        # Fallback: just show a message
        return False
    
    return True

