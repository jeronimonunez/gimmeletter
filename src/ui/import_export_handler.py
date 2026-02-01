"""
Handlers para importar y exportar canciones y sets
"""

from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QDialog

from ..database.models import Song, Set
from ..utils.import_export import songs_are_similar


class ImportExportHandler:
    """Manejador de operaciones de importación y exportación"""
    
    def __init__(self, main_window, db_manager):
        self.main_window = main_window
        self.db = db_manager
    
    def import_songs(self, songs_data):
        """Importa canciones con manejo de conflictos"""
        from .import_conflict_dialog import ImportConflictDialog
        
        imported_count = 0
        skipped_count = 0
        replaced_count = 0
        
        for song_dict in songs_data:
            # Buscar canción similar en la base de datos
            similar_song = None
            for existing_song in self.main_window.songs:
                if songs_are_similar(existing_song.title, song_dict['title']):
                    similar_song = existing_song
                    break
            
            if similar_song:
                # Hay conflicto, mostrar diálogo
                existing_dict = {
                    'title': similar_song.title,
                    'artist': similar_song.artist,
                    'lyrics_with_chords': similar_song.lyrics_with_chords,
                    'bpm': similar_song.bpm,
                    'original_key': similar_song.original_key,
                    'default_scroll_speed': similar_song.default_scroll_speed
                }
                
                dialog = ImportConflictDialog(existing_dict, song_dict, self.main_window)
                
                if dialog.exec() != QDialog.DialogCode.Accepted:
                    # Usuario canceló
                    break
                
                action = dialog.get_action()
                
                if action == ImportConflictDialog.SKIP:
                    skipped_count += 1
                    continue
                
                elif action == ImportConflictDialog.REPLACE:
                    # Actualizar canción existente
                    similar_song.title = song_dict['title']
                    similar_song.artist = song_dict['artist']
                    similar_song.lyrics_with_chords = song_dict['lyrics_with_chords']
                    similar_song.bpm = song_dict['bpm']
                    similar_song.original_key = song_dict['original_key']
                    similar_song.default_scroll_speed = song_dict.get('default_scroll_speed', 50)
                    
                    self.db.update_song(similar_song)
                    replaced_count += 1
                
                elif action == ImportConflictDialog.CREATE_NEW:
                    # Crear nueva canción con nombre modificado
                    new_title = self._get_unique_song_title(song_dict['title'])
                    song_dict['title'] = new_title
                    self._create_song_from_dict(song_dict)
                    imported_count += 1
            
            else:
                # No hay conflicto, crear directamente
                self._create_song_from_dict(song_dict)
                imported_count += 1
        
        # Mostrar resumen
        summary = f"Importación completada:\n\n"
        summary += f"• Canciones nuevas importadas: {imported_count}\n"
        summary += f"• Canciones reemplazadas: {replaced_count}\n"
        summary += f"• Canciones omitidas: {skipped_count}"
        
        QMessageBox.information(self.main_window, "Importación Completa", summary)
        
        return imported_count + replaced_count > 0  # True si hubo cambios
    
    def import_sets(self, sets_data):
        """Importa sets con sus canciones"""
        imported_sets = 0
        imported_songs = 0
        
        for set_dict in sets_data:
            # Crear el set
            new_set = Set(
                name=set_dict['name'],
                created_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            set_id = self.db.add_set(new_set)
            imported_sets += 1
            
            # Importar canciones del set
            for song_config in set_dict['songs']:
                # Buscar si la canción ya existe
                existing_song = None
                for song in self.main_window.songs:
                    if songs_are_similar(song.title, song_config['title']):
                        existing_song = song
                        break
                
                if not existing_song:
                    # Crear la canción
                    song_dict = {
                        'title': song_config['title'],
                        'artist': song_config['artist'],
                        'lyrics_with_chords': song_config['lyrics_with_chords'],
                        'bpm': song_config['bpm'],
                        'original_key': song_config['original_key'],
                        'default_scroll_speed': song_config.get('default_scroll_speed', 50)
                    }
                    song_id = self._create_song_from_dict(song_dict)
                    imported_songs += 1
                else:
                    song_id = existing_song.id
                
                # Agregar al set con configuración
                self.db.add_song_to_set(
                    set_id,
                    song_id,
                    song_config.get('song_order', 0),
                    song_config.get('scroll_speed', 50),
                    song_config.get('transposition', 0)
                )
        
        # Mostrar resumen
        summary = f"Importación completada:\n\n"
        summary += f"• Sets importados: {imported_sets}\n"
        summary += f"• Canciones nuevas: {imported_songs}"
        
        QMessageBox.information(self.main_window, "Importación Completa", summary)
        
        return True  # Hubo cambios
    
    def _create_song_from_dict(self, song_dict):
        """Crea una canción desde un diccionario y la guarda en la BD"""
        new_song = Song(
            title=song_dict['title'],
            artist=song_dict['artist'],
            lyrics_with_chords=song_dict['lyrics_with_chords'],
            bpm=song_dict.get('bpm'),
            original_key=song_dict.get('original_key'),
            default_scroll_speed=song_dict.get('default_scroll_speed', 50),
            created_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        return self.db.add_song(new_song)
    
    def _get_unique_song_title(self, base_title):
        """Genera un título único agregando un número si es necesario"""
        import re
        
        # Eliminar cualquier número al final
        base_title = re.sub(r'\s*\(\d+\)\s*$', '', base_title).strip()
        
        # Buscar el próximo número disponible
        counter = 1
        while True:
            new_title = f"{base_title} ({counter})"
            # Verificar si existe
            exists = False
            for song in self.main_window.songs:
                if songs_are_similar(song.title, new_title):
                    exists = True
                    break
            
            if not exists:
                return new_title
            
            counter += 1
