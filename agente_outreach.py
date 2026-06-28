#!/usr/bin/env python3
"""
Agente de outreach comercial para Myrenting — coste cero.
Genera emails personalizados y los envía via Gmail SMTP (gratis).

Uso:
  python agente_outreach.py preview          # Ver emails sin enviar
  python agente_outreach.py csv              # Exportar CSV
  python agente_outreach.py send             # Enviar (requiere GMAIL_USER + GMAIL_APP_PASSWORD)
  python agente_outreach.py send 3           # Enviar máximo 3 emails
"""
import os, json, csv, smtplib, time, sys
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

CONTACTOS_FILE = os.path.join(os.path.dirname(__file__), 'outreach_contactos.json')
LOG_FILE       = os.path.join(os.path.dirname(__file__), 'agente_outreach.log')

# Gmail: máximo recomendado para no caer en spam
MAX_EMAILS_POR_DIA = 20
PAUSA_ENTRE_EMAILS = 60  # segundos entre envíos

TARGETS_BASE = [
    {'nombre': 'Arval España',       'tipo': 'gestora',      'empresa': 'BNP Paribas',          'ciudad': 'Madrid',    'email': 'comercial@arval.es',          'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Ayvens España',      'tipo': 'gestora',      'empresa': 'Société Générale',      'ciudad': 'Madrid',    'email': 'info@ayvens.com',             'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Alphabet España',    'tipo': 'gestora',      'empresa': 'BMW Group',             'ciudad': 'Madrid',    'email': 'info@alphabet.es',            'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Kinto España',       'tipo': 'gestora',      'empresa': 'Toyota Financial',      'ciudad': 'Madrid',    'email': 'info@kinto-europe.com',       'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Leasys España',      'tipo': 'gestora',      'empresa': 'Stellantis',            'ciudad': 'Barcelona', 'email': 'leasys.spain@leasys.com',     'estado': 'pendiente', 'marca': ''},
    {'nombre': 'LeasePlan España',   'tipo': 'gestora',      'empresa': 'LeasePlan Corporation', 'ciudad': 'Madrid',    'email': 'info@leaseplan.es',           'estado': 'pendiente', 'marca': ''},
    {'nombre': 'REVEL',              'tipo': 'gestora',      'empresa': 'REVEL',                 'ciudad': 'Barcelona', 'email': 'business@driverevel.com',     'estado': 'pendiente', 'marca': ''},
    {'nombre': 'ALD Automotive',     'tipo': 'gestora',      'empresa': 'Société Générale',      'ciudad': 'Madrid',    'email': 'ald@aldautomotive.com',       'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Athlon España',      'tipo': 'gestora',      'empresa': 'Athlon',                'ciudad': 'Madrid',    'email': 'info.es@athlon.com',          'estado': 'pendiente', 'marca': ''},
    {'nombre': 'Mobility by Endesa', 'tipo': 'gestora',      'empresa': 'Endesa',                'ciudad': 'Madrid',    'email': 'movilidad@endesa.com',        'estado': 'pendiente', 'marca': ''},
]

PLANTILLAS = {
    'gestora': {
        'asunto': 'Propuesta de colaboración – Myrenting.es · Leads de renting cualificados',
        'cuerpo_html': """\
<html><body style="font-family:Arial,sans-serif;font-size:14px;color:#222;max-width:600px">
<p>Hola {nombre},</p>

<p>Me llamo <strong>Matthias</strong>, soy el fundador de
<a href="https://myrenting.es">Myrenting.es</a>, comparador de renting de coches
en España con más de 1.000 ofertas activas de las principales gestoras del mercado.</p>

<p>Cada día recibimos visitas de <strong>particulares, autónomos y empresas</strong>
que ya han decidido contratar renting y están comparando precios.
Son leads en <strong>fase final de decisión</strong>, con alta intención de compra.</p>

<p>Me gustaría explorar una colaboración sencilla:
<strong>incluimos vuestras ofertas en nuestra plataforma</strong> y os enviamos esos
leads cualificados a cambio de una comisión acordada.
Sin exclusividad, sin coste fijo para vosotros.</p>

<p>¿Tendríais <strong>15-20 minutos</strong> para una videollamada?
Os propongo estos horarios:</p>
<ul>{slots}</ul>

<p>Un saludo,<br>
<strong>Matthias</strong><br>
Fundador · <a href="https://myrenting.es">Myrenting.es</a><br>
<a href="mailto:mtiagconsulting@gmail.com">mtiagconsulting@gmail.com</a></p>
</body></html>""",
        'cuerpo_texto': """\
Hola {nombre},

Me llamo Matthias, soy el fundador de Myrenting.es, comparador de renting de coches
en España con más de 1.000 ofertas activas de las principales gestoras del mercado.

Cada día recibimos visitas de particulares, autónomos y empresas que ya han decidido
contratar renting y están comparando precios. Son leads en fase final de decisión,
con alta intención de compra.

Me gustaría explorar una colaboración: incluimos vuestras ofertas en nuestra
plataforma y os enviamos esos leads cualificados a cambio de una comisión acordada.
Sin exclusividad, sin coste fijo para vosotros.

¿Tendríais 15-20 minutos para una videollamada? Os propongo:
{slots}

Un saludo,
Matthias
Fundador · Myrenting.es
mtiagconsulting@gmail.com
""",
    },
    'concesionario': {
        'asunto': 'Lleva tu renting a más clientes – Myrenting.es',
        'cuerpo_html': """\
<html><body style="font-family:Arial,sans-serif;font-size:14px;color:#222;max-width:600px">
<p>Hola {nombre},</p>

<p>Soy <strong>Matthias</strong>, fundador de
<a href="https://myrenting.es">Myrenting.es</a>,
el comparador de renting de coches en España.</p>

<p>Muchos clientes buscan renting de <strong>{marca}</strong> online
antes de visitar un concesionario. En Myrenting podéis aparecer directamente
ante esos clientes, <strong>sin coste inicial</strong> y con comisión solo
por lead cerrado.</p>

<p>¿Os interesaría incluir vuestras ofertas en nuestra plataforma?
Una llamada de 15 minutos sería suficiente para explicaros cómo funciona.</p>

<p>Disponibilidad esta semana:</p>
<ul>{slots}</ul>

<p>Saludos,<br>
<strong>Matthias</strong><br>
Myrenting.es · <a href="mailto:mtiagconsulting@gmail.com">mtiagconsulting@gmail.com</a></p>
</body></html>""",
        'cuerpo_texto': """\
Hola {nombre},

Soy Matthias, fundador de Myrenting.es, el comparador de renting de coches en España.

Muchos clientes buscan renting de {marca} online antes de visitar un concesionario.
En Myrenting podéis aparecer directamente ante esos clientes, sin coste inicial
y con comisión solo por lead cerrado.

¿Os interesaría incluir vuestras ofertas? Una llamada de 15 minutos sería suficiente.

Disponibilidad:
{slots}

Saludos,
Matthias
Myrenting.es · mtiagconsulting@gmail.com
""",
    },
}


