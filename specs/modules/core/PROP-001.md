# PROP-001: Core Application Flow {#root}

## 1. Hotkey Trigger {#hotkey.trigger}
- The application listens for a global hotkey: `ctrl+```.
- When pressed, it immediately stops listening to prevent duplicate triggers.
- It simulates the `ctrl+c` keypress to copy whatever text the user has highlighted.

## 2. Clipboard Management {#clipboard.read}
- Wait `0.1` seconds to ensure the clipboard has updated.
- Read the text from the clipboard using `pyperclip`.
- If the clipboard text is empty or unchanged from a previous read, abort the operation.

## 3. LLM Processing {#llm.prompt}
- Initialize the Google Generative AI client (`gemini-2.5-flash`) using the `GEMINI_API_KEY` from the `.env` file.
- Prompt: "You are a helpful dictionary and context explainer. Briefly explain the meaning of the following text in plain, easy-to-understand language. Keep it very concise (1-2 short paragraphs max). Text: [COPIED_TEXT]"
- **CRITICAL**: This is a blocking process, so we must show a "Loading..." state before it returns.

## 4. UI Popup {#ui.popup}
- Use `customtkinter` to create a modern, dark-themed frameless popup (or a simple centered popup).
- The window should appear in the center of the screen and float **always on top**.
- State 1: Displays "Thinking..." while waiting for the Gemini API.
- State 2: Displays the formatted response from Gemini, wrapped text to prevent horizontal scrolling.
- Includes a button or listens to `Esc` to aggressively destroy/close the popup window.

## 5. Background Loop {#app.loop}
- After the UI is closed, re-register the `ctrl+~` hotkey and go back to a sleep/wait state.
