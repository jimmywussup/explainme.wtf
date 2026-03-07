import os
import re
import sys
import io
import json
import time
import socket
import queue
import threading
import platform
import pyperclip
import pystray
from pynput import keyboard as pynput_keyboard
from pynput.keyboard import Key, Controller as KeyboardController
try:
    import keyboard as win_keyboard
except ImportError:
    win_keyboard = None
from PIL import Image, ImageDraw, ImageGrab, ImageTk
import customtkinter as ctk
import webbrowser

from llm_adapter import get_llm_adapter
from dotenv import load_dotenv

load_dotenv()

UI_TRANSLATIONS = {
    "English": {
        "send": "Send",
        "settings_title": "explainme.wtf Settings",
        "provider": "LLM Provider:",
        "api_key": "API Key:",
        "fast_model": "Fast Model ID:",
        "thinking_model": "Thinking Model ID:",
        "fast_model": "Fast Model ID:",
        "thinking_model": "Thinking Model ID:",
        "output_lang": "Output Language:",
        "hotkey": "Hotkey:",
        "click_record": "Click to Record",
        "listening": "Listening...",
        "save_settings": "Save Settings",
        "thinking": "Thinking...",
        "ask_followup": "Ask a follow-up question...",
        "type_message": "Type your message here...",
        "ready": "Ready! How can I help you?",
        "screenshot_captured": "Screenshot captured\n\nAnalyzing image...",
        "selected_text": "Selected Text:",
        "image_attached": "🖼️ Image Attached",
        "error_no_key": "Error: No API key set for",
        "config_error": "Configuration Error:"
    },
    "Russian": {
        "send": "Отправить",
        "settings_title": "Настройки explainme.wtf",
        "provider": "LLM Провайдер:",
        "api_key": "API Ключ:",
        "fast_model": "ID Быстрой Модели:",
        "thinking_model": "ID Вдумчивой Модели:",
        "output_lang": "Язык Ответа:",
        "hotkey": "Горячая Клавиша:",
        "click_record": "Кликните для записи",
        "listening": "Жду нажатия...",
        "save_settings": "Сохранить",
        "thinking": "Думаю...",
        "ask_followup": "Задайте уточняющий вопрос...",
        "type_message": "Введите ваше сообщение...",
        "ready": "Готов! Чем я могу помочь?",
        "screenshot_captured": "Скриншот сделан\n\nАнализирую изображение...",
        "selected_text": "Выделенный текст:",
        "image_attached": "🖼️ Изображение прикреплено",
        "error_no_key": "Ошибка: Не задан API ключ для",
        "config_error": "Ошибка конфигурации:"
    },
    "Ukrainian": {
        "send": "Надіслати",
        "settings_title": "Налаштування explainme.wtf",
        "provider": "LLM Провайдер:",
        "api_key": "API Ключ:",
        "fast_model": "ID Швидкої Моделі:",
        "thinking_model": "ID Вдумливої Моделі:",
        "output_lang": "Мова Відповіді:",
        "hotkey": "Гаряча Клавіша:",
        "save_settings": "Зберегти",
        "thinking": "Думаю...",
        "ask_followup": "Задайте додаткове питання...",
        "type_message": "Введіть ваше повідомлення...",
        "ready": "Готово! Чим я можу допомогти?",
        "screenshot_captured": "Скріншот зроблено\n\nАналізую зображення...",
        "selected_text": "Виділений текст:",
        "image_attached": "🖼️ Зображення прикріплено",
        "error_no_key": "Помилка: Не задано API ключ для",
        "config_error": "Помилка конфігурації:"
    },
    "Spanish": {
        "send": "Enviar",
        "settings_title": "Configuración de explainme.wtf",
        "provider": "Proveedor LLM:",
        "api_key": "Clave API:",
        "fast_model": "ID Modelo Rápido:",
        "thinking_model": "ID Modelo Pensante:",
        "output_lang": "Idioma de Respuesta:",
        "hotkey": "Atajo de teclado:",
        "save_settings": "Guardar",
        "thinking": "Pensando...",
        "ask_followup": "Haz una pregunta...",
        "type_message": "Escribe tu mensaje aquí...",
        "ready": "¡Listo! ¿En qué puedo ayudarte?",
        "screenshot_captured": "Captura de pantalla tomada\n\nAnalizando imagen...",
        "selected_text": "Texto seleccionado:",
        "image_attached": "🖼️ Imagen adjunta",
        "error_no_key": "Error: No hay clave API para",
        "config_error": "Error de configuración:"
    },
    "French": {
        "send": "Envoyer",
        "settings_title": "Paramètres explainme.wtf",
        "provider": "Fournisseur LLM :",
        "api_key": "Clé API :",
        "fast_model": "ID Modèle Rapide :",
        "thinking_model": "ID Modèle Réfléchi :",
        "output_lang": "Langue de réponse :",
        "hotkey": "Raccourci clavier :",
        "save_settings": "Enregistrer",
        "thinking": "En train de penser...",
        "ask_followup": "Posez une question...",
        "type_message": "Tapez votre message ici...",
        "ready": "Prêt ! Comment puis-je vous aider ?",
        "screenshot_captured": "Capture d'écran prise\n\nAnalyse de l'image...",
        "selected_text": "Texte sélectionné :",
        "image_attached": "🖼️ Image jointe",
        "error_no_key": "Erreur : Aucune clé API définie pour",
        "config_error": "Erreur de configuration :"
    },
    "German": {
        "send": "Senden",
        "settings_title": "explainme.wtf Einstellungen",
        "provider": "LLM-Anbieter:",
        "api_key": "API-Schlüssel:",
        "fast_model": "Schnelles Modell ID:",
        "thinking_model": "Denkendes Modell ID:",
        "output_lang": "Antwortsprache:",
        "hotkey": "Tastenkürzel:",
        "save_settings": "Speichern",
        "thinking": "Denke nach...",
        "ask_followup": "Stellen Sie eine Frage...",
        "type_message": "Geben Sie hier Ihre Nachricht ein...",
        "ready": "Bereit! Wie kann ich helfen?",
        "screenshot_captured": "Screenshot aufgenommen\n\nBild wird analysiert...",
        "selected_text": "Ausgewählter Text:",
        "image_attached": "🖼️ Bild angehängt",
        "error_no_key": "Fehler: Kein API-Schlüssel für",
        "config_error": "Konfigurationsfehler:"
    }
}

