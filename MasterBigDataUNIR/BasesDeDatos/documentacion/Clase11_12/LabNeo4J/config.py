"""
Configuración centralizada para el taller de Neo4j
Permite personalizar la conexión a Neo4j y otros parámetros
Autor: Marlon Cárdenas Bonett 2025
"""

# Configuración de conexión a Neo4j
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "abc123456"  # Cambiar por tu contraseña
NEO4J_DATABASE = "fraudedb"  # Base de datos por defecto

# Configuración para generación de datos
NUM_EMPRESAS = 50
NUM_DIRECTIVOS = 30
NUM_TRANSACCIONES = 200
NUM_CUENTAS_BANCARIAS = 40

# Semilla para reproducibilidad
RANDOM_SEED = 42

# Configuración de visualización
PLOT_STYLE = "seaborn-v0_8-darkgrid"
FIGURE_SIZE = (12, 8)