# ── Utilidades ─────────────────────────────────────────────────────────────

def log(msg: str):
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


def slots_reunion() -> tuple[str, str]:
    """Devuelve slots en formato HTML (<li>) y texto plano."""
    hoy = datetime.now()
    dias = []
    dia = hoy + timedelta(days=1)
    while len(dias) < 3:
        if dia.weekday() < 5:
            dias.append(dia)
        dia += timedelta(days=1)

    nombres = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
    html_items, texto_items = [], []
    for d in dias[:2]:
        nd = nombres[d.weekday()]
        fecha = f'{d.day}/{d.month}'
        html_items.append(f'<li>{nd} {fecha} a las 10:00h</li>')
        html_items.append(f'<li>{nd} {fecha} a las 16:00h</li>')
        texto_items.append(f'  · {nd} {fecha} a las 10:00h')
        texto_items.append(f'  · {nd} {fecha} a las 16:00h')

    return '\n'.join(html_items[:4]), '\n'.join(texto_items[:4])


def generar_email(contacto: dict) -> dict:
    tipo = contacto.get('tipo', 'gestora')
    plantilla = PLANTILLAS.get(tipo, PLANTILLAS['gestora'])
    slots_html, slots_txt = slots_reunion()

    vars_ = dict(
        nombre=contacto.get('nombre', 'equipo'),
        empresa=contacto.get('empresa', ''),
        ciudad=contacto.get('ciudad', ''),
        marca=contacto.get('marca', 'vuestros modelos'),
        slots=slots_html,
    )
    vars_txt = {**vars_, 'slots': slots_txt}

    return {
        'asunto':      plantilla['asunto'],
        'cuerpo_html': plantilla['cuerpo_html'].format(**vars_),
        'cuerpo_txt':  plantilla['cuerpo_texto'].format(**vars_txt),
    }


# ── Gmail SMTP ──────────────────────────────────────────────────────────────

