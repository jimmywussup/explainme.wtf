# explainme.wtf

> **Understand anything, anywhere, anytime, instantly.** \
> Eliminate the friction of switching tabs. Highlight text or copy an image anywhere on your PC, press your hotkey, and get an instant AI explanation powered by Gemini, OpenAI, Claude, or DeepSeek.

## ✨ How It Works

1. **Highlight or Copy** — Select confusing text or copy an image (Print Screen) in any app, browser, or game.
2. **Hit the Hotkey** — Press `Ctrl + \`` (customizable).
3. **Understand Instantly** — A sleek, native popup appears over your window containing an immediate, context-aware explanation.

## 🚀 Core Mechanics

- **Instant Context (Multi-modal)**: Automatically grabs your clipboard text or image to provide immediate answers.
- **Interactive Flow**: Don't just get a dictionary definition. Ask follow-up questions in the built-in chat window to fully grasp complex subjects.
- **Advanced Intelligence on Demand (AI Router)**: Need deep reasoning? Switch seamlessly from the **Fast** model to the **Thinking** model directly within the chat for complex logical or mathematical breakdowns.
- **General Assistant Mode**: Press the hotkey with an empty clipboard to open a clean chat and use the app as a standard, lightning-fast AI assistant.
- **Google Search Grounding**: When using Gemini as your provider, the Thinking model has access to real-time Google Search to verify facts and provide up-to-date links.

## 📥 Download & Setup

Download the latest build from the [GitHub Releases](https://github.com/jimmywussup/explainme.wtf/releases/latest) section (or check the CI/CD [Artifacts](../../actions)):

| Platform | Download |
|----------|----------|
| Windows  | `explainme.wtf-Windows.zip` |

### Installation (No Install Required!)
1. Extract the ZIP file.
2. Double-click `explainme.wtf.exe`.
3. The **Settings** window will appear simply asking for your Provider and API Key.

## 🔑 Your Keys, Your AI

You are not locked into a subscription. Bring your own API key. 
We natively support **Google Gemini** (recommended for free-tier users), **OpenAI**, **Anthropic Claude**, and **DeepSeek**. 

You can configure your keys directly in the Settings window, or create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## 🛠️ Developer Setup & Build

Want to build it yourself? It's 100% open source.

```bash
# Clone the repo
git clone https://github.com/jimmywussup/explainme.wtf.git
cd explainme.wtf

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app directly
python src/app.py

# Or build the executable locally
pip install pyinstaller
python -m PyInstaller app.spec --clean
```
The built application will appear in the `dist/` folder.
