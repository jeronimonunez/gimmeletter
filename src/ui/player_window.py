"""
Reproductor de sets con scroll automático
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QSlider, QToolBar, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QAction

from ..database.models import Song
from ..utils.chord_transposer import ChordTransposer
from ..utils.settings import Settings


class PlayerWindow(QMainWindow):
    """Ventana de reproducción con scroll automático"""
    
    def __init__(self, parent=None, set_songs=None, set_name="Set", settings=None):
        super().__init__(parent)
        
        self.set_songs = set_songs or []  # Lista de dict con song, scroll_speed, transposition
        self.set_name = set_name
        self.settings = settings or Settings()
        
        self.current_index = 0
        self.is_playing = False
        self.scroll_position = 0
        self.scroll_accumulator = 0.0  # Acumulador para movimientos suaves con velocidades bajas
        self.current_font_size = 22  # Tamaño de fuente inicial más grande
        
        # Timer para el scroll automático
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.auto_scroll)
        
        self.init_ui()
        self.load_song()
        self.apply_theme()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle(f"GimmeLetter - {self.set_name}")
        self.setMinimumSize(1100, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Barra de herramientas superior
        toolbar = self.create_toolbar()
        self.addToolBar(toolbar)
        
        # Layout horizontal principal: lista de canciones + contenido
        content_layout = QHBoxLayout()
        
        # Lista de canciones (lado izquierdo)
        self.create_song_list()
        content_layout.addWidget(self.song_list)
        
        # Layout vertical del lado derecho (contenido principal)
        right_layout = QVBoxLayout()
        
        # Información de la canción
        self.song_info_label = QLabel()
        self.song_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_font = QFont()
        info_font.setPointSize(14)
        info_font.setBold(True)
        self.song_info_label.setFont(info_font)
        right_layout.addWidget(self.song_info_label)
        
        # Área de texto con letra y acordes
        self.lyrics_display = QTextEdit()
        self.lyrics_display.setReadOnly(True)
        
        # Fuente monoespaciada para los acordes - más grande para mejor lectura
        mono_font = QFont("Monaco, Courier New, monospace")
        mono_font.setPointSize(self.current_font_size)
        self.lyrics_display.setFont(mono_font)
        
        right_layout.addWidget(self.lyrics_display)
        
        # Panel de controles
        controls_layout = self.create_controls()
        right_layout.addLayout(controls_layout)
        
        content_layout.addLayout(right_layout, stretch=3)
        main_layout.addLayout(content_layout)
        
        # Atajos de teclado
        self.setup_shortcuts()
    
    def create_song_list(self):
        """Crea la lista de canciones del set"""
        self.song_list = QListWidget()
        self.song_list.setMaximumWidth(300)
        self.song_list.setMinimumWidth(250)
        
        # Estilo de la lista
        list_font = QFont()
        list_font.setPointSize(14)
        self.song_list.setFont(list_font)
        
        # Poblar la lista
        for i, song_config in enumerate(self.set_songs):
            song = song_config['song']
            item_text = f"{i + 1}. {song.title}\n   {song.artist}"
            item = QListWidgetItem(item_text)
            self.song_list.addItem(item)
        
        # Conectar el evento de clic
        self.song_list.itemClicked.connect(self.on_song_list_clicked)
        
        # Marcar la primera canción como seleccionada
        if self.set_songs:
            self.song_list.setCurrentRow(0)
    
    def create_toolbar(self):
        """Crea la barra de herramientas"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Botón cerrar
        close_action = QAction("✕ Cerrar", self)
        close_action.triggered.connect(self.close)
        toolbar.addAction(close_action)
        
        toolbar.addSeparator()
        
        # Información del set
        set_info = QAction(f"📋 {self.set_name} ({len(self.set_songs)} canciones)", self)
        set_info.setEnabled(False)
        toolbar.addAction(set_info)
        
        toolbar.addSeparator()
        
        # Pantalla completa
        fullscreen_action = QAction("⛶ Pantalla Completa", self)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        toolbar.addAction(fullscreen_action)
        
        return toolbar
    
    def create_controls(self):
        """Crea el panel de controles"""
        controls_layout = QVBoxLayout()
        
        # Velocidad y tamaño de texto en la misma línea
        speed_font_layout = QHBoxLayout()
        
        # Slider de velocidad
        speed_font_layout.addWidget(QLabel("Velocidad:"))
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(5, 200)  # Rango más amplio, desde 5 px/s
        self.speed_slider.setValue(50)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(20)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        speed_font_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("50 px/s")
        self.speed_label.setMinimumWidth(80)
        speed_font_layout.addWidget(self.speed_label)
        
        # Separador visual
        speed_font_layout.addSpacing(20)
        
        # Control de tamaño de fuente
        speed_font_layout.addWidget(QLabel("Tamaño:"))
        
        font_minus_btn = QPushButton("-")
        font_minus_btn.clicked.connect(lambda: self.change_font_size(-2))
        font_minus_btn.setMaximumWidth(40)
        speed_font_layout.addWidget(font_minus_btn)
        
        self.font_size_label = QLabel(f"{self.current_font_size}")
        self.font_size_label.setMinimumWidth(30)
        self.font_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        speed_font_layout.addWidget(self.font_size_label)
        
        font_plus_btn = QPushButton("+")
        font_plus_btn.clicked.connect(lambda: self.change_font_size(2))
        font_plus_btn.setMaximumWidth(40)
        speed_font_layout.addWidget(font_plus_btn)
        
        controls_layout.addLayout(speed_font_layout)
        
        # Botones de control
        buttons_layout = QHBoxLayout()
        
        # Anterior
        prev_btn = QPushButton("⏮ Anterior (←)")
        prev_btn.clicked.connect(self.previous_song)
        prev_btn.setMinimumHeight(40)
        buttons_layout.addWidget(prev_btn)
        
        # Play/Pause
        self.play_pause_btn = QPushButton("▶ Reproducir (Space)")
        self.play_pause_btn.clicked.connect(self.toggle_play)
        self.play_pause_btn.setMinimumHeight(40)
        self.play_pause_btn.setMinimumWidth(180)
        buttons_layout.addWidget(self.play_pause_btn)
        
        # Siguiente
        next_btn = QPushButton("Siguiente ⏭ (→)")
        next_btn.clicked.connect(self.next_song)
        next_btn.setMinimumHeight(40)
        buttons_layout.addWidget(next_btn)
        
        # Rebobinar
        rewind_btn = QPushButton("⏪ Rebobinar (⌫)")
        rewind_btn.clicked.connect(self.rewind)
        rewind_btn.setMinimumHeight(40)
        buttons_layout.addWidget(rewind_btn)
        
        controls_layout.addLayout(buttons_layout)
        
        return controls_layout
    
    def setup_shortcuts(self):
        """Configura los atajos de teclado"""
        # Espacio para play/pause
        play_action = QAction(self)
        play_action.setShortcut(Qt.Key.Key_Space)
        play_action.triggered.connect(self.toggle_play)
        self.addAction(play_action)
        
        # Flechas para navegar
        next_action = QAction(self)
        next_action.setShortcut(Qt.Key.Key_Right)
        next_action.triggered.connect(self.next_song)
        self.addAction(next_action)
        
        prev_action = QAction(self)
        prev_action.setShortcut(Qt.Key.Key_Left)
        prev_action.triggered.connect(self.previous_song)
        self.addAction(prev_action)
        
        # ESC para salir de pantalla completa
        esc_action = QAction(self)
        esc_action.setShortcut(Qt.Key.Key_Escape)
        esc_action.triggered.connect(self.exit_fullscreen)
        self.addAction(esc_action)
        
        # F11 para pantalla completa
        f11_action = QAction(self)
        f11_action.setShortcut(Qt.Key.Key_F11)
        f11_action.triggered.connect(self.toggle_fullscreen)
        self.addAction(f11_action)
        
        # Backspace para rebobinar
        rewind_action = QAction(self)
        rewind_action.setShortcut(Qt.Key.Key_Backspace)
        rewind_action.triggered.connect(self.rewind)
        self.addAction(rewind_action)
    
    def load_song(self):
        """Carga la canción actual"""
        if not self.set_songs or self.current_index >= len(self.set_songs):
            return
        
        # Detener scroll si está reproduciendo
        if self.is_playing:
            self.toggle_play()
        
        # Actualizar selección en la lista
        self.song_list.setCurrentRow(self.current_index)
        
        song_config = self.set_songs[self.current_index]
        song = song_config['song']
        transposition = song_config['transposition']
        scroll_speed = song_config['scroll_speed']
        
        # Actualizar información
        trans_str = ""
        if transposition != 0:
            trans_str = f" (Transposición: {'+' if transposition > 0 else ''}{transposition})"
        
        info_text = f"{song.title} - {song.artist}"
        if song.original_key:
            info_text += f" | Tonalidad: {song.original_key}"
        if song.bpm:
            info_text += f" | BPM: {song.bpm}"
        info_text += trans_str
        info_text += f" | Canción {self.current_index + 1}/{len(self.set_songs)}"
        
        self.song_info_label.setText(info_text)
        
        # Aplicar transposición si es necesario
        lyrics = song.lyrics_with_chords or ""
        if transposition != 0:
            # Detectar si usa notación latina o inglesa
            # Buscar acordes latinos con word boundaries para evitar falsos positivos
            import re
            latin_pattern = r'\b(Do|Re|Mi|Fa|Sol|La|Si)(#|b)?(m|M|maj|min|dim|aug|sus|add|\d)*\b'
            use_latin = bool(re.search(latin_pattern, lyrics))
            lyrics = ChordTransposer.transpose_text(lyrics, transposition, use_latin)
        
        self.lyrics_display.setPlainText(lyrics)
        
        # Configurar velocidad
        self.speed_slider.setValue(scroll_speed)
        
        # Resetear scroll
        self.reset_scroll()
    
    def toggle_play(self):
        """Alterna entre reproducir y pausar"""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_pause_btn.setText("⏸ Pausar (Space)")
            # Iniciar timer con intervalo de 50ms para scroll suave
            self.scroll_timer.start(50)
        else:
            self.play_pause_btn.setText("▶ Reproducir (Space)")
            self.scroll_timer.stop()
    
    def auto_scroll(self):
        """Scroll automático basado en la velocidad configurada"""
        if not self.is_playing:
            return
        
        # Calcular cuántos píxeles mover (velocidad está en px/seg)
        speed = self.speed_slider.value()
        pixels_per_frame = speed / 20  # 50ms = 1/20 de segundo
        
        # Acumular el movimiento para permitir velocidades muy lentas
        self.scroll_accumulator += pixels_per_frame
        
        # Obtener el scroll bar vertical
        scrollbar = self.lyrics_display.verticalScrollBar()
        current_pos = scrollbar.value()
        max_pos = scrollbar.maximum()
        
        # Solo mover cuando hayamos acumulado al menos 1 píxel
        if self.scroll_accumulator >= 1.0:
            pixels_to_move = int(self.scroll_accumulator)
            self.scroll_accumulator -= pixels_to_move
            
            # Incrementar posición
            new_pos = current_pos + pixels_to_move
            
            # Si llegamos al final (y hay contenido para scrollear), pausar
            if max_pos > 0 and new_pos >= max_pos:
                new_pos = max_pos
                scrollbar.setValue(new_pos)
                # Auto-avanzar a la siguiente canción si hay más
                if self.current_index < len(self.set_songs) - 1:
                    self.toggle_play()  # Pausar primero
                    QTimer.singleShot(2000, self.next_song)  # Esperar 2 segundos
                else:
                    self.toggle_play()  # Pausar si es la última canción
            else:
                scrollbar.setValue(new_pos)
    
    def reset_scroll(self):
        """Reinicia el scroll al inicio"""
        scrollbar = self.lyrics_display.verticalScrollBar()
        scrollbar.setValue(0)
        self.scroll_position = 0
        self.scroll_accumulator = 0.0  # Resetear acumulador
    
    def rewind(self):
        """Rebobina al inicio de la canción y detiene el scroll"""
        # Detener si está reproduciendo
        if self.is_playing:
            self.toggle_play()
        
        # Ir al inicio
        self.reset_scroll()
    
    def on_speed_changed(self, value):
        """Actualiza la etiqueta de velocidad"""
        self.speed_label.setText(f"{value} px/s")
        
        # Actualizar la configuración de la canción actual
        if self.set_songs and self.current_index < len(self.set_songs):
            self.set_songs[self.current_index]['scroll_speed'] = value
    
    def next_song(self):
        """Avanza a la siguiente canción"""
        if self.current_index < len(self.set_songs) - 1:
            self.current_index += 1
            self.load_song()
    
    def previous_song(self):
        """Retrocede a la canción anterior"""
        if self.current_index > 0:
            self.current_index -= 1
            self.load_song()
    
    def on_song_list_clicked(self, item):
        """Maneja el clic en una canción de la lista"""
        row = self.song_list.row(item)
        if row != self.current_index:
            self.current_index = row
            self.load_song()
    
    def toggle_fullscreen(self):
        """Alterna pantalla completa"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def exit_fullscreen(self):
        """Sale de pantalla completa"""
        if self.isFullScreen():
            self.showNormal()
    
    def update_font_size(self):
        """Actualiza el tamaño de fuente del texto"""
        mono_font = QFont("Monaco, Courier New, monospace")
        mono_font.setPointSize(self.current_font_size)
        self.lyrics_display.setFont(mono_font)
        self.font_size_label.setText(f"{self.current_font_size}")
    
    def change_font_size(self, delta: int):
        """Cambia el tamaño de fuente"""
        self.current_font_size = max(12, min(48, self.current_font_size + delta))
        self.update_font_size()
    
    def apply_theme(self):
        """Aplica el tema oscuro o claro"""
        dark_mode = self.settings.get_dark_mode()
        
        if dark_mode:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: none;
                    padding: 20px;
                }
                QListWidget {
                    background-color: #252526;
                    color: #d4d4d4;
                    border: none;
                    padding: 8px;
                    outline: none;
                }
                QListWidget::item {
                    padding: 8px;
                    border-radius: 4px;
                    margin: 2px;
                }
                QListWidget::item:selected {
                    background-color: #0e639c;
                    color: white;
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
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #1177bb;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QLabel {
                    color: #d4d4d4;
                    padding: 8px;
                }
                QSlider::groove:horizontal {
                    border: 1px solid #3e3e42;
                    height: 8px;
                    background: #2d2d30;
                    border-radius: 4px;
                }
                QSlider::handle:horizontal {
                    background: #0e639c;
                    border: 1px solid #0e639c;
                    width: 18px;
                    margin: -5px 0;
                    border-radius: 9px;
                }
                QSlider::handle:horizontal:hover {
                    background: #1177bb;
                }
                QToolBar {
                    background-color: #2d2d30;
                    border: none;
                    padding: 4px;
                    spacing: 8px;
                }
                QToolBar QToolButton {
                    color: #d4d4d4;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                QToolBar QToolButton:hover {
                    background-color: #094771;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: none;
                    padding: 20px;
                }
                QListWidget {
                    background-color: #f3f3f3;
                    color: #000000;
                    border: 1px solid #e0e0e0;
                    padding: 8px;
                    outline: none;
                }
                QListWidget::item {
                    padding: 8px;
                    border-radius: 4px;
                    margin: 2px;
                }
                QListWidget::item:selected {
                    background-color: #007acc;
                    color: white;
                }
                QListWidget::item:hover {
                    background-color: #e8e8e8;
                }
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #1177bb;
                }
                QLabel {
                    color: #000000;
                    padding: 8px;
                }
                QToolBar {
                    background-color: #f0f0f0;
                    border: none;
                    padding: 4px;
                }
            """)

    
    def closeEvent(self, event):
        """Limpia el timer antes de cerrar"""
        if self.scroll_timer.isActive():
            self.scroll_timer.stop()
        event.accept()
