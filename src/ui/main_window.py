"""
Ventana principal de la aplicación
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QMessageBox,
    QTabWidget, QStatusBar, QListWidgetItem, QLineEdit, QMenu,
    QFileDialog
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QAction

from ..database.db_manager import DatabaseManager
from ..database.models import Song, SetSong
from ..utils.settings import Settings
from ..utils.import_export import (
    export_songs_to_json, export_sets_to_json, save_json_to_file,
    load_json_from_file, validate_import_data
)
from .song_editor import SongEditorDialog
from .set_manager import SetManagerDialog
from .player_window import PlayerWindow
from .song_preview import SongPreviewDialog
from .song_list_delegate import SongListDelegate
from .import_export_handler import ImportExportHandler
from .settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """Ventana principal de GimmeLetter"""
    
    def __init__(self):
        super().__init__()
        
        self.db = DatabaseManager()
        self.settings = Settings()
        self.import_export = ImportExportHandler(self, self.db)
        
        self.init_ui()
        self.apply_theme()
        self.load_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("GimmeLetter")
        self.setMinimumSize(800, 600)
        
        # Restaurar geometría guardada
        geometry = self.settings.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
        
        # Widget central con tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Tabs para canciones y sets
        self.tabs = QTabWidget()
        
        # Tab de canciones
        self.songs_tab = self.create_songs_tab()
        self.tabs.addTab(self.songs_tab, "📝 Canciones")
        
        # Tab de sets
        self.sets_tab = self.create_sets_tab()
        self.tabs.addTab(self.sets_tab, "🎵 Sets")
        
        layout.addWidget(self.tabs)
        
        # Barra de menú
        self.create_menu_bar()
        
        # Barra de estado
        self.statusBar().showMessage("Listo")
    
    def create_songs_tab(self) -> QWidget:
        """Crea el tab de canciones"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Campo de búsqueda
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Buscar:")
        search_layout.addWidget(search_label)
        
        self.song_search = QLineEdit()
        self.song_search.setPlaceholderText("Buscar por título o artista...")
        self.song_search.textChanged.connect(self.filter_songs)
        search_font = QFont()
        search_font.setPointSize(13)
        self.song_search.setFont(search_font)
        search_layout.addWidget(self.song_search)
        
        layout.addLayout(search_layout)
        
        # Lista de canciones
        self.songs_list = QListWidget()
        self.songs_list.itemDoubleClicked.connect(self.edit_song)
        self.songs_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.songs_list.customContextMenuRequested.connect(self.show_song_context_menu)
        self.songs_list.setMouseTracking(True)  # Habilitar tracking de mouse para hover
        self.songs_list.viewport().setMouseTracking(True)  # También en viewport
        
        # Aplicar delegate personalizado para mostrar "..." en hover
        delegate = SongListDelegate(self.songs_list)
        delegate.main_window = self  # Guardar referencia a la ventana principal
        self.songs_list.setItemDelegate(delegate)
        
        # Configurar fuente más grande
        list_font = QFont()
        list_font.setPointSize(18)
        self.songs_list.setFont(list_font)
        
        layout.addWidget(self.songs_list)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        new_song_btn = QPushButton("Nueva Canción")
        new_song_btn.clicked.connect(self.new_song)
        buttons_layout.addWidget(new_song_btn)
        
        edit_song_btn = QPushButton("Editar")
        edit_song_btn.clicked.connect(self.edit_song)
        buttons_layout.addWidget(edit_song_btn)
        
        preview_song_btn = QPushButton("👁 Vista Previa")
        preview_song_btn.clicked.connect(self.preview_song)
        buttons_layout.addWidget(preview_song_btn)
        
        delete_song_btn = QPushButton("Eliminar")
        delete_song_btn.clicked.connect(self.delete_song)
        buttons_layout.addWidget(delete_song_btn)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def create_sets_tab(self) -> QWidget:
        """Crea el tab de sets"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Lista de sets
        self.sets_list = QListWidget()
        self.sets_list.itemDoubleClicked.connect(self.play_set)
        
        # Configurar fuente más grande
        list_font = QFont()
        list_font.setPointSize(18)
        self.sets_list.setFont(list_font)
        
        layout.addWidget(self.sets_list)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        new_set_btn = QPushButton("Nuevo Set")
        new_set_btn.clicked.connect(self.new_set)
        buttons_layout.addWidget(new_set_btn)
        
        edit_set_btn = QPushButton("Editar")
        edit_set_btn.clicked.connect(self.edit_set)
        buttons_layout.addWidget(edit_set_btn)
        
        play_set_btn = QPushButton("▶ Reproducir")
        play_set_btn.clicked.connect(self.play_set)
        buttons_layout.addWidget(play_set_btn)
        
        delete_set_btn = QPushButton("Eliminar")
        delete_set_btn.clicked.connect(self.delete_set)
        buttons_layout.addWidget(delete_set_btn)
        
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def create_menu_bar(self):
        """Crea la barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("Archivo")
        
        # Exportar canciones
        export_songs_action = QAction("📤 Exportar Canciones...", self)
        export_songs_action.triggered.connect(self.export_songs)
        file_menu.addAction(export_songs_action)
        
        # Exportar sets
        export_sets_action = QAction("📤 Exportar Sets...", self)
        export_sets_action.triggered.connect(self.export_sets)
        file_menu.addAction(export_sets_action)
        
        file_menu.addSeparator()
        
        # Importar
        import_action = QAction("📥 Importar...", self)
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("Ver")
        
        # Configuración
        settings_action = QAction("⚙️ Configuración...", self)
        settings_action.triggered.connect(self.open_settings)
        view_menu.addAction(settings_action)
        
        view_menu.addSeparator()
        
        # Toggle tema
        theme_action = QAction("Cambiar Tema (Oscuro/Claro)", self)
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
        
        view_menu.addSeparator()
        
        # Tamaño de fuente
        font_increase = QAction("Aumentar Fuente", self)
        font_increase.setShortcut("Ctrl++")
        font_increase.triggered.connect(lambda: self.change_font_size(2))
        view_menu.addAction(font_increase)
        
        font_decrease = QAction("Reducir Fuente", self)
        font_decrease.setShortcut("Ctrl+-")
        font_decrease.triggered.connect(lambda: self.change_font_size(-2))
        view_menu.addAction(font_decrease)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("Ayuda")
        
        about_action = QAction("Acerca de", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def load_data(self):
        """Carga los datos de la base de datos"""
        # Cargar canciones
        self.songs_list.clear()
        self.songs = self.db.get_all_songs()
        for song in self.songs:
            item = QListWidgetItem(f"{song.title} - {song.artist}")
            item.setData(Qt.ItemDataRole.UserRole, song.id)
            item.setToolTip("Click derecho para agregar esta canción a un set")
            self.songs_list.addItem(item)
        
        # Cargar sets
        self.sets_list.clear()
        self.sets = self.db.get_all_sets()
        for s in self.sets:
            item = QListWidgetItem(s.name)
            item.setData(Qt.ItemDataRole.UserRole, s.id)
            self.sets_list.addItem(item)
        
        self.statusBar().showMessage(f"{len(self.songs)} canciones, {len(self.sets)} sets")
    
    def filter_songs(self):
        """Filtra las canciones según el texto de búsqueda"""
        search_text = self.song_search.text().lower()
        
        # Mostrar todas si no hay texto de búsqueda
        if not search_text:
            for i in range(self.songs_list.count()):
                self.songs_list.item(i).setHidden(False)
            return
        
        # Filtrar canciones
        for i in range(self.songs_list.count()):
            item = self.songs_list.item(i)
            item_text = item.text().lower()
            # Mostrar si el texto de búsqueda está en el título o artista
            item.setHidden(search_text not in item_text)
    
    def apply_theme(self):
        """Aplica el tema oscuro o claro"""
        dark_mode = self.settings.get_dark_mode()
        
        if dark_mode:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                }
                QListWidget {
                    background-color: #252526;
                    border: 1px solid #3e3e42;
                    color: #d4d4d4;
                }
                QListWidget::item {
                    padding: 10px 8px;
                }
                QListWidget::item:selected {
                    background-color: #094771;
                }
                QListWidget::item:hover {
                    background-color: #2a2d2e;
                }
                QLineEdit {
                    background-color: #252526;
                    color: #d4d4d4;
                    border: 1px solid #3e3e42;
                    padding: 6px;
                    border-radius: 4px;
                }
                QLineEdit:focus {
                    border: 1px solid #007acc;
                }
                QPushButton {
                    background-color: #0e639c;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1177bb;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QTabWidget::pane {
                    border: 1px solid #3e3e42;
                    background-color: #1e1e1e;
                }
                QTabBar::tab {
                    background-color: #2d2d30;
                    color: #d4d4d4;
                    padding: 8px 16px;
                    border: 1px solid #3e3e42;
                }
                QTabBar::tab:selected {
                    background-color: #1e1e1e;
                    border-bottom-color: #1e1e1e;
                }
                QMenuBar {
                    background-color: #2d2d30;
                    color: #d4d4d4;
                }
                QMenuBar::item:selected {
                    background-color: #094771;
                }
                QMenu {
                    background-color: #252526;
                    color: #d4d4d4;
                    border: 1px solid #3e3e42;
                }
                QMenu::item:selected {
                    background-color: #094771;
                }
                QStatusBar {
                    background-color: #007acc;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow, QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QListWidget {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                }
                QListWidget::item {
                    padding: 10px 8px;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 6px;
                    border-radius: 4px;
                }
                QLineEdit:focus {
                    border: 1px solid #007acc;
                }
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1177bb;
                }
                QStatusBar {
                    background-color: #007acc;
                    color: white;
                }
            """)
        
        # Aplicar tamaño de fuente
        font_size = self.settings.get_font_size()
        font = QFont()
        font.setPointSize(font_size)
        self.setFont(font)
    
    def toggle_theme(self):
        """Alterna entre tema oscuro y claro"""
        current = self.settings.get_dark_mode()
        self.settings.set_dark_mode(not current)
        self.apply_theme()
    
    def change_font_size(self, delta: int):
        """Cambia el tamaño de fuente"""
        current = self.settings.get_font_size()
        new_size = max(8, min(32, current + delta))
        self.settings.set_font_size(new_size)
        self.apply_theme()
    
    # Funcionalidades de canciones
    def new_song(self):
        """Abre el diálogo para crear una nueva canción"""
        dialog = SongEditorDialog(self)
        if dialog.exec():
            song = dialog.get_song()
            song_id = self.db.add_song(song)
            self.load_data()
            self.statusBar().showMessage(f"Canción '{song.title}' guardada correctamente", 3000)
    
    def edit_song(self):
        """Abre el diálogo para editar la canción seleccionada"""
        current_item = self.songs_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona una canción para editar")
            return
        
        song_id = current_item.data(Qt.ItemDataRole.UserRole)
        song = self.db.get_song(song_id)
        
        if song:
            dialog = SongEditorDialog(self, song)
            if dialog.exec():
                updated_song = dialog.get_song()
                self.db.update_song(updated_song)
                self.load_data()
                self.statusBar().showMessage(f"Canción '{updated_song.title}' actualizada", 3000)
    
    def preview_song(self):
        """Abre la vista previa de la canción seleccionada"""
        current_item = self.songs_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona una canción para previsualizar")
            return
        
        song_id = current_item.data(Qt.ItemDataRole.UserRole)
        song = self.db.get_song(song_id)
        
        if song:
            dialog = SongPreviewDialog(self, song, self.settings)
            if dialog.exec():
                # Si acepta el diálogo, guardar la velocidad actualizada
                updated_song = dialog.get_song()
                self.db.update_song(updated_song)
                self.statusBar().showMessage(f"Velocidad de scroll guardada para '{updated_song.title}'", 3000)
    
    def delete_song(self):
        """Elimina la canción seleccionada"""
        current_item = self.songs_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona una canción para eliminar")
            return
        
        song_id = current_item.data(Qt.ItemDataRole.UserRole)
        song = self.db.get_song(song_id)
        
        if song:
            reply = QMessageBox.question(
                self,
                "Confirmar eliminación",
                f"¿Estás seguro de que quieres eliminar '{song.title}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.db.delete_song(song_id)
                self.load_data()
                self.statusBar().showMessage(f"Canción '{song.title}' eliminada", 3000)
    
    def show_song_context_menu(self, position):
        """Muestra el menú contextual para canciones"""
        item = self.songs_list.itemAt(position)
        if not item:
            return
        
        # Crear menú contextual
        context_menu = QMenu(self)
        
        # Submenú para agregar a set
        add_to_set_menu = context_menu.addMenu("➕ Agregar a Set")
        
        # Obtener todos los sets
        sets = self.db.get_all_sets()
        
        if not sets:
            no_sets_action = add_to_set_menu.addAction("(No hay sets disponibles)")
            no_sets_action.setEnabled(False)
        else:
            # Agregar cada set como una opción
            for set_obj in sets:
                action = add_to_set_menu.addAction(set_obj.name)
                # Conectar la acción con lambda que captura el set_id y song_id
                song_id = item.data(Qt.ItemDataRole.UserRole)
                action.triggered.connect(
                    lambda checked, sid=song_id, setid=set_obj.id: self.add_song_to_set(sid, setid)
                )
        
        # Mostrar el menú en la posición del cursor
        context_menu.exec(self.songs_list.mapToGlobal(position))
    
    def show_song_context_menu_at_item(self, row_index: int, global_pos: QPoint):
        """Muestra el menú contextual para una canción específica en una posición dada"""
        item = self.songs_list.item(row_index)
        if not item:
            return
        
        # Crear menú contextual
        context_menu = QMenu(self)
        
        # Submenú para agregar a set
        add_to_set_menu = context_menu.addMenu("➕ Agregar a Set")
        
        # Obtener todos los sets
        sets = self.db.get_all_sets()
        
        if not sets:
            no_sets_action = add_to_set_menu.addAction("(No hay sets disponibles)")
            no_sets_action.setEnabled(False)
        else:
            # Agregar cada set como una opción
            for set_obj in sets:
                action = add_to_set_menu.addAction(set_obj.name)
                # Conectar la acción con lambda que captura el set_id y song_id
                song_id = item.data(Qt.ItemDataRole.UserRole)
                action.triggered.connect(
                    lambda checked, sid=song_id, setid=set_obj.id: self.add_song_to_set(sid, setid)
                )
        
        # Mostrar el menú en la posición especificada
        context_menu.exec(global_pos)
    
    def add_song_to_set(self, song_id: int, set_id: int):
        """Agrega una canción a un set"""
        # Obtener la canción y el set
        song = self.db.get_song(song_id)
        set_obj = self.db.get_set(set_id)
        
        if not song or not set_obj:
            return
        
        # Obtener las canciones actuales del set
        set_songs = self.db.get_set_songs(set_id)
        
        # Verificar si la canción ya está en el set (set_songs son sqlite3.Row)
        if any(row['id'] == song_id for row in set_songs):
            QMessageBox.information(
                self,
                "Información",
                f"La canción '{song.title}' ya está en el set '{set_obj.name}'"
            )
            return
        
        # Calcular la nueva posición (al final)
        new_order = len(set_songs)
        
        # Crear el registro de la canción en el set
        set_song = SetSong(
            set_id=set_id,
            song_id=song_id,
            order=new_order,
            scroll_speed=song.default_scroll_speed or 50,
            transposition=0
        )
        
        # Guardar en la base de datos
        self.db.add_song_to_set(set_song)
        
        self.statusBar().showMessage(
            f"'{song.title}' agregada al set '{set_obj.name}'",
            3000
        )
    
    # Funcionalidades de sets
    def new_set(self):
        """Abre el diálogo para crear un nuevo set"""
        dialog = SetManagerDialog(self, self.db)
        if dialog.exec():
            set_obj = dialog.get_set()
            set_songs = dialog.get_set_songs()
            
            # Guardar el set
            set_id = self.db.add_set(set_obj)
            
            # Guardar las canciones del set
            for order, song_config in enumerate(set_songs):
                set_song = SetSong(
                    set_id=set_id,
                    song_id=song_config['song'].id,
                    order=order,
                    scroll_speed=song_config['scroll_speed'],
                    transposition=song_config['transposition']
                )
                self.db.add_song_to_set(set_song)
            
            self.load_data()
            self.statusBar().showMessage(f"Set '{set_obj.name}' guardado correctamente", 3000)
    
    def edit_set(self):
        """Abre el diálogo para editar el set seleccionado"""
        current_item = self.sets_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona un set para editar")
            return
        
        set_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Obtener el set
        for s in self.sets:
            if s.id == set_id:
                dialog = SetManagerDialog(self, self.db, s)
                if dialog.exec():
                    updated_set = dialog.get_set()
                    set_songs = dialog.get_set_songs()
                    
                    # Actualizar nombre del set
                    self.db.connection.execute(
                        "UPDATE sets SET name = ? WHERE id = ?",
                        (updated_set.name, set_id)
                    )
                    
                    # Eliminar canciones anteriores del set
                    self.db.connection.execute(
                        "DELETE FROM set_songs WHERE set_id = ?",
                        (set_id,)
                    )
                    
                    # Agregar canciones actualizadas
                    for order, song_config in enumerate(set_songs):
                        set_song = SetSong(
                            set_id=set_id,
                            song_id=song_config['song'].id,
                            order=order,
                            scroll_speed=song_config['scroll_speed'],
                            transposition=song_config['transposition']
                        )
                        self.db.add_song_to_set(set_song)
                    
                    self.db.connection.commit()
                    self.load_data()
                    self.statusBar().showMessage(f"Set '{updated_set.name}' actualizado", 3000)
                break
    
    def play_set(self):
        """Reproduce el set seleccionado"""
        current_item = self.sets_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona un set para reproducir")
            return
        
        set_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Buscar el set
        set_obj = None
        for s in self.sets:
            if s.id == set_id:
                set_obj = s
                break
        
        if not set_obj:
            return
        
        # Obtener canciones del set con configuración
        set_songs_rows = self.db.get_set_songs(set_id)
        
        if not set_songs_rows:
            QMessageBox.warning(self, "Advertencia", "Este set no tiene canciones")
            return
        
        # Construir lista de canciones con configuración
        set_songs = []
        for row in set_songs_rows:
            song = Song(
                id=row['id'],
                title=row['title'],
                artist=row['artist'],
                original_key=row['original_key'],
                lyrics_with_chords=row['lyrics_with_chords'],
                bpm=row['bpm']
            )
            
            set_songs.append({
                'song': song,
                'scroll_speed': row['scroll_speed'],
                'transposition': row['transposition']
            })
        
        # Abrir ventana de reproducción
        self.player_window = PlayerWindow(
            parent=self,
            set_songs=set_songs,
            set_name=set_obj.name,
            settings=self.settings
        )
        self.player_window.show()
    
    def delete_set(self):
        """Elimina el set seleccionado"""
        current_item = self.sets_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Advertencia", "Por favor selecciona un set para eliminar")
            return
        
        set_id = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Buscar el set
        for s in self.sets:
            if s.id == set_id:
                reply = QMessageBox.question(
                    self,
                    "Confirmar eliminación",
                    f"¿Estás seguro de que quieres eliminar el set '{s.name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    self.db.delete_set(set_id)
                    self.load_data()
                    self.statusBar().showMessage(f"Set '{s.name}' eliminado", 3000)
                break
    
    def export_songs(self):
        """Exporta todas las canciones a un archivo JSON"""
        if not self.songs:
            QMessageBox.information(self, "Info", "No hay canciones para exportar")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Canciones",
            "canciones_gimmeletter.json",
            "Archivos JSON (*.json)"
        )
        
        if file_path:
            try:
                export_data = export_songs_to_json(self.songs)
                save_json_to_file(export_data, file_path)
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Se exportaron {len(self.songs)} canciones correctamente"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")
    
    def export_sets(self):
        """Exporta todos los sets con sus canciones a un archivo JSON"""
        if not self.sets:
            QMessageBox.information(self, "Info", "No hay sets para exportar")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Sets",
            "sets_gimmeletter.json",
            "Archivos JSON (*.json)"
        )
        
        if file_path:
            try:
                export_data = export_sets_to_json(self.sets, self.db)
                save_json_to_file(export_data, file_path)
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Se exportaron {len(self.sets)} sets correctamente"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")
    
    def import_data(self):
        """Importa canciones o sets desde un archivo JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Canciones o Sets",
            "",
            "Archivos JSON (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # Cargar y validar datos
            data = load_json_from_file(file_path)
            is_valid, error_msg, export_type = validate_import_data(data)
            
            if not is_valid:
                QMessageBox.critical(self, "Error", error_msg)
                return
            
            # Importar según el tipo usando el handler
            changed = False
            if export_type == 'songs':
                changed = self.import_export.import_songs(data['songs'])
            elif export_type == 'sets':
                changed = self.import_export.import_sets(data['sets'])
            
            # Recargar datos si hubo cambios
            if changed:
                self.load_data()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al importar: {str(e)}")
    
    def open_settings(self):
        """Abre el diálogo de configuración"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def show_about(self):
        """Muestra el diálogo Acerca de"""
        QMessageBox.about(
            self,
            "Acerca de GimmeLetter",
            "<h2>GimmeLetter</h2>"
            "<p>Aplicación para músicos con scroll automático de letras y acordes.</p>"
            "<p>Version 0.1.0</p>"
            "<p>Desarrollado con PyQt6 y ❤️</p>"
        )
    
    def closeEvent(self, event):
        """Guarda la configuración antes de cerrar"""
        self.settings.set_window_geometry(self.saveGeometry())
        self.db.close()
        event.accept()
