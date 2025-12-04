import tkinter as tk
from tkinter import font
import colorsys

class UIStyle:
    # Кольорова палітра
    COLORS = {
        "bg_dark": "#1a1a1a",      # Темний фон
        "bg_medium": "#2d2d2d",    # Середній фон
        "bg_light": "#404040",     # Світліший фон
        "text_main": "#ffffff",    # Основний текст
        "text_secondary": "#b3b3b3", # Додатковий текст
        "accent": "#ff3333",       # Акцентний колір
        "button": "#404040",       # Колір кнопок
        "button_hover": "#4d4d4d", # Колір кнопок при наведенні
        "button_active": "#666666", # Колір кнопок при натисканні
        "border": "#666666",       # Колір рамок
        "monitor": "#000000",      # Колір монітора
        "monitor_text": "#00ff00"  # Колір тексту на моніторі
    }
    
    # Шрифти
    FONTS = {
        "title": ("Consolas", 24, "bold"),
        "subtitle": ("Consolas", 18, "bold"),
        "text": ("Consolas", 12),
        "button": ("Consolas", 12, "bold"),
        "monitor": ("Consolas", 14)
    }
    
    @staticmethod
    def create_styled_button(parent, text, command, width=25):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=UIStyle.FONTS["button"],
            bg=UIStyle.COLORS["button"],
            fg=UIStyle.COLORS["text_main"],
            activebackground=UIStyle.COLORS["button_active"],
            activeforeground=UIStyle.COLORS["text_main"],
            width=width,
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=5
        )
        
        # Ефект при наведенні
        def on_enter(e):
            button['background'] = UIStyle.COLORS["button_hover"]
        
        def on_leave(e):
            button['background'] = UIStyle.COLORS["button"]
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    @staticmethod
    def create_monitor_frame(parent):
        frame = tk.Frame(
            parent,
            bg=UIStyle.COLORS["monitor"],
            padx=20,
            pady=20
        )
        return frame
    
    @staticmethod
    def create_monitor_text(parent, text):
        label = tk.Label(
            parent,
            text=text,
            font=UIStyle.FONTS["monitor"],
            bg=UIStyle.COLORS["monitor"],
            fg=UIStyle.COLORS["monitor_text"],
            justify=tk.LEFT,
            wraplength=500
        )
        return label
    
    @staticmethod
    def create_title(parent, text):
        label = tk.Label(
            parent,
            text=text,
            font=UIStyle.FONTS["title"],
            bg=UIStyle.COLORS["bg_dark"],
            fg=UIStyle.COLORS["text_main"],
            pady=20
        )
        return label
    
    @staticmethod
    def create_text(parent, text, color=None):
        label = tk.Label(
            parent,
            text=text,
            font=UIStyle.FONTS["text"],
            bg=UIStyle.COLORS["bg_dark"],
            fg=color if color else UIStyle.COLORS["text_secondary"],
            wraplength=500,
            justify=tk.LEFT,
            pady=10
        )
        return label
    
    @staticmethod
    def configure_root(root):
        root.configure(bg=UIStyle.COLORS["bg_dark"])
        root.option_add("*Font", UIStyle.FONTS["text"])
        root.option_add("*Background", UIStyle.COLORS["bg_dark"])
        root.option_add("*Foreground", UIStyle.COLORS["text_main"]) 