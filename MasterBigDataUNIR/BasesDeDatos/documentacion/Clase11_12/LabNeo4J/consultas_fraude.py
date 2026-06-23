"""
Consultas Cypher para Detección de Patrones de Fraude de IVA
Incluye los 6 patrones principales de fraude
Autor: Marlon Cárdenas Bonett @2025

"""

# IMPORTANTE: Ajusta estas variables a tu configuración
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "abc123456"  # Cambia por tu contraseña
NEO4J_DATABASE = "fraudedb"


# ============================================================================
# PATRÓN 1: CADENAS CIRCULARES DE FACTURAS (FRAUDE CARRUSEL)
# ============================================================================

FRAUDE_PATRON_1_DESCRIPCION = """
**Patrón 1: Cadenas Circulares de Facturas (Fraude Carrusel)**

El fraude carrusel implica una cadena circular de empresas que se facturan
mutuamente, típicamente involucra transacciones intracomunitarias.

El patrón busca:
- Cadenas de al menos 3 empresas
- Que formen un ciclo (A → B → C → A)
- Con transacciones de montos significativos
"""

FRAUDE_PATRON_1_QUERY = """
// Detectar cadenas circulares de 3-5 saltos
MATCH path = (e1:Empresa)-[:EMITE_FACTURA*3..5]->(e1)
WHERE ALL(r IN relationships(path) WHERE r.monto_total > 10000)
WITH path, [n IN nodes(path) | n.nombre] AS empresas_en_cadena,
     reduce(total = 0.0, r IN relationships(path) | total + r.monto_total) AS monto_total_cadena,
     length(path) AS longitud
WITH DISTINCT empresas_en_cadena,
     longitud,
     monto_total_cadena
ORDER BY monto_total_cadena DESC
RETURN 
    empresas_en_cadena,
    longitud,
    round(monto_total_cadena) AS monto_total,
    round(monto_total_cadena / longitud) AS promedio_por_trans
LIMIT 10
"""

# ============================================================================
# PATRÓN 2: EMPRESAS CON ALTA ROTACIÓN Y CORTA VIDA (EMPRESAS FANTASMA)
# ============================================================================

FRAUDE_PATRON_2_DESCRIPCION = """
**Patrón 2: Empresas con Alta Rotación y Corta Vida**

Empresas creadas recientemente con gran volumen de transacciones,
características típicas de empresas fantasma.

Indicadores:
- Menos de 1 año desde constitución
- Alto volumen de facturación
- Capital social mínimo
- Pocos o ningún empleado
"""

FRAUDE_PATRON_2_QUERY = """
// Empresas jóvenes con alto volumen de negocio
MATCH (e:Empresa)
WHERE date(e.fecha_constitucion) > date() - duration({months: 12})
OPTIONAL MATCH (e)-[f:EMITE_FACTURA]->()
WITH e,
     count(f) AS num_facturas_emitidas,
     coalesce(sum(f.monto_total), 0) AS total_facturado
WHERE num_facturas_emitidas > 5
RETURN 
    e.nombre AS empresa,
    e.nif AS nif,
    e.fecha_constitucion AS constitución,
    e.capital_social AS capital,
    e.empleados AS empleados,
    num_facturas_emitidas,
    round(total_facturado) AS total_facturado,
    e.es_fantasma AS es_fantasma_real
ORDER BY total_facturado DESC
LIMIT 20
"""

# ============================================================================
# PATRÓN 3: MONTOS DESPROPORCIONADOS VS TAMAÑO EMPRESA
# ============================================================================

FRAUDE_PATRON_3_DESCRIPCION = """
**Patrón 3: Montos Desproporcionados al Tamaño de Empresa**

Empresas pequeñas (poco capital, pocos empleados) con transacciones
de montos muy elevados, indicador de posible fraude.

Señales de alerta:
- Capital social < 10,000
- Empleados < 5
- Transacciones individuales > 100,000
"""

FRAUDE_PATRON_3_QUERY = """
// Empresas pequeñas con transacciones grandes
MATCH (e:Empresa)-[f:EMITE_FACTURA]->()
WHERE e.capital_social < 10000
  AND e.empleados < 5
  AND f.monto_total > 100000
WITH e, f
ORDER BY f.monto_total DESC
RETURN 
    e.nombre AS empresa,
    e.capital_social AS capital,
    e.empleados AS empleados,
    f.numero_factura AS factura,
    round(f.monto_total) AS monto,
    round(f.monto_total / e.capital_social) AS ratio_monto_capital
ORDER BY ratio_monto_capital DESC
LIMIT 20
"""

