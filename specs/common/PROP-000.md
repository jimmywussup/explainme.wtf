# PROP-000: Foundational Decisions {#root}

## 1. Stack {#stack}
- Language: Python 3
- UI: `customtkinter`
- Hotkeys: `keyboard` package
- Clipboard tracking: `pyperclip`
- LLM Integration: `google-generativeai`, `openai`, `anthropic` (Unified adapter layer)

## 2. Architecture {#architecture}
A background process (`explainme.wtf`) listens for a globally registered shortcut. Upon trigger, it captures highlighted text (via Ctrl+C injection), queries the selected LLM provider, and spawns a customtkinter popup with the response.

## 3. Style and Conventions {#style}
- Use atomic development linked to spec URIs.
- Strict adherence to SPEC-PROTOCOL.md and WAL-PROTOCOL.md.
