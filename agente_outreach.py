#!/usr/bin/env python3
"""
Agente de outreach comercial para Myrenting — sin coste, sin APIs de pago.
Genera emails con plantillas Python y gestiona el pipeline de contactos.
"""
import os, json, csv
from datetime import datetime, timedelta

CONTACTOS_FILE = os.path.join(os.path.dirname(__file__), 'outreach_contactos.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'agente_outreach.log')

TARGETS_BASE = [
    {'nombre': 'Arval España',        'tipo': 'gestora',       'empresa': 'BNP Paribas',           'ciudad': 'Madrid',    'email': 'comercial@arval.es',           'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Ayvens España',       'tipo': 'gestora',       'empresa': 'Société Générale',       'ciudad': 'Madrid',    'email': 'info@ayvens.com',              'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Alphabet España',     'tipo': 'gestora',       'empresa': 'BMW Group',              'ciudad': 'Madrid',    'email': 'info@alphabet.es',             'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Kinto España',        'tipo': 'gestora',       'empresa': 'Toyota Financial',       'ciudad': 'Madrid',    'email': 'info@kinto-europe.com',        'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Leasys España',       'tipo': 'gestora',       'empresa': 'Stellantis',             'ciudad': 'Barcelona', 'email': 'leasys.spain@leasys.com',      'estado': 'pendiente', 'marca': ''},
    {'nombre': 'LeasePlan España',    'tipo': 'gestora',       'empresa': 'LeasePlan Corporation',  'ciudad': 'Madrid',    'email': 'info@leaseplan.es',            'estado': 'pendiente', 'marca': ''},
    {'nombre': 'REVEL',               'tipo': 'gestora',       'empresa': 'REVEL',                  'ciudad': 'Barcelona', 'email': 'business@driverevel.com',      'estado': 'pendiente', 'marca': ''},
    {'nombre': 'ALD Automotive',      'tipo': 'gestora',       'empresa': 'Société Générale',       'ciudad': 'Madrid',    'email': 'ald@aldautomotive.com',        'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Athlon España',       'tipo': 'gestora',       'empresa': 'Athlon',                 'ciudad': 'Madrid',    'email': 'info.es@athlon.com',           'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Mobility by Endesa',  'tipo': 'gestora',       'empresa': 'Endesa',                 'ciudad': 'Madrid',    'email': 'movilidad@endesa.com',         'estado': 'pendiente', 'marca': ''},
]

PLANTILLAS = {
    'gestora': {
        'asunto': 'Propuesta de colaboración – Myrenting.es · Comparador de renting n.º 1',
        'cuerpo': """Hola {nombre},

Me llamo Matthias, soy el fundador de Myrenting.es, comparador de renting de coches en España con más de 1.000 ofertas activas de las principales gestoras del mercado.

Cada día recibimos visitas de particulares, autónomos y empresas que ya han decidido contratar renting y están comparando precios. Son leads en fase final de decisión, con alta intención de compra.

Me gustaría explorar una colaboración sencilla: incluimos vuestras ofertas en nuestra plataforma y os enviamos esos leads cualificados a cambio de una comisión acordada. Sin exclusividad, sin coste fijo para vosotros.

¿Tendríais 15-20 minutos para una videollamada esta semana o la próxima? Os propongo:

{slots}

Un saludo,
Matthias
Fundador · Myrenting.es
mtiagconsulting@gmail.com
""",
    },
    'concesionario': {
        'asunto': 'Lleva tu renting a más clientes – Myrenting.es',
        'cuerpo': """Hola {nombre},

Soy Matthias, fundador de Myrenting.es, el comparador de renting de coches en España.

Contacto con vosotros porque sabemos que muchos clientes buscan renting de {marca} online antes de visitar un concesionario. En Myrenting podéis aparecer directamente ante esos clientes, sin coste inicial y con comisión solo por lead cerrado.

¿Os interesaría incluir vuestras ofertas de renting en nuestra plataforma? Una llamada de 15 minutos sería suficiente para explicaros cómo funciona.

Disponibilidad esta semana:

{slots}

Saludos,
Matthias
Myrenting.es · mtiagconsulting@gmail.com
""",
    },
}


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def cargar_contactos() -> list:
    if os.path.exists(CONTACTOS_FILE):
        with open(CONTACTOS_FILE) as f:
            return json.load(f)
    guardar_contactos(TARGETS_BASE)
    return list(TARGETS_BASE)


def guardar_contactos(contactos: list):
    with open(CONTACTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(contactos, f, ensure_ascii=False, indent=2)


def slots_reunion() -> str:
    """Genera 3 slots de reunión para los próximos días hábiles."""
    hoy = datetime.now()
    slots = []
    dia = hoy + timedelta(days=1)
    while len(slots) < 3:
        if dia.weekday() < 5:
            nombre_dia = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][dia.weekday()]
            slots.append(f'  · {nombre_dia} {dia.day}/{dia.month} a las 10:00h')
            slots.append(f'  · {nombre_dia} {dia.day}/{dia.month} a las 16:00h')
        dia += timedelta(days=1)
    return '\n'.join(slots[:4])


def generar_email(contacto: dict) -> dict:
    """Genera email personalizado con plantilla Python (sin coste)."""
    tipo = contacto.get('tipo', 'gestora')
    plantilla = PLANTILLAS.get(tipo, PLANTILLAS['gestora'])

    cuerpo = plantilla['cuerpo'].format(
        nombre=contacto.get('nombre', 'equipo'),
        empresa=contacto.get('empresa', ''),
        ciudad=contacto.get('ciudad', ''),
        marca=contacto.get('marca', 'vuestros modelos'),
        slots=slots_reunion(),
    )

    return {
        'asunto': plantilla['asunto'],
        'cuerpo': cuerpo,
    }


def mostrar_pipeline(contactos: list):
    estados = {}
    for c in contactos:
        e = c.get('estado', 'pendiente')
        estados[e] = estados.get(e, 0) + 1
    print('\n=== PIPELINE DE OUTREACH ===')
    for estado, count in sorted(estados.items()):
        bar = '█' * count
        print(f'  {estado:22s} {bar} {count}')
    print(f'  {"TOTAL":22s} {len(contactos)}')
    print()


def exportar_csv(contactos: list) -> str:
    filepath = os.path.join(
        os.path.dirname(__file__),
        f'outreach_{datetime.now().strftime("%Y%m%d")}.csv'
    )
    fields = ['nombre', 'tipo', 'empresa', 'ciudad', 'email', 'estado',
              'fecha_contacto', 'asunto_email', 'notas']
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(contactos)
    log(f'CSV exportado: {filepath}')
    return filepath


def run_outreach(modo: str = 'preview', max_contactos: int = 5):
    """
    Ejecuta el ciclo de outreach.

    modo='preview'  → imprime emails en pantalla
    modo='csv'      → exporta CSV con asuntos y cuerpos listos para copiar
    """
    log(f'=== Agente Outreach (coste cero) · modo={modo} ===')

    contactos = cargar_contactos()
    pendientes = [c for c in contactos if c.get('estado') == 'pendiente']
    log(f'Pendientes: {len(pendientes)} de {len(contactos)} contactos')

    mostrar_pipeline(contactos)

    procesados = 0
    for contacto in pendientes[:max_contactos]:
        email = generar_email(contacto)

        if modo == 'preview':
            sep = '─' * 60
            print(f'\n{sep}')
            print(f'PARA:    {contacto["nombre"]} <{contacto.get("email","(sin email)")}>')
            print(f'ASUNTO:  {email["asunto"]}')
            print(f'{sep}')
            print(email['cuerpo'])

        # Marcar como preparado y guardar el asunto para el CSV
        idx = next(i for i, c in enumerate(contactos) if c['nombre'] == contacto['nombre'])
        contactos[idx]['estado'] = 'email_preparado'
        contactos[idx]['fecha_contacto'] = datetime.now().strftime('%Y-%m-%d')
        contactos[idx]['asunto_email'] = email['asunto']

        procesados += 1

    guardar_contactos(contactos)
    log(f'Emails preparados: {procesados}')

    if modo == 'csv':
        ruta = exportar_csv(contactos)
        print(f'\nCSV listo para enviar: {ruta}')

    log('=== Agente Outreach completado ===')


def agregar_contacto(nombre: str, empresa: str, ciudad: str,
                     email: str = '', tipo: str = 'concesionario', marca: str = ''):
    """Añade un contacto nuevo al pipeline."""
    contactos = cargar_contactos()
    nuevo = {
        'nombre': nombre, 'empresa': empresa, 'ciudad': ciudad,
        'email': email, 'tipo': tipo, 'marca': marca,
        'estado': 'pendiente',
        'fecha_agregado': datetime.now().strftime('%Y-%m-%d'),
        'notas': '',
    }
    contactos.append(nuevo)
    guardar_contactos(contactos)
    log(f'Añadido: {nombre}')
    return nuevo


def actualizar_estado(nombre: str, estado: str, notas: str = ''):
    """Actualiza el estado tras una respuesta o llamada."""
    contactos = cargar_contactos()
    for c in contactos:
        if c['nombre'] == nombre:
            c['estado'] = estado
            if notas:
                c['notas'] = notas
            c['ultima_actualizacion'] = datetime.now().strftime('%Y-%m-%d')
            break
    guardar_contactos(contactos)
    log(f'Estado actualizado: {nombre} → {estado}')


if __name__ == '__main__':
    import sys
    modo = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    max_c = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    run_outreach(modo=modo, max_contactos=max_c)
