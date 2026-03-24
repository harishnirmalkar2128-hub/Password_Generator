import customtkinter as ctk
import tkinter as tk
import random
import string
import pyperclip
import json
import os
import math
import secrets
from datetime import datetime
import hashlib

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class PasswordGeneratorPro:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("🔐 Password Generator Pro")
        self.window.geometry("550x700")
        self.window.resizable(True, True)
        
        self.password = tk.StringVar()
        self.history_file = "password_history.json"
        self.password_history = self.load_history()
        self.theme_mode = "dark"
        
        self.load_settings()
        self.setup_ui()
    
    def setup_ui(self):
        # Main container with tabs
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Generator tab
        self.generator_tab = self.tabview.add("🎲 Generator")
        self.setup_generator_tab()
        
        # History tab
        self.history_tab = self.tabview.add("📜 History")
        self.setup_history_tab()
        
        # Settings tab
        self.settings_tab = self.tabview.add("⚙️ Settings")
        self.setup_settings_tab()
        
        # Generate initial password
        self.generate_password()
    
    def update_length_label(self, value):
        self.length_label.configure(text=f"{int(value)} characters")
        self.generate_password()
    
    def setup_generator_tab(self):
        # Title
        ctk.CTkLabel(self.generator_tab, text="Secure Password Generator", 
                    font=("Arial", 22, "bold")).pack(pady=15)
        
        # Password display
        display_frame = ctk.CTkFrame(self.generator_tab)
        display_frame.pack(padx=20, pady=10, fill="x")
        
        self.password_entry = ctk.CTkEntry(display_frame, textvariable=self.password,
                                           font=("Courier", 20), height=40,
                                           justify="center", state="readonly")
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0,5))
        
        ctk.CTkButton(display_frame, text="📋", width=40,
                     command=self.copy_password).pack(side="right")
        
        # Strength and entropy display
        info_frame = ctk.CTkFrame(self.generator_tab)
        info_frame.pack(padx=20, pady=5, fill="x")
        
        self.strength_label = ctk.CTkLabel(info_frame, text="Strength: Weak", font=("Arial", 12))
        self.strength_label.pack()
        
        self.entropy_label = ctk.CTkLabel(info_frame, text="Entropy: 0 bits", font=("Arial", 10))
        self.entropy_label.pack()
        
        self.strength_bar = ctk.CTkProgressBar(self.generator_tab, height=10, corner_radius=5)
        self.strength_bar.pack(padx=20, pady=5, fill="x")
        self.strength_bar.set(0.3)
        
        # Password type selection
        type_frame = ctk.CTkFrame(self.generator_tab)
        type_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(type_frame, text="Password Type:").pack()
        self.password_type_var = tk.StringVar(value="Random")
        type_option = ctk.CTkOptionMenu(type_frame, values=["Random", "PIN", "Passphrase", "Memorable"], 
                                       variable=self.password_type_var, command=self.on_type_change)
        type_option.pack(pady=5)
        
        # Options frame
        self.options_frame = ctk.CTkFrame(self.generator_tab)
        self.options_frame.pack(padx=20, pady=10, fill="both")
        
        # Length slider
        ctk.CTkLabel(self.options_frame, text="Password Length:").pack()
        self.length_var = tk.IntVar(value=12)
        length_slider = ctk.CTkSlider(self.options_frame, from_=4, to=64,
                                     variable=self.length_var,
                                     command=self.update_length_label)
        length_slider.pack(fill="x", padx=20, pady=5)
        
        self.length_label = ctk.CTkLabel(self.options_frame, text="12 characters")
        self.length_label.pack()
        
        # Checkboxes
        self.upper_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.options_frame, text="Uppercase (A-Z)", 
                       variable=self.upper_var).pack(pady=2)
        
        self.lower_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.options_frame, text="Lowercase (a-z)", 
                       variable=self.lower_var).pack(pady=2)
        
        self.numbers_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.options_frame, text="Numbers (0-9)", 
                       variable=self.numbers_var).pack(pady=2)
        
        self.symbols_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.options_frame, text="Symbols (!@#$%^&*)", 
                       variable=self.symbols_var).pack(pady=2)
        
        self.exclude_similar_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(self.options_frame, text="Exclude similar characters (0,O,l,1,I)", 
                       variable=self.exclude_similar_var).pack(pady=2)
        
        # Generate button
        ctk.CTkButton(self.generator_tab, text="🎲 Generate Password", 
                     command=self.generate_password,
                     height=40, font=("Arial", 14, "bold")).pack(pady=15)
    
    def setup_history_tab(self):
        # History controls
        controls_frame = ctk.CTkFrame(self.history_tab)
        controls_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkButton(controls_frame, text="Clear History", 
                     command=self.clear_history).pack(side="left", padx=5)
        ctk.CTkButton(controls_frame, text="Export History", 
                     command=self.export_history).pack(side="left", padx=5)
        
        # History list
        self.history_list = ctk.CTkFrame(self.history_tab)
        self.history_list.pack(padx=20, pady=10, fill="both", expand=True)
        
        # History listbox
        self.history_listbox = tk.Listbox(self.history_list, font=("Courier", 10), width=50, height=20)
        self.history_listbox.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.history_list)
        scrollbar.pack(side="right", fill="y")
        
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_listbox.yview)
        
        # Bind double-click to copy
        self.history_listbox.bind("<Double-Button-1>", self.copy_from_history)
        
        # Load history
        self.load_history_list()
    
    def setup_settings_tab(self):
        # Theme mode
        theme_frame = ctk.CTkFrame(self.settings_tab)
        theme_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(theme_frame, text="Theme Mode:").pack()
        self.theme_mode_var = tk.StringVar(value=self.theme_mode)
        theme_mode_option = ctk.CTkOptionMenu(theme_frame, values=["dark", "light", "system"], 
                                              variable=self.theme_mode_var)
        theme_mode_option.pack(pady=5)
        
        # Color theme
        color_frame = ctk.CTkFrame(self.settings_tab)
        color_frame.pack(padx=20, pady=10, fill="x")
        
        ctk.CTkLabel(color_frame, text="Color Theme:").pack()
        self.color_theme_var = tk.StringVar(value="green")
        color_theme_option = ctk.CTkOptionMenu(color_frame, values=["green", "blue", "dark-blue", "red"], 
                                             variable=self.color_theme_var)
        color_theme_option.pack(pady=5)
        
        # Auto-save history
        self.auto_save_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(self.settings_tab, text="Auto-save generated passwords to history", 
                       variable=self.auto_save_var).pack(pady=5)
        
        # Save settings button
        ctk.CTkButton(self.settings_tab, text="Save Settings", 
                     command=self.save_settings).pack(pady=15)
    
    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                return json.load(file)
        else:
            return []
    
    def load_history_list(self):
        self.history_listbox.delete(0, tk.END)
        for password in self.password_history:
            self.history_listbox.insert(tk.END, password)
    
    def save_history(self):
        with open(self.history_file, "w") as file:
            json.dump(self.password_history, file)
    
    def generate_password(self):
        password_type = self.password_type_var.get()
        
        if password_type == "Random":
            password = self.generate_random_password()
        elif password_type == "PIN":
            password = self.generate_pin()
        elif password_type == "Passphrase":
            password = self.generate_passphrase()
        elif password_type == "Memorable":
            password = self.generate_memorable_password()
        else:
            password = self.generate_random_password()
        
        self.password.set(password)
        self.update_strength(password)
        
        # Auto-save to history
        if self.auto_save_var.get():
            self.add_to_history(password)
    
    def generate_random_password(self):
        chars = ""
        if self.upper_var.get():
            chars += string.ascii_uppercase
        if self.lower_var.get():
            chars += string.ascii_lowercase
        if self.numbers_var.get():
            chars += string.digits
        if self.symbols_var.get():
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        if self.exclude_similar_var.get():
            similar = "0O1lI"
            chars = ''.join(c for c in chars if c not in similar)
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        # Use cryptographically secure random
        return ''.join(secrets.choice(chars) for _ in range(self.length_var.get()))
    
    def generate_pin(self):
        length = min(self.length_var.get(), 16)  # Reasonable PIN limit
        return ''.join(secrets.choice(string.digits) for _ in range(length))
    
    def generate_passphrase(self):
        words = [
            "apple", "banana", "orange", "grape", "melon", "peach", "berry", "lemon",
            "tiger", "elephant", "giraffe", "monkey", "dolphin", "penguin", "eagle", "rabbit",
            "mountain", "ocean", "forest", "desert", "river", "valley", "island", "cloud",
            "computer", "keyboard", "monitor", "mouse", "printer", "camera", "phone", "tablet",
            "coffee", "pizza", "burger", "salad", "pasta", "bread", "cheese", "chocolate"
        ]
        
        word_count = max(2, self.length_var.get() // 6)  # Approximate length
        passphrase_words = [secrets.choice(words) for _ in range(word_count)]
        
        # Add numbers and symbols between words for security
        separators = ["-", "_", ".", ""]
        result = []
        for i, word in enumerate(passphrase_words):
            result.append(word.capitalize())
            if i < len(passphrase_words) - 1:
                separator = secrets.choice(separators)
                if separator and self.numbers_var.get():
                    separator += str(secrets.choice(string.digits))
                result.append(separator)
        
        return ''.join(result)
    
    def generate_memorable_password(self):
        # Generate passwords that are easier to remember but still secure
        consonants = "bcdfghjklmnpqrstvwxyz"
        vowels = "aeiou"
        
        if self.exclude_similar_var.get():
            consonants = consonants.replace('l', '').replace('i', '')
        
        password = []
        length = self.length_var.get()
        
        for i in range(length):
            if i % 2 == 0:
                password.append(secrets.choice(consonants))
            else:
                password.append(secrets.choice(vowels))
        
        # Make first character uppercase if enabled
        if self.upper_var.get() and password:
            password[0] = password[0].upper()
        
        # Add a number if enabled
        if self.numbers_var.get() and length > 3:
            password[-1] = secrets.choice(string.digits)
        
        return ''.join(password)
    
    def update_strength(self, password):
        score = 0
        
        # Length scoring
        if len(password) >= 20: score += 3
        elif len(password) >= 16: score += 2
        elif len(password) >= 12: score += 2
        elif len(password) >= 8: score += 1
        
        # Character variety scoring
        if any(c.isupper() for c in password): score += 1
        if any(c.islower() for c in password): score += 1
        if any(c.isdigit() for c in password): score += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): score += 2
        
        # Calculate entropy
        charset_size = 0
        if any(c.isupper() for c in password): charset_size += 26
        if any(c.islower() for c in password): charset_size += 26
        if any(c.isdigit() for c in password): charset_size += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password): charset_size += 25
        
        if charset_size > 0:
            entropy = len(password) * math.log2(charset_size)
        else:
            entropy = 0
        
        # Determine strength
        if score >= 7:
            strength = "Very Strong"
            color = "#27ae60"
            bar_val = 1.0
        elif score >= 5:
            strength = "Strong"
            color = "#2ecc71"
            bar_val = 0.8
        elif score >= 4:
            strength = "Medium"
            color = "#f39c12"
            bar_val = 0.6
        elif score >= 2:
            strength = "Weak"
            color = "#e67e22"
            bar_val = 0.4
        else:
            strength = "Very Weak"
            color = "#e74c3c"
            bar_val = 0.2
        
        self.strength_label.configure(text=f"Strength: {strength}", text_color=color)
        self.entropy_label.configure(text=f"Entropy: {entropy:.1f} bits")
        self.strength_bar.set(bar_val)
        self.strength_bar.configure(progress_color=color)
    
    def copy_password(self):
        if self.password.get():
            pyperclip.copy(self.password.get())
            self.show_tooltip("Copied!")
    
    def copy_from_history(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            password = self.history_listbox.get(selection[0])
            pyperclip.copy(password)
            self.show_tooltip("Copied from history!")
    
    def add_to_history(self, password):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"{timestamp} - {password}"
        
        if entry not in self.password_history:
            self.password_history.append(entry)
            # Keep only last 100 entries
            if len(self.password_history) > 100:
                self.password_history = self.password_history[-100:]
            
            self.save_history()
            self.load_history_list()
    
    def clear_history(self):
        self.password_history = []
        self.save_history()
        self.load_history_list()
        self.show_tooltip("History cleared!")
    
    def export_history(self):
        if not self.password_history:
            self.show_tooltip("No history to export!")
            return
        
        filename = f"password_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write("Password Generator History\n")
            f.write(f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            for entry in self.password_history:
                f.write(entry + "\n")
        
        self.show_tooltip(f"History exported to {filename}!")
    
    def on_type_change(self, choice):
        # Adjust UI based on password type
        if choice == "PIN":
            self.length_var.set(min(self.length_var.get(), 16))
            self.upper_var.set(False)
            self.lower_var.set(False)
            self.symbols_var.set(False)
            self.numbers_var.set(True)
        elif choice == "Passphrase":
            self.length_var.set(20)
            self.upper_var.set(True)
            self.lower_var.set(True)
            self.symbols_var.set(False)
            self.numbers_var.set(True)
        elif choice == "Memorable":
            self.length_var.set(12)
            self.upper_var.set(True)
            self.lower_var.set(True)
            self.symbols_var.set(False)
            self.numbers_var.set(True)
        else:  # Random
            self.upper_var.set(True)
            self.lower_var.set(True)
            self.symbols_var.set(True)
            self.numbers_var.set(True)
        
        self.generate_password()
    
    def save_settings(self):
        self.theme_mode = self.theme_mode_var.get()
        ctk.set_appearance_mode(self.theme_mode)
        
        color_theme = self.color_theme_var.get()
        ctk.set_default_color_theme(color_theme)
        
        settings = {
            "theme_mode": self.theme_mode,
            "color_theme": color_theme,
            "auto_save": self.auto_save_var.get()
        }
        
        with open("settings.json", "w") as f:
            json.dump(settings, f)
        
        self.show_tooltip("Settings saved!")
    
    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.theme_mode = settings.get("theme_mode", "dark")
                ctk.set_appearance_mode(self.theme_mode)
                
                color_theme = settings.get("color_theme", "green")
                ctk.set_default_color_theme(color_theme)
    
    def show_tooltip(self, msg):
        tooltip = ctk.CTkToplevel(self.window)
        tooltip.geometry("+%d+%d" % (self.window.winfo_rootx() + 150,
                                      self.window.winfo_rooty() + 50))
        tooltip.overrideredirect(True)
        ctk.CTkLabel(tooltip, text=msg, fg_color="#2ecc71",
                    text_color="white", padx=20, pady=10).pack()
        tooltip.after(1000, tooltip.destroy)
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = PasswordGeneratorPro()
    app.run()