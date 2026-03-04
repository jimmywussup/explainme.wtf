# FEAT-001: Interactive Chat Mode {#root}

## 1. UI Updates {#chat.ui}
- Expand `PROP-001#ui.popup` to include an input text field (`ctk.CTkEntry`) at the bottom of the popup.
- Add a "Send" button (`ctk.CTkButton`) next to the input field.
- The user can press `Enter` to submit their chat message.

## 2. Conversation State {#chat.state}
- Instead of using `model.generate_content()`, the app must initialize a `chat` session (`model.start_chat(history=[])`) when the popup opens.
- The initial message from the app will still be the hidden prompt asking to explain the copied text. The response will be displayed in the textbox.
- The popup needs to hold this `chat` object in memory as long as the window is open.

## 3. Handling Follow-ups {#chat.flow}
- When the user types a message and hits Send:
    1. Append the user's message to the `textbox` UI ("User: [message]").
    2. Disable the input field.
    3. Send the message via `chat.send_message(user_message)` in a background thread to prevent UI freezing.
    4. Append the response to the `textbox` ("Gemini: [response]").
    5. Re-enable the input field.

## 4. Window Dismissal {#chat.cleanup}
- The standard `Esc` to close behavior must remain intact.
- Upon closing, the `chat` object should be garbage collected/discarded so a fresh chat starts on the next hotkey trigger.
