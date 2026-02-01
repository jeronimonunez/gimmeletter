# Copilot Instructions - GimmeLetter

## 📋 Descripción del Proyecto

**GimmeLetter** es una aplicación de escritorio para macOS que ayuda a músicos a gestionar canciones con letras y acordes, organizarlas en sets para conciertos, y reproducirlas con auto-scroll configurable.

### Características Principales
- ✅ Gestión de canciones con letras y acordes (entrada de texto manual)
- ✅ Transposición automática de acordes (notación latina y anglosajona)
- ✅ Creación y gestión de sets/setlists
- ✅ Reproductor con auto-scroll configurable (5-200 px/s)
- ✅ Preview de canciones con ajuste de velocidad
- ✅ Búsqueda y filtrado de canciones
- ✅ Temas claro/oscuro
- ✅ Interfaz intuitiva con PyQt6

---

## 🛠️ Stack Tecnológico

### Core
- **Python**: 3.10.4
- **PyQt6**: 6.6.1 - Framework GUI
- **SQLite**: Base de datos local
- **Virtual Environment**: `.venv/`

### Empaquetado
- **PyInstaller**: 6.18.0 - Creación de aplicación standalone
- **py2app**: 0.28.9 - Alternativa para macOS (tiene problemas de permisos)

### Herramientas de Desarrollo
- **Git**: Control de versiones (repo: github.com/jeronimonunez/gimmeletter)
- **VSCode**: Editor principal

---

## 📁 Estructura del Proyecto

```
gimmeletter/
├── src/
│   ├── main.py                    # Punto de entrada
│   ├── database/
│   │   ├── db_manager.py          # Gestión de base de datos
│   │   └── models.py              # Modelos Song, Set, SetSong
│   ├── ui/
│   │   ├── main_window.py         # Ventana principal con tabs
│   │   ├── song_editor.py         # Editor de canciones
│   │   ├── set_manager.py         # Gestor de sets
│   │   ├── player_window.py       # Reproductor con auto-scroll
│   │   └── song_preview.py        # Preview para probar velocidad
│   └── utils/
│       └── chord_transposer.py    # Lógica de transposición
├── gimmeletter.db                 # Base de datos SQLite (gitignored)
├── setup.py                       # Config py2app
├── gimmeletter.spec               # Config PyInstaller (USADO)
├── create_dmg.sh                  # Script para crear DMG
├── build_app.sh                   # Script todo-en-uno para build
├── README_INSTALADOR.md           # Guía de instalación
└── .gitignore
```

---

## 🗄️ Esquema de Base de Datos

### Tabla: songs
```sql
- id: INTEGER PRIMARY KEY
- title: TEXT NOT NULL
- artist: TEXT NOT NULL
- lyrics_with_chords: TEXT NOT NULL
- bpm: INTEGER
- original_key: TEXT
- default_scroll_speed: INTEGER DEFAULT 50
- created_date: TEXT
```

### Tabla: sets
```sql
- id: INTEGER PRIMARY KEY
- name: TEXT NOT NULL
- created_date: TEXT
```

### Tabla: set_songs (relación N:M)
```sql
- id: INTEGER PRIMARY KEY
- set_id: INTEGER (FK to sets)
- song_id: INTEGER (FK to songs)
- song_order: INTEGER
- scroll_speed: INTEGER
- transposition: INTEGER
```

**Acceso a datos**: Usar `row['column_name']` con `sqlite3.Row`

---

## 🎨 Arquitectura y Patrones

### Ventanas
- **MainWindow**: Tabs para Canciones y Sets
- **SongEditor**: Diálogo modal para crear/editar canciones
- **SetManager**: Diálogo para gestionar sets con drag-drop
- **PlayerWindow**: Ventana de reproducción con lista lateral
- **SongPreview**: Preview rápido para ajustar velocidad

### Auto-Scroll
- **Timer**: QTimer con intervalos de 50ms
- **Acumulador de flotante**: `self.scroll_accumulator` para precisión sub-píxel
- **Fórmula**: `delta = (speed_px_per_sec / 1000.0) * 50`
- **Rango**: 5-200 px/s

