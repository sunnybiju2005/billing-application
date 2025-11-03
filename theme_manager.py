"""
Theme manager for light and dark mode support
"""

class ThemeManager:
    """Manages application themes"""
    
    LIGHT_THEME = {
        'bg': '#FFFFFF',
        'fg': '#000000',
        'secondary_bg': '#F5F5F5',
        'secondary_fg': '#333333',
        'accent': '#4A90E2',
        'accent_hover': '#357ABD',
        'success': '#28A745',
        'danger': '#DC3545',
        'warning': '#FFC107',
        'border': '#CCCCCC',
        'entry_bg': '#FFFFFF',
        'entry_fg': '#000000',
        'button_bg': '#4A90E2',
        'button_fg': '#FFFFFF',
        'button_hover': '#357ABD',
        'text': '#000000',
        'watermark': '#E0E0E0'
    }
    
    DARK_THEME = {
        'bg': '#1E1E1E',
        'fg': '#FFFFFF',
        'secondary_bg': '#2D2D2D',
        'secondary_fg': '#CCCCCC',
        'accent': '#5BA3F5',
        'accent_hover': '#4A90E2',
        'success': '#4CAF50',
        'danger': '#F44336',
        'warning': '#FF9800',
        'border': '#555555',
        'entry_bg': '#2D2D2D',
        'entry_fg': '#FFFFFF',
        'button_bg': '#5BA3F5',
        'button_fg': '#FFFFFF',
        'button_hover': '#4A90E2',
        'text': '#FFFFFF',
        'watermark': '#3A3A3A'
    }
    
    def __init__(self, theme='light'):
        self.current_theme = theme
        self.colors = self.LIGHT_THEME if theme == 'light' else self.DARK_THEME
    
    def set_theme(self, theme):
        """Set the current theme"""
        self.current_theme = theme
        self.colors = self.LIGHT_THEME if theme == 'light' else self.DARK_THEME
    
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.set_theme('dark' if self.current_theme == 'light' else 'light')
    
    def get_color(self, key):
        """Get a color value by key"""
        return self.colors.get(key, '#000000')

