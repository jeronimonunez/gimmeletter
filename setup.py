"""
Setup script para crear aplicación macOS con py2app
Uso: python setup.py py2app
"""

from setuptools import setup

APP = ['src/main.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'packages': ['PyQt6', 'sqlite3'],
    'excludes': ['tkinter'],
    'iconfile': None,  # Puedes agregar un icono .icns aquí
    'plist': {
        'CFBundleName': 'GimmeLetter',
        'CFBundleDisplayName': 'GimmeLetter',
        'CFBundleIdentifier': 'com.gimmeletter.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2026',
        'NSHighResolutionCapable': True,
    }
}

setup(
    name='GimmeLetter',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
