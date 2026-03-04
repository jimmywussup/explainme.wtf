import os
import sys
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
from PIL import Image, ImageDraw
import customtkinter as ctk

from llm_adapter import get_llm_adapter
from dotenv import load_dotenv

load_dotenv()

# Configuration management
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "hotkey": "ctrl+`",
    "provider": "gemini",
    "api_key_gemini": "",
    "api_key_openai": "",
    "api_key_anthropic": "",
    "api_key_deepseek": "",
    "model_id": "gemini-2.5-flash",
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
        self.title("explainme.wtf - Settings")
        self.geometry("400x350")
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))
        self.on_save = on_save_callback
        self.config = current_config
        
        # UI Elements
        self.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="LLM Provider:", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, padx=10, pady=(20, 10), sticky="w")
        self.provider_var = ctk.StringVar(value=self.config.get("provider", "gemini"))
        self.current_ui_provider = self.provider_var.get()
        self.provider_dropdown = ctk.CTkOptionMenu(self, variable=self.provider_var, values=["gemini", "openai", "anthropic", "deepseek"], command=self.on_provider_change)
        self.provider_dropdown.grid(row=0, column=1, padx=10, pady=(20, 10), sticky="ew")
        
        self.api_key_label = ctk.CTkLabel(self, text=f"{self.current_ui_provider.capitalize()} API Key:")
        self.api_key_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        self.api_key_entry = ctk.CTkEntry(self, show="*")
        self.api_key_entry.insert(0, self._get_api_key(self.current_ui_provider))
        self.api_key_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Model ID:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.model_entry = ctk.CTkEntry(self)
        self.model_entry.insert(0, self.config.get("model_id", "gemini-2.5-flash"))
        self.model_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Output Language:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.language_var = ctk.StringVar(value=self.config.get("language", "English"))
        self.language_dropdown = ctk.CTkOptionMenu(self, variable=self.language_var, values=["English", "Russian", "Ukrainian", "Spanish", "French", "German"])
        self.language_dropdown.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Hotkey:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.hotkey_entry = ctk.CTkEntry(self)
        self.hotkey_entry.insert(0, self.config.get("hotkey", "ctrl+`"))
        self.hotkey_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        self.save_btn = ctk.CTkButton(self, text="Save Settings", command=self.save_settings)
        self.save_btn.grid(row=5, column=0, columnspan=2, pady=30)
        
    def on_provider_change(self, choice):
        self.config[f"api_key_{self.current_ui_provider}"] = self.api_key_entry.get().strip()
        self.current_ui_provider = choice
        self.api_key_label.configure(text=f"{choice.capitalize()} API Key:")
        self.api_key_entry.delete(0, 'end')
        self.api_key_entry.insert(0, self._get_api_key(choice))
        
        defaults = {
            "gemini": "gemini-2.5-flash",
            "openai": "gpt-4o",
            "anthropic": "claude-3-5-sonnet-20241022",
            "deepseek": "deepseek-chat"
        }
        self.model_entry.delete(0, 'end')
        self.model_entry.insert(0, defaults.get(choice, ""))
    
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
            "model_id": self.model_entry.get().strip(),
            "language": self.language_var.get().strip(),
            "hotkey": self.hotkey_entry.get().strip()
        }
        self.on_save(new_config)
        self.destroy()

class ExplainerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Hide the main background window
        self.queue = queue.Queue()
        
        self.config = load_config()
        self.current_adapter = None
        self.active_hotkey = self.config.get("hotkey", "ctrl+`")
        self.settings_window = None
        self.register_hotkey()
        
        # Setup PyStray in background
        self.setup_tray()
        
        if self.config.pop("_is_first_run", False):
            self.after(500, lambda: self.queue.put(("SHOW_SETTINGS", None)))
        
        # Fast UI poller
        self.after(50, self.poll_queue)

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
                # Use keyboard library on Windows
                win_combo = hotkey_str.lower().replace("cmd", "win").replace("command", "win")
                win_keyboard.add_hotkey(win_combo, self._on_hotkey_wrapper, suppress=True)
                self.hotkey_listener_type = "windows"
            else:
                # Use pynput on macOS/Linux
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
            pass

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
        self.unregister_hotkey()
        # Simulate Ctrl+C (Windows/Linux) or Cmd+C (macOS) to copy selected text
        kb = KeyboardController()
        modifier = Key.cmd if platform.system() == "Darwin" else Key.ctrl
        kb.press(modifier)
        kb.press('c')
        kb.release('c')
        kb.release(modifier)
        time.sleep(0.15)
        text = pyperclip.paste().strip()
        
        if text:
            self.queue.put(("SHOW_UI", text))
        else:
            self.register_hotkey()

    def poll_queue(self):
        try:
            msg, payload = self.queue.get_nowait()
            if msg == "SHOW_UI":
                self.show_popup(payload)
            elif msg == "SHOW_SETTINGS":
                if not self.settings_window or not self.settings_window.winfo_exists():
                    self.settings_window = SettingsWindow(self, self.config, self.update_config)
                else:
                    self.settings_window.focus_force()
            elif msg == "TOGGLE_SETTINGS":
                if self.settings_window and self.settings_window.winfo_exists():
                    self.settings_window.destroy()
                    self.settings_window = None
                else:
                    self.settings_window = SettingsWindow(self, self.config, self.update_config)
            elif msg == "QUIT":
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

    def show_popup(self, text):
        popup = ctk.CTkToplevel(self)
        popup.title("explainme.wtf")
        popup.geometry("500x400")
        popup.attributes("-topmost", True)
        popup.after(200, lambda: popup.attributes("-topmost", False))
        
        ws = popup.winfo_screenwidth()
        hs = popup.winfo_screenheight()
        x = int((ws/2) - (500/2))
        y = int((hs/2) - (400/2))
        popup.geometry('+%d+%d' % (x, y))
        popup.focus_force()
        
        textbox = ctk.CTkTextbox(popup, wrap="word", font=("Segoe UI", 15))
        textbox.pack(fill="both", expand=True, padx=15, pady=(15, 5))
        
        input_frame = ctk.CTkFrame(popup, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        chat_input = ctk.CTkEntry(input_frame, placeholder_text="Ask a follow-up question...", font=("Segoe UI", 14))
        chat_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        chat_input.configure(state="disabled")
        
        send_btn = ctk.CTkButton(input_frame, text="Send", width=60)
        send_btn.pack(side="right")
        send_btn.configure(state="disabled")
        
        textbox.insert("0.0", f"Selected Text: \"{text}\"\n\nThinking...")
        textbox.configure(state="disabled")
        
        def on_close():
            pyperclip.copy("")
            popup.destroy()
            self.register_hotkey()
            
        popup.protocol("WM_DELETE_WINDOW", on_close)
        popup.bind("<Escape>", lambda e: on_close())

        provider = self.config.get("provider", "gemini")
        # Try local config first, then fallback to .env environment variables
        api_key = self.config.get(f"api_key_{provider}", "")
        if not api_key:
            env_key_map = {
                "gemini": "GEMINI_API_KEY",
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "deepseek": "DEEPSEEK_API_KEY"
            }
            api_key = os.environ.get(env_key_map.get(provider, ""), "")
            
        model_id = self.config.get("model_id", "")
        
        if not api_key:
            textbox.configure(state="normal")
            textbox.delete("0.0", "end")
            textbox.insert("0.0", f"Error: No API key set for {provider}.\nRight-click the system tray icon to enter Settings, or add it to your .env file.")
            textbox.configure(state="disabled")
            return

        # Initialize the chosen adapter
        try:
            adapter = get_llm_adapter(provider, api_key, model_id)
        except Exception as e:
            textbox.configure(state="normal")
            textbox.delete("0.0", "end")
            textbox.insert("0.0", f"Configuration Error: {e}")
            textbox.configure(state="disabled")
            return

        def handle_send(event=None):
            msg = chat_input.get().strip()
            if not msg:
                return
            chat_input.delete(0, 'end')
            chat_input.configure(state="disabled")
            send_btn.configure(state="disabled")
            
            textbox.configure(state="normal")
            textbox.insert("end", f"\n\nYou: {msg}\nThinking...")
            textbox.see("end")
            textbox.configure(state="disabled")
            threading.Thread(target=self.send_chat_message, args=(adapter, msg, textbox, popup, chat_input, send_btn), daemon=True).start()

        send_btn.configure(command=handle_send)
        chat_input.bind("<Return>", handle_send)
        
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
            explanation = adapter.send_message(prompt)
        except Exception as e:
            explanation = f"Error fetching explanation:\n{str(e)}"
            
        if popup.winfo_exists():
            def apply_update():
                textbox.configure(state="normal")
                textbox.delete("0.0", "end")
                textbox.insert("0.0", f"Selected Text: \"{text}\"\n\n{explanation}")
                textbox.see("end")
                textbox.configure(state="disabled")
                chat_input.configure(state="normal")
                send_btn.configure(state="normal")
                chat_input.focus_set()
            popup.after(0, apply_update)

    def send_chat_message(self, adapter, msg, textbox, popup, chat_input, send_btn):
        try:
            response_text = adapter.send_message(msg)
        except Exception as e:
            response_text = f"Error: {str(e)}"
            
        if popup.winfo_exists():
            def apply_update():
                textbox.configure(state="normal")
                current_text = textbox.get("1.0", "end-1c")
                if current_text.endswith("Thinking..."):
                    textbox.delete("end-12c", "end")
                textbox.insert("end", f"\n{self.config.get('provider').capitalize()}: {response_text}")
                textbox.see("end")
                textbox.configure(state="disabled")
                chat_input.configure(state="normal")
                send_btn.configure(state="normal")
                chat_input.focus_set()
            popup.after(0, apply_update)

if __name__ == "__main__":
    # Prevent print() crash in windowed mode by redirecting stdout/stderr
    try:
        devnull = open(os.devnull, "w", encoding="utf-8")
        sys.stdout = devnull
        sys.stderr = devnull
    except Exception:
        pass

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

