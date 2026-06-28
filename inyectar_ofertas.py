#!/usr/bin/env python3
"""
Lee ofertas-db.json e inyecta los datos en const _OFERTAS del index.html.
"""
import json, re, unicodedata
from pathlib import Path

BASE = Path(__file__).parent
JSON_PATH = BASE / "ofertas-db.json"
HTML_PATH = BASE / "index.html"
IMG_DIR = BASE / "img" / "modelos"


def limpiar(s: str) -> str:
    s = re.sub(r'[\x00-\x1f\x7f]', ' ', s)
    return re.sub(r' +', ' ', s).strip()


def _slugify(text: str) -> str:
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')


def _build_local_images() -> dict:
    mapping = {}
    if IMG_DIR.exists():
        for p in IMG_DIR.glob('*.png'):
            mapping[p.stem] = f'/img/modelos/{p.name}'
    return mapping


_LOCAL_IMAGES = _build_local_images()


def _local_image(make: str, model: str) -> str:
    slug = _slugify(f'{make} {model}')
    if slug in _LOCAL_IMAGES:
        return _LOCAL_IMAGES[slug]
    # try make-only prefix match for compound model names
    make_slug = _slugify(make)
    for key, path in _LOCAL_IMAGES.items():
        if key.startswith(make_slug + '-') and _slugify(model).startswith(key[len(make_slug)+1:]):
            return path
    return ''


def aplanar(o: dict) -> dict:
    precios = o.get('precios') or []
    duracion = int(precios[0][0]) if precios else int(o.get('duracion', 48) or 48)
    km = int(precios[0][1]) if precios else int(o.get('km', 10000) or 10000)
    make = limpiar(o.get('make', ''))
    model = limpiar(o.get('model', ''))
    local_img = _local_image(make, model)
    image = local_img or limpiar(o.get('image', ''))
    return {
        'fuente':       limpiar(o.get('fuente', '')),
        'tipo':         limpiar(o.get('tipo', 'empresa')),
        'make':         make,
        'model':        model,
        'version':      limpiar(o.get('version', '')),
        'fuel':         limpiar(o.get('fuel', '')),
        'precio_desde': o.get('precio_desde', 0),
        'duracion':     duracion,
        'km':           km,
        'url':          limpiar(o.get('link_oferta', o.get('url', ''))),
        'category':     limpiar(o.get('category', '')),
        'image':        image,
    }


from datetime import datetime
_MESES = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
FECHA_HOY = f"{datetime.now().day} {_MESES[datetime.now().month-1]} {datetime.now().year}"

with open(JSON_PATH, encoding='utf-8') as f:
    raw = json.load(f)

ofertas = [aplanar(o) for o in raw if o.get('make') and o.get('precio_desde', 0) > 0]
print(f"Ofertas: {len(ofertas)}")

json_str = json.dumps(ofertas, ensure_ascii=False, separators=(',', ':'))

# Verificar que el JSON es válido antes de inyectar
json.loads(json_str)

html = HTML_PATH.read_text(encoding='utf-8')
patron = r'(const _OFERTAS\s*=\s*)\[.*?\];'
html_nuevo, n = re.subn(patron, rf'\g<1>{json_str};', html, count=1, flags=re.DOTALL)

if n == 0:
    print("ERROR: No se encontro _OFERTAS en index.html")
else:
    # Inject date into hero eyebrow
    # Replace "Actualizado hoy" with actual date (handles HTML entities)
    html_nuevo = re.sub(
        r'Actualizado hoy\s*(?:&middot;|·)',
        f'Actualizado {FECHA_HOY} &middot;',
        html_nuevo
    )
    # Inject gestoras count
    gestoras_n = len(set(o.get('fuente','') for o in raw if o.get('fuente')))
    html_nuevo = re.sub(
        r'<div class="sbar-val">6</div>',
        f'<div class="sbar-val">{gestoras_n}</div>',
        html_nuevo
    )
    HTML_PATH.write_text(html_nuevo, encoding='utf-8')
    print(f"OK: index.html actualizado con {len(ofertas)} ofertas, fecha={FECHA_HOY}")
