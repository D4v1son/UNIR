"""
Script para generar datos sintéticos de fraude de IVA
Genera empresas, directivos, facturas y transacciones con patrones de fraude

Este script crea datos que simulan:
1. Empresas fantasmas (creadas recientemente, sin actividad real)
2. Fraude carrusel (cadenas circulares de facturas)
3. Redes de empresas con administradores comunes
4. Transacciones desproporcionadas
5. Flujos anómalos entre países

Autor: Marlon Cárdenas Bonett 2025
"""

import random
import json
from datetime import datetime, timedelta
from faker import Faker
import config

# Configurar Faker para generar datos en español
fake = Faker('es_ES')
random.seed(config.RANDOM_SEED)
Faker.seed(config.RANDOM_SEED)

# Lista de países para el fraude carrusel (intracomunitario)
PAISES_UE = ['España', 'Francia', 'Alemania', 'Italia', 'Países Bajos', 
             'Bélgica', 'Portugal', 'Polonia', 'República Checa']

# Sectores económicos
SECTORES = ['Tecnología', 'Construcción', 'Comercio al por mayor', 
            'Servicios', 'Consultoría', 'Importación/Exportación']


def generar_nif():
    """Genera un NIF español sintético"""
    letra = random.choice('ABCDEFGHJKLMNPQRSUVW')
    numeros = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{letra}{numeros}"


def generar_dni():
    """Genera un DNI español sintético válido"""
    # Generar 8 dígitos aleatorios
    numeros = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    
    # Calcular letra del DNI
    letras_dni = 'TRWAGMYFPDXBNJZSQVHLCKE'
    letra = letras_dni[int(numeros) % 23]
    
    return f"{numeros}{letra}"


def generar_iban(pais='ES'):
    """Genera un IBAN sintético"""
    if pais == 'España':
        pais_code = 'ES'
    elif pais == 'Francia':
        pais_code = 'FR'
    elif pais == 'Alemania':
        pais_code = 'DE'
    elif pais == 'Italia':
        pais_code = 'IT'
    else:
        pais_code = 'ES'
    
    check = random.randint(10, 99)
    banco = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    sucursal = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    cuenta = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    
    return f"{pais_code}{check}{banco}{sucursal}{cuenta}"


def generar_empresas(num_empresas):
    """
    Genera un conjunto de empresas con características variadas
    Algunas serán empresas legítimas y otras empresas fantasma
    """
    empresas = []
    
    # 30% serán empresas fantasma (con características sospechosas)
    num_fantasma = int(num_empresas * 0.3)
    
    for i in range(num_empresas):
        es_fantasma = i < num_fantasma
        pais = random.choice(PAISES_UE)
        
        # Fecha de constitución
        if es_fantasma:
            # Empresas fantasma: creadas recientemente
            fecha_constitucion = fake.date_between(start_date='-1y', end_date='today')
        else:
            # Empresas legítimas: más antiguas
            fecha_constitucion = fake.date_between(start_date='-10y', end_date='-1y')
        
        # Capital social
        if es_fantasma:
            # Empresas fantasma: capital mínimo
            capital_social = random.choice([3000, 3100, 3500])
        else:
            # Empresas legítimas: capital variable
            capital_social = random.choice([10000, 25000, 50000, 100000, 500000])
        
        empresa = {
            'id': i + 1,
            'nif': generar_nif(),
            'nombre': fake.company() if not es_fantasma else f"Comercial {fake.last_name()} S.L.",
            'pais': pais,
            'fecha_constitucion': fecha_constitucion.isoformat(),
            'capital_social': capital_social,
            'sector': random.choice(SECTORES),
            'es_fantasma': es_fantasma,
            'empleados': 0 if es_fantasma else random.randint(5, 100),
            'direccion': fake.address().replace('\n', ', ')
        }
        
        empresas.append(empresa)
    
    return empresas


