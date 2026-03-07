# explainme.wtf

> **Understand anything instantly.** Highlight text or copy an image anywhere on your PC, press a hotkey, and get a concise AI explanation.

## ✨ Features

- ⚡ **Lightning Fast** — Get answers natively over your current window without opening a browser tab
- 🖼️ **Image Understanding** — Copy any image to your clipboard to instantly analyze it with vision-enabled LLMs
- 🧠 **Multi-LLM Support** — Bring your own API key for Gemini, OpenAI, Claude, or DeepSeek
- 💬 **Contextual Chat** — Ask follow-up questions in the built-in chat window
- 🌍 **Multi-Language** — Get explanations in English, Russian, Ukrainian, Spanish, French, or German
- 🪶 **Lightweight** — Runs quietly in the background (System Tray on Windows/Linux, Dock on macOS)

## 📥 Download

Download the latest build from the [GitHub Actions](../../actions) **Artifacts** section:

| Platform | File |
|----------|------|
| Windows  | `explainme.wtf-Windows.zip` |
| macOS    | `explainme.wtf-macOS.zip` |

### Windows
1. Download and extract the ZIP
2. Double-click `explainme.wtf.exe`
3. Enter your API key in the Settings window (auto-opens on first run)

### macOS
1. Download and extract the ZIP
2. Move the `explainme` app to your Applications folder
3. **First launch:** Right-click the app and select **Open** (this bypasses the Apple security warning)
4. **Grant Accessibility**: Go to **System Settings → Privacy & Security → Accessibility** and enable the app (required for the global hotkey to work)
5. Enter your API key in the main Settings window
   - Note: The app stays alive in your Dock. If you close the settings window, simply click the app icon in your Dock to reopen it!

## 🛠️ Run from Source

```bash
# Clone the repo
git clone https://github.com/jimmywussup/explainme.wtf.git
cd explainme.wtf

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python src/app.py
```

## 🔑 API Keys

You can configure API keys in two ways:
1. **Settings Window** — Enter your key directly in the app's Settings
2. **`.env` file** — Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_key_here
   DEEPSEEK_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   ```

## 📦 Build Locally

```bash
pip install pyinstaller
python -m PyInstaller app.spec --clean
```

The built application will be in the `dist/explainme.wtf/` folder.
