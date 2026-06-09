"""
Consultas y ejemplos con APOC (Awesome Procedures on Cypher)
Para uso en el notebook 02_apoc_plugins.ipynb
Autor: Marlon Cárdenas Bonett @2025

"""

# ============================================================================
# 1. UTILIDADES Y FUNCIONES BÁSICAS
# ============================================================================

APOC_METADATOS = {
    "descripcion": "Explorar metadatos del grafo",
    "queries": {
        "schema": "CALL apoc.meta.schema()",
        "stats": "CALL apoc.meta.stats()",
        "node_type_properties": "CALL apoc.meta.nodeTypeProperties()",
        "relationship_types": "CALL apoc.meta.relTypeProperties()"
    }
}

APOC_FECHAS = {
    "descripcion": "Manipulación de fechas y tiempos",
    "ejemplos": [
        "RETURN apoc.date.format(timestamp(), 'ms', 'yyyy-MM-dd HH:mm:ss') AS fecha_formateada",
        "RETURN apoc.date.parse('2024-01-15', 'ms', 'yyyy-MM-dd') AS timestamp",
        "WITH apoc.date.parse('2024-01-15', 'ms', 'yyyy-MM-dd') AS fecha RETURN apoc.date.add(fecha, 30, 'd') AS fecha_mas_30_dias"
    ]
}

APOC_TEXT = {
    "descripcion": "Manipulación de texto",
    "ejemplos": [
        "RETURN apoc.text.camelCase('detección de fraude') AS camel",
        "RETURN apoc.text.join(['Neo4j', 'APOC', 'GDS'], ' + ') AS joined",
        "RETURN apoc.text.distance('García', 'Garcia') AS distancia_leveenshtein"
    ]
}

APOC_COLLECTIONS = {
    "descripcion": "Operaciones con colecciones",
    "ejemplos": [
        "RETURN apoc.coll.sum([1, 2, 3, 4, 5]) AS suma",
        "RETURN apoc.coll.avg([10, 20, 30, 40]) AS promedio",
        "RETURN apoc.coll.partition([1,2,3,4,5,6,7,8], 3) AS particiones"
    ]
}

# ============================================================================
# 2. ALGORITMOS DE CENTRALIDAD (DEPRECADOS EN APOC 5+, MIGRAR A GDS)
# ============================================================================

# NOTA: En APOC 5.x, los algoritmos de grafos están deprecados
# Se recomienda usar GDS (Graph Data Science) en su lugar
# Los incluimos aquí con fines educativos

APOC_PAGERANK = {
    "descripcion": """
    PageRank: Mide la importancia de un nodo basándose en la cantidad y calidad de enlaces entrantes.
    
    **NOTA**: En APOC 5.x, usar GDS en su lugar.
    Para APOC 4.x:
    """,
    "query_legacy": """
    // DEPRECATED en APOC 5.x - Usar GDS
    CALL apoc.algo.pageRank('Empresa', 'EMITE_FACTURA', {iterations: 20, write: false})
    YIELD node, score
    RETURN node.nombre AS empresa, score
    ORDER BY score DESC
    LIMIT 10
    """
}

# ============================================================================
# 3. PATH EXPANSION - EXPANSIÓN DE CAMINOS
# ============================================================================

APOC_PATH_EXPANSION = {
    "descripcion": "Expandir caminos con criterios complejos",
    "query_paths_between": """
    // Encontrar todos los caminos entre dos empresas
    MATCH (inicio:Empresa {nombre: 'Empresa A'}),
          (fin:Empresa {nombre: 'Empresa B'})
    CALL apoc.path.expandConfig(inicio, {
        relationshipFilter: 'EMITE_FACTURA>',
       labelFilter: '+Empresa',
        minLevel: 1,
        maxLevel: 4,
        endNodes: [fin],
        uniqueness: 'NODE_PATH'
    })
    YIELD path
    RETURN path, length(path) AS longitud
    ORDER BY longitud
    LIMIT 10
    """,
    
    "query_subgraph": """
    // Expandir subgrafo desde un nodo
    MATCH (e:Empresa) WHERE e.es_fantasma = true
    WITH e LIMIT 1
    CALL apoc.path.subgraphAll(e, {
        relationshipFilter: 'EMITE_FACTURA',
        maxLevel: 2
    })
    YIELD nodes, relationships
    RETURN nodes, relationships
    """
}

# ============================================================================
# 4. PERIODIC ITERATE - OPERACIONES EN LOTES
# ============================================================================

APOC_PERIODIC = {
    "descripcion": "Ejecutar operaciones en lotes para mejor rendimiento",
    
    "example_update_batch": """
    // Actualizar propiedades en lotes
    CALL apoc.periodic.iterate(
        'MATCH (e:Empresa) RETURN e',
        'SET e.procesado = true, e.fecha_proceso = datetime()',
        {batchSize: 100, parallel: false}
    )
    YIELD batches, total
    RETURN batches, total
    """,
    
    "example_delete_batch": """
    //  Eliminar relaciones en lotes
    CALL apoc.periodic.iterate(
        'MATCH ()-[r:EMITE_FACTURA]->() WHERE r.monto_total < 100 RETURN r',
        'DELETE r',
        {batchSize: 1000}
    )
    """
}

