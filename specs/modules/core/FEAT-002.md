# FEAT-002: System Tray & Packaging {#root}

## 1. System Tray Icon {#tray.icon}
- Integrate the `pystray` library into `app.py`.
- When the app is launched, it should not show a terminal window. Instead, it places an icon in the Windows System Tray (bottom right corner).
- Right-clicking the icon provides options: "Settings" (future feature) and "Quit".
- "Quit" safely destroys the application and unregisters the `ctrl+``` hotkey.

## 2. Packaging (PyInstaller) {#tray.packager}
- Use `PyInstaller` to bundle the app into a single `.exe` file.
- The command should include `--noconsole` and `--onefile`.
- Special care must be taken to include the `customtkinter` assets (themes) using `--add-data` in the PyInstaller spec.
- The resulting `.exe` should be created in a `dist/` directory inside the project folder.

## 3. Environment Variables Strategy {#tray.env}
- Since the public won't have the user's `.env` file, the `.exe` must gracefully handle the absence of `GEMINI_API_KEY`.
- If the key is missing on execution, the app should use `customtkinter` to show a one-time "Setup" window prompting the user to paste their API key.
- This key should be saved to an `.env` file next to the `.exe` (or in `%APPDATA%`).

## 4. Single-Instance & Stability {#tray.stability}
- To prevent ghost icons and execution of multiple system tray instances, the app binds a local TCP socket (`47200`) upon launch. If the port is occupied, the app sends a "SHOW_SETTINGS" message to the running instance via the socket and exits instantly, allowing the user to seamlessly open the existing app.
- When compiled via PyInstaller with `--windowed`, Python background apps do not have a console to print to. Therefore, all standard output (`sys.stdout` and `sys.stderr`) MUST be redirected to `os.devnull` to prevent instant, silent crashes without littering the user's filesystem with log files.
- The tray icon should support a default action (left-click) to easily toggle the Settings window open and closed.
