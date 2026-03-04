# FEAT-004: Multi-LLM Provider Support {#root}

## 1. Goal {#llm.goal}
The application must support multiple LLM Providers (e.g., Google Gemini, OpenAI ChatGPT, Anthropic Claude, DeepSeek) so users are not locked into one service. The default should remain Gemini, but users can provide their own API keys for others.

## 2. Abstraction Layer {#llm.adapter}
- Introduce a unified chat interface in `app.py`.
- Instead of calling `genai.GenerativeModel` directly in the UI logic, the UI should call a wrapper like `LLMProvider.chat(prompt, history)`.
- Support `google-generativeai` and `openai` (which also supports many OpenAI-compatible endpoints) libraries.

## 3. Settings UI {#llm.ui}
- When the user right-clicks the system tray icon, they select "Settings".
- A `customtkinter` Settings Window opens.
- **Provider Dropdown**: Select between Gemini, OpenAI, Anthropic, DeepSeek, Custom.
- **Dynamic API Key Input**: A single password-masked entry field that dynamically updates its value and label based on the selected LLM Provider.
- **Model Input**: String field for the specific model ID (e.g., `gemini-2.5-flash`, `gpt-4o`).
- **Output Language**: Dropdown field allowing the user to select the default reply language (English, Russian, Ukrainian, Spanish, French, German).
- The settings are saved to the `config.json` file.
- **Environment Fallback**: If an API key is missing from `config.json`, the application will seamlessly attempt to load it from a local `.env` file via `python-dotenv`.
