# Notas de Refactorización

## 31 de Enero, 2026

### Objetivo
Reducir el tamaño del archivo `main_window.py` que había crecido a 1093 líneas, separando funcionalidad en módulos más pequeños y manejables.

### Cambios Realizados

#### 1. Extracción de SongListDelegate (109 líneas)
**Archivo creado:** `src/ui/song_list_delegate.py`

- Mueve el delegate personalizado para mostrar el botón "⋯" en hover
- Incluye toda la lógica de pintado, detección de hover y manejo de clicks
- Reduce acoplamiento con la ventana principal

#### 2. Extracción de ImportExportHandler (176 líneas)
**Archivo creado:** `src/ui/import_export_handler.py`

Centraliza toda la lógica de importación/exportación:
- `import_songs()` - Importa canciones con manejo de conflictos
- `import_sets()` - Importa sets con sus canciones
- `_create_song_from_dict()` - Crea canciones desde diccionarios
- `_get_unique_song_title()` - Genera títulos únicos con contador

**Beneficios:**
- Separación de responsabilidades
- Más fácil de probar y mantener
- Puede ser reutilizado en otros contextos

#### 3. Simplificación de main_window.py
**Cambios en imports:**
```python
# Removidos
from PyQt6.QtWidgets import QStyledItemDelegate, QDialog
from PyQt6.QtCore import QRect
from PyQt6.QtGui import QPainter
from ..utils.import_export import songs_are_similar
from .import_conflict_dialog import ImportConflictDialog

# Agregados
from .song_list_delegate import SongListDelegate
from .import_export_handler import ImportExportHandler
```

**Inicialización simplificada:**
```python
def __init__(self):
    # ...
    self.import_export = ImportExportHandler(self, self.db)
```

**Método import_data() simplificado:**
- Ahora delega en `self.import_export.import_songs()` o `import_sets()`
- Elimina ~250 líneas de lógica de importación
- Mantiene solo la UI (diálogos de archivo, validación)

### Resultados

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Líneas en main_window.py | 1093 | 837 | -256 líneas (23%) |
| Archivos UI | 6 | 8 | +2 módulos |
| Responsabilidades por archivo | 8-10 | 4-6 | Mejor SRP |

### Estructura Mejorada

```
src/ui/
├── main_window.py (837 líneas)       ← Ventana principal
├── song_list_delegate.py (109 líneas) ← Delegate de lista
├── import_export_handler.py (176 líneas) ← Handler de I/E
├── song_editor.py                     ← Editor de canciones
├── set_manager.py                     ← Gestor de sets
├── player_window.py                   ← Ventana de reproducción
├── song_preview.py                    ← Vista previa
└── import_conflict_dialog.py          ← Diálogo de conflictos
```

### Próximos Pasos Potenciales

1. **Extraer Menu Handler**
   - Mover lógica de creación de menús a `menu_handler.py`
   - ~50 líneas adicionales

2. **Extraer Theme Manager**
   - Centralizar lógica de tema claro/oscuro
   - ~30 líneas adicionales

3. **Extraer Search Filter Logic**
   - Separar filtrado de búsqueda en componente reutilizable
   - ~40 líneas adicionales

### Validación
✅ Aplicación se ejecuta sin errores después de refactorización
✅ Import/export funciona correctamente
✅ Delegate de hover funciona como antes
✅ Todos los tests manuales pasan

### Lecciones Aprendidas

1. **Separar por responsabilidad, no por tamaño**
   - SongListDelegate: Responsable de UI de lista
   - ImportExportHandler: Responsable de I/O de datos
   - MainWindow: Responsable de orquestar componentes

2. **Mantener interfaces limpias**
   - Handler recibe referencias mínimas (main_window, db)
   - Delegate se mantiene independiente con setter para main_window

3. **Refactorizar incrementalmente**
   - Primero extraer delegate (simple, sin dependencias)
   - Luego handler (más complejo, pero bien aislado)
   - Probar después de cada extracción

### Notas Técnicas

- El patrón Handler es útil para agrupar operaciones relacionadas
- Los delegates deben mantenerse livianos y reutilizables
- Imports circulares se evitan pasando referencias en __init__

