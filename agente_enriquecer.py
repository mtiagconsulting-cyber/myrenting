#!/usr/bin/env python3
"""
Agente de enriquecimiento de datos de coches.
Para cada modelo en ofertas-db.json busca:
  - Descripción (Wikipedia ES, gratis)
  - Ficha técnica: potencia, consumo, CO2, dimensiones (Wikidata, gratis)
  - Imagen: prioriza local /img/modelos/, luego Arval URL, luego Wikidata

Guarda resultado en coches-specs.json (incremental, no re-fetcha lo ya guardado).
Uso: python agente_enriquecer.py
"""
import json, re, time, os, sys
from pathlib import Path
from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError
from urllib.parse import quote, urlencode
from datetime import datetime

BASE = Path(__file__).parent
OFERTAS_FILE = BASE / 'ofertas-db.json'
SPECS_FILE   = BASE / 'coches-specs.json'
IMG_DIR      = BASE / 'img' / 'modelos'
LOG_FILE     = BASE / 'agente_enriquecer.log'

HEADERS = {'User-Agent': 'Myrenting/1.0 (myrenting.es; bot@myrenting.es)'}
PAUSA   = 1.0  # segundos entre peticiones (respetar rate limits)


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def get(url: str, timeout=15) -> bytes | None:
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=timeout) as r:
            return r.read()
    except Exception as e:
        log(f'  GET error {url[:60]}: {e}')
        return None


def get_json(url: str) -> dict | None:
    raw = get(url)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except Exception:
        return None


# ── Slug / nombre de imagen local ────────────────────────────────────────────

def img_slug(make: str, model: str) -> str:
    t = f'{make}-{model}'.lower()
    for a, b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ü','u'),('ñ','n')]:
        t = t.replace(a, b)
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', t)).strip('-')


def imagen_local(make: str, model: str) -> str | None:
    """Devuelve la ruta web /img/modelos/xxx si existe un archivo local."""
    base_slug = img_slug(make, model)
    for ext in ('png', 'jpg', 'webp', 'avif'):
        p = IMG_DIR / f'{base_slug}.{ext}'
        if p.exists():
            return f'/img/modelos/{base_slug}.{ext}'
    # Intentar con solo make
    make_slug = re.sub(r'[^a-z0-9]+', '-', make.lower()).strip('-')
    for ext in ('png', 'jpg', 'webp', 'avif'):
        p = IMG_DIR / f'{make_slug}.{ext}'
        if p.exists():
            return f'/img/modelos/{make_slug}.{ext}'
    return None


# ── Wikipedia ES ──────────────────────────────────────────────────────────────

WIKI_ALIAS = {
    'VOLKSWAGEN': 'Volkswagen', 'VW': 'Volkswagen',
    'BMW': 'BMW', 'MERCEDES': 'Mercedes-Benz', 'MERCEDES-BENZ': 'Mercedes-Benz',
    'CITROEN': 'Citroën', 'PEUGEOT': 'Peugeot', 'RENAULT': 'Renault',
    'SEAT': 'SEAT', 'CUPRA': 'Cupra', 'SKODA': 'Škoda', 'AUDI': 'Audi',
    'FORD': 'Ford', 'OPEL': 'Opel', 'TOYOTA': 'Toyota', 'HONDA': 'Honda',
    'NISSAN': 'Nissan', 'HYUNDAI': 'Hyundai', 'KIA': 'Kia', 'DACIA': 'Dacia',
    'FIAT': 'Fiat', 'ALFA ROMEO': 'Alfa Romeo', 'VOLVO': 'Volvo',
    'LAND ROVER': 'Land Rover', 'JEEP': 'Jeep', 'MINI': 'MINI',
    'TESLA': 'Tesla', 'LEXUS': 'Lexus', 'MAZDA': 'Mazda',
    'MITSUBISHI': 'Mitsubishi', 'SUBARU': 'Subaru', 'SUZUKI': 'Suzuki',
    'ALPINE': 'Alpine', 'DS': 'DS Automobiles', 'POLESTAR': 'Polestar',
    'BYD': 'BYD', 'MG': 'MG Motor', 'JAECOO': 'Jaecoo', 'OMODA': 'Omoda',
}

