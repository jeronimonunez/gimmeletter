"""
Editor de canciones - Diálogo para crear/editar canciones
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QLabel,
    QSpinBox, QGroupBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..database.models import Song


class SongEditorDialog(QDialog):
    """Diálogo para crear o editar una canción"""
    
    def __init__(self, parent=None, song: Song = None):
        super().__init__(parent)
        
        self.song = song if song else Song()
        self.is_new = song is None
        
        self.init_ui()
        self.load_song_data()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Nueva Canción" if self.is_new else "Editar Canción")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Grupo de información básica
        info_group = QGroupBox("Información de la Canción")
        info_layout = QFormLayout()
        
        # Campo título
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Nombre de la canción")
        info_layout.addRow("Título:*", self.title_input)
        
        # Campo artista
        self.artist_input = QLineEdit()
        self.artist_input.setPlaceholderText("Nombre del artista o banda")
        info_layout.addRow("Artista:", self.artist_input)
        
        # Campos en línea: Tonalidad y BPM
        key_bpm_layout = QHBoxLayout()
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Ej: Am, G, C#m")
        self.key_input.setMaximumWidth(150)
        key_bpm_layout.addWidget(QLabel("Tonalidad:"))
        key_bpm_layout.addWidget(self.key_input)
        
        key_bpm_layout.addSpacing(20)
        
        self.bpm_input = QSpinBox()
        self.bpm_input.setRange(0, 300)
        self.bpm_input.setValue(0)
        self.bpm_input.setSpecialValueText("No especificado")
        self.bpm_input.setMaximumWidth(150)
        key_bpm_layout.addWidget(QLabel("BPM:"))
        key_bpm_layout.addWidget(self.bpm_input)
        
        key_bpm_layout.addStretch()
        
        info_layout.addRow(key_bpm_layout)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Grupo de letra y acordes
        lyrics_group = QGroupBox("Letra y Acordes")
        lyrics_layout = QVBoxLayout()
        
        # Instrucciones
        instructions = QLabel(
            "💡 Escribe los acordes en la línea sobre la letra.\n"
            "Ejemplo:\n"
            "    Am         F          C\n"
            "    Esta es la letra de la canción"
        )
        instructions.setStyleSheet("padding: 8px; background-color: rgba(100, 100, 100, 0.2); border-radius: 4px;")
        lyrics_layout.addWidget(instructions)
        
        # Editor de texto grande
        self.lyrics_input = QTextEdit()
        self.lyrics_input.setAcceptRichText(False)  # Solo texto plano, sin formato
        self.lyrics_input.setPlaceholderText(
            "Escribe o pega aquí la letra con los acordes...\n\n"
            "Ejemplo:\n"
            "[Intro]\n"
            "Am  F  C  G\n\n"
            "[Verso 1]\n"
            "Am              F\n"
            "Primera línea de letra\n"
            "    C                G\n"
            "Segunda línea de letra"
        )
        
        # Fuente monoespaciada para mejor alineación de acordes
        mono_font = QFont("Monaco, Courier New, monospace")
        mono_font.setPointSize(12)
        self.lyrics_input.setFont(mono_font)
        
        lyrics_layout.addWidget(self.lyrics_input)
        lyrics_group.setLayout(lyrics_layout)
        layout.addWidget(lyrics_group)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("💾 Guardar")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept_song)
        save_btn.setMinimumWidth(120)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
    
    def load_song_data(self):
        """Carga los datos de la canción en los campos"""
        if not self.is_new and self.song:
            self.title_input.setText(self.song.title or "")
            self.artist_input.setText(self.song.artist or "")
            self.key_input.setText(self.song.original_key or "")
            self.bpm_input.setValue(self.song.bpm or 0)
            self.lyrics_input.setPlainText(self.song.lyrics_with_chords or "")
    
    def accept_song(self):
        """Valida y acepta el diálogo"""
        # Validación básica
        if not self.title_input.text().strip():
            self.title_input.setFocus()
            self.title_input.setStyleSheet("border: 2px solid red;")
            return
        
        # Actualizar el objeto song con los datos del formulario
        self.song.title = self.title_input.text().strip()
        self.song.artist = self.artist_input.text().strip()
        self.song.original_key = self.key_input.text().strip()
        self.song.bpm = self.bpm_input.value() if self.bpm_input.value() > 0 else None
        self.song.lyrics_with_chords = self.lyrics_input.toPlainText()
        
        self.accept()
    
    def get_song(self) -> Song:
        """Retorna el objeto canción con los datos editados"""
        return self.song
