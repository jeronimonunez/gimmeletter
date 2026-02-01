"""
Gestor de base de datos SQLite
"""

import sqlite3
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from .models import Song, Set, SetSong


class DatabaseManager:
    """Gestiona todas las operaciones de base de datos"""
    
    def __init__(self, db_path: str = "gimmeletter.db"):
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        self.init_database()
    
    def init_database(self):
        """Inicializa la base de datos y crea las tablas si no existen"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        
        cursor = self.connection.cursor()
        
        # Tabla de canciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT,
                original_key TEXT,
                lyrics_with_chords TEXT,
                bpm INTEGER,
                default_scroll_speed INTEGER DEFAULT 50,
                created_date TEXT
            )
        """)
        
        # Migración: Agregar columna default_scroll_speed si no existe
        try:
            cursor.execute("ALTER TABLE songs ADD COLUMN default_scroll_speed INTEGER DEFAULT 50")
            self.connection.commit()
        except sqlite3.OperationalError:
            # La columna ya existe, ignorar
            pass
        
        # Tabla de sets
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_date TEXT
            )
        """)
        
        # Tabla de relación set-canción
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS set_songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                set_id INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                song_order INTEGER NOT NULL,
                scroll_speed INTEGER DEFAULT 50,
                transposition INTEGER DEFAULT 0,
                FOREIGN KEY (set_id) REFERENCES sets (id) ON DELETE CASCADE,
                FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE
            )
        """)
        
        self.connection.commit()
    
    # OPERACIONES DE CANCIONES
    
    def add_song(self, song: Song) -> int:
        """Agrega una canción y retorna su ID"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO songs (title, artist, original_key, lyrics_with_chords, bpm, default_scroll_speed, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            song.title,
            song.artist,
            song.original_key,
            song.lyrics_with_chords,
            song.bpm,
            song.default_scroll_speed,
            datetime.now().isoformat()
        ))
        self.connection.commit()
        return cursor.lastrowid
    
    def get_song(self, song_id: int) -> Optional[Song]:
        """Obtiene una canción por ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
        row = cursor.fetchone()
        
        if row:
            # Manejar columnas que pueden no existir en bases de datos antiguas
            try:
                default_scroll_speed = row['default_scroll_speed']
            except (KeyError, IndexError):
                default_scroll_speed = 50
            
            return Song(
                id=row['id'],
                title=row['title'],
                artist=row['artist'],
                original_key=row['original_key'],
                lyrics_with_chords=row['lyrics_with_chords'],
                bpm=row['bpm'],
                default_scroll_speed=default_scroll_speed,
                created_date=row['created_date']
            )
        return None
    
    def get_all_songs(self) -> List[Song]:
        """Obtiene todas las canciones"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM songs ORDER BY title")
        rows = cursor.fetchall()
        
        songs = []
        for row in rows:
            # Manejar columnas que pueden no existir en bases de datos antiguas
            try:
                default_scroll_speed = row['default_scroll_speed']
            except (KeyError, IndexError):
                default_scroll_speed = 50
            
            songs.append(Song(
                id=row['id'],
                title=row['title'],
                artist=row['artist'],
                original_key=row['original_key'],
                lyrics_with_chords=row['lyrics_with_chords'],
                bpm=row['bpm'],
                default_scroll_speed=default_scroll_speed,
                created_date=row['created_date']
            ))
        
        return songs
    
    def update_song(self, song: Song):
        """Actualiza una canción existente"""
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE songs
            SET title = ?, artist = ?, original_key = ?, 
                lyrics_with_chords = ?, bpm = ?, default_scroll_speed = ?
            WHERE id = ?
        """, (
            song.title,
            song.artist,
            song.original_key,
            song.lyrics_with_chords,
            song.bpm,
            song.default_scroll_speed,
            song.id
        ))
        self.connection.commit()
    
    def delete_song(self, song_id: int):
        """Elimina una canción"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM songs WHERE id = ?", (song_id,))
        self.connection.commit()
    
    # OPERACIONES DE SETS
    
    def add_set(self, set_obj: Set) -> int:
        """Agrega un set y retorna su ID"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO sets (name, created_date)
            VALUES (?, ?)
        """, (set_obj.name, datetime.now().isoformat()))
        self.connection.commit()
        return cursor.lastrowid
    
    def get_all_sets(self) -> List[Set]:
        """Obtiene todos los sets"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sets ORDER BY created_date DESC")
        rows = cursor.fetchall()
        
        return [Set(
            id=row['id'],
            name=row['name'],
            created_date=row['created_date']
        ) for row in rows]
    
    def get_set(self, set_id: int) -> Set:
        """Obtiene un set por su ID"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM sets WHERE id = ?", (set_id,))
        row = cursor.fetchone()
        
        if row:
            return Set(
                id=row['id'],
                name=row['name'],
                created_date=row['created_date']
            )
        return None
    
    def delete_set(self, set_id: int):
        """Elimina un set"""
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM sets WHERE id = ?", (set_id,))
        self.connection.commit()
    
    # OPERACIONES DE SET-CANCIONES
    
    def add_song_to_set(self, set_song: SetSong) -> int:
        """Agrega una canción a un set"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO set_songs (set_id, song_id, song_order, scroll_speed, transposition)
            VALUES (?, ?, ?, ?, ?)
        """, (
            set_song.set_id,
            set_song.song_id,
            set_song.order,
            set_song.scroll_speed,
            set_song.transposition
        ))
        self.connection.commit()
        return cursor.lastrowid
    
    def get_set_songs(self, set_id: int) -> List[tuple]:
        """Obtiene todas las canciones de un set con su configuración"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT s.*, ss.scroll_speed, ss.transposition, ss.song_order
            FROM songs s
            JOIN set_songs ss ON s.id = ss.song_id
            WHERE ss.set_id = ?
            ORDER BY ss.song_order
        """, (set_id,))
        
        return cursor.fetchall()
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.connection:
            self.connection.close()
