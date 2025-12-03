# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['desktop/desktop_app.py'],
    pathex=['src'],
    binaries=[],
    datas=[('src/app/templates', 'app/templates'), ('src/app/static', 'app/static'), ('src/app/tolerance-fir-verifier.icns', 'app'), ('src/app/tolerance-fir-verifier.png', 'app')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ToleranceFitVerifier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src/app/tolerance-fir-verifier.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ToleranceFitVerifier',
)
app = BUNDLE(
    coll,
    name='ToleranceFitVerifier.app',
    icon='src/app/tolerance-fir-verifier.icns',
    bundle_identifier=None,
)
