#!/usr/bin/env python3
"""
actualizar_ofertas_seguro.py — Inyecta ofertas en index.html SIN romper la web.

Flujo:
  1. Lee las ofertas recién scrapeadas (ofertas-db.json, salida de scrape_myrenting.py).
  2. Preserva las gestoras que NO se scrapean (ofertas-manuales.json: KIA Armotors,
     M-Automocion, etc.) para que nunca desaparezcan.
  3. Fallback por gestora: si una gestora scrapeada devuelve muy pocas ofertas
     (scrape roto), mantiene las anteriores de esa gestora en vez de perderlas.
  4. Validacion global: si el total cae por debajo del umbral -> ABORTA sin tocar nada.
  5. Backup de index.html; si tras inyectar falta algun marcador clave -> ROLLBACK.

Uso:  python3 actualizar_ofertas_seguro.py
Salida != 0  => no se toco la web (el workflow no debe commitear).
"""
import json, re, sys, shutil
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
HTML = BASE / 'index.html'
SCRAPED_FILE = BASE / 'ofertas-db.json'
MANUAL_FILE = BASE / 'ofertas-manuales.json'
BACKUP = BASE / 'index.html.bak'

# Gestoras que cubre scrape_myrenting.py
SCRAPED_SOURCES = set()  # Arval/Ayvens/Alphabet desactivados: solo M Automoción

# Guardarrailes
MIN_TOTAL_ABS = 500          # el sitio nunca puede quedar con menos de esto
MIN_FRACTION_VS_PREV = 0.6   # ni por debajo del 60% de lo que habia
GESTORA_MIN_ABS = 10         # minimo por gestora para considerar el scrape "vivo"
GESTORA_MIN_FRACTION = 0.5   # o al menos el 50% de lo que tenia

MARKERS = ['const _OFERTAS', 'function buildAC', 'id="ac-drop"', 'id="search-libre"']
_MESES = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']


def die(msg):
    print(f'ABORTADO (web intacta): {msg}')
    sys.exit(1)


def load_json(p):
    try:
        return json.load(open(p, encoding='utf-8'))
    except Exception as e:
        return None if not p.exists() else die(f'{p.name} ilegible: {e}')


def by_source(offers):
    d = {}
    for o in offers:
        d.setdefault(o.get('fuente', ''), []).append(o)
    return d


def valid_offer(o):
    try:
        p = float(o.get('precio_desde', 0))
    except Exception:
        return False
    return bool(o.get('make')) and 30 <= p <= 4000


def main():
    if not HTML.exists():
        die('no existe index.html')
    html = HTML.read_text(encoding='utf-8')

    # --- estado previo (baseline) desde el propio index.html ---
    m = re.search(r'const _OFERTAS\s*=\s*(\[.*?\]);', html, re.DOTALL)
    if not m:
        die('no se encontro const _OFERTAS en index.html')
    try:
        prev = json.loads(m.group(1))
    except Exception as e:
        die(f'_OFERTAS actual no parsea: {e}')
    prev_by = by_source(prev)
    prev_total = len(prev)
    print(f'Previo: {prev_total} ofertas · {[(k,len(v)) for k,v in prev_by.items()]}')

    # --- datos nuevos ---
    scraped = load_json(SCRAPED_FILE) or []
    scraped = [o for o in scraped if valid_offer(o)]
    manual = load_json(MANUAL_FILE) or []
    manual = [o for o in manual if valid_offer(o)]
    scraped_by = by_source(scraped)

    # --- fallback por gestora scrapeada ---
    final = []
    for src in SCRAPED_SOURCES:
        nuevas = scraped_by.get(src, [])
        prev_n = len(prev_by.get(src, []))
        floor = max(GESTORA_MIN_ABS, int(prev_n * GESTORA_MIN_FRACTION))
        if len(nuevas) >= floor or prev_n == 0:
            final += nuevas
            print(f'  {src}: {len(nuevas)} (nuevas)')
        else:
            final += prev_by.get(src, [])
            print(f'  {src}: scrape flojo ({len(nuevas)}<{floor}) -> mantengo {prev_n} anteriores')

    # --- gestoras manuales/no scrapeadas: preservar SIEMPRE ---
    manual_by = by_source(manual)
    for src, offers in manual_by.items():
        final += offers
        print(f'  {src}: {len(offers)} (manual, preservada)')
    # cualquier gestora previa que no este ni en scrape ni en manual -> preservar
    for src, offers in prev_by.items():
        if src not in SCRAPED_SOURCES and src not in manual_by:
            final += offers
            print(f'  {src}: {len(offers)} (previa sin fuente, preservada)')

    # --- validacion global ---
    total = len(final)
    umbral = max(MIN_TOTAL_ABS, int(prev_total * MIN_FRACTION_VS_PREV))
    if total < umbral:
        die(f'total {total} < umbral {umbral}. El scrape parece roto.')

    final.sort(key=lambda o: float(o.get('precio_desde', 9999)))
    gestoras_n = len({o.get('fuente', '') for o in final if o.get('fuente')})
    fecha = f"{datetime.now().day} {_MESES[datetime.now().month-1]} {datetime.now().year}"
    json_str = json.dumps(final, ensure_ascii=False, separators=(',', ':'))
    json.loads(json_str)  # sanity

    # --- backup + inyeccion ---
    shutil.copy2(HTML, BACKUP)
    nuevo = re.sub(r'(const _OFERTAS\s*=\s*)\[.*?\];', lambda mm: mm.group(1)+json_str+';',
                   html, count=1, flags=re.DOTALL)
    nuevo = re.sub(r'Actualizado hoy\s*(?:&middot;|·)', f'Actualizado {fecha} &middot;', nuevo)
    nuevo = re.sub(r'(<div class="sbar-val">)\d+(</div>)', rf'\g<1>{gestoras_n}\g<2>', nuevo, count=1)

    # --- validacion de salida (post) ---
    faltan = [mk for mk in MARKERS if mk not in nuevo]
    if faltan:
        die(f'faltarian marcadores tras inyectar: {faltan} (no escribo)')
    m2 = re.search(r'const _OFERTAS\s*=\s*(\[.*?\]);', nuevo, re.DOTALL)
    if not m2 or len(json.loads(m2.group(1))) != total:
        die('el _OFERTAS resultante no parsea o no cuadra (no escribo)')
    if len(nuevo) < len(html) * 0.5:
        die('el index.html resultante es sospechosamente pequeno (no escribo)')

    HTML.write_text(nuevo, encoding='utf-8')
    print(f'OK: index.html actualizado -> {total} ofertas, {gestoras_n} gestoras, fecha {fecha}')
    print(f'    (backup en {BACKUP.name})')


if __name__ == '__main__':
    main()