# ============================================================================
# PATRÓN 4: REDES DE EMPRESAS CON ADMINISTRADORES COMUNES
# ============================================================================

FRAUDE_PATRON_4_DESCRIPCION = """
**Patrón 4: Redes de Empresas con Administradores Comunes**

Directivos que administran múltiples empresas, especialmente si estas
empresas comercian entre sí. Típico en redes de fraude organizadas.

Indicadores:
- Un directivo administra 3+ empresas
- Estas empresas se facturan mutuamente
- Patrón de "empresas pantalla"
"""

FRAUDE_PATRON_4_QUERY = """
// Directivos que administran múltiples empresas que comercian entre sí
MATCH (d:Directivo)-[:ADMINISTRA]->(e1:Empresa)
WITH d, collect(e1) AS empresas_administradas
WHERE size(empresas_administradas) >= 2
UNWIND empresas_administradas AS emp1
UNWIND empresas_administradas AS emp2
MATCH (emp1)-[f:EMITE_FACTURA]->(emp2)
WHERE emp1 <> emp2
WITH d,
     empresas_administradas,
     collect(DISTINCT {de: emp1.nombre, a: emp2.nombre, monto: round(f.monto_total)}) AS transacciones_entre_sus_empresas,
     sum(f.monto_total) AS total_facturado_interno
RETURN 
    d.nombre AS directivo,
    d.dni AS dni,
    size(empresas_administradas) AS num_empresas,
    [e IN empresas_administradas | e.nombre] AS empresas,
    size(transacciones_entre_sus_empresas) AS num_transacciones_internas,
    round(total_facturado_interno) AS total_interno
ORDER BY num_empresas DESC, total_interno DESC
LIMIT 15
"""

# ============================================================================
# PATRÓN 5: EMPRESAS QUE SOLO COMPRAN/VENDEN ENTRE SÍ (COMUNIDADES CERRADAS)
# ============================================================================

FRAUDE_PATRON_5_DESCRIPCION = """
**Patrón 5: Empresas que Solo Comercian Entre Sí**

Grupos de empresas que forman una comunidad cerrada, sin transacciones
con el exterior. Indicador de red de facturación falsa.

Características:
- Grupo de 3+ empresas
- Solo comercian entre miembros del grupo
- Sin O con pocas transacciones a empresas externas
"""

FRAUDE_PATRON_5_QUERY = """
// Encontrar componentes fuertemente conectados pequeños
// (grupos cerrados de empresas)
MATCH (e:Empresa)
OPTIONAL MATCH (e)-[:EMITE_FACTURA]-(otras:Empresa)
WITH e, collect(DISTINCT otras) AS socios_comerciales
WHERE size(socios_comerciales) >= 2 AND size(socios_comerciales) <= 6
WITH collect({empresa: e, socios: socios_comerciales}) AS grupos

UNWIND grupos AS grupo1
UNWIND grupos AS grupo2
WITH grupo1, grupo2
WHERE grupo1.empresa.id < grupo2.empresa.id
  AND grupo2.empresa IN grupo1.socios
  AND grupo1.empresa IN grupo2.socios

WITH collect(DISTINCT grupo1.empresa) + collect(DISTINCT grupo2.empresa) AS miembros_grupo
WHERE size(miembros_grupo) >= 3

// Verificar que comercian principalmente entre ellos
UNWIND miembros_grupo AS miembro
MATCH (miembro)-[f:EMITE_FACTURA]-(otra:Empresa)
WITH miembros_grupo, 
     miembro,
     count(CASE WHEN otra IN miembros_grupo THEN 1 END) AS trans_internas,
     count(CASE WHEN NOT otra IN miembros_grupo THEN 1 END) AS trans_externas
WHERE trans_internas > trans_externas

RETURN 
    [m IN miembros_grupo | m.nombre] AS grupo_empresas,
    size(miembros_grupo) AS tamaño_grupo,
    avg(trans_internas) AS promedio_trans_internas,
    avg(trans_externas) AS promedio_trans_externas
LIMIT 10
"""

# ============================================================================
# PATRÓN 6: FLUJOS ANÓMALOS ENTRE PAÍSES (FRAUDE INTRACOMUNITARIO)
# ============================================================================