# ============================================================================
# 5. CYPHER DINÁMICO
# ============================================================================

APOC_CYPHER_DINAMICO = {
    "descripcion": "Ejecutar consultas Cypher construidas dinámicamente",
    
    "example_run": """
    // Ejecutar query dinámica
    WITH 'MATCH (e:Empresa) WHERE e.pais = $pais RETURN count(e) AS total' AS query
    CALL apoc.cypher.run(query, {pais: 'España'})
    YIELD value
    RETURN value.total AS empresas_espanolas
    """,
    
    "example_parallel": """
    // Ejecutar consultas en paralelo para diferentes países
    WITH ['España', 'Francia', 'Alemania', 'Italia'] AS paises
    UNWIND paises AS pais
    CALL apoc.cypher.run(
        'MATCH (e:Empresa {pais: $p})-[f:EMITE_FACTURA]->() 
         RETURN $p AS pais, sum(f.monto_total) AS total',
        {p: pais}
    )
    YIELD value
    RETURN value.pais AS pais, value.total AS volumen_negocio
    ORDER BY volumen_negocio DESC
    """
}

# ============================================================================
# 6. IMPORTACIÓN/EXPORTACIÓN DE DATOS
# ============================================================================

APOC_LOAD_JSON = {
    "descripcion": "Cargar datos desde JSON",
    
    "example_load_json": """
    // Cargar desde archivo JSON local o URL
    CALL apoc.load.json('file:///datos_fraude_iva.json')
    YIELD value
    RETURN value.metadatos AS metadatos
    """,
    
    "example_load_json_path": """
    // Cargar parte específica del JSON
    CALL apoc.load.json('file:///datos_fraude_iva.json', '$.empresas[0:5]')
    YIELD value
    RETURN value.nombre AS empresa, value.pais AS pais
    """
}

APOC_LOAD_CSV = {
    "descripcion": "Cargar CSV con opciones avanzadas",
    
    "example": """
    // Cargar CSV con separador personalizado
    CALL apoc.load.csv('file:///empresas.csv', {
        sep: ';',
        header: true,
        ignore: ['columna_a_ignorar']
    })
    YIELD map AS row
    CREATE (e:Empresa {
        nif: row.nif,
        nombre: row.nombre
    })
    """
}

APOC_EXPORT = {
    "descripcion": "Exportar datos a múltiples formatos",
    
    "export_json": """
    // Exportar subgrafo a JSON
    MATCH path = (e:Empresa {es_fantasma: true})-[r:EMITE_FACTURA*1..2]->()
    WITH collect(path) AS paths
    CALL apoc.export.json.data(
        apoc.coll.toSet(apoc.coll.flatten([p IN paths | nodes(p)])),
        apoc.coll.toSet(apoc.coll.flatten([p IN paths | relationships(p)])),
        'empresas_fantasma.json',
        {}
    )
    YIELD file, nodes, relationships
    RETURN file, nodes, relationships
    """,
    
    "export_csv": """
    // Exportar query a CSV
    CALL apoc.export.csv.query(
        'MATCH (e:Empresa)-[f:EMITE_FACTURA]->() 
         RETURN e.nombre AS empresa, sum(f.monto_total) AS total
         ORDER BY total DESC',
        'volumen_empresas.csv',
        {}
    )
    YIELD file, rows
    RETURN file, rows
    """
}

# ============================================================================
# 7. REFACTORING - REESTRUCTURACIÓN DEL GRAFO
# ============================================================================

APOC_REFACTOR = {
    "descripcion": "Reestructurar el grafo: merge nodes, cambiar tipos, etc.",
    
    "merge_nodes": """
    // Fusionar nodos duplicados
    MATCH (e1:Empresa {nif: 'A12345678'})
    MATCH (e2:Empresa  {nif: 'A12345678'})
    WHERE id(e1) < id(e2)
    CALL apoc.refactor.mergeNodes([e1, e2], {
        properties: 'combine',
        mergeRels: true
    })
    YIELD node
    RETURN node
    """,
    
    "normalize_relationships": """
    // Convertir relaciones con propiedades en nodos
    MATCH (e1:Empresa)-[f:EMITE_FACTURA]->(e2:Empresa)
    WITH e1, e2, f LIMIT 1
    CALL apoc.refactor.normalizeAsBoolean(f, 'es_intracomunitaria', ['SI', 'TRUE'], ['NO', 'FALSE'])
    YIELD input, output
    RETURN input, output
    """
}

# ============================================================================
# 8. TRIGGERS Y LIFECYCLE
# ============================================================================

APOC_TRIGGERS = {
    "descripcion": "Crear triggers para ejecutar lógica automáticamente",
    
    "example_trigger": """
    // Crear trigger para auditar cambios (requiere configuración en neo4j.conf)
    CALL apoc.trigger.add(
        'auditoria_empresas',
        'UNWIND $createdNodes AS node
         WITH node WHERE node:Empresa
         CREATE (a:Auditoria {
             accion: "CREATED",
             empresa_id: node.id,
             timestamp: datetime()
         })',
        {phase: 'after'}
    )
    """,
    
    "list_triggers": "CALL apoc.trigger.list()",
    "remove_trigger": "CALL apoc.trigger.remove('auditoria_empresas')"
}

