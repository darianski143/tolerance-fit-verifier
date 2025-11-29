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

## Run (desktop, dev)
```bash
set PYTHONPATH=src   # PowerShell: $env:PYTHONPATH="src"
python desktop/desktop_app.py
```

## Build executable

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

### macOS / Linux
```bash
export PYTHONPATH=src
python -m pip install -r requirements.txt
python -m pip install pyinstaller
python -m PyInstaller --noconsole --onefile --paths src \
  --add-data "src/app/templates:app/templates" \
  --add-data "src/app/static:app/static" \
  desktop/desktop_app.py
```

## Project structure
- `src/app/web.py`: Flask server + routes.
- `src/app/logic.py`: tolerance calculations.
- `src/app/templates/`: UI.
- `src/app/static/`: CSS/assets.
- `desktop/desktop_app.py`: desktop launcher (pywebview + Waitress).
- `requirements.txt`: dependencies.
