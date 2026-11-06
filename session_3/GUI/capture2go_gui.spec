# capture2go_gui.spec
# PyInstaller spec file – generates a single-file executable for Windows/macOS/Linux.
# Run with:  pyinstaller capture2go_gui.spec
#
# Windows: dist/capture2go_gui.exe
# macOS  : dist/capture2go_gui.app  (run with --windowed on macOS)
# Linux  : dist/capture2go_gui        (ELF binary)

import sys
from pathlib import Path

# ── Locate the capture2go package so PyInstaller can bundle it ────────────────
import capture2go as _c2g_module
C2G_PATH = str(Path(_c2g_module.__file__).parent)

block_cipher = None

a = Analysis(
    ['session_3/capture2go_gui.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        # Bundle the entire capture2go package (SDK + examples)
        (C2G_PATH, 'capture2go'),
    ],
    hiddenimports=[
        'capture2go',
        'capture2go.pkg',
        'capture2go.utils',
        'capture2go.ble',
        'capture2go.usb',
        'capture2go.device',
        'capture2go.parsing',
        'bleak',
        'bleak.backends',
        'bleak.backends.bluezdbus',    # Linux BLE
        'bleak.backends.corebluetooth', # macOS BLE
        'bleak.backends.winrt',         # Windows BLE
        'asyncio',
        'queue',
        'threading',
        'numpy',
        'matplotlib',
        'matplotlib.backends.backend_tkagg',
        'matplotlib.animation',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ── Single-file executable (--onefile equivalent) ─────────────────────────────
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='capture2go_gui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # no terminal window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# ── macOS .app bundle ─────────────────────────────────────────────────────────
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='capture2go_gui.app',
        icon=None,          # add an .icns file path here if you have an icon
        bundle_identifier='com.sensostim.capture2go.gui',
        info_plist={
            'NSHighResolutionCapable': True,
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleName': 'Capture2Go GUI',
        },
    )

