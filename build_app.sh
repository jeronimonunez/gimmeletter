#!/bin/bash
# Script de construcción para GimmeLetter
# Uso: ./build_app.sh [version]

VERSION="${1:-1.0.0}"
APP_NAME="GimmeLetter"

echo "🏗️  Construyendo ${APP_NAME} v${VERSION}..."
echo ""

# Verificar que estamos en el entorno virtual
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Activando entorno virtual..."
    source .venv/bin/activate
fi

# Limpiar builds anteriores
echo "🧹 Limpiando builds anteriores..."
rm -rf build dist *.dmg

# Construir con PyInstaller
echo "📦 Construyendo aplicación con PyInstaller..."
.venv/bin/pyinstaller gimmeletter.spec

if [ $? -ne 0 ]; then
    echo "❌ Error al construir la aplicación"
    exit 1
fi

# Probar que la app se abre
echo "🧪 Probando la aplicación..."
open dist/${APP_NAME}.app
sleep 3

# Preguntar si continuar con el DMG
echo ""
read -p "¿La aplicación se abre correctamente? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "⚠️  Construcción cancelada. Revisa los errores."
    exit 1
fi

# Actualizar versión en el script DMG si se proporcionó
if [ ! -z "$1" ]; then
    sed -i '' "s/VERSION=.*/VERSION=\"${VERSION}\"/" create_dmg.sh
fi

# Crear DMG
echo "💿 Creando DMG..."
./create_dmg.sh

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ¡Construcción completada!"
    echo ""
    echo "📦 Archivos generados:"
    ls -lh ${APP_NAME}-*.dmg
    echo ""
    echo "📁 Aplicación standalone:"
    echo "   dist/${APP_NAME}.app"
    echo ""
    echo "🎉 Listo para distribuir!"
else
    echo "❌ Error al crear DMG"
    exit 1
fi
