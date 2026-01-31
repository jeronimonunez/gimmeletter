"""
Ventana principal de la aplicación
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLabel, QMessageBox,
    QTabWidget, QStatusBar, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction

from ..database.db_manager import DatabaseManager
from ..database.models import Song
from ..utils.settings import Settings
from .song_editor import SongEditorDialog


class MainWindow(QMainWindow):
    """Ventana principal de GimmeLetter"""
    
    def __init__(self):
        super().__init__()
        
        self.db = DatabaseManager()
        self.settings = Settings()
        
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
        
        # Lista de canciones
        self.songs_list = QListWidget()
        self.songs_list.itemDoubleClicked.connect(self.edit_song)
        layout.addWidget(self.songs_list)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        new_song_btn = QPushButton("Nueva Canción")
        new_song_btn.clicked.connect(self.new_song)
        buttons_layout.addWidget(new_song_btn)
        
        edit_song_btn = QPushButton("Editar")
        edit_song_btn.clicked.connect(self.edit_song)
        buttons_layout.addWidget(edit_song_btn)
        
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
        
        # Menú Ver
        view_menu = menubar.addMenu("Ver")
        
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
            self.songs_list.addItem(item)
        
        # Cargar sets
        self.sets_list.clear()
        self.sets = self.db.get_all_sets()
        for s in self.sets:
            item = QListWidgetItem(s.name)
            item.setData(Qt.ItemDataRole.UserRole, s.id)
            self.sets_list.addItem(item)
        
        self.statusBar().showMessage(f"{len(self.songs)} canciones, {len(self.sets)} sets")
    
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
                QListWidget::item:selected {
                    background-color: #094771;
                }
                QListWidget::item:hover {
                    background-color: #2a2d2e;
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
    
    def new_set(self):
        QMessageBox.information(self, "Info", "Funcionalidad en desarrollo: Nuevo Set")
    
    def edit_set(self):
        QMessageBox.information(self, "Info", "Funcionalidad en desarrollo: Editar Set")
    
    def play_set(self):
        QMessageBox.information(self, "Info", "Funcionalidad en desarrollo: Reproducir Set")
    
    def delete_set(self):
        QMessageBox.information(self, "Info", "Funcionalidad en desarrollo: Eliminar Set")
    
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
