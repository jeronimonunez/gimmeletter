# GimmeLetter - Guía de Instalación

## 📦 Archivos de Instalación Generados

Tu aplicación GimmeLetter ha sido empaquetada exitosamente para macOS:

- **GimmeLetter-1.0.0.dmg** (31 MB) - Instalador DMG listo para distribución
- **dist/GimmeLetter.app** - Aplicación standalone

## 🚀 Instalación para Usuarios

### Opción 1: Desde el DMG (Recomendado)
1. Abre el archivo `GimmeLetter-1.0.0.dmg`
2. Arrastra GimmeLetter.app a la carpeta Aplicaciones
3. Listo! Abre GimmeLetter desde Launchpad o Finder

### Opción 2: Directamente
1. Copia `dist/GimmeLetter.app` donde quieras
2. Haz doble click para abrir

## ⚠️ Nota de Seguridad de macOS

Al abrir por primera vez, macOS puede mostrar una advertencia porque la app no está firmada con un certificado de desarrollador de Apple.

**Para abrir la app:**
1. Click derecho en GimmeLetter.app
2. Selecciona "Abrir"
3. Click en "Abrir" en el diálogo de confirmación

O alternativamente:
1. Ve a Preferencias del Sistema > Seguridad y Prividad
2. En la pestaña "General", click en "Abrir de todos modos"

## 📁 Ubicación de la Base de Datos

La base de datos de canciones y sets se guarda en:
```
/Users/[tu_usuario]/gimmeletter.db
```

## 🔄 Actualizar la Aplicación

Para generar una nueva versión:

```bash
cd /Users/jeronimonunez/projects/gimmeletter

# 1. Actualizar tu código fuente
# 2. Limpiar builds anteriores
rm -rf build dist *.dmg

# 3. Reconstruir
.venv/bin/pyinstaller gimmeletter.spec

# 4. Crear nuevo DMG
./create_dmg.sh
```

## 🎨 Personalizar el Icono (Opcional)

Para agregar un icono personalizado:

1. Crea o consigue un archivo `.icns` de 512x512 px
2. Edita `gimmeletter.spec` y actualiza:
   ```python
   icon='path/to/icon.icns'
   ```
3. Reconstruye la app

## 📝 Firmar la App (Para Distribución Pública)

Si quieres distribuir la app sin advertencias de seguridad:

1. Inscríbete en el Apple Developer Program ($99/año)
2. Obtén un certificado de firma de código
3. Firma la app:
   ```bash
   codesign --deep --force --verify --verbose --sign "Developer ID Application: Tu Nombre" dist/GimmeLetter.app
   ```
4. Notariza la app (para macOS 10.15+):
   ```bash
   xcrun altool --notarize-app --file GimmeLetter-1.0.0.dmg --primary-bundle-id com.gimmeletter.app
   ```

## 🔧 Solución de Problemas

**La app no abre:**
- Revisa los permisos de seguridad en Preferencias del Sistema
- Verifica que Python 3.10+ esté instalado en el sistema

**Error de base de datos:**
- Asegúrate de tener permisos de escritura en tu directorio home
- La base de datos se creará automáticamente la primera vez

**La app es muy grande:**
- PyInstaller incluye todo Python y PyQt6 (~31 MB es normal)
- Puedes usar UPX para comprimir (agrega `upx=True` en el .spec)

## 📮 Distribución

Para distribuir la app:

1. **DMG**: Comparte el archivo `GimmeLetter-1.0.0.dmg`
2. **GitHub Releases**: Sube el DMG a una release en tu repositorio
3. **Web**: Hospeda el DMG en tu sitio web

## 🎵 Uso de la Aplicación

Una vez instalada:

1. **Agregar canciones**: Click en "Nueva Canción", pega letras con acordes
2. **Crear sets**: Organiza canciones en sets para tus conciertos
3. **Reproducir**: Usa el auto-scroll con velocidad ajustable
4. **Transponer**: Cambia tonalidad automáticamente

¡Disfruta de GimmeLetter! 🎸