def generar_directivos(num_directivos, empresas):
    """
    Genera directivos que administran empresas
    Algunos directivos administrarán múltiples empresas (patrón de fraude)
    """
    directivos = []
    
    for i in range(num_directivos):
        directivo = {
            'id': i + 1,
            'dni': generar_dni(),
            'nombre': fake.name(),
            'fecha_nacimiento': fake.date_of_birth(minimum_age=25, maximum_age=70).isoformat(),
            'nacionalidad': random.choice(PAISES_UE)
        }
        directivos.append(directivo)
    
    # Asignar directivos a empresas
    administraciones = []
    
    # 20% de los directivos administrarán múltiples empresas (patrón de fraude)
    directivos_multiples = random.sample(directivos, k=int(num_directivos * 0.2))
    
    for empresa in empresas:
        # Empresas fantasma: más probable que tengan directivos compartidos
        if empresa['es_fantasma'] and random.random() < 0.7:
            directivo = random.choice(directivos_multiples)
        else:
            directivo = random.choice(directivos)
        
        administraciones.append({
            'directivo_id': directivo['id'],
            'empresa_id': empresa['id'],
            'cargo': random.choice(['Administrador Único', 'Consejero', 'Presidente']),
            'fecha_inicio': empresa['fecha_constitucion']
        })
    
    return directivos, administraciones


def generar_cuentas_bancarias(num_cuentas, empresas):
    """
    Genera cuentas bancarias asociadas a empresas
    """
    cuentas = []
    
    for i in range(num_cuentas):
        empresa = random.choice(empresas)
        
        cuenta = {
            'id': i + 1,
            'iban': generar_iban(empresa['pais']),
            'banco': fake.company() + ' Bank',
            'empresa_id': empresa['id'],
            'fecha_apertura': fake.date_between(
                start_date=datetime.fromisoformat(empresa['fecha_constitucion']), 
                end_date='today'
            ).isoformat()
        }
        cuentas.append(cuenta)
    
    return cuentas


def generar_transacciones(num_transacciones, empresas):
    """
    Genera transacciones (facturas) entre empresas
    Incluye patrones de fraude:
    - Cadenas circulares (fraude carrusel)
    - Montos desproporcionados
    - Empresas que solo comercian entre sí
    """
    transacciones = []
    
    # Crear algunas cadenas circulares para fraude carrusel
    # Seleccionar 3-4 empresas fantasma para cada cadena
    num_cadenas = 3
    empresas_fantasma = [e for e in empresas if e['es_fantasma']]
    
    cadenas_circulares = []
    for _ in range(num_cadenas):
        if len(empresas_fantasma) >= 4:
            cadena = random.sample(empresas_fantasma, k=random.randint(3, 5))
            cadenas_circulares.append(cadena)
    
    transaccion_id = 1
    
    # Generar transacciones para cadenas circulares (fraude carrusel)
    for cadena in cadenas_circulares:
        for i in range(len(cadena)):
            emisor = cadena[i]
            receptor = cadena[(i + 1) % len(cadena)]  # Circular
            
            # Múltiples transacciones en la cadena
            for _ in range(random.randint(3, 7)):
                # Montos altos (típico del fraude carrusel)
                monto_base = random.uniform(50000, 500000)
                iva_pct = 0.21
                
                fecha = fake.date_between(start_date='-6m', end_date='today')
                
                transaccion = {
                    'id': transaccion_id,
                    'numero_factura': f"FC-{transaccion_id:06d}",
                    'emisor_id': emisor['id'],
                    'receptor_id': receptor['id'],
                    'fecha': fecha.isoformat(),
                    'monto_base': round(monto_base, 2),
                    'iva': round(monto_base * iva_pct, 2),
                    'monto_total': round(monto_base * (1 + iva_pct), 2),
                    'concepto': f"Venta de mercancías - {fake.catch_phrase()}",
                    'es_intracomunitaria': emisor['pais'] != receptor['pais'],
                    'patron_fraude': 'carrusel'
                }
                
                transacciones.append(transaccion)
                transaccion_id += 1
    
    # Generar transacciones normales y otras con patrones sospechosos
    while transaccion_id <= num_transacciones:
        emisor = random.choice(empresas)
        receptor = random.choice([e for e in empresas if e['id'] != emisor['id']])
        
        # Determinar si es una transacción sospechosa
        es_sospechosa = random.random() < 0.3
        
        if es_sospechosa and emisor['es_fantasma']:
            # Monto desproporcionado para empresa fantasma
            monto_base = random.uniform(100000, 1000000)
            patron = 'monto_desproporcionado'
        else:
            # Monto normal
            monto_base = random.uniform(1000, 50000)
            patron = None
        
        iva_pct = 0.21 if emisor['pais'] == 'España' else 0.19
        fecha = fake.date_between(start_date='-1y', end_date='today')
        
        transaccion = {
            'id': transaccion_id,
            'numero_factura': f"FC-{transaccion_id:06d}",
            'emisor_id': emisor['id'],
            'receptor_id': receptor['id'],
            'fecha': fecha.isoformat(),
            'monto_base': round(monto_base, 2),
            'iva': round(monto_base * iva_pct, 2),
            'monto_total': round(monto_base * (1 + iva_pct), 2),
            'concepto': fake.catch_phrase(),
            'es_intracomunitaria': emisor['pais'] != receptor['pais'],
            'patron_fraude': patron
        }
        
        transacciones.append(transaccion)
        transaccion_id += 1
    
    return transacciones


