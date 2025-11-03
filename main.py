"""
DROP - Desktop Billing Application
Main entry point for the application
"""

import tkinter as tk
from login_screen import LoginScreen

def main():
    """Initialize and run the DROP billing application"""
    root = tk.Tk()
    app = LoginScreen(root)
    root.mainloop()

if __name__ == "__main__":
    main()

