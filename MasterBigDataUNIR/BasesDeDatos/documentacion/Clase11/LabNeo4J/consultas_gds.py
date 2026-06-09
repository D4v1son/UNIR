"""
Consultas y ejemplos con GDS (Graph Data Science)
Para uso en el notebook 03_gds_plugins.ipynb
Autor: Marlon Cárdenas Bonett 2025

"""

# ============================================================================
# 1. PROYECCIÓN DE GRAFOS
# ============================================================================

GDS_PROYECCION_NATIVE = {
    "descripcion": """
    Proyección Nativa: La forma más eficiente de proyectar grafos en GDS.
    Usa etiquetas y tipos de relación directamente.
    """,
    
    "example_simple": """
    // Proyectar grafo simple de empresas y facturas
    CALL gds.graph.project(
        'red-empresas',           // Nombre del grafo
        'Empresa',                 // Etiquetas de nodos
        'EMITE_FACTURA'           // Tipos de relación
    )
    YIELD graphName, nodeCount, relationshipCount
    RETURN graphName, nodeCount, relationshipCount
    """,
    
    "example_with_properties": """
    // Proyectar con propiedades para algoritmos ponderados
    CALL gds.graph.project(
        'red-ponderada',
        'Empresa',
        {
            EMITE_FACTURA: {
                orientation: 'NATURAL',
                properties: 'monto_total'
            }
        },
        {
            nodeProperties: ['capital_social', 'empleados']
        }
    )
    YIELD graphName, nodeCount, relationshipCount
    RETURN graphName, nodeCount, relationshipCount
    """
}

GDS_PROYECCION_CYPHER = {
    "descripcion": """
    Proyección Cypher: Más flexible, permite filtros y transformaciones complejas.
    """,
    
    "example_filtered": """
    // Proyectar solo empresas con alto volumen
    CALL gds.graph.project.cypher(
        'empresas-alto-volumen',
        'MATCH (e:Empresa)-[f:EMITE_FACTURA]->()
         WITH e, sum(f.monto_total) AS volumen
         WHERE volumen > 50000
         RETURN id(e) AS id, labels(e) AS labels, e.nombre AS nombre',
        'MATCH (e1:Empresa)-[f:EMITE_FACTURA]->(e2:Empresa)
         WHERE f.monto_total > 10000
         RETURN id(e1) AS source, id(e2) AS target, f.monto_total AS peso'
    )
    YIELD graphName, nodeCount, relationshipCount
    RETURN graphName, nodeCount, relationshipCount
    """
}

GDS_PROYECCION_MANAGEMENT = {
    "descripcion": "Gestión de proyecciones de grafos",
    "list_graphs": "CALL gds.graph.list() YIELD graphName, nodeCount, relationshipCount",
    "drop_graph": "CALL gds.graph.drop('red-empresas') YIELD graphName",
    "exists": "CALL gds.graph.exists('red-empresas') YIELD exists"
}

# ============================================================================
# 2. ALGORITMOS DE CENTRALIDAD
# ============================================================================

GDS_PAGERANK = {
    "descripcion": """
    **PageRank**: Mide la importancia de un nodo basándose en la estructura del grafo.
    
    Útil para:
    - Identificar empresas centrales en la red
    - Detectar nodos influyentes
    - Encontrar puntos clave en flujos de dinero
    """,
    
    "stream": """
    // Modo STREAM: Retorna resultados sin escribir en el grafo
    CALL gds.pageRank.stream('red-empresas')
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS empresa, score
    RETURN 
        empresa.nombre AS empresa,
        empresa.pais AS pais,
        round(score, 4) AS pagerank_score
    ORDER BY score DESC
    LIMIT 20
    """,
    
    "write": """
    // Modo WRITE: Escribe resultados como propiedad del nodo
    CALL gds.pageRank.write('red-empresas', {
        writeProperty: 'pagerank',
        maxIterations: 20,
        dampingFactor: 0.85
    })
    YIELD nodePropertiesWritten, ranIterations
    RETURN nodePropertiesWritten, ranIterations
    """,
    
    "stats": """
    // Modo STATS: Solo estadísticas, no retorna ni escribe datos
    CALL gds.pageRank.stats('red-empresas')
    YIELD centralityDistribution
    RETURN centralityDistribution
    """
}

