# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Recolectar datos y módulos adicionales necesarios
numpy_data = collect_data_files('numpy')
scipy_data = collect_data_files('scipy')
matplotlib_data = collect_data_files('matplotlib')
statsmodels_data = collect_data_files('statsmodels')
pandas_data = collect_data_files('pandas')
pil_data = collect_data_files('PIL')

# Recolectar submódulos necesarios
statsmodels_submodules = collect_submodules('statsmodels')
pandas_submodules = collect_submodules('pandas')
matplotlib_submodules = collect_submodules('matplotlib')
pil_submodules = collect_submodules('PIL')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.ico', '.'),
        *numpy_data,
        *scipy_data,
        *matplotlib_data,
        *statsmodels_data,
        *pandas_data,
        *pil_data
    ],
    hiddenimports=[
        'numpy',
        'scipy',
        'scipy.signal',
        'scipy.fft',
        'scipy.fftpack',
        'matplotlib',
        'soundfile',
        'matchering',
        'librosa.util',
        'librosa.feature',
        'tkinter',
        'tkinter.ttk',
        'tkinter.scrolledtext',
        'pandas',
        'statsmodels',
        'PIL',
        'PIL._tkinter_finder',
        *statsmodels_submodules,
        *pandas_submodules,
        *matplotlib_submodules,
        *pil_submodules
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'PyQt5', 'PyQt6', 'PySide6', 'PySide2',  # GUIs no usadas
        'IPython', 'jupyter', 'notebook',  # Entornos interactivos
        'opencv', 'cv2',  # No usamos visión por computadora
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Master-W',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch='x64',
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    version='file_version_info.txt'
)