def enviar_gmail(destinatario: str, asunto: str,
                 cuerpo_html: str, cuerpo_txt: str,
                 gmail_user: str, gmail_app_password: str) -> bool:
    """Envía un email via Gmail SMTP. Devuelve True si tuvo éxito."""
    msg = MIMEMultipart('alternative')
    msg['Subject'] = asunto
    msg['From']    = f'Matthias · Myrenting.es <{gmail_user}>'
    msg['To']      = destinatario
    msg['Reply-To'] = gmail_user

    msg.attach(MIMEText(cuerpo_txt,  'plain', 'utf-8'))
    msg.attach(MIMEText(cuerpo_html, 'html',  'utf-8'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=30) as server:
            server.ehlo()
            server.starttls()
            server.login(gmail_user, gmail_app_password)
            server.sendmail(gmail_user, destinatario, msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError:
        log('ERROR: Credenciales Gmail incorrectas. Revisa GMAIL_USER y GMAIL_APP_PASSWORD.')
        raise
    except Exception as e:
        log(f'ERROR enviando a {destinatario}: {e}')
        return False


def emails_enviados_hoy(contactos: list) -> int:
    hoy = datetime.now().strftime('%Y-%m-%d')
    return sum(1 for c in contactos if c.get('fecha_envio') == hoy)


# ── Pipeline ────────────────────────────────────────────────────────────────

def mostrar_pipeline(contactos: list):
    estados: dict[str, int] = {}
    for c in contactos:
        e = c.get('estado', 'pendiente')
        estados[e] = estados.get(e, 0) + 1
    print('\n=== PIPELINE DE OUTREACH ===')
    for estado, count in sorted(estados.items()):
        print(f'  {estado:25s} {"█" * count} {count}')
    print(f'  {"TOTAL":25s} {len(contactos)}')
    print()


def exportar_csv(contactos: list) -> str:
    ruta = os.path.join(
        os.path.dirname(__file__),
        f'outreach_{datetime.now().strftime("%Y%m%d")}.csv'
    )
    fields = ['nombre', 'tipo', 'empresa', 'ciudad', 'email',
              'estado', 'fecha_envio', 'asunto_email', 'notas']
    with open(ruta, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(contactos)
    log(f'CSV exportado: {ruta}')
    return ruta


# ── Main ────────────────────────────────────────────────────────────────────

def run_outreach(modo: str = 'preview', max_contactos: int = 5):
    """
    modo='preview'  → imprime emails en pantalla, no envía nada
    modo='csv'      → exporta CSV con todos los datos
    modo='send'     → envía emails reales via Gmail SMTP
    """
    log(f'=== Agente Outreach · modo={modo} ===')

    # Credenciales solo necesarias en modo send
    gmail_user = os.environ.get('GMAIL_USER', '')
    gmail_pass = os.environ.get('GMAIL_APP_PASSWORD', '')
    if modo == 'send' and (not gmail_user or not gmail_pass):
        log('ERROR: Faltan GMAIL_USER o GMAIL_APP_PASSWORD en variables de entorno.')
        log('       Configúralos en GitHub Secrets o en tu .env local.')
        sys.exit(1)

    contactos = cargar_contactos()
    pendientes = [c for c in contactos if c.get('estado') == 'pendiente' and c.get('email')]

    mostrar_pipeline(contactos)
    log(f'Pendientes con email: {len(pendientes)}')

    if modo == 'send':
        ya_enviados_hoy = emails_enviados_hoy(contactos)
        restantes_hoy   = MAX_EMAILS_POR_DIA - ya_enviados_hoy
        if restantes_hoy <= 0:
            log(f'Límite diario alcanzado ({MAX_EMAILS_POR_DIA} emails/día). Ejecútalo mañana.')
            return
        max_contactos = min(max_contactos, restantes_hoy)
        log(f'Enviando máximo {max_contactos} emails hoy (límite diario: {MAX_EMAILS_POR_DIA})')

    enviados = 0
    for contacto in pendientes[:max_contactos]:
        email = generar_email(contacto)

        if modo == 'preview':
            sep = '─' * 62
            print(f'\n{sep}')
            print(f'PARA:   {contacto["nombre"]} <{contacto["email"]}>')
            print(f'ASUNTO: {email["asunto"]}')
            print(sep)
            print(email['cuerpo_txt'])

        elif modo == 'send':
            log(f'Enviando a: {contacto["nombre"]} <{contacto["email"]}>')
            ok = enviar_gmail(
                destinatario=contacto['email'],
                asunto=email['asunto'],
                cuerpo_html=email['cuerpo_html'],
                cuerpo_txt=email['cuerpo_txt'],
                gmail_user=gmail_user,
                gmail_app_password=gmail_pass,
            )
            if ok:
                log(f'  ✓ Enviado correctamente')
                enviados += 1
                # Actualizar estado
                idx = next(i for i, c in enumerate(contactos) if c['nombre'] == contacto['nombre'])
                contactos[idx]['estado']       = 'contactado'
                contactos[idx]['fecha_envio']  = datetime.now().strftime('%Y-%m-%d')
                contactos[idx]['asunto_email'] = email['asunto']
                guardar_contactos(contactos)

                if enviados < max_contactos:
                    log(f'  Esperando {PAUSA_ENTRE_EMAILS}s antes del siguiente envío...')
                    time.sleep(PAUSA_ENTRE_EMAILS)
            else:
                log(f'  ✗ Error al enviar, marcando para reintentar')

        # En modo preview, marcar como preparado
        if modo == 'preview':
            idx = next(i for i, c in enumerate(contactos) if c['nombre'] == contacto['nombre'])
            contactos[idx]['estado']       = 'email_preparado'
            contactos[idx]['asunto_email'] = email['asunto']

    guardar_contactos(contactos)

    if modo == 'send':
        log(f'Emails enviados en esta ejecución: {enviados}')
    if modo == 'csv':
        exportar_csv(contactos)

    log('=== Agente Outreach completado ===')


def agregar_contacto(nombre: str, empresa: str, ciudad: str,
                     email: str = '', tipo: str = 'concesionario', marca: str = ''):
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
    modo   = sys.argv[1] if len(sys.argv) > 1 else 'preview'
    max_c  = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    run_outreach(modo=modo, max_contactos=max_c)