### Transposición de Acordes
- **Detección automática**: Regex con `\b` (word boundaries)
- **Patrones**:
  - Latin: `r'\b(Do|Re|Mi|Fa|Sol|La|Si)(#|b)?(m|M|maj|min|dim|aug|sus|add|\d)*\b'`
  - English: `r'\b[A-G](#|b)?(m|M|maj|min|dim|aug|sus|add|\d)*\b'`
- **Preservación de espaciado**: Usar `re.sub()` NO `split/join`
- **Validación**: 100% acordes O 70%+ con mínimo 2 acordes

---

## 🎯 Decisiones de Diseño Importantes

### 1. Entrada Manual de Texto
- NO importar archivos automáticamente
- Usuario pega letras con acordes en texto plano
- `QTextEdit.setAcceptRichText(False)` para evitar formato

### 2. Fuentes
- **Monaco/Courier**: Monoespaciada para alineación de acordes
- **Tamaños**:
  - Letras en reproductor: 22pt (ajustable 12-48pt)
  - Listas principales: 18pt
  - Lista del reproductor: 14pt
  - Búsqueda: 13pt

### 3. Tema
- Dark/Light toggle en menú Ver
- Colores ajustados para ambos modos

### 4. UX Enhancements
- **Tooltips**: Guiar al usuario en acciones no obvias
- **Search filters**: Filtrado en tiempo real
- **Context menus**: Click derecho para acciones rápidas
- **Hover buttons**: "⋯" button con QStyledItemDelegate
- **Padding**: 10px 8px en items de lista

---

## 🔧 Problemas Resueltos y Soluciones

### 1. Auto-Scroll Jerky
**Problema**: Scroll se veía entrecortado con valores bajos
**Solución**: Acumulador flotante para precisión sub-píxel
```python
self.scroll_accumulator = 0.0
delta = (self.current_speed / 1000.0) * 50
self.scroll_accumulator += delta
new_pos = current_pos + int(self.scroll_accumulator)
self.scroll_accumulator -= int(self.scroll_accumulator)
```

### 2. Transposición Rompiendo Espaciado
**Problema**: `split/join` destruía espacios en líneas de acordes
**Solución**: Usar `re.sub()` directamente
```python
def _transpose_line_preserve_spacing(line, semitones, use_latin):
    pattern = LATIN_PATTERN if use_latin else ENGLISH_PATTERN
    return re.sub(pattern, lambda m: transpose_chord(m.group(), semitones, use_latin), line)
```

### 3. Falsos Positivos en Detección de Acordes
**Problema**: "La" en "algunas" detectado como acorde La
**Solución**: Word boundaries `\b` en regex
```python
r'\b(Do|Re|Mi|Fa|Sol|La|Si)(#|b)?...\b'
```

### 4. UnboundLocalError en Auto-Scroll
**Problema**: `setValue()` fuera del if block en línea 309
**Solución**: Remover la línea duplicada

### 5. AttributeError con get_set()
**Problema**: Método no existía en db_manager
**Solución**: Implementar `get_set(set_id)` que retorna objeto Set

### 6. Hover Button No Interactivo
**Problema**: Button "⋯" sin cursor change ni click
**Solución**: 
- `QListWidget.setMouseTracking(True)`
- `viewport().setMouseTracking(True)`
- `QStyledItemDelegate` con `editorEvent()` para MouseMove y MouseButtonRelease
- `viewport().setCursor(Qt.CursorShape.PointingHandCursor)`

---

## 📝 Instrucciones para Copilot

### Al Editar Código
1. **Siempre** preservar espaciado y alineación en código de acordes
2. Usar `re.sub()` para manipular texto con acordes, NO `split/join`
3. Usar `row['column']` para acceder a sqlite3.Row, NO `.column`
4. Incluir 3-5 líneas de contexto en `replace_string_in_file`
5. NO crear archivos markdown de resumen sin que se solicite
6. Usar `multi_replace_string_in_file` para múltiples edits independientes

### Al Agregar Features
1. Seguir patrones existentes (diálogos modales, QLayouts)
2. Fonts monoespaciadas para texto con acordes
3. Agregar tooltips para guiar al usuario
4. Probar con `pkill -9 -f "python.*src.main" && .venv/bin/python -m src.main`
5. Actualizar este archivo si se cambian decisiones arquitectónicas

