"""
Gestor de sets - Diálogo para crear/editar sets de canciones
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QListWidget,
    QGroupBox, QSpinBox, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt

from ..database.models import Set, SetSong, Song
from ..database.db_manager import DatabaseManager


class SetManagerDialog(QDialog):
    """Diálogo para crear o editar un set de canciones"""
    
    def __init__(self, parent=None, db: DatabaseManager = None, set_obj: Set = None):
        super().__init__(parent)
        
        self.db = db
        self.set_obj = set_obj if set_obj else Set()
        self.is_new = set_obj is None
        
        # Lista de canciones disponibles
        self.available_songs = self.db.get_all_songs() if self.db else []
        
        # Canciones en el set actual (con configuración)
        self.set_songs = []  # Lista de dict con {song, scroll_speed, transposition}
        
        self.init_ui()
        self.load_set_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Nuevo Set" if self.is_new else "Editar Set")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Nombre del set
        name_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nombre del set (ej: Concierto Acústico)")
        name_layout.addRow("Nombre del Set:*", self.name_input)
        layout.addLayout(name_layout)
        
        # Panel principal con dos columnas
        main_panel = QHBoxLayout()
        
        # Columna izquierda: Canciones disponibles
        left_panel = QVBoxLayout()
        available_group = QGroupBox("Canciones Disponibles")
        available_layout = QVBoxLayout()
        
        # Buscador de canciones
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar canciones...")
        self.search_input.textChanged.connect(self.filter_available_songs)
        self.search_input.setClearButtonEnabled(True)
        available_layout.addWidget(self.search_input)
        
        self.available_list = QListWidget()
        self.available_list.itemDoubleClicked.connect(self.add_song_to_set)
        available_layout.addWidget(self.available_list)
        
        add_btn = QPushButton("➡ Agregar al Set")
        add_btn.clicked.connect(self.add_song_to_set)
        available_layout.addWidget(add_btn)
        
        available_group.setLayout(available_layout)
        left_panel.addWidget(available_group)
        main_panel.addLayout(left_panel)
        
        # Columna derecha: Canciones en el set
        right_panel = QVBoxLayout()
        set_group = QGroupBox("Canciones en el Set")
        set_layout = QVBoxLayout()
        
        self.set_list = QListWidget()
        self.set_list.itemClicked.connect(self.on_set_song_selected)
        set_layout.addWidget(self.set_list)
        
        # Botones de orden
        order_layout = QHBoxLayout()
        up_btn = QPushButton("⬆ Subir")
        up_btn.clicked.connect(self.move_song_up)
        order_layout.addWidget(up_btn)
        
        down_btn = QPushButton("⬇ Bajar")
        down_btn.clicked.connect(self.move_song_down)
        order_layout.addWidget(down_btn)
        
        remove_btn = QPushButton("⬅ Quitar")
        remove_btn.clicked.connect(self.remove_song_from_set)
        order_layout.addWidget(remove_btn)
        
        set_layout.addLayout(order_layout)
        
        # Configuración de canción seleccionada
        config_group = QGroupBox("Configuración de Canción")
        config_layout = QFormLayout()
        
        self.scroll_speed_input = QSpinBox()
        self.scroll_speed_input.setRange(5, 200)  # Rango más amplio
        self.scroll_speed_input.setValue(50)
        self.scroll_speed_input.setSuffix(" px/seg")
        self.scroll_speed_input.valueChanged.connect(self.update_song_config)
        config_layout.addRow("Velocidad de scroll:", self.scroll_speed_input)
        
        self.transposition_input = QSpinBox()
        self.transposition_input.setRange(-11, 11)
        self.transposition_input.setValue(0)
        self.transposition_input.setSuffix(" semitonos")
        self.transposition_input.valueChanged.connect(self.update_song_config)
        config_layout.addRow("Transposición:", self.transposition_input)
        
        config_group.setLayout(config_layout)
        set_layout.addWidget(config_group)
        
        set_group.setLayout(set_layout)
        right_panel.addWidget(set_group)
        main_panel.addLayout(right_panel)
        
        layout.addLayout(main_panel)
        
        # Info
        info_label = QLabel("💡 Doble-click en una canción para agregarla al set")
        info_label.setStyleSheet("padding: 8px; background-color: rgba(100, 100, 100, 0.2); border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Guardar Set")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept_set)
        save_btn.setMinimumWidth(120)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_set_data(self):
        """Carga los datos del set y las canciones disponibles"""
        # Cargar canciones disponibles
        self.available_list.clear()
        for song in self.available_songs:
            item = QListWidgetItem(f"{song.title} - {song.artist}")
            item.setData(Qt.ItemDataRole.UserRole, song)
            self.available_list.addItem(item)
        
        # Si es un set existente, cargar las canciones del set
        if not self.is_new and self.set_obj.id:
            self.name_input.setText(self.set_obj.name)
            
            # Obtener canciones del set desde la BD
            set_songs_rows = self.db.get_set_songs(self.set_obj.id)
            
            for row in set_songs_rows:
                song = Song(
                    id=row['id'],
                    title=row['title'],
                    artist=row['artist'],
                    original_key=row['original_key'],
                    lyrics_with_chords=row['lyrics_with_chords'],
                    bpm=row['bpm']
                )
                
                self.set_songs.append({
                    'song': song,
                    'scroll_speed': row['scroll_speed'],
                    'transposition': row['transposition']
                })
            
            self.refresh_set_list()
    
    def refresh_set_list(self):
        """Actualiza la lista de canciones en el set"""
        self.set_list.clear()
        for i, song_config in enumerate(self.set_songs):
            song = song_config['song']
            speed = song_config['scroll_speed']
            trans = song_config['transposition']
            
            trans_str = f"+{trans}" if trans > 0 else str(trans)
            item_text = f"{i+1}. {song.title} - {song.artist} [{speed}px/s"
            
            if trans != 0:
                item_text += f", {trans_str} semitonos"
            item_text += "]"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)
            self.set_list.addItem(item)
    
    def add_song_to_set(self):
        """Agrega la canción seleccionada al set"""
        current_item = self.available_list.currentItem()
        if not current_item:
            return
        
        song = current_item.data(Qt.ItemDataRole.UserRole)
        
        # Verificar si ya está en el set
        if any(s['song'].id == song.id for s in self.set_songs):
            QMessageBox.warning(self, "Advertencia", "Esta canción ya está en el set")
            return
        
        # Agregar con la velocidad predeterminada de la canción
        self.set_songs.append({
            'song': song,
            'scroll_speed': song.default_scroll_speed,  # Usar velocidad guardada
            'transposition': 0
        })
        
        self.refresh_set_list()
        
        # Seleccionar la canción recién agregada
        self.set_list.setCurrentRow(len(self.set_songs) - 1)
    
    def remove_song_from_set(self):
        """Quita la canción seleccionada del set"""
        current_row = self.set_list.currentRow()
        if current_row < 0:
            return
        
        del self.set_songs[current_row]
        self.refresh_set_list()
    
    def move_song_up(self):
        """Mueve la canción seleccionada hacia arriba"""
        current_row = self.set_list.currentRow()
        if current_row <= 0:
            return
        
        # Intercambiar posiciones
        self.set_songs[current_row], self.set_songs[current_row - 1] = \
            self.set_songs[current_row - 1], self.set_songs[current_row]
        
        self.refresh_set_list()
        self.set_list.setCurrentRow(current_row - 1)
    
    def move_song_down(self):
        """Mueve la canción seleccionada hacia abajo"""
        current_row = self.set_list.currentRow()
        if current_row < 0 or current_row >= len(self.set_songs) - 1:
            return
        
        # Intercambiar posiciones
        self.set_songs[current_row], self.set_songs[current_row + 1] = \
            self.set_songs[current_row + 1], self.set_songs[current_row]
        
        self.refresh_set_list()
        self.set_list.setCurrentRow(current_row + 1)
    
    def filter_available_songs(self):
        """Filtra la lista de canciones disponibles según el texto de búsqueda"""
        search_text = self.search_input.text().lower()
        
        for i in range(self.available_list.count()):
            item = self.available_list.item(i)
            song = item.data(Qt.ItemDataRole.UserRole)
            
            # Buscar en título y artista
            matches = (
                search_text in song.title.lower() or
                search_text in song.artist.lower()
            )
            
            # Mostrar u ocultar el item según si coincide con la búsqueda
            item.setHidden(not matches)
    
    def on_set_song_selected(self):
        """Cuando se selecciona una canción del set, cargar su configuración"""
        current_row = self.set_list.currentRow()
        if current_row < 0:
            return
        
        song_config = self.set_songs[current_row]
        
        # Bloquear señales para evitar bucle
        self.scroll_speed_input.blockSignals(True)
        self.transposition_input.blockSignals(True)
        
        self.scroll_speed_input.setValue(song_config['scroll_speed'])
        self.transposition_input.setValue(song_config['transposition'])
        
        self.scroll_speed_input.blockSignals(False)
        self.transposition_input.blockSignals(False)
    
    def update_song_config(self):
        """Actualiza la configuración de la canción seleccionada"""
        current_row = self.set_list.currentRow()
        if current_row < 0:
            return
        
        self.set_songs[current_row]['scroll_speed'] = self.scroll_speed_input.value()
        self.set_songs[current_row]['transposition'] = self.transposition_input.value()
        
        self.refresh_set_list()
        self.set_list.setCurrentRow(current_row)
    
    def accept_set(self):
        """Valida y acepta el diálogo"""
        # Validación básica
        if not self.name_input.text().strip():
            self.name_input.setFocus()
            self.name_input.setStyleSheet("border: 2px solid red;")
            QMessageBox.warning(self, "Advertencia", "El set debe tener un nombre")
            return
        
        if not self.set_songs:
            QMessageBox.warning(self, "Advertencia", "El set debe tener al menos una canción")
            return
        
        # Actualizar el objeto set
        self.set_obj.name = self.name_input.text().strip()
        
        self.accept()
    
    def get_set(self) -> Set:
        """Retorna el objeto set"""
        return self.set_obj
    
    def get_set_songs(self) -> list:
        """Retorna la lista de canciones del set con su configuración"""
        return self.set_songs
