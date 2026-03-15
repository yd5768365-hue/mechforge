# MechForge AI Desktop Application Specification

## Overview

This document describes the desktop application packaging configuration for MechForge AI GUI.

## Packaging Solution

**Solution**: PyWebView + PyInstaller

- **PyWebView**: Provides native webview window for displaying the GUI
- **PyInstaller**: Bundles Python runtime and dependencies into a standalone .exe

## Project Structure

```
gui/
├── desktop_app.py      # Desktop application entry point
├── build.py            # Build/packaging script
├── requirements-desktop.txt  # Python dependencies
├── SPEC.md             # This file
├── run_gui.py          # Original HTTP server (reused)
├── index.html          # GUI frontend
├── styles.css
├── app.js
├── core/
│   ├── event-bus.js
│   └── api-client.js
└── services/
    ├── ai-service.js
    └── config-service.js
```

## Build Instructions

### Prerequisites

```bash
# Install dependencies
pip install -r requirements-desktop.txt

# Verify pywebview works
python -c "import webview; print('OK')"
```

### Development Mode

```bash
# Run desktop app in development mode
python desktop_app.py
```

### Production Build

```bash
# Build standalone .exe
python build.py

# Or with output directory
python build.py -o output
```

### Clean Build

```bash
# Remove build artifacts
python build.py --clean
```

## Output

The build produces:
- `dist/MechForgeAI.exe` - Standalone executable

## Configuration

### Window Settings (desktop_app.py)

| Parameter | Value | Description |
|-----------|-------|-------------|
| width | 1200 | Window width |
| height | 800 | Window height |
| min_width | 900 | Minimum width |
| min_height | 600 | Minimum height |
| resizable | True | Allow resize |
| fullscreen | False | Default to windowed mode |

### Server Settings

| Parameter | Value | Description |
|-----------|-------|-------------|
| host | 127.0.0.1 | Localhost only |
| port | 5000 | HTTP server port |

## Known Limitations

1. **Windows only**: PyWebView uses Edge WebView2 on Windows
2. **Network**: App requires WebView2 runtime (usually pre-installed on Windows 10/11)
3. **Offline**: The app will work offline after initial load

## Troubleshooting

### WebView2 not found

Download and install: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

### Build fails

1. Clean build: `python build.py --clean`
2. Reinstall dependencies: `pip install -r requirements-desktop.txt`
3. Check Python version: Python 3.8+

### App doesn't start

1. Run from command line to see errors
2. Check if port 5000 is available
3. Verify all GUI files are included

## Future Improvements

- [ ] Add system tray support
- [ ] Add window minimize to tray
- [ ] Add auto-update functionality
- [ ] Add custom window frame
- [ ] Add native file dialogs
