## Current Phase
Project Complete

## Completed
- PROP-000: Base Project Setup, Virtual Env, Dependencies. (Rebranded to explainme.wtf)
- PROP-001: Core App Flow (Clipboard ingestion, LLM API call, Window Popups).
- FEAT-001: Interactive Follow-up Chat functionality.
- FEAT-004: Multi-LLM System (Abstracted into `llm_adapter.py` supporting Gemini, OpenAI, and Anthropic).
- FEAT-002: System Tray & Packaging (Added `pystray` icon with internal settings popup, compiled `.exe` with PyInstaller to `dist/`).
- FEAT-003: Public Landing Page (Created `/landing_page` directory with `index.html` and `index.css`).
- BUGFIX: Enforced single-instance architecture using local TCP socket binding. Second instances now trigger the first instance to show its Settings window.
- BUGFIX: Prevented `--windowed` PyInstaller crashes by redirecting `sys.stdout` and `sys.stderr` to `os.devnull`.
- BUGFIX: Fixed window `topmost` locking issue.
- UX: System tray icon left-click now toggles the Settings window.
- UX: Settings window opens automatically on the first application run.
- UX: Simplified Settings window to only display a single, dynamically updating API Key field based on the selected LLM provider.
- FEAT-004: Multi-Language Output (Added dropdown to Settings UI allowing the user to select their preferred response language).
- FEAT-004: DeepSeek Support (Integrated DeepSeek chat API as a supported provider).
- BUGFIX: Added dynamic Model ID switching to the Settings UI so the field auto-populates correctly (e.g., `deepseek-chat`) when changing providers.
- FEAT-004: Environment Fallback (Added `python-dotenv` support to load missing API keys from a local `.env` file).
- CROSS-PLATFORM: Replaced `keyboard` library with `pynput` for macOS compatibility (no root required).
- CI/CD: Added GitHub Actions workflow (`.github/workflows/build.yml`) for automated Windows + macOS builds.
- DOCS: Created `README.md` with download, setup, and developer instructions.
- REPO: Published to GitHub at `github.com/jimmywussup/explainme.wtf`. Cleaned repo to only include essential build files (`src/`, `.github/`, `app.spec`, `requirements.txt`, `README.md`).

## In Progress
None. Core requirements are satisfied.

## Known Issues
None.

## Decisions Pending
None. All builds are automated via GitHub Actions.

## Session Context
Project is live on GitHub. Automated CI/CD builds for Windows and macOS.
Next: Distribution via GitHub Releases or landing page download links.
