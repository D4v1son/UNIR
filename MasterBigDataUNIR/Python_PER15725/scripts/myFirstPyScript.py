
import sys

print("\n")

print(f"¡Hola, Mundo desde Python {sys.version}!\n")
print(f"Estoy usando Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\n")

print(f"Ubicación del intérprete: {sys.executable}\n")

try:
    import math
    import random
    import datetime
    print("Módulos básicos importados correctamente.\n")
except ImportError as e:
    print(f"Error al importar módulos: {e}\n")

"""
___
Lo anterior son una serie de comprobaciones del entorno virtual.
Ahora pasamos a un primer programa que incluye algunas características básicas de Python.
___
"""

# Programa de bienvenida mejorado
import random
from datetime import datetime

# Obtener información del sistema
nombre_usuario = input("¿Cómo te llamas? ")

# Obtener la hora actual
hora_actual = datetime.now()
hora_del_dia = hora_actual.hour

# Determinar el saludo según la hora
if 5 <= hora_del_dia < 12:
    saludo = "Buenos días"
elif 12 <= hora_del_dia < 20:
    saludo = "Buenas tardes"
else:
    saludo = "Buenas noches"

# Lista de mensajes motivadores
mensajes = [
    "¡El aprendizaje es un viaje emocionante!",
    "Cada línea de código te acerca a ser un experto.",
    "La programación es como la magia moderna.",
    "Con Python, las posibilidades son infinitas."
]

# Seleccionar un mensaje aleatorio
mensaje_aleatorio = random.choice(mensajes)

# Mostrar el mensaje personalizado
print(f"\n{saludo}, {nombre_usuario}!")
print(f"Hoy es {hora_actual.strftime('%d/%m/%Y')} y son las {hora_actual.strftime('%H:%M')}.")
print(f"\nMensaje para ti: {mensaje_aleatorio}")
print("\n¡Bienvenido/a al mundo de Python!")
