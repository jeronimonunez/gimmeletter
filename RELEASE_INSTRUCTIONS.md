# Instrucciones para Publicar el Release

El tag v1.0.0 ha sido creado y subido a GitHub. Ahora necesitas crear el Release manualmente:

## Pasos:

1. **Ve a GitHub Releases:**
   https://github.com/jeronimonunez/gimmeletter/releases

2. **Haz clic en "Draft a new release"**

3. **Configura el release:**
   - Tag: `v1.0.0` (ya existe, selecciónalo del dropdown)
   - Release title: `GimmeLetter 1.0.0`
   - Description:
     ```
     ## 🎸 GimmeLetter v1.0.0 - Initial Release
     
     Primera versión oficial de GimmeLetter, tu compañero perfecto para tocar en vivo.
     
     ### ✨ Características
     
     - 🎨 **Nuevo**: Icono personalizado de la aplicación
     - ⚙️ **Nuevo**: Configuración de colores del reproductor (fondo y texto)
     - ⚡ Scroll automático con control de velocidad (5-200 px/s)
     - 🎵 Transposición inteligente de acordes
     - 📋 Gestión de sets para presentaciones en vivo
     - ⌨️ Atajos de teclado completos
     - 💾 Import/Export de canciones y sets
     - 🌓 Tema oscuro y claro
     - ⛶ Modo pantalla completa
     - 🔍 Búsqueda rápida de canciones
     
     ### 📦 Instalación
     
     1. Descarga el archivo `GimmeLetter-1.0.0.dmg`
     2. Abre el DMG
     3. Arrastra GimmeLetter a la carpeta Aplicaciones
     4. Al abrir por primera vez: clic derecho → "Abrir" (la app no está firmada)
     5. Acepta el aviso de seguridad de macOS
     
     ### ⚠️ Requisitos
     
     - macOS 10.15 o superior
     - ~31 MB de espacio en disco
     
     ### 🐛 Reportar Issues
     
     Si encuentras algún problema, por favor [abre un issue](https://github.com/jeronimonunez/gimmeletter/issues/new).
     ```

4. **Sube el archivo DMG:**
   - Arrastra o selecciona el archivo: `GimmeLetter-1.0.0.dmg` (ubicado en la raíz del proyecto)

5. **Publica el release:**
   - Marca la casilla "Set as the latest release"
   - Haz clic en "Publish release"

## Resultado:

El DMG estará disponible en:
`https://github.com/jeronimonunez/gimmeletter/releases/latest/download/GimmeLetter-1.0.0.dmg`

Este es el link que ya está configurado en el sitio web (`docs/index.html`).

---

**El sitio web está listo para usarse:**
- Está en `docs/index.html`
- GitHub Pages ya debería estar sirviendo el sitio
- El link de descarga apunta al release que acabas de crear
