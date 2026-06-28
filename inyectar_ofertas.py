#!/usr/bin/env python3
"""
Lee ofertas-db.json e inyecta los datos en const _OFERTAS del index.html.
"""
import json, re
from pathlib import Path

BASE = Path(__file__).parent
JSON_PATH = BASE / "ofertas-db.json"
HTML_PATH = BASE / "index.html"


def limpiar(s: str) -> str:
    s = re.sub(r'[\x00-\x1f\x7f]', ' ', s)
    return re.sub(r' +', ' ', s).strip()


def aplanar(o: dict) -> dict:
    precios = o.get('precios') or []
    duracion = int(precios[0][0]) if precios else int(o.get('duracion', 48) or 48)
    km = int(precios[0][1]) if precios else int(o.get('km', 10000) or 10000)
    return {
        'fuente':       limpiar(o.get('fuente', '')),
        'tipo':         limpiar(o.get('tipo', 'empresa')),
        'make':         limpiar(o.get('make', '')),
        'model':        limpiar(o.get('model', '')),
        'version':      limpiar(o.get('version', '')),
        'fuel':         limpiar(o.get('fuel', '')),
        'precio_desde': o.get('precio_desde', 0),
        'duracion':     duracion,
        'km':           km,
        'url':          limpiar(o.get('link_oferta', o.get('url', ''))),
        'category':     limpiar(o.get('category', '')),
        'image':        limpiar(o.get('image', '')),
    }


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
    HTML_PATH.write_text(html_nuevo, encoding='utf-8')
    print(f"OK: index.html actualizado con {len(ofertas)} ofertas")