def wiki_buscar(make: str, model: str) -> dict:
    """Busca en Wikipedia ES y devuelve {descripcion, imagen_wiki}."""
    make_norm = WIKI_ALIAS.get(make.upper(), make.title())
    titulo = f'{make_norm} {model.title()}'
    url = f'https://es.wikipedia.org/api/rest_v1/page/summary/{quote(titulo)}'
    data = get_json(url)
    time.sleep(PAUSA)

    if data and data.get('type') not in ('disambiguation', 'https://mediawiki.org/wiki/HyperSwitch/errors/not_found#page_revisions'):
        desc = data.get('extract', '')
        # Limpiar y truncar a 3 frases
        frases = re.split(r'(?<=[.!?])\s+', desc.strip())
        desc_corta = ' '.join(frases[:3]) if frases else ''
        img_wiki = data.get('thumbnail', {}).get('source', '') or data.get('originalimage', {}).get('source', '')
        return {'descripcion': desc_corta, 'imagen_wiki': img_wiki}

    # Fallback: buscar en inglés
    url_en = f'https://en.wikipedia.org/api/rest_v1/page/summary/{quote(titulo)}'
    data_en = get_json(url_en)
    time.sleep(PAUSA)
    if data_en and data_en.get('extract'):
        extract = data_en['extract']
        frases = re.split(r'(?<=[.!?])\s+', extract.strip())
        return {'descripcion': ' '.join(frases[:2]), 'imagen_wiki': data_en.get('thumbnail', {}).get('source', '')}

    return {'descripcion': '', 'imagen_wiki': ''}


# ── Wikidata ──────────────────────────────────────────────────────────────────

# Propiedades Wikidata relevantes para coches
WD_PROPS = {
    'P2565': 'consumo_l100',       # fuel consumption
    'P2281': 'co2_gkm',            # CO2 per km
    'P2049': 'ancho_mm',           # width
    'P2048': 'alto_mm',            # height
    'P2046': 'longitud_mm',        # area (se usa para long en algunos)
    'P2240': 'peso_kg',            # mass
    'P2610': 'cilindrada_cc',      # displacement
    'P6': 'asientos',              # number of seats
    'P571': 'anio_inicio',         # inception
    'P582': 'anio_fin',            # end time
}

def wikidata_buscar(make: str, model: str) -> dict:
    """Busca en Wikidata y extrae specs técnicas."""
    query = f'{make.title()} {model.title()}'
    url = ('https://www.wikidata.org/w/api.php?'
           f'action=wbsearchentities&search={quote(query)}&language=es'
           '&format=json&type=item&limit=5')
    data = get_json(url)
    time.sleep(PAUSA)
    if not data or not data.get('search'):
        return {}

    # Tomar primera entidad que parezca un modelo de coche
    qid = None
    for item in data['search']:
        desc = (item.get('description') or '').lower()
        label = (item.get('label') or '').lower()
        if any(w in desc for w in ['automóvil','coche','vehículo','automobile','car','model']):
            qid = item['id']
            break
        if any(w in desc for w in ['marca','empresa','company','corporation']):
            continue
        if query.lower() in label:
            qid = item['id']
            break

    if not qid:
        return {}

    url2 = f'https://www.wikidata.org/wiki/Special:EntityData/{qid}.json'
    entity_data = get_json(url2)
    time.sleep(PAUSA)
    if not entity_data:
        return {}

    claims = entity_data.get('entities', {}).get(qid, {}).get('claims', {})
    specs = {}

    for prop, key in WD_PROPS.items():
        if prop not in claims:
            continue
        try:
            snak = claims[prop][0]['mainsnak']
            val = snak.get('datavalue', {}).get('value', {})
            if isinstance(val, dict) and 'amount' in val:
                specs[key] = float(val['amount'])
            elif isinstance(val, dict) and 'time' in val:
                # Año: "+2018-01-01T00:00:00Z"
                m = re.search(r'\+?(\d{4})', val['time'])
                if m:
                    specs[key] = int(m.group(1))
            elif isinstance(val, (int, float)):
                specs[key] = val
        except Exception:
            continue

    # Imagen Wikidata (P18)
    if 'P18' in claims:
        try:
            img_name = claims['P18'][0]['mainsnak']['datavalue']['value']
            img_name_enc = img_name.replace(' ', '_')
            specs['imagen_wikidata'] = f'https://commons.wikimedia.org/wiki/Special:FilePath/{quote(img_name_enc)}'
        except Exception:
            pass

    return specs


# ── Descargar imagen si no existe localmente ──────────────────────────────────

