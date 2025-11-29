#!/usr/bin/env zsh
set -euo pipefail

# Build macOS .app for Tolerance Fit Verifier
# - Creates venv if missing
# - Installs deps (including pyobjc)
# - Runs PyInstaller using spec or CLI flags

ROOT_DIR=${0:a:h}/..
cd "$ROOT_DIR"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller pyobjc

# Prefer spec to keep config centralized
if [[ -f desktop/desktop_app.spec ]]; then
  pyinstaller --clean --noconfirm desktop/desktop_app.spec
else
  pyinstaller --clean --noconfirm --windowed \
    --paths src \
    --add-data "src/app/templates:app/templates" \
    --add-data "src/app/static:app/static" \
    --name "ToleranceFitVerifier" \
    desktop/desktop_app.py
fi

echo "Build complete: dist/ToleranceFitVerifier.app"