GDS_BETWEENNESS = {
    "descripcion": """
    **Betweenness Centrality**: Mide cuántos caminos más cortos pasan por un nodo.
    
    Útil para:
    - Identificar "puentes" en la red
    - Detectar intermediarios críticos
    - Encontrar cuellos de botella en flujos
    """,
    
    "stream": """
    CALL gds.betweenness.stream('red-empresas')
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS empresa, score
    WHERE score > 0
    RETURN 
        empresa.nombre AS empresa,
        round(score, 2) AS betweenness_score
    ORDER BY score DESC
    LIMIT 15
    """
}

GDS_DEGREE_CENTRALITY = {
    "descripcion": """
    **Degree Centrality**: Cuenta el número de conexiones de un nodo.
    
    Tipos:
    - Degree: Total de conexiones
    - In-Degree: Conexiones entrantes
    - Out-Degree: Conexiones salientes
    """,
    
    "stream": """
    CALL gds.degree.stream('red-empresas' )
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS empresa, score
    RETURN 
        empresa.nombre AS empresa,
        score AS num_conexiones
    ORDER BY score DESC
    LIMIT 15
    """
}

GDS_CLOSENESS = {
    "descripcion": """
    **Closeness Centrality**: Mide qué tan cerca está un nodo de todos los demás.
    
    Útil para:
    - Identificar nodos con acceso rápido a la red
    - Detectar posiciones estratégicas
    """,
    
    "stream": """
    CALL gds.closeness.stream('red-empresas')
    YIELD nodeId, score
    WITH gds.util.asNode(nodeId) AS empresa, score
    RETURN 
        empresa.nombre AS empresa,
        round(score, 4) AS closeness_score
    ORDER BY score DESC
    LIMIT 15
    """
}

# ============================================================================
# 3. DETECCIÓN DE COMUNIDADES
# ============================================================================

GDS_LOUVAIN = {
    "descripcion": """
    **Louvain**: Detecta comunidades maximizando la modularidad.
    
    Útil para:
    - Identificar grupos de empresas que comercian frecuentemente
    - Detectar redes de fraude organizadas
    - Segmentar el grafo en clusters
    """,
    
    "stream": """
    CALL gds.louvain.stream('red-empresas')
    YIELD nodeId, communityId
    WITH gds.util.asNode(nodeId) AS empresa, communityId
    WITH communityId, collect(empresa.nombre) AS miembros, count(*) AS tamaño
    WHERE tamaño >= 3
    RETURN 
        communityId,
        tamaño,
        miembros[0..5] AS ejemplos_empresas
    ORDER BY tamaño DESC
    """,
    
    "write": """
    CALL gds.louvain.write('red-empresas', {
        writeProperty: 'community',
        includeIntermediateCommunities: true
    })
    YIELD communityCount, modularity
    RETURN communityCount, round(modularity, 4) AS modularity
    """
}

GDS_LABEL_PROPAGATION = {
    "descripcion": """
    **Label Propagation**: Propaga etiquetas entre nodos vecinos.
    
    Más rápido que Louvain pero puede ser menos estable.
    """,
    
    "stream": """
    CALL gds.labelPropagation.stream('red-empresas', {
        maxIterations: 10
    })
    YIELD nodeId, communityId
    WITH gds.util.asNode(nodeId) AS empresa, communityId
    WITH communityId, collect(empresa.nombre) AS miembros, count(*) AS tamaño
    RETURN communityId, tamaño, miembros[0..5] AS ejemplos
    ORDER BY tamaño DESC
    LIMIT 10
    """
}

