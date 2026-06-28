#!/usr/bin/env python3
"""
Agente de outreach comercial para Myrenting.
Identifica gestoras/concesionarios, redacta emails personalizados
y gestiona una agenda de reuniones.
"""
import os, json, csv, re, time
from datetime import datetime, timedelta
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))

CONTACTOS_FILE = os.path.join(os.path.dirname(__file__), 'outreach_contactos.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'agente_outreach.log')

# Base de datos de contactos objetivo (gestoras y concesionarios de renting en España)
TARGETS_BASE = [
    # Gestoras nacionales
    {'nombre': 'Arval España', 'tipo': 'gestora', 'empresa': 'BNP Paribas Leasing Solutions', 'ciudad': 'Madrid', 'email': 'comercial@arval.es', 'web': 'arval.es', 'contactado': False, 'estado': 'pendiente'},
    {'nombre': 'Ayvens España', 'tipo': 'gestora', 'empresa': 'Société Générale', 'ciudad': 'Madrid', 'email': 'info@ayvens.com', 'web': 'ayvens.com', 'contactado': False, 'estado': 'pendiente'},
    {'nombre': 'Alphabet España', 'tipo': 'gestora', 'empresa': 'BMW Group', 'ciudad': 'Madrid', 'email': 'info@alphabet.es', 'web': 'alphabet.es', 'contactado': False, 'estado': 'pendiente'},
    {'nombre': 'Kinto España', 'tipo': 'gestora', 'empresa': 'Toyota Financial Services', 'ciudad': 'Madrid', 'email': 'info@kinto-europe.com', 'web': 'kinto-europe.com', 'contactado': False, 'estado': 'pendiente'},
    {'nombre': 'Leasys España', 'tipo': 'gestora', 'empresa': 'Stellantis', 'ciudad': 'Barcelona', 'email': 'leasys.spain@leasys.com', 'web': 'leasys.com', 'contactado': False, 'estado': 'pendiente'},
    {'nombre': 'LeasePlan España', 'tipo': 'gestora', 'empresa': 'LeasePlan Corporation', 'ciudad': 'Madrid', 'email': 'info@leaseplan.es', 'web': 'leaseplan.es', 'contactado': False, 'estado': 'pendiente'},
    {'nombre': 'Mobility by Endesa', 'tipo': 'gestora', 'empresa': 'Endesa', 'ciudad': 'Madrid', 'email': 'movilidad@endesa.com', 'web': 'endesa.com', 'contactado': False, 'estado': 'pendiente'},
    {'nombre': 'REVEL', 'tipo': 'gestora', 'empresa': 'REVEL', 'ciudad': 'Barcelona', 'email': 'business@driverevel.com', 'web': 'driverevel.com', 'contactado': False, 'estado': 'pendiente'},
    # Concesionarios premium Barcelona
    {'nombre': 'Automoviles Riera', 'tipo': 'concesionario', 'empresa': 'Grupo Riera', 'ciudad': 'Barcelona', 'marca': 'BMW', 'email': '', 'web': '', 'contactado': False, 'estado': 'pendiente'},
    {'nombre': 'AUTISA Madrid', 'tipo': 'concesionario', 'empresa': 'AUTISA', 'ciudad': 'Madrid', 'marca': 'Volkswagen', 'email': '', 'web': '', 'contactado': False, 'estado': 'pendiente'},
    {'nombre': 'Stellantis Barcelona', 'tipo': 'concesionario', 'empresa': 'Stellantis', 'ciudad': 'Barcelona', 'marca': 'Peugeot/Citroën', 'email': '', 'web': '', 'contactado': False, 'estado': 'pendiente'},
]


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
    # Inicializar con base
    guardar_contactos(TARGETS_BASE)
    return TARGETS_BASE


def guardar_contactos(contactos: list):
    with open(CONTACTOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(contactos, f, ensure_ascii=False, indent=2)


def generar_email_claude(contacto: dict, contexto: dict = None) -> dict:
    """
    Usa Claude para generar un email personalizado de colaboración.
    Devuelve {'asunto': str, 'cuerpo': str}
    """
    tipo = contacto.get('tipo', 'empresa')
    nombre = contacto.get('nombre', '')
    empresa = contacto.get('empresa', '')
    ciudad = contacto.get('ciudad', '')
    marca = contacto.get('marca', '')

    prompt_tipo = {
        'gestora': f"""Eres el fundador de Myrenting.es, el comparador de renting de coches número 1 en España.
Escribe un email profesional y personalizado a {nombre} ({empresa}), una gestora de renting,
para proponer una colaboración de afiliación: ellos nos pagan una comisión por cada lead cualificado que les enviemos.

Datos de Myrenting:
- Comparamos +1.000 ofertas de 6+ gestoras en España
- Tráfico orgánico creciente de personas buscando renting
- Sin registro requerido para los usuarios
- Leads cualificados (ya han buscado y comparado)

El email debe ser conciso (máximo 200 palabras), profesional pero cercano,
mencionar el beneficio concreto para ellos, y terminar con una propuesta de reunión corta (15-20 min por videollamada).
NO uses lenguaje de spam. NO prometas resultados específicos de tráfico.
Incluye una firma con: Matthias (fundador Myrenting.es)""",

        'concesionario': f"""Eres el fundador de Myrenting.es, el comparador de renting de coches en España.
Escribe un email profesional a {nombre}, concesionario de {marca} en {ciudad},
para proponer que listen sus ofertas de renting en nuestra plataforma a cambio de comisión por lead.

El email debe ser conciso (máximo 180 palabras), mencionar que podemos
traerles clientes ya decididos a contratar renting, y proponer una llamada corta.
Firma: Matthias (fundador Myrenting.es)""",
    }

    prompt = prompt_tipo.get(tipo, prompt_tipo['gestora'])

    try:
        message = client.messages.create(
            model='claude-sonnet-4-6',
            max_tokens=800,
            messages=[{'role': 'user', 'content': prompt}]
        )
        texto = message.content[0].text

        # Extraer asunto y cuerpo
        asunto = f'Propuesta de colaboración - Myrenting.es · Comparador de renting'
        if 'Asunto:' in texto:
            lines = texto.split('\n')
            for i, l in enumerate(lines):
                if l.startswith('Asunto:'):
                    asunto = l.replace('Asunto:', '').strip()
                    texto = '\n'.join(lines[i+1:]).strip()
                    break

        return {'asunto': asunto, 'cuerpo': texto}
    except Exception as e:
        log(f'Error generando email con Claude: {e}')
        return generar_email_fallback(contacto)


def generar_email_fallback(contacto: dict) -> dict:
    """Email genérico cuando Claude no está disponible."""
    nombre = contacto.get('nombre', 'equipo')
    return {
        'asunto': 'Propuesta de colaboración – Myrenting.es',
        'cuerpo': f"""Hola,

Me pongo en contacto desde Myrenting.es, comparador de renting de coches en España con más de 1.000 ofertas activas.

Me gustaría explorar una posible colaboración: incluir vuestras ofertas en nuestra plataforma y enviaros leads cualificados a cambio de una comisión acordada.

¿Tendríais 15 minutos para una videollamada esta semana?

Un saludo,
Matthias
Fundador · Myrenting.es
mtiagconsulting@gmail.com"""
    }


def proponer_reunion(contacto: dict) -> dict:
    """Genera propuesta de horarios de reunión para los próximos días hábiles."""
    hoy = datetime.now()
    slots = []
    dia = hoy + timedelta(days=1)
    count = 0
    while count < 3:
        if dia.weekday() < 5:  # Lunes-Viernes
            slots.append(dia.strftime('%A %d de %B') + ' a las 10:00')
            slots.append(dia.strftime('%A %d de %B') + ' a las 16:00')
            count += 1
        dia += timedelta(days=1)
    return {'slots': slots[:4], 'zoom_link': 'https://cal.app/myrenting'}


def exportar_csv(contactos: list, filepath: str = None):
    """Exporta los contactos a CSV para seguimiento."""
    if not filepath:
        filepath = os.path.join(os.path.dirname(__file__), f'outreach_{datetime.now().strftime("%Y%m%d")}.csv')
    fields = ['nombre', 'tipo', 'empresa', 'ciudad', 'email', 'estado', 'fecha_contacto', 'notas']
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(contactos)
    log(f'CSV exportado: {filepath}')
    return filepath


def mostrar_pipeline(contactos: list):
    """Muestra el estado del pipeline de outreach."""
    estados = {}
    for c in contactos:
        e = c.get('estado', 'pendiente')
        estados[e] = estados.get(e, 0) + 1
    print('\n=== PIPELINE DE OUTREACH ===')
    for estado, count in sorted(estados.items()):
        print(f'  {estado:20s}: {count:3d}')
    print(f'  {"TOTAL":20s}: {len(contactos):3d}')
    print()


def run_outreach(modo: str = 'preview', max_contactos: int = 3):
    """
    Ejecuta el ciclo de outreach.
    modo='preview': muestra emails sin enviar
    modo='csv': exporta CSV listo para enviar con herramienta externa
    modo='send': (requiere configuración SMTP) envía emails
    """
    log(f'=== Agente Outreach iniciado · modo={modo} ===')

    contactos = cargar_contactos()
    pendientes = [c for c in contactos if c.get('estado') == 'pendiente']
    log(f'Contactos pendientes: {len(pendientes)}')

    mostrar_pipeline(contactos)

    procesados = 0
    for contacto in pendientes[:max_contactos]:
        log(f'Generando email para: {contacto["nombre"]}')

        email = generar_email_claude(contacto)
        reuniones = proponer_reunion(contacto)

        # Añadir slots de reunión al cuerpo del email
        slots_texto = '\n\nHorarios disponibles para videollamada:\n'
        for slot in reuniones['slots'][:3]:
            slots_texto += f'  · {slot}\n'
        email['cuerpo'] += slots_texto

        if modo == 'preview':
            print(f'\n{"="*60}')
            print(f'DESTINATARIO: {contacto["nombre"]} <{contacto.get("email","(sin email)")}>')
            print(f'ASUNTO: {email["asunto"]}')
            print(f'\n{email["cuerpo"]}')
            print('='*60)

        # Actualizar estado del contacto
        idx = next(i for i, c in enumerate(contactos) if c['nombre'] == contacto['nombre'])
        contactos[idx]['estado'] = 'email_preparado' if modo == 'preview' else 'contactado'
        contactos[idx]['fecha_contacto'] = datetime.now().strftime('%Y-%m-%d')
        contactos[idx]['asunto_email'] = email['asunto']

        procesados += 1
        time.sleep(1)  # Pausa entre generaciones

    guardar_contactos(contactos)
    log(f'Emails preparados: {procesados}')

    if modo == 'csv':
        exportar_csv(contactos)

    log('=== Agente Outreach completado ===')
    return contactos


def agregar_contacto(nombre: str, empresa: str, ciudad: str, email: str = '',
                     tipo: str = 'concesionario', marca: str = ''):
    """Añade un nuevo contacto al pipeline."""
    contactos = cargar_contactos()
    nuevo = {
        'nombre': nombre, 'empresa': empresa, 'ciudad': ciudad,
        'email': email, 'tipo': tipo, 'marca': marca,
        'contactado': False, 'estado': 'pendiente',
        'fecha_agregado': datetime.now().strftime('%Y-%m-%d'),
        'notas': '',
    }
    contactos.append(nuevo)
    guardar_contactos(contactos)
    log(f'Contacto añadido: {nombre}')
    return nuevo


def actualizar_estado(nombre: str, estado: str, notas: str = ''):
    """Actualiza el estado de un contacto (ej: tras respuesta)."""
    contactos = cargar_contactos()
    for c in contactos:
        if c['nombre'] == nombre:
            c['estado'] = estado
            c['notas'] = notas
            c['ultima_actualizacion'] = datetime.now().strftime('%Y-%m-%d')
            break
    guardar_contactos(contactos)
    log(f'Estado actualizado: {nombre} → {estado}')


if __name__ == '__main__':
    import sys
    modo = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    max_c = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    run_outreach(modo=modo, max_contactos=max_c)