### Al Depurar
1. Revisar primero logs de terminal (Exit Code)
2. Verificar imports de PyQt6 (siempre desde PyQt6.QtWidgets, etc.)
3. Confirmar que métodos/atributos existen antes de llamarlos
4. Usar `hasattr()` para verificar propiedades opcionales

### Comandos Comunes
```bash
# Ejecutar app en desarrollo
.venv/bin/python -m src.main

# Reiniciar app
pkill -9 -f "python.*src.main" 2>/dev/null; sleep 2; .venv/bin/python -m src.main

# Construir instalador
./build_app.sh [version]

# Solo crear app (sin DMG)
.venv/bin/pyinstaller gimmeletter.spec

# Probar app construida
open dist/GimmeLetter.app
```

---

## 🚀 Features Pendientes (No Implementadas)

- [ ] Importar archivos de letras/acordes
- [ ] Exportar/importar setlists
- [ ] Icono personalizado (.icns)
- [ ] Metrónomo visual/audio
- [ ] Notas por canción
- [ ] Historial de cambios
- [ ] Sincronización en la nube
- [ ] Modo presentación (pantalla completa sin controles)

---

## 📦 Build y Distribución

### Proceso Actual (PyInstaller)
```bash
# 1. Limpiar
rm -rf build dist *.dmg

# 2. Build
.venv/bin/pyinstaller gimmeletter.spec

# 3. Crear DMG
./create_dmg.sh

# Resultado: GimmeLetter-1.0.0.dmg (31 MB)
```

### Notas
- py2app tiene problemas de permisos con libssl
- PyInstaller funciona perfectamente
- App NO está firmada (requiere certificado de Apple Developer)
- Usuarios verán advertencia de seguridad en primera ejecución

---

## 🧪 Testing

No hay tests automatizados. Testing manual:
1. Crear canción con acordes
2. Probar transposición (latin y english)
3. Crear set con múltiples canciones
4. Reproducir con auto-scroll
5. Cambiar velocidad y tamaño de fuente
6. Filtrar canciones
7. Click derecho → agregar a set
8. Cambiar tema

---

## 📅 Historial de Desarrollo (31 Enero 2026)

### Implementaciones Principales
1. ✅ App base con PyQt6 + SQLite
2. ✅ CRUD de canciones
3. ✅ Gestor de sets con configuración por canción
4. ✅ Reproductor con auto-scroll (acumulador flotante)
5. ✅ Transposición con preservación de espaciado
6. ✅ Migración DB para default_scroll_speed
7. ✅ Fonts grandes (22pt lyrics, 18pt lists)
8. ✅ Search filters en main window y set manager
9. ✅ Context menus (right-click)
10. ✅ Hover buttons con delegate personalizado
11. ✅ Tooltips y UX improvements
12. ✅ Controles en una sola línea (velocidad + tamaño)
13. ✅ Build con PyInstaller + DMG

### Bugs Corregidos
- Auto-scroll con UnboundLocalError
- Transposición destruyendo espacios
- Detección falsa de acordes ("La" en "algunas")
- sqlite3.Row access con atributos
- get_set() method missing
- Hover button sin interactividad
- Cursor no cambiando en hover

---

## 🎵 Uso Típico

1. **Agregar canción**: Canciones → Nueva Canción → Pegar letra con acordes
2. **Crear set**: Sets → Nuevo Set → Agregar canciones → Reordenar
3. **Configurar por canción**: En set manager, ajustar velocidad/transposición
4. **Reproducir**: Doble-click en set → Usa controles de velocidad/tamaño
5. **Transponer**: En reproductor, ajustar transposición (+/- semitonos)

---

## 💡 Tips para Copilot

- Usuario prefiere español en UX y comentarios
- Mantener estilo de código existente (snake_case, docstrings)
- Priorizar simplicidad sobre features complejas
- Siempre probar cambios reiniciando la app
- NO romper la funcionalidad de transposición (es crítica)
- Preservar el sistema de acumulador en auto-scroll
- Mantener fonts monoespaciadas para acordes

---

**Última actualización**: 31 Enero 2026
**Versión de app**: 1.0.0
**Estado**: Funcional y lista para distribución
