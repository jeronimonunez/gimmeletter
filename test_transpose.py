#!/usr/bin/env python
"""Script de prueba para la transposición de acordes"""

from src.utils.chord_transposer import ChordTransposer

print('=== NOTACIÓN INGLESA ===')
print('Original: C Am F G')
print('Transponer +2:', ChordTransposer.transpose_text('C Am F G', 2, False))
print('Transponer -3:', ChordTransposer.transpose_text('C Am F G', -3, False))
print()

# Prueba con acorde individual
print('C -> +5 semitonos:', ChordTransposer.transpose_chord('C', 5, False))
print('Am7 -> +2 semitonos:', ChordTransposer.transpose_chord('Am7', 2, False))
print('G#m -> -1 semitono:', ChordTransposer.transpose_chord('G#m', -1, False))
print()

# Prueba con notación latina
print('=== NOTACIÓN LATINA ===')
print('Original: Do Lam Fa Sol')
print('Transponer +2:', ChordTransposer.transpose_text('Do Lam Fa Sol', 2, True))
print('Transponer -3:', ChordTransposer.transpose_text('Do Lam Fa Sol', -3, True))
print()

# Prueba con texto completo
texto_prueba = """Do        Lam
Primera linea de letra
Fa         Sol
Segunda linea de letra"""

print('Texto con letra y acordes (notación latina):')
print(texto_prueba)
print('\nTranspuesto +3 semitonos:')
print(ChordTransposer.transpose_text(texto_prueba, 3, True))
print()

# Prueba con acordes ingleses y letra
texto_ingles = """C          Am
This is the first line
F          G
This is the second line"""

print('Texto con letra y acordes (notación inglesa):')
print(texto_ingles)
print('\nTranspuesto +2 semitonos:')
print(ChordTransposer.transpose_text(texto_ingles, 2, False))
print()

# Prueba con líneas de acordes más realistas
texto_realista = """C                 Am
Hoy me levante pensando en ti
F                  G
Y no pude dejar de sonreir
C                 Am
Tu amor es como el sol
F                  G                C
Que ilumina todo mi corazon"""

print('=== TEXTO MÁS REALISTA ===')
print('Original:')
print(texto_realista)
print('\nTranspuesto +2:')
resultado = ChordTransposer.transpose_text(texto_realista, 2, False)
print(resultado)

# DEBUG: ver qué líneas se detectan como acordes
print('\n=== DEBUG: Detección de líneas ===')
for i, line in enumerate(texto_realista.split('\n')):
    words = line.split()
    is_chord = ChordTransposer._is_chord_line(words, False)
    print(f"Línea {i}: {'[ACORDES]' if is_chord else '[LETRA]'} - {line[:50]}")