def get_text(lang, key):
    return UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS["English"]).get(key, UI_TRANSLATIONS["English"].get(key, key))


# Configuration management
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "hotkey": "ctrl+`",
    "provider": "gemini",
    "api_key_gemini": "",
    "api_key_openai": "",
    "api_key_anthropic": "",
    "api_key_deepseek": "",
    "fast_model_id": "gemini-2.5-flash-lite",
    "thinking_model_id": "gemini-2.5-pro",
    "language": "English"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        config = DEFAULT_CONFIG.copy()
        config["_is_first_run"] = True
        return config
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def create_tray_icon():
    # Generate a simple icon for the system tray
    image = Image.new('RGB', (64, 64), color=(11, 15, 25))
    dc = ImageDraw.Draw(image)
    dc.rectangle((16, 16, 48, 48), fill=(0, 242, 254))
    return image

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent, current_config, on_save_callback):
        super().__init__(parent)
        self.config = current_config
        lang = self.config.get("language", "English")
        
        self.provider_models = {
            "gemini": {
                "fast": ["gemini-3.1-flash-lite-preview", "gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-flash-lite"],
                "thinking": ["gemini-3.1-pro-preview", "gemini-2.5-pro"]
            },
            "openai": {
                "fast": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
                "thinking": ["o3-mini", "o1-mini", "o1"]
            },
            "anthropic": {
                "fast": ["claude-3-5-haiku-latest", "claude-haiku-4-5"],
                "thinking": ["claude-3-7-sonnet-latest", "claude-sonnet-4-6", "claude-opus-4-6"]
            },
            "deepseek": {
                "fast": ["deepseek-chat"],
                "thinking": ["deepseek-reasoner"]
            }
        }
        
        self.title(get_text(lang, "settings_title"))
        self.geometry("450x320")
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))
        self.on_save = on_save_callback
        
        # Handle macOS window close explicitly so it doesn't kill the ctk mainloop implicitly
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # UI Elements
        self.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text=get_text(lang, "provider"), font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=10, pady=(20, 10), sticky="w")
        self.provider_var = ctk.StringVar(value=self.config.get("provider", "gemini"))
        self.current_ui_provider = self.provider_var.get()
        self.provider_dropdown = ctk.CTkOptionMenu(self, variable=self.provider_var, values=["gemini", "openai", "anthropic", "deepseek"], command=self.on_provider_change)
        self.provider_dropdown.grid(row=0, column=1, padx=10, pady=(20, 10), sticky="ew")
        
        self.api_key_label = ctk.CTkLabel(self, text=f"{self.current_ui_provider.capitalize()} {get_text(lang, 'api_key')}")
        self.api_key_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.api_key_entry = ctk.CTkEntry(self, show="*")
        self.api_key_entry.insert(0, self._get_api_key(self.current_ui_provider))
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text=get_text(lang, "output_lang")).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.language_var = ctk.StringVar(value=self.config.get("language", "English"))
        self.language_dropdown = ctk.CTkOptionMenu(self, variable=self.language_var, values=["English", "Russian", "Ukrainian", "Spanish", "French", "German"])
        self.language_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text=get_text(lang, "hotkey")).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        # Hotkey Recording UI
        self.hotkey_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.hotkey_frame.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        
        self.hotkey_var = ctk.StringVar(value=self.config.get("hotkey", "ctrl+`"))
        self.hotkey_label = ctk.CTkLabel(
            self.hotkey_frame, 
            textvariable=self.hotkey_var, 
            fg_color=("gray80", "gray20"), 
            corner_radius=6, 
            width=140,
            font=("Segoe UI", 14, "bold"),
            text_color=("black", "white")
        )
        self.hotkey_label.pack(side="left", padx=(0, 10))
        
        self.is_recording = False
        default_btn_text = get_text(lang, "click_record") if "click_record" in UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS["English"]) else "Click to Record"
        self.recording_listener = None
        self.current_keys = set()
        
        self.record_btn = ctk.CTkButton(
            self.hotkey_frame, 
            text=default_btn_text, 
            width=80, 
            fg_color=("gray75", "gray30"),
            text_color=("black", "white"),
            hover_color=("gray65", "gray40"),
            command=self.toggle_recording
        )
        self.record_btn.pack(side="left", fill="x", expand=True)

        self.advanced_visible = ctk.BooleanVar(value=False)
        self.advanced_toggle_btn = ctk.CTkButton(
            self, text="▶ Advanced Settings", fg_color="transparent", 
            text_color=("gray10", "gray90"), hover_color=("gray75", "gray25"),
            anchor="w", command=self.toggle_advanced
        )
        self.advanced_toggle_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=(15, 5), sticky="ew")

        # Advanced Settings Frame (Hidden by default)
        self.advanced_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.advanced_frame.grid_columnconfigure(1, weight=1)
        
        # Fast Model ID
        ctk.CTkLabel(self.advanced_frame, text=get_text(lang, "fast_model")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        fast_models = self.provider_models.get(self.current_ui_provider, {}).get("fast", [])
        def_fast = fast_models[0] if fast_models else ""
        self.fast_model_var = ctk.StringVar(value=self.config.get("fast_model_id", def_fast) or def_fast)
        self.fast_model_dropdown = ctk.CTkOptionMenu(self.advanced_frame, variable=self.fast_model_var, values=fast_models)
        self.fast_model_dropdown.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Thinking Model ID
        ctk.CTkLabel(self.advanced_frame, text=get_text(lang, "thinking_model")).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        thinking_models = self.provider_models.get(self.current_ui_provider, {}).get("thinking", [])
        def_thinking = thinking_models[0] if thinking_models else ""
        self.thinking_model_var = ctk.StringVar(value=self.config.get("thinking_model_id", def_thinking) or def_thinking)
        self.thinking_model_dropdown = ctk.CTkOptionMenu(self.advanced_frame, variable=self.thinking_model_var, values=thinking_models)
        self.thinking_model_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.save_btn = ctk.CTkButton(self, text=get_text(lang, "save_settings"), command=self.save_settings)
        self.save_btn.grid(row=6, column=0, columnspan=2, pady=(20, 10))
        
    def toggle_advanced(self):
        if self.advanced_visible.get():
            self.advanced_frame.grid_remove()
            self.advanced_toggle_btn.configure(text="▶ Advanced Settings")
            self.advanced_visible.set(False)
            self.geometry("450x320")
        else:
            self.advanced_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=0, pady=0)
            self.advanced_toggle_btn.configure(text="▼ Advanced Settings")
            self.advanced_visible.set(True)
            self.geometry("450x430")
            
    def toggle_recording(self):
        lang = self.config.get("language", "English")
        if self.is_recording:
            self.stop_recording()
            return
            
        self.is_recording = True
        listening_text = get_text(lang, "listening") if "listening" in UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS["English"]) else "Listening..."
        self.record_btn.configure(text=listening_text, fg_color="#FFA500", text_color="black") # Orange indicating recording
        self.current_keys.clear()
        
        if platform.system() == "Windows" and win_keyboard is not None:
            def record_win():
                try:
                    # read_hotkey blocks until a combination is fully pressed
                    combo = win_keyboard.read_hotkey(suppress=False)
                    
                    # Normalize Cyrillic layouts to QWERTY for clean display/saving
                    cyrillic_map = {
                        'й': 'q', 'ц': 'w', 'у': 'e', 'к': 'r', 'е': 't', 'н': 'y', 'г': 'u', 'ш': 'i', 'щ': 'o', 'з': 'p', 'х': '[', 'ъ': ']',
                        'ф': 'a', 'ы': 's', 'в': 'd', 'а': 'f', 'п': 'g', 'р': 'h', 'о': 'j', 'л': 'k', 'д': 'l', 'ж': ';', 'э': "'",
                        'я': 'z', 'ч': 'x', 'с': 'c', 'м': 'v', 'и': 'b', 'т': 'n', 'ь': 'm', 'б': ',', 'ю': '.', '.': '/', 'ё': '`'
                    }
                    mapped_parts = []
                    for part in combo.split('+'):
                        mapped_parts.append(cyrillic_map.get(part, part))
                    combo = '+'.join(mapped_parts)
                    
                    if self.is_recording:
                        self.after(0, lambda c=combo: self.hotkey_var.set(c))
                        self.after(10, self.stop_recording)
                except Exception:
                    pass
                    
            self.windows_record_thread = threading.Thread(target=record_win, daemon=True)
            self.windows_record_thread.start()
            return

        # Pynput logic for macOS / Linux
        def on_press(key):
            try:
                key_name = key.name if hasattr(key, 'name') else key.char
                if key_name is None and hasattr(key, 'vk'):
                    key_name = f"<{key.vk}>"
            except AttributeError:
                key_name = str(key)

            modifier_map = {
                'ctrl_l': 'ctrl', 'ctrl_r': 'ctrl',
                'shift_l': 'shift', 'shift_r': 'shift',
                'alt_l': 'alt', 'alt_r': 'alt', 'alt_gr': 'alt',
                'cmd_l': 'cmd', 'cmd_r': 'cmd'
            }
            key_name = modifier_map.get(key_name, key_name)
            
            if key_name:
                self.current_keys.add(key_name.lower())
                
        def on_release(key):
            if not self.current_keys:
                return False
                
            modifiers_order = ['ctrl', 'alt', 'shift', 'cmd']
            pressed_mods = [m for m in modifiers_order if m in self.current_keys]
            other_keys = [k for k in self.current_keys if k not in modifiers_order]
            
            if other_keys:
                combo = "+".join(pressed_mods + other_keys)
                self.hotkey_var.set(combo)
            elif pressed_mods:
                self.hotkey_var.set(pressed_mods[0])
                
            self.after(10, self.stop_recording)
            return False
            
        self.recording_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
        self.recording_listener.start()
        
    def stop_recording(self):
        lang = self.config.get("language", "English")
        self.is_recording = False
        default_btn_text = get_text(lang, "click_record") if "click_record" in UI_TRANSLATIONS.get(lang, UI_TRANSLATIONS["English"]) else "Click to Record"
        self.record_btn.configure(
            text=default_btn_text, 
            fg_color=("gray75", "gray30"), 
            text_color=("black", "white"),
            hover_color=("gray65", "gray40")
        )
        if hasattr(self, 'windows_record_thread') and self.windows_record_thread and self.windows_record_thread.is_alive():
            try:
                # To kill keyboard.read_hotkey without blocking, 
                # we just simulate a dummy press to unblock it safely
                import keyboard as win_keyboard
                win_keyboard.send('esc')
            except Exception:
                pass
                
        if self.recording_listener:
            self.recording_listener.stop()
            self.recording_listener = None
        
    def on_provider_change(self, choice):
        lang = self.config.get("language", "English")
        self.config[f"api_key_{self.current_ui_provider}"] = self.api_key_entry.get().strip()
        self.current_ui_provider = choice
        self.api_key_label.configure(text=f"{choice.capitalize()} {get_text(lang, 'api_key')}")
        self.api_key_entry.delete(0, 'end')
        self.api_key_entry.insert(0, self._get_api_key(choice))
        
        fast_values = self.provider_models.get(choice, {}).get("fast", [])
        thinking_values = self.provider_models.get(choice, {}).get("thinking", [])
        
        self.fast_model_dropdown.configure(values=fast_values)
        self.thinking_model_dropdown.configure(values=thinking_values)
        
        if fast_values:
            self.fast_model_var.set(fast_values[0])
        if thinking_values:
            self.thinking_model_var.set(thinking_values[0])
    
    def _get_api_key(self, provider):
        """Get API key from config first, then fallback to .env."""
        key = self.config.get(f"api_key_{provider}", "")
        if not key:
            env_key_map = {
                "gemini": "GEMINI_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY"
            }
            key = os.environ.get(env_key_map.get(provider, ""), "")
        return key
        
    def save_settings(self):
        self.config[f"api_key_{self.current_ui_provider}"] = self.api_key_entry.get().strip()
        
        new_config = {
            "provider": self.provider_var.get(),
            "api_key_gemini": self.config.get("api_key_gemini", ""),
            "api_key_openai": self.config.get("api_key_openai", ""),
            "api_key_anthropic": self.config.get("api_key_anthropic", ""),
            "api_key_deepseek": self.config.get("api_key_deepseek", ""),
            "fast_model_id": self.fast_model_var.get().strip(),
            "thinking_model_id": self.thinking_model_var.get().strip(),
            "language": self.language_var.get().strip(),
            "hotkey": self.hotkey_var.get().strip()
        }
        
        # Ensure we stop recording if they hit save while it was listening
        if hasattr(self, 'is_recording') and self.is_recording:
            self.stop_recording()
            
        self.on_save(new_config)
        
        # On macOS, don't destroy the window, just withdraw (hide) it so the app doesn't quit
        if platform.system() == "Darwin":
            self.withdraw()
        else:
            self.destroy()

    def on_closing(self):
        # Handle the native "X" button click
        if platform.system() == "Darwin":
            self.withdraw() # Just hide it, don't destroy, so click-on-dock can restore it
        else:
            self.destroy()

class ExplainerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        if platform.system() != "Darwin":
            self.withdraw()  # Hide the main background window on Windows/Linux
            
        self.queue = queue.Queue()
        
        self.config = load_config()
        self.current_adapter = None
        self.active_hotkey = self.config.get("hotkey", "ctrl+`")
        self.settings_window = None
        self.last_hotkey_time = 0.0
        self.register_hotkey()
        
        # Setup PyStray in background if not macOS
        if platform.system() != "Darwin":
            self.setup_tray()
        else:
            # On macOS we don't have a background tray so we just show settings as main window
            self.after(500, lambda: self.queue.put(("SHOW_SETTINGS", None)))
        
        if self.config.pop("_is_first_run", False) and platform.system() != "Darwin":
            self.after(500, lambda: self.queue.put(("SHOW_SETTINGS", None)))
            
        # Bind macOS Reopen event (when user clicks the dock icon of an already running app)
        if platform.system() == "Darwin":
            self.createcommand("::tk::mac::ReopenApplication", self.on_mac_reopen)
        
        # Fast UI poller
        self.after(50, self.poll_queue)

    def on_mac_reopen(self):
        self.queue.put(("SHOW_SETTINGS", None))

    def setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("Settings", self.on_tray_settings, default=True),
            pystray.MenuItem("Quit", self.on_tray_quit)
        )
        self.icon = pystray.Icon("explainme.wtf", create_tray_icon(), "explainme.wtf", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def on_tray_settings(self, icon, item):
        self.queue.put(("TOGGLE_SETTINGS", None))

    def on_tray_quit(self, icon, item):
        self.queue.put(("QUIT", None))
        
    def register_hotkey(self):
        try:
            hotkey_str = self.active_hotkey
            
            if platform.system() == "Windows" and win_keyboard is not None:
                try:
                    # Use keyboard library on Windows
                    win_combo = hotkey_str.lower().replace("cmd", "win").replace("command", "win")
                    win_keyboard.add_hotkey(win_combo, self._on_hotkey_wrapper)
                    self.hotkey_listener_type = "windows"
                    return  # Success, skip pynput
                except ValueError:
                    pass  # Key not in layout, fall through to pynput
            
            # Use pynput on macOS/Linux/Fallback
            parts = hotkey_str.lower().split("+")
            pynput_parts = []
            for p in parts:
                p = p.strip()
                if p in ("ctrl", "control"):
                    pynput_parts.append("<ctrl>")
                elif p in ("alt",):
                    pynput_parts.append("<alt>")
                elif p in ("shift",):
                    pynput_parts.append("<shift>")
                elif p in ("cmd", "command", "win"):
                    pynput_parts.append("<cmd>")
                else:
                    pynput_parts.append(p)
            pynput_combo = "+".join(pynput_parts)
            
            self.hotkey_listener = pynput_keyboard.GlobalHotKeys({
                pynput_combo: self.on_hotkey
            })
            self.hotkey_listener.start()
            self.hotkey_listener_type = "pynput"
        except Exception as e:
            import traceback
            traceback.print_exc()

    def unregister_hotkey(self):
        try:
            if getattr(self, 'hotkey_listener_type', None) == "windows":
                if win_keyboard is not None:
                    # remove_all_hotkeys can sometimes throw if hotkey isn't found perfectly, but it's safe
                    win_keyboard.remove_all_hotkeys()
            elif getattr(self, 'hotkey_listener_type', None) == "pynput":
                if hasattr(self, 'hotkey_listener') and self.hotkey_listener is not None:
                    self.hotkey_listener.stop()
                    self.hotkey_listener = None
        except Exception:
            pass

    def _on_hotkey_wrapper(self):
        # We need a wrapper because the keyboard module calls this in a background thread 
        # and we need to pass control cleanly, or just call on_hotkey directly 
        # since on_hotkey already queues the UI thread
        self.on_hotkey()

    def on_hotkey(self):
        current_time = time.time()
        if current_time - self.last_hotkey_time < 1.0:
            return # Debounce: Prevent double firing if pressed rapidly or OS glitches
        self.last_hotkey_time = current_time

        self.unregister_hotkey()

        # Step 1: Save the current clipboard image before we potentially destroy it
        saved_image_bytes = self._check_clipboard_image()

        # Step 2: Empty the text clipboard to ensure we don't grab stale text
        pyperclip.copy("")

        # Step 3: Simulate Ctrl+C (Windows/Linux) or Cmd+C (macOS) to copy selected text
        kb = KeyboardController()
        modifier = Key.cmd if platform.system() == "Darwin" else Key.ctrl
        kb.press(modifier)
        kb.press('c')
        kb.release('c')
        kb.release(modifier)
        time.sleep(0.15)
        
        # Step 4: Check if any new text was copied
        text = pyperclip.paste().strip()
        
        # Step 5: Decide what to send to the LLM (Text has priority)
        if text:
            # We found new text from the Ctrl+C
            self.queue.put(("SHOW_UI", text))
        elif saved_image_bytes:
            # No text, but we had an image saved from before the Ctrl+C
            self.queue.put(("SHOW_UI_IMAGE", saved_image_bytes))
        else:
            # Nothing at all - empty chat
            self.queue.put(("SHOW_UI_EMPTY", None))

    def _check_clipboard_image(self):
        """Check if the clipboard contains an image and return PNG bytes."""
        try:
            img = ImageGrab.grabclipboard()
            if img is not None and isinstance(img, Image.Image):
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                return buf.getvalue()
        except Exception:
            pass
        return None

    def poll_queue(self):
        try:
            msg, payload = self.queue.get_nowait()
            if msg == "SHOW_UI":
                self.show_popup(payload)
            elif msg == "SHOW_UI_IMAGE":
                self.show_popup(None, image_bytes=payload)
            elif msg == "SHOW_UI_EMPTY":
                self.show_popup(None, is_empty=True)
            elif msg == "SHOW_SETTINGS":
                if not self.settings_window or not self.settings_window.winfo_exists():
                    self.settings_window = SettingsWindow(self, self.config, self.update_config)
                else:
                    if platform.system() == "Darwin":
                        self.settings_window.deiconify() # Restore if it was withdrawn
                    self.settings_window.focus_force()
            elif msg == "TOGGLE_SETTINGS":
                if self.settings_window and self.settings_window.winfo_exists():
                    if platform.system() == "Darwin":
                        self.settings_window.withdraw()
                    else:
                        self.settings_window.destroy()
                        self.settings_window = None
                else:
                    self.settings_window = SettingsWindow(self, self.config, self.update_config)
            elif msg == "QUIT":
                if platform.system() != "Darwin" and hasattr(self, 'icon'):
                    self.icon.stop()
                self.destroy()
        except queue.Empty:
            pass
        self.after(50, self.poll_queue)
        
    def update_config(self, new_config):
        self.unregister_hotkey() # Stop listening to old
        save_config(new_config)
        self.config = new_config
        self.active_hotkey = new_config.get("hotkey", "ctrl+`")
        self.register_hotkey() # Start listening to new

    def show_popup(self, text, image_bytes=None, is_empty=False):
        lang = self.config.get("language", "English")
        is_image_mode = image_bytes is not None
        popup = ctk.CTkToplevel(self)
        popup.title("explainme.wtf")
        popup_width = 550 if is_image_mode else 500
        popup_height = 500 if is_image_mode else 400
        popup.geometry(f"{popup_width}x{popup_height}")
        popup.attributes("-topmost", True)
        popup.after(200, lambda: popup.attributes("-topmost", False))
        
        ws = popup.winfo_screenwidth()
        hs = popup.winfo_screenheight()
        x = int((ws/2) - (popup_width/2))
        y = int((hs/2) - (popup_height/2))
        popup.geometry('+%d+%d' % (x, y))
        popup.focus_force()
        
        # Show a thumbnail preview for screenshots
        if is_image_mode:
            try:
                pil_image = Image.open(io.BytesIO(image_bytes))
                pil_image.thumbnail((popup_width - 30, 150))
                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=pil_image.size)
                img_label = ctk.CTkLabel(popup, image=ctk_image, text="")
                img_label.image = ctk_image
                img_label.pack(padx=15, pady=(10, 5))
            except Exception:
                pass
        
        textbox = ctk.CTkTextbox(popup, wrap="word", font=("Segoe UI", 15))
        textbox.pack(fill="both", expand=True, padx=15, pady=(15 if not is_image_mode else 5, 5))
        
        # Attachment indicator frame — sits between textbox and input row
        attachment_frame = ctk.CTkFrame(popup, fg_color="transparent", height=0)
        attachment_frame.pack(fill="x", padx=15, pady=0)
        
        input_frame = ctk.CTkFrame(popup, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        chat_input = ctk.CTkEntry(input_frame, placeholder_text=get_text(lang, "ask_followup") if not is_empty else get_text(lang, "type_message"), font=("Segoe UI", 14))
        chat_input.pack(side="left", fill="x", expand=True, padx=(0, 5))
        if not is_empty:
            chat_input.configure(state="disabled")
        
        # Mode dropdown — compact, next to Send
        mode_var = ctk.StringVar(value="Auto")
        mode_dropdown = ctk.CTkOptionMenu(
            input_frame,
            values=["Auto", "Fast", "Thinking"],
            variable=mode_var,
            width=90,
            font=("Segoe UI", 12)
        )
        mode_dropdown.pack(side="left", padx=(0, 5))
        
        send_btn = ctk.CTkButton(input_frame, text=get_text(lang, "send"), width=60)
        send_btn.pack(side="right")
        if not is_empty:
            send_btn.configure(state="disabled")
        
        if is_empty:
            textbox.insert("0.0", get_text(lang, "ready"))
        elif is_image_mode:
            textbox.insert("0.0", get_text(lang, "screenshot_captured"))
        else:
            textbox.insert("0.0", f"{get_text(lang, 'selected_text')} \"{text}\"\n\n{get_text(lang, 'thinking')}")
        textbox.configure(state="disabled")
        
        def on_close():
            pyperclip.copy("")
            popup.destroy()
            self.register_hotkey()
            
        popup.protocol("WM_DELETE_WINDOW", on_close)
        popup.bind("<Escape>", lambda e: on_close())

        provider = self.config.get("provider", "gemini")
        api_key = self.config.get(f"api_key_{provider}", "")
        if not api_key:
            env_key_map = {
                "gemini": "GEMINI_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY"
            }
            api_key = os.environ.get(env_key_map.get(provider, ""), "")
            
        fast_model_id = self.config.get("fast_model_id", "")
        thinking_model_id = self.config.get("thinking_model_id", "")
        
        if not api_key:
            textbox.configure(state="normal")
            textbox.delete("0.0", "end")
            textbox.insert("0.0", f"{get_text(lang, 'error_no_key')} {provider}.\nRight-click the system tray icon to enter Settings, or add it to your .env file.")
            textbox.configure(state="disabled")
            return

        try:
            adapter = get_llm_adapter(provider, api_key, fast_model_id, thinking_model_id)
        except Exception as e:
            textbox.configure(state="normal")
            textbox.delete("0.0", "end")
            textbox.insert("0.0", f"{get_text(lang, 'config_error')} {e}")
            textbox.configure(state="disabled")
            return

        def handle_send(event=None):
            msg = chat_input.get().strip()
            if not msg:
                return
            chat_input.delete(0, 'end')
            chat_input.configure(state="disabled")
            send_btn.configure(state="disabled")
            
            # Grab and clear any attached image bytes
            img_bytes_to_send = None
            if hasattr(self, 'attached_image_bytes') and self.attached_image_bytes:
                img_bytes_to_send = self.attached_image_bytes
                self.attached_image_bytes = None
                if hasattr(self, 'attachment_label') and self.attachment_label.winfo_exists():
                    self.attachment_label.destroy()
            
            textbox.configure(state="normal")
            textbox.insert("end", f"\n\nYOU:\n{msg}\n\n")
            textbox.insert("end", get_text(lang, "thinking"))
            textbox.see("end")
            textbox.configure(state="disabled")
            
            # Read the current mode from the toggle
            current_mode = mode_var.get()
            threading.Thread(target=self.send_chat_message, args=(adapter, msg, img_bytes_to_send, textbox, popup, chat_input, send_btn, current_mode), daemon=True).start()

        def handle_paste(event):
            try:
                # First check for image
                clipboard_image = ImageGrab.grabclipboard()
                if clipboard_image is not None and isinstance(clipboard_image, Image.Image):
                    # Convert to bytes
                    img_byte_arr = io.BytesIO()
                    clipboard_image.save(img_byte_arr, format='PNG')
                    self.attached_image_bytes = img_byte_arr.getvalue()
                    
                    # Show badge in the attachment frame (above input row)
                    if hasattr(self, 'attachment_label') and self.attachment_label.winfo_exists():
                        self.attachment_label.destroy()
                    self.attachment_label = ctk.CTkLabel(attachment_frame, text=get_text(lang, "image_attached"), text_color="#4CAF50", font=("Segoe UI", 12))
                    self.attachment_label.pack(side="left", padx=(0, 5), pady=(2, 2))
                    return "break" # Prevent default paste behavior
            except Exception:
                pass
            
            # If no image or error, allow default text paste
            return None

        send_btn.configure(command=handle_send)
        chat_input.bind("<Return>", handle_send)
        chat_input.bind("<Control-v>", handle_paste)
        chat_input.bind("<Command-v>", handle_paste) # Mac
        
        if is_empty:
            # No initial explanation needed, just wait for user to type
            pass
        elif is_image_mode:
            threading.Thread(target=self.fetch_initial_image_explanation, args=(adapter, image_bytes, textbox, popup, chat_input, send_btn), daemon=True).start()
        else:
            threading.Thread(target=self.fetch_initial_explanation, args=(adapter, text, textbox, popup, chat_input, send_btn), daemon=True).start()

    def fetch_initial_explanation(self, adapter, text, textbox, popup, chat_input, send_btn):
        language_pref = self.config.get("language", "English")
        try:
            prompt = (
                "You are a helpful dictionary and context explainer. "
                "Briefly explain the meaning of the following text in plain, easy-to-understand language. "
                f"You MUST answer in the {language_pref} language. "
                "Keep it very concise (1-2 short paragraphs max). \n\n"
                f"Selected Text: {text}"
            )
            explanation, model_type = adapter.send_message(prompt, force_simple=True)
        except Exception as e:
            explanation = f"Error fetching explanation:\n{str(e)}"
            model_type = "ERROR"
            
        if popup.winfo_exists():
            def apply_update():
                textbox.configure(state="normal")
                textbox.delete("0.0", "end")
                provider_name = self.config.get('provider', 'AI').upper()
                display_name = f"{provider_name} ({model_type})" if model_type != "ERROR" else provider_name
                textbox.insert("0.0", f"Selected Text: \"{text}\"\n\n{display_name}:\n{explanation}\n\n================================================\n")
                self._linkify(textbox)
                textbox.see("end")
                textbox.configure(state="disabled")
                chat_input.configure(state="normal")
                send_btn.configure(state="normal")
                chat_input.focus_set()
            popup.after(0, apply_update)

    def fetch_initial_image_explanation(self, adapter, image_bytes, textbox, popup, chat_input, send_btn):
        language_pref = self.config.get("language", "English")
        try:
            prompt = (
                "You are a helpful visual content analyzer and explainer. "
                "Analyze this screenshot and describe its content in plain, easy-to-understand language. "
                "If the image contains text, tables, or data, extract and explain the key information. "
                f"You MUST answer in the {language_pref} language. "
                "Keep it very concise, providing just a short direct answer (1-2 sentences max)."
            )
            explanation, model_type = adapter.send_message(prompt, image_bytes=image_bytes, force_simple=True)
        except NotImplementedError:
            explanation = (
                f"Error: {self.config.get('provider', 'this provider').capitalize()} does not support image input.\n"
                "Please configure Gemini, OpenAI, or Anthropic in settings for screenshot support."
            )
            model_type = "ERROR"
        except Exception as e:
            explanation = f"Error fetching image explanation:\n{str(e)}"
            model_type = "ERROR"
            
        if popup.winfo_exists():
            def apply_update():
                textbox.configure(state="normal")
                textbox.delete("0.0", "end")
                provider_name = self.config.get('provider', 'AI').upper()
                display_name = f"{provider_name} ({model_type})" if model_type != "ERROR" else provider_name
                textbox.insert("0.0", f"Screenshot captured\n\n{display_name}:\n{explanation}\n\n================================================\n")
                self._linkify(textbox)
                textbox.see("end")
                textbox.configure(state="disabled")
                chat_input.configure(state="normal")
                send_btn.configure(state="normal")
                chat_input.focus_set()
            popup.after(0, apply_update)

    def send_chat_message(self, adapter, msg, attached_image_bytes, textbox, popup, chat_input, send_btn, mode="Auto"):
        model_type = "UNKNOWN"
        try:
            # Hardcoded keyword override: triggers Thinking model (with Google Search grounding)
            # This prevents hallucinated links by ensuring real web data is used
            msg_lower = msg.lower()
            thinking_keywords = [
                "google", "search", "look up", "look it up", "find online",
                "provide link", "provide me link", "give me link", "send me link",
                "provide source", "give me source", "show me source",
                "proof", "proofs", "evidence",
                "source", "sources", "reference", "references",
                "current news", "latest news", "what's happening",
            ]
            if mode == "Auto" and any(kw in msg_lower for kw in thinking_keywords):
                force_simple = False
                force_thinking = True
            else:
                force_simple = (mode == "Fast")
                force_thinking = (mode == "Thinking")
            
            # Use a clean system_instruction parameter instead of prepending it to the user's msg
            language_pref = self.config.get("language", "English")
            sys_instruct = (
                f"Keep your answer concise and to the point (1-3 short paragraphs max). "
                f"Answer in {language_pref}. "
                f"Only give a longer, detailed answer if the user explicitly asks for it."
            )
            response_text, model_type = adapter.send_message(
                msg, 
                image_bytes=attached_image_bytes, 
                force_simple=force_simple, 
                force_thinking=force_thinking,
                system_instruction=sys_instruct
            )
        except Exception as e:
            response_text = f"Error: {str(e)}"
            
        if popup.winfo_exists():
            def apply_update():
                textbox.configure(state="normal")
                # Find and delete 'Thinking...'
                idx = textbox.search("Thinking...", "1.0", backwards=True)
                if idx:
                    textbox.delete(idx, f"{idx}+11c")
                
                provider_name = self.config.get('provider', 'AI').upper()
                display_name = f"{provider_name} ({model_type})" if model_type not in ("UNKNOWN",) else provider_name
                textbox.insert("end", f"{display_name}:\n{response_text}\n\n================================================")
                self._linkify(textbox)
                textbox.see("end")
                textbox.configure(state="disabled")
                chat_input.configure(state="normal")
                send_btn.configure(state="normal")
                chat_input.focus_set()
            popup.after(0, apply_update)

    def _linkify(self, textbox):
        """Scan all text in the textbox for URLs and make them clickable."""
        # Access the underlying tkinter Text widget
        tw = textbox._textbox if hasattr(textbox, '_textbox') else textbox
        
        # Remove old link tags to avoid duplicates
        for tag in tw.tag_names():
            if tag.startswith("link_"):
                tw.tag_delete(tag)
        
        # Configure cursor change for hovering over links
        url_pattern = re.compile(r'https?://[^\s\)\]\}>\"\',]+')
        content = tw.get("1.0", "end")
        
        link_count = 0
        for match in url_pattern.finditer(content):
            url = match.group()
            # Find the position in the text widget
            start_idx = f"1.0 + {match.start()} chars"
            end_idx = f"1.0 + {match.end()} chars"
            
            tag_name = f"link_{link_count}"
            tw.tag_add(tag_name, start_idx, end_idx)
            tw.tag_config(tag_name, foreground="#4da6ff", underline=True)
            tw.tag_bind(tag_name, "<Button-1>", lambda e, u=url: webbrowser.open(u))
            tw.tag_bind(tag_name, "<Enter>", lambda e: tw.configure(cursor="hand2"))
            tw.tag_bind(tag_name, "<Leave>", lambda e: tw.configure(cursor=""))
            link_count += 1

if __name__ == "__main__":
    # Prevent print() crash in windowed mode by redirecting stdout/stderr
    #try:
    #    devnull = open(os.devnull, "w", encoding="utf-8")
    #    sys.stdout = devnull
    #    sys.stderr = devnull
    #except Exception:
    #    pass

    # Enforce single instance by binding to a local TCP port
    lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lock_socket.bind(("127.0.0.1", 47200))
        lock_socket.listen(1)
        
        app_instance = ExplainerApp()
        
        # Start a thread to listen for IPC messages
        def ipc_server(target_app):
            while True:
                try:
                    conn, addr = lock_socket.accept()
                    data = conn.recv(1024).decode()
                    if data == "SHOW_SETTINGS":
                        target_app.queue.put(("SHOW_SETTINGS", None))
                    conn.close()
                except Exception:
                    pass
        threading.Thread(target=ipc_server, args=(app_instance,), daemon=True).start()
        
        app_instance.mainloop()
    except Exception:
        # Already running. Tell the running instance to show settings.
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(("127.0.0.1", 47200))
            client.sendall(b"SHOW_SETTINGS")
            client.close()
        except Exception:
            pass
        sys.exit(0)

