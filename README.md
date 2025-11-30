# Tolerance Fit Verifier

Web app + desktop wrapper for ISO 286 fits (range 20–50 mm). Desktop window defaults to 1043x777.

## Features
- Fit type: clearance, transition, or interference.
- System: hole basis vs shaft basis.
- Preferred fit check and suggestions.

## Run (web, dev)
1) Set `PYTHONPATH=src`  
   - PowerShell: `$env:PYTHONPATH="src"`  
   - bash/zsh: `export PYTHONPATH=src`
2) Install deps:
   ```bash
   python -m pip install -r requirements.txt
   ```
3) Start server:
   ```bash
   python -m app.web
   ```
4) Open `http://127.0.0.1:5000`.

### Linux (web only)
- Dev server:
   ```bash
   ./scripts/run-web.sh
   ```
- Production (Waitress):
   ```bash
   ./scripts/run-web.sh prod
   ```
- Customize host/port via env vars:
   ```bash
   HOST=0.0.0.0 PORT=8000 ./scripts/run-web.sh prod
   ```

## Run (desktop, dev)
```bash
set PYTHONPATH=src   # PowerShell: $env:PYTHONPATH="src"
python desktop/desktop_app.py
```

## Build executable

Note: On Linux, prefer running as a web app (see above). Desktop packaging is only supported for Windows and macOS.

### Windows (Python 3.12)
```bash
py -3.12 -m venv .venv312
.venv312\Scripts\python -m pip install --upgrade pip
.venv312\Scripts\python -m pip install -r requirements.txt
.venv312\Scripts\python -m pip install pyinstaller
.venv312\Scripts\python -m PyInstaller --noconsole --onefile --paths src ^
  --add-data "src\\app\\templates;app/templates" ^
  --add-data "src\\app\\static;app/static" ^
  desktop/desktop_app.py
```

### macOS
```bash
# setup
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller pyobjc

# build via spec (preferred)
pyinstaller --clean --noconfirm desktop/desktop_app.spec

# or build via CLI flags
pyinstaller --clean --windowed --paths src \
   --add-data "src/app/templates:app/templates" \
   --add-data "src/app/static:app/static" \
   --name "ToleranceFitVerifier" \
   desktop/desktop_app.py

# run
open dist/ToleranceFitVerifier.app

# troubleshoot: see logs if it closes
cd dist/ToleranceFitVerifier.app/Contents/MacOS && ./ToleranceFitVerifier
```

Optional DMG:
```bash
hdiutil create -volname "Tolerance Fit Verifier" \
   -srcfolder "dist/ToleranceFitVerifier.app" \
   -ov -format UDZO "ToleranceFitVerifier.dmg"
```

## Project structure
- `src/app/web.py`: Flask server + routes.
- `src/app/logic.py`: tolerance calculations.
- `src/app/templates/`: UI.
- `src/app/static/`: CSS/assets.
- `desktop/desktop_app.py`: desktop launcher (pywebview + Waitress).
- `requirements.txt`: dependencies.
