"""
Diálogo de configuración de la aplicación
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QColorDialog, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from ..utils.settings import Settings


class SettingsDialog(QDialog):
    """Diálogo para configurar preferencias de la aplicación"""
    
    # Señal emitida cuando se guardan los cambios
    settings_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = Settings()
        
        # Colores actuales
        self.player_bg_color = self.settings.get_player_background_color()
        self.player_text_color = self.settings.get_player_text_color()
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializa la interfaz del diálogo"""
        self.setWindowTitle("Configuración")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Grupo de colores del reproductor
        player_colors_group = QGroupBox("🎨 Colores del Reproductor")
        player_colors_layout = QFormLayout()
        
        # Color de fondo
        bg_color_layout = QHBoxLayout()
        self.bg_color_preview = QLabel("      ")
        self.bg_color_preview.setStyleSheet(
            f"background-color: {self.player_bg_color}; border: 1px solid #666;"
        )
        self.bg_color_preview.setFixedSize(60, 30)
        
        bg_color_btn = QPushButton("Elegir Color")
        bg_color_btn.clicked.connect(self.choose_bg_color)
        
        bg_color_layout.addWidget(self.bg_color_preview)
        bg_color_layout.addWidget(bg_color_btn)
        bg_color_layout.addStretch()
        
        player_colors_layout.addRow("Color de Fondo:", bg_color_layout)
        
        # Color de texto
        text_color_layout = QHBoxLayout()
        self.text_color_preview = QLabel("      ")
        self.text_color_preview.setStyleSheet(
            f"background-color: {self.player_text_color}; border: 1px solid #666;"
        )
        self.text_color_preview.setFixedSize(60, 30)
        
        text_color_btn = QPushButton("Elegir Color")
        text_color_btn.clicked.connect(self.choose_text_color)
        
        text_color_layout.addWidget(self.text_color_preview)
        text_color_layout.addWidget(text_color_btn)
        text_color_layout.addStretch()
        
        player_colors_layout.addRow("Color de Texto:", text_color_layout)
        
        # Botón para restaurar valores por defecto
        reset_colors_btn = QPushButton("🔄 Restaurar Colores por Defecto")
        reset_colors_btn.clicked.connect(self.reset_colors)
        player_colors_layout.addRow("", reset_colors_btn)
        
        player_colors_group.setLayout(player_colors_layout)
        layout.addWidget(player_colors_group)
        
        layout.addStretch()
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setDefault(True)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
    def choose_bg_color(self):
        """Abre el diálogo para elegir color de fondo"""
        current_color = QColor(self.player_bg_color)
        color = QColorDialog.getColor(current_color, self, "Elegir Color de Fondo")
        
        if color.isValid():
            self.player_bg_color = color.name()
            self.bg_color_preview.setStyleSheet(
                f"background-color: {self.player_bg_color}; border: 1px solid #666;"
            )
    
    def choose_text_color(self):
        """Abre el diálogo para elegir color de texto"""
        current_color = QColor(self.player_text_color)
        color = QColorDialog.getColor(current_color, self, "Elegir Color de Texto")
        
        if color.isValid():
            self.player_text_color = color.name()
            self.text_color_preview.setStyleSheet(
                f"background-color: {self.player_text_color}; border: 1px solid #666;"
            )
    
    def reset_colors(self):
        """Restaura los colores por defecto"""
        self.player_bg_color = "#1e1e1e"
        self.player_text_color = "#ffffff"
        
        self.bg_color_preview.setStyleSheet(
            f"background-color: {self.player_bg_color}; border: 1px solid #666;"
        )
        self.text_color_preview.setStyleSheet(
            f"background-color: {self.player_text_color}; border: 1px solid #666;"
        )
    
    def save_settings(self):
        """Guarda la configuración y cierra el diálogo"""
        self.settings.set_player_background_color(self.player_bg_color)
        self.settings.set_player_text_color(self.player_text_color)
        
        # Emitir señal de cambio
        self.settings_changed.emit()
        
        self.accept()
