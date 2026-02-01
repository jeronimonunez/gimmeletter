#!/usr/bin/env python
"""Script de prueba para verificar que se preservan los espacios"""

from src.utils.chord_transposer import ChordTransposer

# Ejemplo del usuario con espacios importantes
texto_usuario = """Bm                 A                           G                  D
Yo sé que algunas veces me equivoco demasiado"""

print('=== EJEMPLO DEL USUARIO ===')
print('Original:')
print(texto_usuario)
print()

resultado = ChordTransposer.transpose_text(texto_usuario, 2, False)
print('Transpuesto +2:')
print(resultado)
print()

print('Verificación de espacios:')
print('Línea original de acordes:', repr(texto_usuario.split('\n')[0]))
print('Línea transpuesta:', repr(resultado.split('\n')[0]))
print()

# Ejemplo más completo
texto_completo = """Bm                 A
Yo sé que algunas veces
G                  D
me equivoco demasiado
Bm                 A
pero siempre vuelvo
G                  D
a intentarlo otra vez"""

print('=== CANCIÓN COMPLETA ===')
print('Original:')
print(texto_completo)
print()
print('Transpuesto +2:')
print(ChordTransposer.transpose_text(texto_completo, 2, False))
