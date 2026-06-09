"""
Script para cargar los datos generados en Neo4j
Crea nodos, relaciones, índices y constraints
"""

import json
from neo4j import GraphDatabase
import config

# Conectar a Neo4j
driver = GraphDatabase.driver(
    config.NEO4J_URI,
    auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
)

def ejecutar_consulta(query, parametros=None):
    """
    Ejecuta una consulta Cypher
    """
    with driver.session(database=config.NEO4J_DATABASE) as session:
        resultado = session.run(query, parametros or {})
        return [record.data() for record in resultado]


def limpiar_base_datos():
    """
    Elimina todos los nodos y relaciones
    """
    print("🗑️  Limpiando base de datos...")
    ejecutar_consulta("MATCH (n) DETACH DELETE n")
    print("   ✓ Base de datos limpiada")


def crear_constraints_e_indices():
    """
    Crea constraints e índices para optimizar consultas
    """
    print("🔧 Creando constraints e índices...")
    
    constraints = [
        # Constraints de unicidad
        "CREATE CONSTRAINT empresa_nif IF NOT EXISTS FOR (e:Empresa) REQUIRE e.nif IS UNIQUE",
        "CREATE CONSTRAINT directivo_dni IF NOT EXISTS FOR (d:Directivo) REQUIRE d.dni IS UNIQUE",
        "CREATE CONSTRAINT cuenta_iban IF NOT EXISTS FOR (c:CuentaBancaria) REQUIRE c.iban IS UNIQUE",
        
        # Índices para búsquedas
        "CREATE INDEX empresa_nombre IF NOT EXISTS FOR (e:Empresa) ON (e.nombre)",
        "CREATE INDEX empresa_pais IF NOT EXISTS FOR (e:Empresa) ON (e.pais)",
        "CREATE INDEX directivo_nombre IF NOT EXISTS FOR (d:Directivo) ON (d.nombre)",
    ]
    
    for constraint in constraints:
        try:
            ejecutar_consulta(constraint)
        except Exception as e:
            # Algunos constraints pueden ya existir
            pass
    
    print("   ✓ Constraints e índices creados")


def cargar_empresas(empresas):
    """
    Carga los nodos de empresas
    """
    print(f"🏢 Cargando {len(empresas)} empresas...")
    
    query = """
    UNWIND $empresas AS emp
    CREATE (e:Empresa {
        id: emp.id,
        nif: emp.nif,
        nombre: emp.nombre,
        pais: emp.pais,
        fecha_constitucion: date(emp.fecha_constitucion),
        capital_social: emp.capital_social,
        sector: emp.sector,
        empleados: emp.empleados,
        es_fantasma: emp.es_fantasma,
        direccion: emp.direccion
    })
    """
    
    ejecutar_consulta(query, {'empresas': empresas})
    print(f"   ✓ {len(empresas)} empresas cargadas")


def cargar_directivos(directivos):
    """
    Carga los nodos de directivos
    """
    print(f"👔 Cargando {len(directivos)} directivos...")
    
    query = """
    UNWIND $directivos AS dir
    CREATE (d:Directivo {
        id: dir.id,
        dni: dir.dni,
        nombre: dir.nombre,
        fecha_nacimiento: date(dir.fecha_nacimiento),
        nacionalidad: dir.nacionalidad
    })
    """
    
    ejecutar_consulta(query, {'directivos': directivos})
    print(f"   ✓ {len(directivos)} directivos cargados")


def cargar_cuentas_bancarias(cuentas):
    """
    Carga los nodos de cuentas bancarias
    """
    print(f"🏦 Cargando {len(cuentas)} cuentas bancarias...")
    
    query = """
    UNWIND $cuentas AS cta
    CREATE (c:CuentaBancaria {
        id: cta.id,
        iban: cta.iban,
        banco: cta.banco,
        fecha_apertura: date(cta.fecha_apertura)
    })
    """
    
    ejecutar_consulta(query, {'cuentas': cuentas})
    print(f"   ✓ {len(cuentas)} cuentas bancarias cargadas")


def cargar_administraciones(administraciones):
    """
    Crea las relaciones ADMINISTRA entre directivos y empresas
    """
    print(f"🔗 Creando {len(administraciones)} relaciones ADMINISTRA...")
    
    query = """
    UNWIND $administraciones AS adm
    MATCH (d:Directivo {id: adm.directivo_id})
    MATCH (e:Empresa {id: adm.empresa_id})
    CREATE (d)-[:ADMINISTRA {
        cargo: adm.cargo,
        fecha_inicio: date(adm.fecha_inicio)
    }]->(e)
    """
    
    ejecutar_consulta(query, {'administraciones': administraciones})
    print(f"   ✓ {len(administraciones)} relaciones ADMINISTRA creadas")


