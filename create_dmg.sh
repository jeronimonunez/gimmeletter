#!/bin/bash
# Script para crear un DMG instalable para macOS

APP_NAME="GimmeLetter"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"

# Limpiar DMG anterior si existe
rm -f "${DMG_NAME}"

# Crear DMG
hdiutil create -volname "${APP_NAME}" -srcfolder dist/${APP_NAME}.app -ov -format UDZO "${DMG_NAME}"

echo "✅ DMG creado: ${DMG_NAME}"