# ============================================================================
# 9. VIRTUAL NODES AND RELATIONSHIPS
# ============================================================================

APOC_VIRTUAL = {
    "descripcion": "Crear nodos y relaciones virtuales para visualización",
    
    "example_virtual_graph": """
    // Crear grafo virtual agregado por país
    MATCH (e:Empresa)
    WITH e.pais AS pais, collect(e) AS empresas
    CALL apoc.create.vNode(['Pais'], {nombre: pais, num_empresas: size(empresas)})
    YIELD node AS pais_node
    WITH pais_node, empresas
    UNWIND empresas AS empresa
    CALL apoc.create.vRelationship(empresa, 'UBICADA_EN', {}, pais_node)
    YIELD rel
    RETURN pais_node, empresa, rel
    LIMIT 50
    """
}

# ============================================================================
# 10. SCORING Y DETECCIÓN DE PATRONES CON APOC
# ============================================================================

APOC_SCORING_FRAUDE = {
    "descripcion": "Usar APOC para cálculos complejos de scoring",
    
    "query": """
    MATCH (e:Empresa)
    OPTIONAL MATCH (e)-[f:EMITE_FACTURA]->()
    
    // Calcular estadísticas usando apoc.coll
    WITH e,
         apoc.coll.sum(collect(f.monto_total)) AS volumen_total,
         apoc.coll.avg(collect(f.monto_total)) AS promedio_factura,
         count(f) AS num_facturas,
         apoc.coll.max(collect(f.monto_total)) AS factura_maxima
    
    // Calcular scoring con APOC map functions
    WITH e, volumen_total, promedio_factura, num_facturas,
         apoc.map.fromPairs([
             ['empresa_joven', CASE WHEN date(e.fecha_constitucion) > date() - duration({months: 12}) THEN 20 ELSE 0 END],
             ['capital_bajo', CASE WHEN e.capital_social < 5000 THEN 15 ELSE 0 END],
             ['sin_empleados', CASE WHEN e.empleados = 0 THEN 15 ELSE 0 END],
             ['alto_volumen', CASE WHEN num_facturas > 20 THEN 15 ELSE 0 END],
             ['factura_anomala', CASE WHEN promedio_factura > 100000 THEN 20 ELSE 0 END]
         ]) AS scores_individuales
    
    // Sumar scores
    WITH e, volumen_total, num_facturas,
         apoc.coll.sum(apoc.map.values(scores_individuales)) AS score_total,
         scores_individuales
    
    RETURN 
        e.nombre AS empresa,
        score_total,
        CASE 
            WHEN score_total >= 50 THEN 'ALTO'
            WHEN score_total >= 30 THEN 'MEDIO'
            ELSE 'BAJO'
        END AS nivel_riesgo,
        num_facturas,
        round(volumen_total) AS volumen,
        scores_individuales
    ORDER BY score_total DESC
    LIMIT 20
    """
}

# ============================================================================
# LISTA COMPLETA DE CATEGORÍAS APOC
# ============================================================================

APOC_CATEGORIAS = {
    "Meta": ["apoc.meta.schema", "apoc.meta.stats", "apoc.meta.nodeTypeProperties"],
    "Date/Time": ["apoc.date.format", "apoc.date.parse", "apoc.date.add"],
    "Text": ["apoc.text.camelCase", "apoc.text.join", "apoc.text.distance"],
    "Collections": ["apoc.coll.sum", "apoc.coll.avg", "apoc.coll.partition"],
    "Path": ["apoc.path.expandConfig", "apoc.path.subgraphAll"],
    "Periodic": ["apoc.periodic.iterate", "apoc.periodic.commit"],
    "Cypher": ["apoc.cypher.run", "apoc.cypher.runFile"],
    "Load": ["apoc.load.json", "apoc.load.csv", "apoc.load.xml"],
    "Export": ["apoc.export.json.all", "apoc.export.csv.query"],
    "Refactor": ["apoc.refactor.mergeNodes", "apoc.refactor.normalizeAsBoolean"],
    "Trigger": ["apoc.trigger.add", "apoc.trigger.list"],
    "Virtual": ["apoc.create.vNode", "apoc.create.vRelationship"],
    "Map": ["apoc.map.fromPairs", "apoc.map.values", "apoc.map.merge"]
}


if __name__ == "__main__":
    print("=" * 70)
    print("CONSULTAS Y EJEMPLOS APOC")
    print("=" * 70)
    print()
    print("Este archivo contiene ejemplos de los procedimientos APOC más útiles")
    print("para el análisis de fraude de IVA.")
    print()
    print("Categorías disponibles:")
    for cat, funcs in APOC_CATEGORIAS.items():
        print(f"\n{cat}:")
        for func in funcs[:3]:  # Mostrar primeras 3
            print(f"  - {func}")
    print("\n" + "=" * 70)