def descargar_imagen(make: str, model: str, url: str) -> str | None:
    """Intenta descargar imagen y guardarla en img/modelos/. Devuelve ruta local."""
    if not url or not url.startswith('http'):
        return None
    nombre = img_slug(make, model)
    ext = 'jpg'
    for candidate in ['.png', '.jpg', '.jpeg', '.webp']:
        if candidate in url.lower():
            ext = candidate.lstrip('.')
            break
    dest = IMG_DIR / f'{nombre}.{ext}'
    if dest.exists():
        return f'/img/modelos/{nombre}.{ext}'
    try:
        req = Request(url, headers=HEADERS)
        with urlopen(req, timeout=20) as resp:
            data = resp.read()
        if len(data) < 5000:  # imagen demasiado pequeña, probablemente error
            return None
        dest.write_bytes(data)
        log(f'  ✓ Imagen descargada: {dest.name}')
        return f'/img/modelos/{nombre}.{ext}'
    except Exception as e:
        log(f'  ! Imagen no descargada: {e}')
        return None


# ── Datos por defecto para los modelos más comunes ────────────────────────────

SPECS_DEFECTO = {
    # SUVs populares
    'NISSAN QASHQAI':          {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'SUV familiar compacto con tecnología mild hybrid. Uno de los más vendidos de España con 43 modelos disponibles en renting.'},
    'VOLKSWAGEN T-ROC':        {'asientos': 5, 'anio_inicio': 2017, 'descripcion': 'SUV compacto de Volkswagen con diseño dinámico, deportivo y acabados de alta calidad.'},
    'VOLKSWAGEN TIGUAN':       {'asientos': 5, 'anio_inicio': 2024, 'descripcion': 'SUV familiar de referencia de VW, espacioso y con múltiples versiones electrificadas.'},
    'SEAT ARONA':              {'asientos': 5, 'anio_inicio': 2017, 'descripcion': 'SUV urbano de SEAT, versátil y económico, ideal para ciudad y carretera.'},
    'KIA SPORTAGE':            {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'SUV coreano de gran éxito con garantía de 7 años y versiones híbridas enchufables.'},
    'HYUNDAI TUCSON':          {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'SUV familiar con diseño paramétrico único y mecánicas completamente electrificadas.'},
    'AUDI Q3':                 {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'SUV premium de Audi con interior de alta calidad, tecnología avanzada y plataforma MQB.'},
    'AUDI Q3 SPORTBACK':       {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Versión cupé del Audi Q3, con línea más deportiva y el mismo espacio interior práctico.'},
    'BMW X1':                  {'asientos': 5, 'anio_inicio': 2022, 'descripcion': 'SUV premium compacto de BMW con versión totalmente eléctrica iX1 y plataforma modular.'},
    'BMW X2':                  {'asientos': 5, 'anio_inicio': 2023, 'descripcion': 'Crossover premium de BMW con línea deportiva y versión eléctrica iX2 de hasta 313 CV.'},
    'BMW X3':                  {'asientos': 5, 'anio_inicio': 2024, 'descripcion': 'SUV mediano de BMW de nueva generación con opción totalmente eléctrica iX3.'},
    'FORD KUGA':               {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'SUV familiar de Ford con opciones híbridas, enchufables y mild hybrid disponibles.'},
    'FORD PUMA':               {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Crossover compacto con mild hybrid EcoBoost y maletero MegaBox de 80 litros extra.'},
    'OPEL MOKKA':              {'asientos': 5, 'anio_inicio': 2020, 'descripcion': 'Crossover compacto rediseñado con interiores Vizor futuristas y versión 100% eléctrica Mokka-e.'},
    'OPEL GRANDLAND X':        {'asientos': 5, 'anio_inicio': 2017, 'descripcion': 'SUV familiar de Opel con versión enchufable y tecnología avanzada de asistencia a la conducción.'},
    'PEUGEOT 3008':            {'asientos': 5, 'anio_inicio': 2024, 'descripcion': 'SUV de referencia renovado en 2024 con pantalla panorámica y versión 100% eléctrica.'},
    'PEUGEOT 5008':            {'asientos': 7, 'anio_inicio': 2024, 'descripcion': 'SUV grande de 7 plazas de Peugeot, renovado en 2024 con versión eléctrica de largo alcance.'},
    'RENAULT ARKANA':          {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'SUV cupé de Renault con mecánica full hybrid sin enchufar y diseño cupé diferenciador.'},
    'RENAULT CAPTUR':          {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Crossover compacto de Renault, líder en su segmento con versión E-Tech enchufable.'},
    'TOYOTA C-HR':             {'asientos': 5, 'anio_inicio': 2023, 'descripcion': 'Crossover híbrido con diseño vanguardista y exclusividad de mecánica full hybrid.'},
    'TOYOTA RAV4':             {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'SUV híbrido familiar de Toyota. Referente en fiabilidad con consumo real de 6 L/100km.'},
    'SKODA KAROQ':             {'asientos': 5, 'anio_inicio': 2017, 'descripcion': 'SUV compacto de Škoda con gran habitabilidad, practicidad y tecnología VW a buen precio.'},
    'SKODA KODIAQ':            {'asientos': 7, 'anio_inicio': 2023, 'descripcion': 'SUV grande de Škoda con 7 plazas opcionales y renovado diseño exterior en su segunda generación.'},
    'NISSAN JUKE':             {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Crossover urbano de Nissan con diseño extrovertido y mecánica mild hybrid.'},
    'MERCEDES-BENZ GLA':       {'asientos': 5, 'anio_inicio': 2020, 'descripcion': 'SUV compacto premium de Mercedes con AMG Line disponible y sistema MBUX de última generación.'},
    'MERCEDES-BENZ GLB':       {'asientos': 7, 'anio_inicio': 2019, 'descripcion': 'SUV compacto de Mercedes con 7 plazas opcionales en un formato compacto y práctico.'},
    'CUPRA FORMENTOR':         {'asientos': 5, 'anio_inicio': 2020, 'descripcion': 'SUV deportivo de CUPRA, el primero exclusivo de la marca. Hasta 310 CV y versión enchufable.'},
    'CUPRA TERRAMAR':          {'asientos': 5, 'anio_inicio': 2024, 'descripcion': 'Nuevo SUV de CUPRA sobre plataforma MQB-evo con mecánicas híbridas enchufables.'},
    'MINI COUNTRYMAN':         {'asientos': 5, 'anio_inicio': 2023, 'descripcion': 'El SUV de MINI en su tercera generación, con versión eléctrica de hasta 313 km de autonomía.'},
    'LAND ROVER DEFENDER':     {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'SUV icónico reinventado con capacidades todoterreno extremas y opción PHEV.'},
    'JEEP COMPASS':            {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'SUV de Jeep con capacidades 4x4 y versión enchufable 4xe con 50 km de autonomía eléctrica.'},
    # Compactos
    'VOLKSWAGEN GOLF':         {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'El referente del segmento compacto durante décadas. Calidad, tecnología y eficiencia insuperables.'},
    'VOLKSWAGEN POLO':         {'asientos': 5, 'anio_inicio': 2017, 'descripcion': 'Referente del segmento B con calidad alemana en formato compacto y motores TDI y TSI.'},
    'SEAT LEON':               {'asientos': 5, 'anio_inicio': 2020, 'descripcion': 'Compacto de referencia fabricado en España. Mecánicas mild hybrid y enchufables disponibles.'},
    'SEAT IBIZA':              {'asientos': 5, 'anio_inicio': 2017, 'descripcion': 'Urbano clásico de SEAT con plataforma MQB-A0. Eficiencia y equipamiento por encima de su precio.'},
    'SKODA FABIA':             {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'Urbano premium de Škoda con el maletero más grande de su segmento (380 litros).'},
    'SKODA SCALA':             {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Compacto de Škoda con diseño elegante y maletero de 467 litros. La berlina más espaciosa del segmento.'},
    'SKODA OCTAVIA':           {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'El familiar más espacioso del segmento C con maletero de 600 litros. Excelente relación calidad-precio.'},
    'FORD FOCUS':              {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'Berlina compacta con excelente comportamiento dinámico, amplio equipamiento y motores EcoBoost.'},
    'RENAULT CLIO':            {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'El coche más vendido de España. Disponible con mecánica full hybrid sin enchufar.'},
    'PEUGEOT 208':             {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Urbano de referencia con el revolucionario i-Cockpit y versión 100% eléctrica e-208.'},
    'OPEL CORSA':              {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Urbano renovado de Opel sobre plataforma CMP con versión totalmente eléctrica Corsa-e.'},
    'DACIA SANDERO':           {'asientos': 5, 'anio_inicio': 2020, 'descripcion': 'El coche nuevo más barato de España. Mecánica LPG y bi-fuel disponible en versión Bi-Fuel.'},
    'FIAT 500':                {'asientos': 4, 'anio_inicio': 2020, 'descripcion': 'Icónico urbano italiano renovado en 2020. Disponible en versión 100% eléctrica con hasta 321 km.'},
    'HYUNDAI I20':             {'asientos': 5, 'anio_inicio': 2020, 'descripcion': 'Urbano coreano con tecnología mild hybrid 48V de serie en las versiones superiores.'},
    'HYUNDAI BAYON':           {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'Crossover urbano de Hyundai que combina practicidad de SUV con precio de segmento B.'},
    'KIA STONIC':              {'asientos': 5, 'anio_inicio': 2017, 'descripcion': 'Crossover urbano de Kia con garantía de 7 años y tecnología de asistencia avanzada.'},
    'KIA CEED':                {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'Compacto coreano con diseño europeo, garantía de 7 años y múltiples carrocerías disponibles.'},
    'OPEL ASTRA':              {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'Compacto renovado de Opel con versión plug-in hybrid Astra-e y diseño elegante.'},
    'TOYOTA COROLLA':          {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'El coche más vendido de la historia en versión híbrida autorrecargable con bajo consumo.'},
    # Berlinas
    'AUDI A3':                 {'asientos': 5, 'anio_inicio': 2020, 'descripcion': 'Compacto premium de Audi con interior sofisticado, pantallas MMI y versión enchufable 45 TFSI-e.'},
    'AUDI A4':                 {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Berlina media premium de Audi con mayor habitabilidad y tecnología de asistencia avanzada.'},
    'BMW SERIE 1':             {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Compacto premium de BMW con tracción delantera y motor de hasta 306 CV en versión M135i.'},
    'BMW SERIE 3':             {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'La berlina de referencia del segmento D premium. Disponible en versión plug-in hybrid 330e.'},
    'BMW SERIE 5':             {'asientos': 5, 'anio_inicio': 2023, 'descripcion': 'Berlina ejecutiva de BMW renovada en 2023 con versión totalmente eléctrica i5.'},
    'MERCEDES-BENZ CLASE A':   {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'Compacto premium de Mercedes con pantalla MBUX dual de 10,25" y diseño coupé.'},
    'FORD MONDEO':             {'asientos': 5, 'anio_inicio': 2022, 'descripcion': 'Familiar de Ford disponible solo como hybrid en su nueva generación familiar.'},
    'RENAULT MEGANE':          {'asientos': 5, 'anio_inicio': 2020, 'descripcion': 'Compacto clásico de Renault con versión E-Tech híbrida y enchufable disponibles.'},
    'PEUGEOT 308':             {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'Compacto de referencia renovado con el revolucionario i-Cockpit digital y versión eléctrica e-308.'},
    'PEUGEOT 508':             {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'Berlina fastback de Peugeot con diseño premium y versión enchufable 508 Hybrid de 225 CV.'},
    # Eléctricos
    'TESLA 3':                 {'asientos': 5, 'anio_inicio': 2017, 'consumo_kwh100': 14.9, 'co2_gkm': 0, 'descripcion': 'El sedán eléctrico más vendido del mundo. Hasta 678 km de autonomía en versión Long Range.'},
    'HYUNDAI IONIQ 5':         {'asientos': 5, 'anio_inicio': 2021, 'consumo_kwh100': 17.7, 'co2_gkm': 0, 'descripcion': 'SUV eléctrico de Hyundai con carga ultrarrápida de 800V y hasta 507 km de autonomía WLTP.'},
    'KIA EV6':                 {'asientos': 5, 'anio_inicio': 2021, 'consumo_kwh100': 18.0, 'co2_gkm': 0, 'descripcion': 'Crossover eléctrico de Kia ganador del Car of the Year 2022, con hasta 528 km de autonomía.'},
    'KIA EV3':                 {'asientos': 5, 'anio_inicio': 2024, 'consumo_kwh100': 14.3, 'co2_gkm': 0, 'descripcion': 'SUV eléctrico compacto de Kia con hasta 605 km de autonomía y precio competitivo.'},
    'FORD MUSTANG MACH-E':     {'asientos': 5, 'anio_inicio': 2020, 'consumo_kwh100': 19.5, 'co2_gkm': 0, 'descripcion': 'SUV eléctrico inspirado en el Mustang con hasta 610 km de autonomía y 487 CV en GT.'},
    'VOLKSWAGEN ID.4':         {'asientos': 5, 'anio_inicio': 2020, 'consumo_kwh100': 18.5, 'co2_gkm': 0, 'descripcion': 'SUV eléctrico de VW sobre plataforma MEB con hasta 543 km de autonomía WLTP.'},
    'RENAULT ZOE':             {'asientos': 5, 'anio_inicio': 2019, 'consumo_kwh100': 17.2, 'co2_gkm': 0, 'descripcion': 'Pionero del coche eléctrico en España. Urbano eléctrico con 395 km de autonomía WLTP.'},
    'POLESTAR 4':              {'asientos': 5, 'anio_inicio': 2023, 'consumo_kwh100': 19.2, 'co2_gkm': 0, 'descripcion': 'SUV cupé eléctrico de Polestar sin luneta trasera, con hasta 591 km de autonomía y 544 CV.'},
    'BMW I4':                  {'asientos': 5, 'anio_inicio': 2021, 'consumo_kwh100': 18.1, 'co2_gkm': 0, 'descripcion': 'Gran berlina eléctrica de BMW con hasta 590 km WLTP y la dinámica característica de la marca.'},
    'BMW IX1':                 {'asientos': 5, 'anio_inicio': 2022, 'consumo_kwh100': 18.5, 'co2_gkm': 0, 'descripcion': 'SUV eléctrico compacto de BMW con 438 km de autonomía WLTP y carga rápida de 130 kW.'},
    'BMW IX3':                 {'asientos': 5, 'anio_inicio': 2020, 'consumo_kwh100': 18.0, 'co2_gkm': 0, 'descripcion': 'SUV eléctrico de BMW basado en el X3 con 461 km de autonomía WLTP.'},
    'BYD ATTO 2':              {'asientos': 5, 'anio_inicio': 2024, 'consumo_kwh100': 13.7, 'co2_gkm': 0, 'descripcion': 'SUV eléctrico compacto de BYD con batería Blade y hasta 312 km de autonomía WLTP.'},
    'BYD SEAL U':              {'asientos': 5, 'anio_inicio': 2023, 'consumo_kwh100': 17.2, 'co2_gkm': 0, 'descripcion': 'SUV eléctrico de tamaño mediano de BYD con hasta 420 km de autonomía y batería Blade.'},
    'HYUNDAI IONIQ':           {'asientos': 5, 'anio_inicio': 2023, 'consumo_kwh100': 16.0, 'co2_gkm': 0, 'descripcion': 'Berlina eléctrica de Hyundai con batería de 77 kWh y hasta 614 km de autonomía WLTP.'},
    'CITROEN E-C3':            {'asientos': 5, 'anio_inicio': 2024, 'consumo_kwh100': 13.5, 'co2_gkm': 0, 'descripcion': 'El eléctrico urbano más asequible de Europa desde 23.300€ con 320 km de autonomía WLTP.'},
    # Furgonetas y vehículos de empresa
    'RENAULT KANGOO':          {'asientos': 5, 'anio_inicio': 2021, 'descripcion': 'Furgoneta familiar o comercial con nueva generación más espaciosa y versión eléctrica E-Tech.'},
    'PEUGEOT PARTNER':         {'asientos': 2, 'anio_inicio': 2018, 'descripcion': 'Furgoneta compacta de reparto muy popular entre autónomos y pymes con opciones gasolina y eléctrica.'},
    'CITROEN BERLINGO':        {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'Furgoneta multiusos disponible como familiar y comercial. Plataforma EMP2 con todas las motorizaciones.'},
    'FORD TRANSIT CONNECT':    {'asientos': 2, 'anio_inicio': 2018, 'descripcion': 'Furgoneta de reparto media de Ford con gran modularidad y versiones de una o dos toneladas.'},
    'OPEL COMBO':              {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'Furgoneta compacta de Opel con versión eléctrica y familiar Combo Life de 7 plazas.'},
    'MERCEDES-BENZ SPRINTER':  {'asientos': 3, 'anio_inicio': 2018, 'descripcion': 'La furgoneta grande más vendida de Europa, disponible en gasolina, diesel, eléctrica y gas.'},
    'VOLKSWAGEN TRANSPORTER':  {'asientos': 3, 'anio_inicio': 2024, 'descripcion': 'Icónica furgoneta de VW en su 7ª generación. Solo disponible en versión eléctrica.'},
    'FIAT DUCATO':             {'asientos': 3, 'anio_inicio': 2021, 'descripcion': 'Líder en furgonetas grandes en Europa. Disponible con propulsión eléctrica e-Ducato.'},
    'PEUGEOT BOXER':           {'asientos': 3, 'anio_inicio': 2021, 'descripcion': 'Furgoneta grande de Peugeot con amplia gama de carrocerías y versiones eléctricas.'},
    'RENAULT MASTER':          {'asientos': 3, 'anio_inicio': 2024, 'descripcion': 'Furgoneta grande de Renault renovada en 2024. Versión eléctrica E-Tech con 200 km de autonomía.'},
    'RENAULT TRAFIC':          {'asientos': 3, 'anio_inicio': 2021, 'descripcion': 'Furgoneta media de Renault con múltiples versiones de carga y pasajeros.'},
    # Lujo y premium
    'AUDI Q5':                 {'asientos': 5, 'anio_inicio': 2020, 'descripcion': 'SUV mediano premium de Audi con interiores de alta calidad y versión enchufable 55 TFSI-e.'},
    'AUDI Q8':                 {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'SUV flagship de Audi con diseño cupé, pantallas táctiles y mecánicas MHEV de serie.'},
    'BMW X4':                  {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'SUV cupé de BMW que combina la practicidad del X3 con un diseño fastback dinámico.'},
    'BMW X5':                  {'asientos': 7, 'anio_inicio': 2018, 'descripcion': 'SUV grande de BMW con 7 plazas opcionales y versión enchufable xDrive45e PHEV.'},
    'LAND ROVER RANGE ROVER EVOQUE': {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'SUV premium de Land Rover con diseño elegante y versión mild hybrid P200 de 200 CV.'},
    'VOLVO XC40':              {'asientos': 5, 'anio_inicio': 2017, 'consumo_kwh100': 20.4, 'co2_gkm': 0, 'descripcion': 'SUV premium compacto de Volvo disponible en versión eléctrica de hasta 423 km de autonomía.'},
    'VOLVO XC60':              {'asientos': 5, 'anio_inicio': 2017, 'descripcion': 'SUV mediano premium de Volvo con versión enchufable T8 Recharge de 455 CV y mecánicas mild hybrid.'},
    'LEXUS UX':                {'asientos': 5, 'anio_inicio': 2018, 'descripcion': 'SUV compacto premium de Lexus con mecánica full hybrid de serie y acabados de altísima calidad.'},
    'MAZDA CX-5':              {'asientos': 5, 'anio_inicio': 2022, 'descripcion': 'SUV mediano de Mazda con diseño kodo premiado y motor SkyActiv de alta compresión.'},
    'MAZDA CX-60':             {'asientos': 5, 'anio_inicio': 2022, 'descripcion': 'SUV grande de Mazda con motor 6 cilindros en línea y versión enchufable PHEV de 327 CV.'},
    'MAZDA CX-30':             {'asientos': 5, 'anio_inicio': 2019, 'descripcion': 'Crossover compacto de Mazda entre el CX-3 y el CX-5, con mecánica e-SkyActiv mild hybrid.'},
}

CONSUMOS_DEFECTO = {
    'Gasolina':              {'consumo_l100': 6.5,  'co2_gkm': 148},
    'Diesel':                {'consumo_l100': 5.1,  'co2_gkm': 133},
    'Hibrido':               {'consumo_l100': 4.8,  'co2_gkm': 109},
    'Hibrido enchufable':    {'consumo_l100': 1.8,  'co2_gkm': 42},
    'Electrico':             {'consumo_kwh100': 16, 'co2_gkm': 0},
    'Micro hibrido':         {'consumo_l100': 5.8,  'co2_gkm': 133},
}


# ── Lógica principal ──────────────────────────────────────────────────────────

def cargar_specs() -> dict:
    try:
        with open(SPECS_FILE, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_specs(specs: dict):
    with open(SPECS_FILE, 'w', encoding='utf-8') as f:
        json.dump(specs, f, ensure_ascii=False, indent=2)


def enriquecer_modelo(make: str, model: str, ofertas: list, specs_actuales: dict) -> dict:
    key = f'{make}||{model}'
    existing = specs_actuales.get(key, {})

    # Si ya tiene descripción y specs básicas, no re-fetchar Wikipedia/Wikidata
    ya_enriquecido = existing.get('descripcion') and (existing.get('asientos') or existing.get('consumo_l100'))

    log(f'  {make} {model} {"(ya enriquecido, solo imagen)" if ya_enriquecido else "(buscando datos)"}')

    resultado = dict(existing)

    # ── Imagen ──────────────────────────────────────────────────────────────
    if not resultado.get('imagen_local'):
        local = imagen_local(make, model)
        if local:
            resultado['imagen_local'] = local
        else:
            # Intentar descargar desde URL Arval
            arval_urls = [o.get('image', '') for o in ofertas if 'arval' in (o.get('image') or '').lower() and o.get('image')]
            if arval_urls:
                dl = descargar_imagen(make, model, arval_urls[0])
                if dl:
                    resultado['imagen_local'] = dl

    # ── Fuentes y precio mínimo ──────────────────────────────────────────────
    resultado['precio_desde'] = min(o.get('precio_desde', 9999) for o in ofertas)
    resultado['num_ofertas']  = len(ofertas)
    resultado['fuentes']      = list({o.get('fuente', '') for o in ofertas if o.get('fuente')})
    resultado['fuels']        = list({o.get('fuel', '') for o in ofertas if o.get('fuel')})
    resultado['category']     = ofertas[0].get('category', '') if ofertas else ''

    if ya_enriquecido:
        return resultado

    # ── Datos por defecto hardcodeados ──────────────────────────────────────
    clave_defecto = f'{make} {model}'
    if clave_defecto in SPECS_DEFECTO:
        for k, v in SPECS_DEFECTO[clave_defecto].items():
            if not resultado.get(k):
                resultado[k] = v

    # Consumo por defecto según combustible principal
    fuel_principal = ofertas[0].get('fuel', '') if ofertas else ''
    for fuel_key, consumo_vals in CONSUMOS_DEFECTO.items():
        if fuel_key.lower() in fuel_principal.lower():
            for k, v in consumo_vals.items():
                if not resultado.get(k):
                    resultado[k] = v
            break

    # ── Wikipedia ES ──────────────────────────────────────────────────────
    wiki = wiki_buscar(make, model)
    if wiki.get('descripcion') and not resultado.get('descripcion'):
        resultado['descripcion'] = wiki['descripcion']
    if wiki.get('imagen_wiki') and not resultado.get('imagen_local'):
        dl = descargar_imagen(make, model, wiki['imagen_wiki'])
        resultado['imagen_local'] = dl or wiki['imagen_wiki']

    # ── Wikidata ──────────────────────────────────────────────────────────
    wd = wikidata_buscar(make, model)
    for campo in ['consumo_l100','co2_gkm','asientos','anio_inicio','anio_fin',
                  'ancho_mm','alto_mm','peso_kg','cilindrada_cc']:
        if wd.get(campo) and not resultado.get(campo):
            resultado[campo] = wd[campo]
    if wd.get('imagen_wikidata') and not resultado.get('imagen_local'):
        dl = descargar_imagen(make, model, wd['imagen_wikidata'])
        resultado['imagen_local'] = dl or wd['imagen_wikidata']

    return resultado


def main():
    log('=== Agente de enriquecimiento iniciado ===')
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    with open(OFERTAS_FILE, encoding='utf-8') as f:
        raw = json.load(f)

    # Agrupar por make+model
    modelos: dict[str, list] = {}
    for o in raw:
        make  = (o.get('make') or '').strip().upper()
        model = (o.get('model') or '').strip().upper()
        if make and model:
            modelos.setdefault(f'{make}||{model}', []).append(o)

    specs = cargar_specs()
    log(f'Modelos a enriquecer: {len(modelos)} | Ya en cache: {len(specs)}')

    nuevos = 0
    for i, (key, ofertas) in enumerate(modelos.items(), 1):
        make, model = key.split('||')
        log(f'[{i}/{len(modelos)}] {make} {model}')
        try:
            resultado = enriquecer_modelo(make, model, ofertas, specs)
            specs[key] = resultado
            nuevos += 1
        except Exception as e:
            log(f'  ERROR: {e}')
            continue

        # Guardar cada 10 modelos (por si se interrumpe)
        if nuevos % 10 == 0:
            guardar_specs(specs)
            log(f'  Checkpoint: {nuevos} modelos procesados')

    guardar_specs(specs)
    log(f'=== Completado: {len(specs)} modelos en coches-specs.json ===')

    # Resumen
    con_desc  = sum(1 for v in specs.values() if v.get('descripcion'))
    con_img   = sum(1 for v in specs.values() if v.get('imagen_local'))
    con_specs = sum(1 for v in specs.values() if v.get('consumo_l100') or v.get('consumo_kwh100'))
    log(f'  Con descripción: {con_desc}/{len(specs)}')
    log(f'  Con imagen local: {con_img}/{len(specs)}')
    log(f'  Con specs técnicas: {con_specs}/{len(specs)}')


if __name__ == '__main__':
    main()