def cargar_relaciones_cuentas(cuentas):
    """
    Crea las relaciones TIENE_CUENTA entre empresas y cuentas bancarias
    """
    print(f"🔗 Creando relaciones TIENE_CUENTA...")
    
    query = """
    UNWIND $cuentas AS cta
    MATCH (e:Empresa {id: cta.empresa_id})
    MATCH (c:CuentaBancaria {id: cta.id})
    CREATE (e)-[:TIENE_CUENTA]->(c)
    """
    
    ejecutar_consulta(query, {'cuentas': cuentas})
    print(f"   ✓ Relaciones TIENE_CUENTA creadas")


def cargar_transacciones(transacciones):
    """
    Crea las relaciones EMITE_FACTURA entre empresas
    """
    print(f"💰 Creando {len(transacciones)} relaciones EMITE_FACTURA...")
    
    # Cargar en lotes para mejor rendimiento
    batch_size = 100
    for i in range(0, len(transacciones), batch_size):
        batch = transacciones[i:i+batch_size]
        
        query = """
        UNWIND $transacciones AS tx
        MATCH (emisor:Empresa {id: tx.emisor_id})
        MATCH (receptor:Empresa {id: tx.receptor_id})
        CREATE (emisor)-[:EMITE_FACTURA {
            numero_factura: tx.numero_factura,
            fecha: date(tx.fecha),
            monto_base: tx.monto_base,
            iva: tx.iva,
            monto_total: tx.monto_total,
            concepto: tx.concepto,
            es_intracomunitaria: tx.es_intracomunitaria
        }]->(receptor)
        """
        
        ejecutar_consulta(query, {'transacciones': batch})
    
    print(f"   ✓ {len(transacciones)} relaciones EMITE_FACTURA creadas")


def verificar_carga():
    """
    Verifica que los datos se hayan cargado correctamente
    """
    print("\\n✅ Verificando carga de datos...")
    
    consultas_verificacion = [
        ("Empresas", "MATCH (e:Empresa) RETURN count(e) AS total"),
        ("Directivos", "MATCH (d:Directivo) RETURN count(d) AS total"),
        ("Cuentas Bancarias", "MATCH (c:CuentaBancaria) RETURN count(c) AS total"),
        ("Relaciones ADMINISTRA", "MATCH ()-[r:ADMINISTRA]->() RETURN count(r) AS total"),
        ("Relaciones TIENE_CUENTA", "MATCH ()-[r:TIENE_CUENTA]->() RETURN count(r) AS total"),
        ("Relaciones EMITE_FACTURA", "MATCH ()-[r:EMITE_FACTURA]->() RETURN count(r) AS total"),
    ]
    
    print()
    for nombre, query in consultas_verificacion:
        resultado = ejecutar_consulta(query)
        total = resultado[0]['total']
        print(f"   {nombre}: {total}")


def main():
    """
    Función principal
    """
    print("=" * 70)
    print("CARGA DE DATOS DE FRAUDE DE IVA EN NEO4J")
    print("=" * 70)
    print()
    
    # Cargar datos del JSON
    print("📂 Cargando datos desde JSON...")
    try:
        with open('datos_fraude_iva.json', 'r', encoding='utf-8') as f:
            datos = json.load(f)
        print("   ✓ Datos cargados desde JSON")
        print()
    except FileNotFoundError:
        print("   ✗ Error: No se encontró 'datos_fraude_iva.json'")
        print("   Ejecuta primero: python generar_datos_fraude.py")
        return
    
    # Limpiar base de datos
    limpiar_base_datos()
    print()
    
    # Crear constraints e índices
    crear_constraints_e_indices()
    print()
    
    # Cargar nodos
    cargar_empresas(datos['empresas'])
    cargar_directivos(datos['directivos'])
    cargar_cuentas_bancarias(datos['cuentas_bancarias'])
    print()
    
    # Cargar relaciones
    cargar_administraciones(datos['administraciones'])
    cargar_relaciones_cuentas(datos['cuentas_bancarias'])
    cargar_transacciones(datos['transacciones'])
    
    # Verificar
    verificar_carga()
    
    print()
    print("=" * 70)
    print("✅ ¡CARGA COMPLETADA EXITOSAMENTE!")
    print("=" * 70)
    print()
    print("Ahora puedes:")
    print("  1. Abrir Neo4j Browser: http://localhost:7474")
    print("  2. Explorar el grafo con: MATCH (n) RETURN n LIMIT 50")
    print("  3. Continuar con los notebooks de Jupyter")
    
    # Cerrar conexión
    driver.close()


if __name__ == "__main__":
    main()
