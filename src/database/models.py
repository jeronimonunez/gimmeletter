"""
Modelos de datos para la aplicación GimmeLetter
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Song:
    """Modelo de canción"""
    id: Optional[int] = None
    title: str = ""
    artist: str = ""
    original_key: str = ""
    lyrics_with_chords: str = ""
    bpm: Optional[int] = None
    default_scroll_speed: int = 50  # Velocidad por defecto en px/seg
    created_date: Optional[str] = None
    
    def __str__(self):
        return f"{self.title} - {self.artist}"


@dataclass
class Set:
    """Modelo de set/setlist"""
    id: Optional[int] = None
    name: str = ""
    created_date: Optional[str] = None
    
    def __str__(self):
        return self.name


@dataclass
class SetSong:
    """Relación entre set y canción con configuración específica"""
    id: Optional[int] = None
    set_id: int = 0
    song_id: int = 0
    order: int = 0
    scroll_speed: int = 50  # Velocidad en píxeles por segundo
    transposition: int = 0  # Semitonos para transponer