GDS_WCC = {
    "descripcion": """
    **Weakly Connected Components (WCC)**: Encuentra componentes conectados.
    
    Útil para:
    - Identificar redes desconectadas
    - Detectar islas en el grafo
    """,
    
    "stream": """
    CALL gds.wcc.stream('red-empresas')
    YIELD nodeId, componentId
    WITH gds.util.asNode(nodeId) AS empresa, componentId
    WITH componentId, count(*) AS tamaño, collect(empresa.nombre) AS miembros
    RETURN 
        componentId,
        tamaño,
        CASE WHEN tamaño <= 5 THEN miembros ELSE miembros[0..5] END AS empresas
    ORDER BY tamaño DESC
    """
}

GDS_TRIANGLE_COUNT = {
    "descripcion": """
    **Triangle Count & Clustering Coefficient**: Cuenta triángulos y mide clustering.
    
    Útil para:
    - Detectar grupos densamente conectados
    - Medir cohesión local
    """,
    
    "stream": """
    CALL gds.triangleCount.stream('red-empresas-undirected')
    YIELD nodeId, triangleCount
    WITH gds.util.asNode(nodeId) AS empresa, triangleCount
    WHERE triangleCount > 0
    RETURN 
        empresa.nombre AS empresa,
        triangleCount AS num_triangulos
    ORDER BY triangleCount DESC
    LIMIT 15
    """
}

# ============================================================================
# 4. SIMILITUD
# ============================================================================

GDS_NODE_SIMILARITY = {
    "descripcion": """
    **Node Similarity**: Encuentra nodos similares basándose en vecinos comunes.
    
    Útil para:
    - Detectar empresas con patrones de negocio similares
    - Encontrar duplicados o empresas relacionadas
    """,
    
    "stream": """
    CALL gds.nodeSimilarity.stream('red-empresas', {
        similarityCutoff: 0.5
    })
    YIELD node1, node2, similarity
    WITH gds.util.asNode(node1) AS emp1, 
         gds.util.asNode(node2) AS emp2,
         similarity
    RETURN 
        emp1.nombre AS empresa1,
        emp2.nombre AS empresa2,
        round(similarity, 3) AS similitud
    ORDER BY similarity DESC
    LIMIT 20
    """
}

GDS_KNN = {
    "descripcion": """
    **K-Nearest Neighbors**: Encuentra los K vecinos más similares.
    
    Basado en propiedades de nodos.
    """,
    
    "stream": """
    // Primero asegurar que las propiedades estén proyectadas
    CALL gds.knn.stream('red-ponderada', {
        topK: 5,
        nodeProperties: ['capital_social', 'empleados'],
        randomSeed: 42
    })
    YIELD node1, node2, similarity
    WITH gds.util.asNode(node1) AS emp1,
         gds.util.asNode(node2) AS emp2,
         similarity
    RETURN 
        emp1.nombre AS empresa,
        emp2.nombre AS similar_a,
        round(similarity, 3) AS similitud
    ORDER BY emp1.nombre, similarity DESC
    LIMIT 25
    """
}

# ============================================================================
# 5. PATH FINDING
# ============================================================================

GDS_SHORTEST_PATH = {
    "descripcion": """
    **Shortest Path (Dijkstra)**: Encuentra el camino más corto entre dos nodos.
    """,
    
    "query": """
    // Primero encontrar IDs de nodos
    MATCH (inicio:Empresa {nombre: 'Empresa A'})
    MATCH (fin:Empresa {nombre: 'Empresa B'})
    WITH id(inicio) AS startId, id(fin) AS endId
    
    // Ejecutar Dijkstra
    CALL gds.shortestPath.dijkstra.stream('red-ponderada', {
        sourceNode: startId,
        targetNode: endId,
        relationshipWeightProperty: 'monto_total'
    })
    YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
    RETURN 
        [nodeId IN nodeIds | gds.util.asNode(nodeId).nombre] AS camino,
        totalCost AS costo_total,
        size(nodeIds) - 1 AS longitud
    """
}