def guardar_datos(empresas, directivos, administraciones, cuentas, transacciones):
    """
    Guarda todos los datos generados en archivos JSON
    """
    datos = {
        'empresas': empresas,
        'directivos': directivos,
        'administraciones': administraciones,
        'cuentas_bancarias': cuentas,
        'transacciones': transacciones,
        'metadatos': {
            'fecha_generacion': datetime.now().isoformat(),
            'num_empresas': len(empresas),
            'num_empresas_fantasma': len([e for e in empresas if e['es_fantasma']]),
            'num_directivos': len(directivos),
            'num_transacciones': len(transacciones),
            'num_transacciones_carrusel': len([t for t in transacciones if t.get('patron_fraude') == 'carrusel'])
        }
    }
    
    with open('datos_fraude_iva.json', 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Datos generados y guardados en 'datos_fraude_iva.json'")
    print(f"  - Empresas: {len(empresas)} ({datos['metadatos']['num_empresas_fantasma']} fantasma)")
    print(f"  - Directivos: {len(directivos)}")
    print(f"  - Transacciones: {len(transacciones)} ({datos['metadatos']['num_transacciones_carrusel']} en cadenas circulares)")
    print(f"  - Cuentas bancarias: {len(cuentas)}")


def main():
    """
    Función principal que orquesta la generación de datos
    """
    print("=" * 60)
    print("GENERADOR DE DATOS SINTÉTICOS DE FRAUDE DE IVA")
    print("=" * 60)
    print()
    
    print("1. Generando empresas...")
    empresas = generar_empresas(config.NUM_EMPRESAS)
    print(f"   ✓ {len(empresas)} empresas generadas")
    
    print("2. Generando directivos y administraciones...")
    directivos, administraciones = generar_directivos(config.NUM_DIRECTIVOS, empresas)
    print(f"   ✓ {len(directivos)} directivos generados")
    print(f"   ✓ {len(administraciones)} relaciones de administración")
    
    print("3. Generando cuentas bancarias...")
    cuentas = generar_cuentas_bancarias(config.NUM_CUENTAS_BANCARIAS, empresas)
    print(f"   ✓ {len(cuentas)} cuentas bancarias generadas")
    
    print("4. Generando transacciones (incluyendo patrones de fraude)...")
    transacciones = generar_transacciones(config.NUM_TRANSACCIONES, empresas)
    print(f"   ✓ {len(transacciones)} transacciones generadas")
    
    print()
    print("5. Guardando datos en archivo JSON...")
    guardar_datos(empresas, directivos, administraciones, cuentas, transacciones)
    
    print()
    print("=" * 60)
    print("¡Generación completada exitosamente!")
    print("=" * 60)


if __name__ == "__main__":
    main()
