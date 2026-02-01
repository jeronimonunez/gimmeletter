"""
Vista previa de canción - Reproduce una canción individual para configurar velocidad
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QSlider, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from ..database.models import Song
from ..utils.settings import Settings


class SongPreviewDialog(QDialog):
    """Diálogo de vista previa para una canción individual"""
    
    def __init__(self, parent=None, song: Song = None, settings: Settings = None):
        super().__init__(parent)
        
        self.song = song
        self.settings = settings or Settings()
        self.is_playing = False
        self.saved_speed = song.default_scroll_speed if song else 50
        self.scroll_accumulator = 0.0  # Acumulador para velocidades bajas
        
        # Timer para el scroll
        self.scroll_timer = QTimer()
        self.scroll_timer.timeout.connect(self.auto_scroll)
        
        self.init_ui()
        self.load_song()
        self.apply_theme()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Vista Previa de Canción")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Información de la canción
        self.song_info_label = QLabel()
        self.song_info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_font = QFont()
        info_font.setPointSize(14)
        info_font.setBold(True)
        self.song_info_label.setFont(info_font)
        layout.addWidget(self.song_info_label)
        
        # Área de texto con letra y acordes
        self.lyrics_display = QTextEdit()
        self.lyrics_display.setReadOnly(True)
        
        mono_font = QFont("Monaco, Courier New, monospace")
        mono_font.setPointSize(22)  # Tamaño grande para mejor visibilidad
        self.lyrics_display.setFont(mono_font)
        
        layout.addWidget(self.lyrics_display)
        
        # Slider de velocidad
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Velocidad de scroll:"))
        
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(5, 200)  # Rango más amplio, desde 5 px/s
        self.speed_slider.setValue(self.saved_speed)
        self.speed_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.speed_slider.setTickInterval(20)
        self.speed_slider.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel(f"{self.saved_speed} px/s")
        self.speed_label.setMinimumWidth(80)
        speed_layout.addWidget(self.speed_label)
        
        layout.addLayout(speed_layout)
        
        # Checkbox para guardar velocidad
        self.save_speed_checkbox = QCheckBox("Guardar esta velocidad como predeterminada para esta canción")
        self.save_speed_checkbox.setChecked(True)
        layout.addWidget(self.save_speed_checkbox)
        
        # Botones de control
        controls_layout = QHBoxLayout()
        
        # Play/Pause
        self.play_pause_btn = QPushButton("▶ Reproducir")
        self.play_pause_btn.clicked.connect(self.toggle_play)
        self.play_pause_btn.setMinimumHeight(40)
        self.play_pause_btn.setMinimumWidth(150)
        controls_layout.addWidget(self.play_pause_btn)
        
        # Reiniciar
        reset_btn = QPushButton("⟲ Reiniciar")
        reset_btn.clicked.connect(self.reset_scroll)
        reset_btn.setMinimumHeight(40)
        controls_layout.addWidget(reset_btn)
        
        layout.addLayout(controls_layout)
        
        # Info
        info_label = QLabel("💡 Prueba la velocidad de scroll y guárdala para usar en sets")
        info_label.setStyleSheet("padding: 8px; background-color: rgba(100, 100, 100, 0.2); border-radius: 4px;")
        layout.addWidget(info_label)
        
        # Botones finales
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close_preview)
        buttons_layout.addWidget(close_btn)
        
        save_btn = QPushButton("💾 Guardar y Cerrar")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.save_and_close)
        save_btn.setMinimumWidth(150)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_song(self):
        """Carga la canción"""
        if not self.song:
            return
        
        # Información
        info_text = f"{self.song.title} - {self.song.artist}"
        if self.song.original_key:
            info_text += f" | Tonalidad: {self.song.original_key}"
        if self.song.bpm:
            info_text += f" | BPM: {self.song.bpm}"
        
        self.song_info_label.setText(info_text)
        
        # Letra y acordes
        self.lyrics_display.setPlainText(self.song.lyrics_with_chords or "")
        
        self.reset_scroll()
    
    def toggle_play(self):
        """Alterna entre reproducir y pausar"""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            self.play_pause_btn.setText("⏸ Pausar")
            self.scroll_timer.start(50)
        else:
            self.play_pause_btn.setText("▶ Reproducir")
            self.scroll_timer.stop()
    
    def auto_scroll(self):
        """Scroll automático"""
        if not self.is_playing:
            return
        
        speed = self.speed_slider.value()
        pixels_per_frame = speed / 20
        
        # Acumular el movimiento para permitir velocidades muy lentas
        self.scroll_accumulator += pixels_per_frame
        
        scrollbar = self.lyrics_display.verticalScrollBar()
        max_pos = scrollbar.maximum()
        
        # Solo mover cuando hayamos acumulado al menos 1 píxel
        if self.scroll_accumulator >= 1.0:
            pixels_to_move = int(self.scroll_accumulator)
            self.scroll_accumulator -= pixels_to_move
            
            current_pos = scrollbar.value()
            new_pos = current_pos + pixels_to_move
            
            if new_pos >= max_pos:
                new_pos = max_pos
                self.toggle_play()  # Pausar al final
            
            scrollbar.setValue(new_pos)
    
    def reset_scroll(self):
        """Reinicia el scroll"""
        scrollbar = self.lyrics_display.verticalScrollBar()
        scrollbar.setValue(0)
        self.scroll_accumulator = 0.0  # Resetear acumulador
    
    def on_speed_changed(self, value):
        """Actualiza la etiqueta de velocidad"""
        self.speed_label.setText(f"{value} px/s")
        self.saved_speed = value
    
    def save_and_close(self):
        """Guarda la velocidad y cierra"""
        if self.save_speed_checkbox.isChecked():
            self.song.default_scroll_speed = self.saved_speed
        self.accept()
    
    def close_preview(self):
        """Cierra sin guardar"""
        self.reject()
    
    def get_song(self) -> Song:
        """Retorna la canción con la velocidad actualizada"""
        return self.song
    
    def apply_theme(self):
        """Aplica el tema"""
        dark_mode = self.settings.get_dark_mode()
        
        if dark_mode:
            self.setStyleSheet("""
                QDialog {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: 1px solid #3e3e42;
                    padding: 15px;
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
                QLabel {
                    color: #d4d4d4;
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
                QCheckBox {
                    color: #d4d4d4;
                }
            """)
        else:
            self.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #cccccc;
                    padding: 15px;
                }
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
            """)
    
    def closeEvent(self, event):
        """Limpia antes de cerrar"""
        if self.scroll_timer.isActive():
            self.scroll_timer.stop()
        event.accept()