FRAUDE_PATRON_6_DESCRIPCION = """
**Patrón 6: Flujos Anómalos Entre Países**

Patrones sospechosos en transacciones intracomunitarias:
- Alto volumen entre países específicos
- Desequilibrios (mucho más en una  dirección)
- Empresas que solo operan internacionalmente

Típico en fraude carrusel intracomunitario.
"""

FRAUDE_PATRON_6_QUERY = """
// Análisis de flujos intracomunitarios
MATCH (e1:Empresa)-[f:EMITE_FACTURA]->(e2:Empresa)
WHERE e1.pais <> e2.pais
  AND f.es_intracomunitaria = true
WITH e1.pais AS pais_origen,
     e2.pais AS pais_destino,
     count(f) AS num_transacciones,
     sum(f.monto_total) AS total_flujo,
     avg(f.monto_total) AS promedio_transaccion,
     collect(DISTINCT e1.nombre) AS empresas_origen

// Buscar flujos significativos
WHERE num_transacciones >= 3

RETURN 
    pais_origen,
    pais_destino,
    num_transacciones,
    round(total_flujo) AS total_flujo,
    round(promedio_transaccion) AS promedio_por_transaccion,
    size(empresas_origen) AS num_empresas_involucradas,
    empresas_origen[0..3] AS ejemplos_empresas
ORDER BY total_flujo DESC
LIMIT 20
"""

# ============================================================================
# CONSULTA COMBINADA: SCORING DE RIESGO
# ============================================================================

SCORING_RIESGO_DESCRIPCION = """
**Scoring de Riesgo de Fraude**

Combina múltiples indicadores para calcular un score de riesgo por empresa:
- Es empresa fantasma (marcador directo) = 40 puntos
- Empresa joven (< 1 año) = 15 puntos
- Capital bajo (< 5000) = 10 puntos
- Sin empleados = 10 puntos
- Alto volumen transacciones = 10 puntos
- Participa en ciclos = 15 puntos

Score > 50 = ALTO RIESGO
Score 30-50 = MEDIO RIESGO
Score < 30 = BAJO RIESGO
"""

SCORING_RIESGO_QUERY = """
MATCH (e:Empresa)
OPTIONAL MATCH (e)-[f:EMITE_FACTURA]->()

// Calcular indicadores individuales
WITH e,
     count(f) AS num_transacciones,
     coalesce(sum(f.monto_total), 0) AS volumen_total,
     
     // Indicador 1: Es fantasma (conocido)
     CASE WHEN e.es_fantasma THEN 40 ELSE 0 END AS score_fantasma,
     
     // Indicador 2: Empresa joven
     CASE WHEN date(e.fecha_constitucion) > date() - duration({months: 12}) 
          THEN 15 ELSE 0 END AS score_joven,
     
     // Indicador 3: Capital bajo
     CASE WHEN e.capital_social < 5000 THEN 10 ELSE 0 END AS score_capital_bajo,
     
     // Indicador 4: Sin empleados
     CASE WHEN e.empleados = 0 THEN 10 ELSE 0 END AS score_sin_empleados,
     
     // Indicador 5: Alto volumen
     CASE WHEN count(f) > 15 THEN 10 ELSE 0 END AS score_alto_volumen

// Detectar participación en ciclos
OPTIONAL MATCH ciclo = (e)-[:EMITE_FACTURA*2..4]->(e)
WITH e, num_transacciones, volumen_total,
     score_fantasma, score_joven, score_capital_bajo, score_sin_empleados, score_alto_volumen,
     CASE WHEN count(ciclo) > 0 THEN 15 ELSE 0 END AS score_en_ciclo

// Calcular score total
WITH e, num_transacciones, volumen_total,
     score_fantasma + score_joven + score_capital_bajo + score_sin_empleados + 
     score_alto_volumen + score_en_ciclo AS score_total,
     score_fantasma, score_joven, score_capital_bajo, score_sin_empleados, score_alto_volumen, score_en_ciclo

// Clasificar riesgo
WITH e, num_transacciones, volumen_total, score_total,
     score_fantasma, score_joven, score_capital_bajo, score_sin_empleados, score_alto_volumen, score_en_ciclo,
     CASE 
         WHEN score_total >= 50 THEN 'ALTO'
         WHEN score_total >= 30 THEN 'MEDIO'
         ELSE 'BAJO'
     END AS nivel_riesgo

RETURN 
    e.nombre AS empresa,
    e.nif AS nif,
    score_total AS score_riesgo,
    nivel_riesgo,
    num_transacciones,
    round(volumen_total) AS volumen_total,
    e.es_fantasma AS es_fantasma_real,
    // Desglose del score
    {fantasma: score_fantasma, joven: score_joven, capital_bajo: score_capital_bajo,
     sin_empleados: score_sin_empleados, alto_volumen: score_alto_volumen, en_ciclo: score_en_ciclo} AS desglose_score
ORDER BY score_riesgo DESC, volumen_total DESC
LIMIT 30
"""

