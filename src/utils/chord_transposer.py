"""
Utilidad para transponer acordes musicales
"""

import re


class ChordTransposer:
    """Transpone acordes musicales a diferentes tonalidades"""
    
    # Notas en notación latina e inglesa
    NOTES_LATIN = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
    NOTES_ENGLISH = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Bemoles equivalentes
    FLATS_LATIN = {'Reb': 'Do#', 'Mib': 'Re#', 'Solb': 'Fa#', 'Lab': 'Sol#', 'Sib': 'La#'}
    FLATS_ENGLISH = {'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'}
    
    @classmethod
    def transpose_chord(cls, chord: str, semitones: int, use_latin: bool = False) -> str:
        """
        Transpone un acorde individual
        
        Args:
            chord: El acorde a transponer (ej: "Am7", "C#m", "Fa")
            semitones: Número de semitonos a transponer (positivo = arriba, negativo = abajo)
            use_latin: Si True usa notación latina (Do, Re, Mi...), si False usa inglesa (C, D, E...)
        
        Returns:
            El acorde transpuesto
        """
        if not chord or semitones == 0:
            return chord
        
        notes = cls.NOTES_LATIN if use_latin else cls.NOTES_ENGLISH
        flats = cls.FLATS_LATIN if use_latin else cls.FLATS_ENGLISH
        
        # Patrón para detectar la nota base del acorde
        if use_latin:
            pattern = r'^(Do|Re|Mi|Fa|Sol|La|Si)(#|b)?'
        else:
            pattern = r'^([A-G])(#|b)?'
        
        match = re.match(pattern, chord, re.IGNORECASE)
        if not match:
            return chord
        
        note = match.group(0)
        suffix = chord[len(note):]  # El resto del acorde (m, 7, sus4, etc.)
        
        # Convertir bemoles a sostenidos
        if note in flats:
            note = flats[note]
        
        # Encontrar la posición de la nota
        try:
            # Preservar el case original
            note_upper = note[0].upper() + note[1:] if len(note) > 1 else note.upper()
            current_index = notes.index(note_upper)
        except ValueError:
            return chord
        
        # Calcular nueva posición
        new_index = (current_index + semitones) % 12
        new_note = notes[new_index]
        
        # Preservar el case original si era minúscula
        if note[0].islower():
            new_note = new_note.lower()
        
        return new_note + suffix
    
    @classmethod
    def transpose_text(cls, text: str, semitones: int, use_latin: bool = False) -> str:
        """
        Transpone todos los acordes en un texto
        
        Args:
            text: Texto con letra y acordes
            semitones: Número de semitonos a transponer
            use_latin: Si True usa notación latina
        
        Returns:
            Texto con acordes transpuestos
        """
        if semitones == 0:
            return text
        
        lines = text.split('\n')
        result = []
        
        for line in lines:
            # Detectar si la línea contiene acordes (heurística simple)
            # Una línea de acordes típicamente tiene espacios y acordes cortos
            words = line.split()
            
            if cls._is_chord_line(words, use_latin):
                # Transponer cada palabra (acorde)
                transposed_words = [
                    cls.transpose_chord(word, semitones, use_latin) 
                    for word in words
                ]
                result.append(' '.join(transposed_words))
            else:
                # Es una línea de letra, mantenerla igual
                result.append(line)
        
        return '\n'.join(result)
    
    @classmethod
    def _is_chord_line(cls, words: list, use_latin: bool = False) -> bool:
        """Determina si una línea contiene acordes"""
        if not words:
            return False
        
        if use_latin:
            chord_pattern = r'^(Do|Re|Mi|Fa|Sol|La|Si)(#|b)?(m|M|maj|min|dim|aug|sus|add|\d)*'
        else:
            chord_pattern = r'^[A-G](#|b)?(m|M|maj|min|dim|aug|sus|add|\d)*'
        
        # Si más del 50% de las palabras parecen acordes, es una línea de acordes
        chord_count = sum(1 for word in words if re.match(chord_pattern, word, re.IGNORECASE))
        
        return chord_count / len(words) >= 0.5
    
    @classmethod
    def get_key_name(cls, semitones_from_c: int, use_latin: bool = False) -> str:
        """Obtiene el nombre de la tonalidad dado un número de semitonos desde Do/C"""
        notes = cls.NOTES_LATIN if use_latin else cls.NOTES_ENGLISH
        return notes[semitones_from_c % 12]
