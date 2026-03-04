# FEAT-002: System Tray & Packaging {#root}

## 1. System Tray Icon {#tray.icon}
- Integrate the `pystray` library into `app.py`.
- When the app is launched, it should not show a terminal window. Instead, it places an icon in the System Tray.
- Right-clicking the icon provides options: "Settings" (future feature) and "Quit".
- "Quit" safely destroys the application and unregisters the global hotkey.

## 2. Packaging (PyInstaller) {#tray.packager}
- Use `PyInstaller` to bundle the app into a distributable package.
- Special care must be taken to include the `customtkinter` assets (themes) using `collect_all` in the PyInstaller spec.
- The resulting build is created in a `dist/` directory inside the project folder.
- **Cross-platform**: The `app.spec` uses forward slashes for paths to work on both Windows and macOS.

## 3. CI/CD (GitHub Actions) {#tray.cicd}
- A GitHub Actions workflow (`.github/workflows/build.yml`) automatically builds the app on every push to `main`.
- Two parallel jobs run: `build-windows` (on `windows-latest`) and `build-macos` (on `macos-latest`).
- Build artifacts (ZIP files) are uploaded and downloadable from the GitHub Actions Artifacts tab.

## 4. Environment Variables Strategy {#tray.env}
- Since the public won't have the user's `.env` file, the app must gracefully handle the absence of API keys.
- If the key is missing on execution, the app shows a Settings window prompting the user to paste their API key.
- This key is saved to a `config.json` file next to the executable.

## 5. Single-Instance & Stability {#tray.stability}
- To prevent ghost icons and execution of multiple system tray instances, the app binds a local TCP socket (`47200`) upon launch. If the port is occupied, the app sends a "SHOW_SETTINGS" message to the running instance via the socket and exits instantly.
- When compiled via PyInstaller with `--windowed`, all standard output (`sys.stdout` and `sys.stderr`) are redirected to `os.devnull` to prevent silent crashes.
- The tray icon supports a default action (left-click) to toggle the Settings window.

## 6. Cross-Platform Hotkey {#tray.hotkey}
- The global hotkey system uses `pynput` (replaces the Windows-only `keyboard` library).
- `pynput.keyboard.GlobalHotKeys` works on both Windows and macOS without requiring root/sudo.
- The clipboard copy simulation is platform-aware: `Ctrl+C` on Windows, `Cmd+C` on macOS.