# ============================================================================
# COLECCIÓN DE TODAS LAS CONSULTAS
# ============================================================================

CONSULTAS_FRAUDE = {
    "patron_1_cadenas_circulares": {
        "descripcion": FRAUDE_PATRON_1_DESCRIPCION,
        "query": FRAUDE_PATRON_1_QUERY
    },
    "patron_2_empresas_fantasma": {
        "descripcion": FRAUDE_PATRON_2_DESCRIPCION,
        "query": FRAUDE_PATRON_2_QUERY
    },
    "patron_3_montos_desproporcionados": {
        "descripcion": FRAUDE_PATRON_3_DESCRIPCION,
        "query": FRAUDE_PATRON_3_QUERY
    },
    "patron_4_administradores_comunes": {
        "descripcion": FRAUDE_PATRON_4_DESCRIPCION,
        "query": FRAUDE_PATRON_4_QUERY
    },
    "patron_5_comunidades_cerradas": {
        "descripcion": FRAUDE_PATRON_5_DESCRIPCION,
        "query": FRAUDE_PATRON_5_QUERY
    },
    "patron_6_flujos_anomalos": {
        "descripcion": FRAUDE_PATRON_6_DESCRIPCION,
        "query": FRAUDE_PATRON_6_QUERY
    },
    "scoring_riesgo": {
        "descripcion": SCORING_RIESGO_DESCRIPCION,
        "query": SCORING_RIESGO_QUERY
    }
}


# ============================================================================
# CONSULTAS DE EXPLORACIÓN BÁSICA
# ============================================================================

CONSULTAS_EXPLORACION = {
    "estadisticas_generales": """
    // Estadísticas generales del grafo
    MATCH (e:Empresa)
    OPTIONAL MATCH (e)-[f:EMITE_FACTURA]->()
    RETURN 
        count(DISTINCT e) AS total_empresas,
        count(DISTINCT f) AS total_facturas,
        round(avg(e.capital_social)) AS capital_promedio,
        round(sum(f.monto_total)) AS volumen_total_negocio
    """,
    
    "top_empresas_por_volumen": """
    // Top 10 empresas por volumen de negocio
    MATCH (e:Empresa)-[f:EMITE_FACTURA]->()
    WITH e, count(f) AS num_facturas, sum(f.monto_total) AS volumen
    RETURN 
        e.nombre AS empresa,
        e.pais AS pais,
        num_facturas,
        round(volumen) AS volumen_total
    ORDER BY volumen DESC
    LIMIT 10
    """,
    
    "distribucion_por_pais": """
    // Distribución de empresas y volumen por país
    MATCH (e:Empresa)
    OPTIONAL MATCH (e)-[f:EMITE_FACTURA]->()
    WITH e.pais AS pais,
         count(DISTINCT e) AS num_empresas,
         count(f) AS num_transacciones,
         sum(f.monto_total) AS volumen_total
    RETURN 
        pais,
        num_empresas,
        num_transacciones,
        round(coalesce(volumen_total, 0)) AS volumen_total
    ORDER BY volumen_total DESC
    """,
    
    "empresas_mas_conectadas": """
    // Empresas con más conexiones (grado)
    MATCH (e:Empresa)
    OPTIONAL MATCH (e)-[:EMITE_FACTURA]-(otra:Empresa)
    WITH e, count(DISTINCT otra) AS num_conexiones
    WHERE num_conexiones > 0
    RETURN 
        e.nombre AS empresa,
        e.sector AS sector,
        num_conexiones
    ORDER BY num_conexiones DESC
    LIMIT 15
    """
}


if __name__ == "__main__":
    print("=" * 70)
    print("CONSULTAS DE DETECCIÓN DE FRAUDE DE IVA")
    print("=" * 70)
    print()
    print("Este archivo contiene las consultas Cypher para detectar")
    print("los 6 patrones principales de fraude de IVA.")
    print()
    print("Patrones disponibles:")
    for i, (key, value) in enumerate(CONSULTAS_FRAUDE.items(), 1):
        print(f"  {i}. {key}")
    print()
    print("Usa estas consultas en los notebooks o Neo4j Browser.")
    print("=" * 70)
