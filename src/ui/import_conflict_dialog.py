"""
Diálogo para resolver conflictos al importar canciones
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup, QTextEdit
)
from PyQt6.QtCore import Qt


class ImportConflictDialog(QDialog):
    """Diálogo para resolver conflictos cuando se importa una canción similar"""
    
    REPLACE = 1
    CREATE_NEW = 2
    SKIP = 3
    
    def __init__(self, existing_song, imported_song, parent=None):
        super().__init__(parent)
        
        self.existing_song = existing_song
        self.imported_song = imported_song
        self.result_action = None
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Conflicto de Importación")
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Mensaje principal
        title_label = QLabel("Se encontró una canción similar")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # Info de canción existente
        existing_group = QLabel("Canción existente en la base de datos:")
        existing_group.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(existing_group)
        
        existing_info = QTextEdit()
        existing_info.setReadOnly(True)
        existing_info.setMaximumHeight(120)
        existing_info.setPlainText(self._format_song_info(self.existing_song))
        layout.addWidget(existing_info)
        
        # Info de canción a importar
        imported_group = QLabel("Canción a importar:")
        imported_group.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(imported_group)
        
        imported_info = QTextEdit()
        imported_info.setReadOnly(True)
        imported_info.setMaximumHeight(120)
        imported_info.setPlainText(self._format_song_info(self.imported_song))
        layout.addWidget(imported_info)
        
        # Opciones
        options_label = QLabel("¿Qué deseas hacer?")
        options_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(options_label)
        
        self.button_group = QButtonGroup()
        
        self.replace_radio = QRadioButton("Reemplazar la canción existente con la importada")
        self.button_group.addButton(self.replace_radio, self.REPLACE)
        layout.addWidget(self.replace_radio)
        
        self.create_new_radio = QRadioButton("Crear como canción nueva (se agregará un número al nombre)")
        self.button_group.addButton(self.create_new_radio, self.CREATE_NEW)
        layout.addWidget(self.create_new_radio)
        
        self.skip_radio = QRadioButton("Omitir esta canción (no importar)")
        self.button_group.addButton(self.skip_radio, self.SKIP)
        layout.addWidget(self.skip_radio)
        
        # Seleccionar opción por defecto
        self.create_new_radio.setChecked(True)
        
        layout.addStretch()
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar Importación")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("Continuar")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self.accept_choice)
        buttons_layout.addWidget(ok_btn)
        
        layout.addLayout(buttons_layout)
    
    def _format_song_info(self, song_dict):
        """Formatea la información de la canción para mostrar"""
        info = f"Título: {song_dict.get('title', 'N/A')}\n"
        info += f"Artista: {song_dict.get('artist', 'N/A')}\n"
        info += f"Tono original: {song_dict.get('original_key', 'N/A')}\n"
        info += f"BPM: {song_dict.get('bpm', 'N/A')}\n"
        info += f"Velocidad scroll: {song_dict.get('default_scroll_speed', 50)} px/s\n"
        
        # Mostrar primeras líneas de la letra
        lyrics = song_dict.get('lyrics_with_chords', '')
        lines = lyrics.split('\n')[:3]
        if lines:
            info += f"\nPrimeras líneas:\n{chr(10).join(lines)}"
            if len(lyrics.split('\n')) > 3:
                info += "\n..."
        
        return info
    
    def accept_choice(self):
        """Acepta la opción seleccionada"""
        checked_button = self.button_group.checkedButton()
        if checked_button:
            self.result_action = self.button_group.id(checked_button)
            self.accept()
    
    def get_action(self):
        """Retorna la acción seleccionada"""
        return self.result_action