GDS_ALL_SHORTEST_PATHS = {
    "descripcion": """
    **All Shortest Paths**: Todos los caminos más cortos desde un nodo.
    """,
    
    "query": """
    MATCH (inicio:Empresa) WHERE inicio.es_fantasma = true
    WITH id(inicio) AS startId, inicio LIMIT 1
    
    CALL gds.allShortestPaths.dijkstra.stream('red-ponderada', {
        sourceNode: startId
    })
    YIELD sourceNode, targetNode, totalCost, nodeIds
    WITH gds.util.asNode(targetNode) AS destino, totalCost, nodeIds
    WHERE totalCost > 0
    RETURN 
        destino.nombre AS destino,
        totalCost AS costo,
        size(nodeIds) - 1 AS saltos
    ORDER BY totalCost
    LIMIT 15
    """
}

# ============================================================================
# 6. EMBEDDINGS Y MACHINE LEARNING
# ============================================================================

GDS_NODE2VEC = {
    "descripcion": """
    **Node2Vec**: Crea embeddings de nodos usando random walks.
    
    Útil para:
    - Representar nodos en espacio vectorial
    - Clustering basado en embeddings
    - ML downstream tasks
    """,
    
    "stream": """
    CALL gds.node2vec.stream('red-empresas', {
        embeddingDimension: 64,
        iterations: 10,
        walkLength: 80,
        walksPerNode: 10
    })
    YIELD nodeId, embedding
    WITH gds.util.asNode(nodeId) AS empresa, embedding
    RETURN empresa.nombre AS empresa, embedding[0..5] AS primeras_dims
    LIMIT 10
    """
}

GDS_FASTRP = {
    "descripcion": """
    **FastRP (Fast Random Projection)**: Embeddings rápidos y escalables.
    
    Más rápido que Node2Vec, bueno para grafos grandes.
    """,
    
    "stream": """
    CALL gds.fastRP.stream('red-empresas', {
        embeddingDimension: 128,
        iterationWeights: [0.0, 1.0, 1.0]
    })
    YIELD nodeId, embedding
    WITH gds.util.asNode(nodeId) AS empresa, embedding
    RETURN empresa.nombre AS empresa, size(embedding) AS dim
    LIMIT 10
    """
}

# ============================================================================
# 7. PIPELINE COMPLETO DE ANÁLISIS
# ============================================================================

GDS_PIPELINE_FRAUDE = {
    "descripcion": """
    Pipeline completo para análisis de fraude:
    1. Proyectar grafo
    2. Calcular múltiples métricas
    3. Combinar en scoring
    """,
    
    "paso_1_proyectar": """
    // 1. Proyectar grafo con propiedades
    CALL gds.graph.project(
        'analisis-fraude',
        'Empresa',
        {
            EMITE_FACTURA: {
                properties: ['monto_total']
            }
        },
        {
            nodeProperties: ['capital_social', 'empleados']
        }
    )
    """,
    
    "paso_2_pagerank": """
    // 2. Calcular PageRank
    CALL gds.pageRank.write('analisis-fraude', {
        writeProperty: 'pagerank_score',
        dampingFactor: 0.85
    })
    """,
    
    "paso_3_comunidades": """
    // 3. Detectar comunidades
    CALL gds.louvain.write('analisis-fraude', {
        writeProperty: 'community_id'
    })
    """,
    
    "paso_4_betweenness": """
    // 4. Calcular Betweenness
    CALL gds.betweenness.write('analisis-fraude', {
        writeProperty: 'betweenness_score'
    })
    """,
    
    "paso_5_analisis": """
    // 5. Análisis combinado
    MATCH (e:Empresa)
    WHERE e.pagerank_score IS NOT NULL
    
    // Normalizar scores y combinar
    WITH e,
         e.pagerank_score AS pagerank,
         e.betweenness_score AS betweenness,
         e.community_id AS community,         
         CASE WHEN e.es_fantasma THEN 50 ELSE 0 END AS flag_fantasma,
         CASE WHEN e.capital_social < 5000 THEN 20 ELSE 0 END AS flag_capital,
         CASE WHEN e.empleados = 0 THEN 15 ELSE 0 END AS flag_empleados
    
    // Score combinado
    WITH e, pagerank, betweenness, community,
         (pagerank * 10) + (betweenness * 5) + flag_fantasma + flag_capital + flag_empleados AS score_total
    
    RETURN 
        e.nombre AS empresa,
        community AS comunidad,
        round(pagerank, 4) AS pagerank,
        round(betweenness, 2) AS betweenness,
        round(score_total, 2) AS score_fraude,
        CASE 
            WHEN score_total > 50 THEN 'ALTO'
            WHEN score_total > 25 THEN 'MEDIO'
            ELSE 'BAJO'
        END AS nivel_riesgo
    ORDER BY score_fraude DESC
    LIMIT 30
    """
}

