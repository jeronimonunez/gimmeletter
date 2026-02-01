"""
Utilidades para exportar e importar canciones y sets
"""

import json
import re
from datetime import datetime
from difflib import SequenceMatcher


def normalize_song_title(title):
    """
    Normaliza un título de canción para comparación
    - Convierte a minúsculas
    - Elimina espacios extras
    - Elimina números entre paréntesis al final (1), (2), etc.
    - Elimina caracteres especiales
    """
    # Convertir a minúsculas
    normalized = title.lower().strip()
    
    # Eliminar números entre paréntesis al final: " (1)", " (2)", etc.
    normalized = re.sub(r'\s*\(\d+\)\s*$', '', normalized)
    
    # Eliminar espacios múltiples
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized


def songs_are_similar(title1, title2, threshold=0.85):
    """
    Determina si dos títulos de canciones son similares
    usando SequenceMatcher y normalización
    
    Args:
        title1: Primer título
        title2: Segundo título
        threshold: Umbral de similitud (0-1), por defecto 0.85
    
    Returns:
        bool: True si son similares
    """
    norm1 = normalize_song_title(title1)
    norm2 = normalize_song_title(title2)
    
    # Si son exactamente iguales después de normalizar
    if norm1 == norm2:
        return True
    
    # Calcular similitud
    ratio = SequenceMatcher(None, norm1, norm2).ratio()
    return ratio >= threshold


def export_songs_to_json(songs):
    """
    Exporta lista de canciones a formato JSON
    
    Args:
        songs: Lista de objetos Song
    
    Returns:
        dict: Diccionario con estructura JSON
    """
    export_data = {
        'export_type': 'songs',
        'export_date': datetime.now().isoformat(),
        'version': '1.0',
        'songs': []
    }
    
    for song in songs:
        song_data = {
            'title': song.title,
            'artist': song.artist,
            'lyrics_with_chords': song.lyrics_with_chords,
            'bpm': song.bpm,
            'original_key': song.original_key,
            'default_scroll_speed': song.default_scroll_speed
        }
        export_data['songs'].append(song_data)
    
    return export_data


def export_sets_to_json(sets_with_songs, db_manager):
    """
    Exporta sets completos con sus canciones y configuraciones
    
    Args:
        sets_with_songs: Lista de objetos Set
        db_manager: DatabaseManager para obtener detalles de canciones
    
    Returns:
        dict: Diccionario con estructura JSON
    """
    export_data = {
        'export_type': 'sets',
        'export_date': datetime.now().isoformat(),
        'version': '1.0',
        'sets': []
    }
    
    for set_obj in sets_with_songs:
        # Obtener canciones del set
        set_songs_rows = db_manager.get_set_songs(set_obj.id)
        
        songs_in_set = []
        for row in set_songs_rows:
            song_data = {
                'title': row['title'],
                'artist': row['artist'],
                'lyrics_with_chords': row['lyrics_with_chords'],
                'bpm': row['bpm'],
                'original_key': row['original_key'],
                'default_scroll_speed': row['default_scroll_speed'],
                # Configuración específica del set
                'scroll_speed': row['scroll_speed'],
                'transposition': row['transposition'],
                'song_order': row['song_order']
            }
            songs_in_set.append(song_data)
        
        set_data = {
            'name': set_obj.name,
            'songs': songs_in_set
        }
        export_data['sets'].append(set_data)
    
    return export_data


def save_json_to_file(data, file_path):
    """Guarda datos JSON en archivo"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json_from_file(file_path):
    """Carga datos JSON desde archivo"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def validate_import_data(data):
    """
    Valida que los datos importados tengan la estructura correcta
    
    Returns:
        tuple: (is_valid, error_message, export_type)
    """
    if not isinstance(data, dict):
        return False, "El archivo no tiene formato JSON válido", None
    
    if 'export_type' not in data:
        return False, "El archivo no contiene información de tipo de exportación", None
    
    export_type = data['export_type']
    
    if export_type == 'songs':
        if 'songs' not in data or not isinstance(data['songs'], list):
            return False, "El archivo no contiene una lista de canciones válida", None
    
    elif export_type == 'sets':
        if 'sets' not in data or not isinstance(data['sets'], list):
            return False, "El archivo no contiene una lista de sets válida", None
    
    else:
        return False, f"Tipo de exportación desconocido: {export_type}", None
    
    return True, None, export_type
