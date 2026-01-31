"""
Gestor de configuración de la aplicación usando QSettings
"""

from PyQt6.QtCore import QSettings


class Settings:
    """Gestiona las preferencias de usuario"""
    
    def __init__(self):
        self.settings = QSettings("GimmeLetter", "GimmeLetter")
    
    # TEMA
    def get_dark_mode(self) -> bool:
        """Obtiene si el modo oscuro está activado"""
        return self.settings.value("theme/dark_mode", True, type=bool)
    
    def set_dark_mode(self, enabled: bool):
        """Activa/desactiva el modo oscuro"""
        self.settings.setValue("theme/dark_mode", enabled)
    
    # FUENTE
    def get_font_size(self) -> int:
        """Obtiene el tamaño de fuente"""
        return self.settings.value("display/font_size", 14, type=int)
    
    def set_font_size(self, size: int):
        """Establece el tamaño de fuente"""
        self.settings.setValue("display/font_size", size)
    
    # SCROLL
    def get_default_scroll_speed(self) -> int:
        """Obtiene la velocidad de scroll por defecto"""
        return self.settings.value("playback/scroll_speed", 50, type=int)
    
    def set_default_scroll_speed(self, speed: int):
        """Establece la velocidad de scroll por defecto"""
        self.settings.setValue("playback/scroll_speed", speed)
    
    # VENTANA
    def get_window_geometry(self) -> bytes:
        """Obtiene la geometría de la ventana"""
        return self.settings.value("window/geometry", b"")
    
    def set_window_geometry(self, geometry: bytes):
        """Guarda la geometría de la ventana"""
        self.settings.setValue("window/geometry", geometry)