# ============================================================================
# 8. UTILIDADES GDS
# ============================================================================

GDS_UTILIDADES = {
    "version": "RETURN gds.version() AS version",
    "list_algos": "CALL gds.list() YIELD name, description",
    "node_properties": "CALL gds.graph.nodeProperties.stream('red-empresas', ['capital_social'])",
    "degree_distribution": "CALL gds.graph.relationships.stream('red-empresas') YIELD sourceNodeId",
}


# ============================================================================
# CATÁLOGO DE ALGORITMOS GDS
# ============================================================================

GDS_ALGORITMOS_CATALOGO = {
    "Centralidad": {
        "PageRank": "gds.pageRank",
        "ArticleRank": "gds.articleRank",
        "Betweenness": "gds.betweenness",
        "Closeness": "gds.closeness",
        "Degree": "gds.degree",
        "Harmonic": "gds.closeness.harmonic"
    },
    "Comunidades": {
        "Louvain": "gds.louvain",
        "Label Propagation": "gds.labelPropagation",
        "WCC": "gds.wcc",
        "Triangle Count": "gds.triangleCount",
        "Local Clustering Coefficient": "gds.localClusteringCoefficient"
    },
    "Similitud": {
        "Node Similarity": "gds.nodeSimilarity",
        "KNN": "gds.knn",
        "Filtered KNN": "gds.knn.filtered"
    },
    "Path Finding": {
        "Dijkstra": "gds.shortestPath.dijkstra",
        "A*": "gds.shortestPath.astar",
        "Yen's K-Shortest": "gds.shortestPath.yens",
        "All Shortest Paths": "gds.allShortestPaths.dijkstra",
        "Random Walk": "gds.randomWalk"
    },
    "Embeddings": {
        "Node2Vec": "gds.node2vec",
        "FastRP": "gds.fastRP",
        "GraphSAGE": "gds.beta.graphSage"
    },
    "Link Prediction": {
        "Adamic Adar": "gds.linkprediction.adamicAdar",
        "Common Neighbors": "gds.linkprediction.commonNeighbors",
        "Preferential Attachment": "gds.linkprediction.preferentialAttachment"
    }
}


if __name__ == "__main__":
    print("=" * 70)
    print("CONSULTAS Y EJEMPLOS GDS (GRAPH DATA SCIENCE)")
    print("=" * 70)
    print()
    print("Este archivo contiene ejemplos de los algoritmos GDS más útiles")
    print("para el análisis de fraude de IVA.")
    print()
    print("Categorías de algoritmos:")
    for cat, algos in GDS_ALGORITMOS_CATALOGO.items():
        print(f"\n{cat} ({len(algos)} algoritmos):")
        for nombre in list(algos.keys())[:3]:
            print(f"  - {nombre}")
    print("\n" + "=" * 70)
