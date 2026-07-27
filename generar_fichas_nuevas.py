#!/usr/bin/env python3
"""
generar_fichas_nuevas.py — Crea fichas para modelos nuevos de M Automoción
clonando una ficha existente de la MISMA marca y sustituyendo:
  - nombre "Marca Modelo" (3 formas: display / MAYUS / slug)
  - precios/offerCount/category del <head> + JSON-LD (lo que NO toca
    actualizar_fichas.py; la tabla y el hero se regeneran después).

Tras ejecutarlo:  python3 actualizar_fichas.py   (rellena tabla + IVA + datos)

Idempotente: si la ficha destino ya existe, la salta.
"""
import json, re, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
IDX = BASE / 'index.html'

# datos reales desde index.html (_OFERTAS)
_idx = IDX.read_text(encoding='utf-8')
_ALL = json.loads(re.search(r'const _OFERTAS\s*=\s*(\[.*?\]);', _idx, re.DOTALL).group(1))


def model_stats(make, model):
    offs = [o for o in _ALL if o['make'] == make and o['model'] == model]
    if not offs:
        return None
    ps = [float(o['precio_desde']) for o in offs]
    img = next((o['image'] for o in offs), '')
    return dict(low=int(min(ps)), high=int(round(max(ps))), n=len(offs), img=img)


# nuevos modelos: (template_stem, new_make, new_model_upper, disp_old, disp_new, cat)
#   disp_old / disp_new = "Marca Modelo" tal como aparece en el <h1> (display)
NUEVOS = [
    ('mazda-cx-5',       'MAZDA', '2',          'Mazda Cx-5',        'Mazda 2',          'urbano'),
    ('mazda-cx-5',       'MAZDA', '3',          'Mazda Cx-5',        'Mazda 3',          'compacto'),
    ('mazda-cx-5',       'MAZDA', 'CX-30',      'Mazda Cx-5',        'Mazda Cx-30',      'suv'),
    ('mazda-cx-5',       'MAZDA', 'CX-60',      'Mazda Cx-5',        'Mazda Cx-60',      'suv'),
    ('volkswagen-t-roc', 'VOLKSWAGEN', 'POLO',  'Volkswagen T-Roc',  'Volkswagen Polo',  'urbano'),
    ('jaecoo-7',         'JAECOO', '8',         'Jaecoo 7',          'Jaecoo 8',         'suv'),
    ('opel-frontera',    'OPEL', 'COMBO-E',     'Opel Frontera',     'Opel Combo-e',     'furgoneta'),
    ('citroen-berlingo', 'CITROEN', 'E-BERLINGO', 'Citroën Berlingo', 'Citroën E-Berlingo', 'furgoneta'),
    # ficha antigua (formato pre-v4) reconstruida como comparador v4:
    ('toyota-yaris-cross', 'TOYOTA', 'YARIS',     'Toyota Yaris Cross', 'Toyota Yaris',    'urbano'),
    # KIA (furgonetas electricas de M Automoción) — clon inter-marca desde Citroën
    ('citroen-berlingo', 'KIA', 'PV5 CARGO',     'Citroën Berlingo', 'Kia Pv5 Cargo',     'furgoneta'),
    ('citroen-berlingo', 'KIA', 'PV5 PASSENGER', 'Citroën Berlingo', 'Kia Pv5 Passenger', 'furgoneta'),
]


def slugify(s):
    s = s.lower()
    for a, b in [('á','a'),('à','a'),('ä','a'),('é','e'),('è','e'),('ë','e'),
                 ('í','i'),('ó','o'),('ö','o'),('ú','u'),('ü','u'),('ñ','n')]:
        s = s.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')


def main():
    creadas = saltadas = 0
    for tmpl, make, model, disp_old, disp_new, cat in NUEVOS:
        st = model_stats(make, model)
        if not st:
            print(f'  SKIP {make} {model}: sin ofertas en index'); saltadas += 1; continue
        new_slug = slugify(f'{make} {model}')
        dest = BASE / f'renting-{new_slug}.html'
        if dest.exists():
            print(f'  ya existe {dest.name}'); saltadas += 1; continue
        src = BASE / f'renting-{tmpl}.html'
        if not src.exists():
            print(f'  SKIP {dest.name}: falta plantilla {src.name}'); saltadas += 1; continue
        c = src.read_text(encoding='utf-8')

        old_slug = tmpl
        old_up = disp_old.upper()
        new_up = disp_new.upper()

        # 1) valores del template (para sustituir por los reales del modelo nuevo)
        t_low = re.search(r'desde (\d+)€', c)
        t_low = t_low.group(1) if t_low else None
        t_high = re.search(r'"highPrice":\s*"(\d+)"', c)
        t_high = t_high.group(1) if t_high else None
        t_cnt = re.search(r'"offerCount":\s*"(\d+)"', c)
        t_cnt = t_cnt.group(1) if t_cnt else None
        t_lowld = re.search(r'"lowPrice":\s*"(\d+)"', c)
        t_lowld = t_lowld.group(1) if t_lowld else None
        t_cat = re.search(r'"category":\s*"([^"]+)"', c)
        t_cat = t_cat.group(1) if t_cat else None

        # 2) sustitucion de nombre (formas: display, MAYUS, slug)
        n0 = c.count(disp_old)
        c = c.replace(disp_old, disp_new)
        c = c.replace(old_up, new_up)
        c = c.replace(old_slug, new_slug)

        # 2b) clon inter-marca: limpia restos de la marca del template (marca
        #     suelta en breadcrumb/JSON-LD + enlace al hub renting-<marca>.html)
        old_brand = disp_old.split()[0]          # p.ej. "Citroën"
        new_brand = disp_new.split()[0]          # p.ej. "Kia"
        if slugify(old_brand) != slugify(new_brand):
            c = c.replace(old_brand, new_brand)
            c = c.replace(old_brand.upper(), new_brand.upper())
            c = c.replace(f'renting-{slugify(old_brand)}.html',
                          f'renting-{slugify(new_brand)}.html')

        # 2c) quita la seccion "por ciudades": enlaza a paginas de ciudad que
        #     NO existen para un modelo nuevo (serian 404)
        c = re.sub(r'<section class="ciudades-seo".*?</section>', '', c, flags=re.DOTALL)

        # 3) precios/contadores/categoria (solo head + JSON-LD; tabla se regenera)
        if t_lowld:
            c = re.sub(r'("lowPrice":\s*")\d+(")', rf'\g<1>{st["low"]}\g<2>', c)
        if t_high:
            c = re.sub(r'("highPrice":\s*")\d+(")', rf'\g<1>{st["high"]}\g<2>', c)
        if t_cnt:
            c = re.sub(r'("offerCount":\s*")\d+(")', rf'\g<1>{st["n"]}\g<2>', c)
        if t_cat:
            c = re.sub(r'("category":\s*")[^"]+(")', rf'\g<1>{cat}\g<2>', c, count=1)
        # precio visible "desde X€" y "N ofertas reales" (texto del head/FAQ)
        if t_low:
            c = c.replace(f'desde {t_low}€', f'desde {st["low"]}€')
            c = re.sub(rf'\b{t_low}€', f'{st["low"]}€', c)
        c = re.sub(r'\b\d+ ofertas reales', f'{st["n"]} ofertas reales', c)

        # 4) imagen del modelo (og:image + car-img-wrap)
        c = re.sub(r'(<meta property="og:image" content=")[^"]+(")',
                   rf'\g<1>{st["img"]}\g<2>', c, count=1)
        c = re.sub(r'(class="car-img-wrap"><img src=")[^"]+(")',
                   rf'\g<1>{st["img"]}\g<2>', c, count=1)

        dest.write_text(c, encoding='utf-8')
        print(f'  CREADA {dest.name}  (desde {st["low"]}€, {st["n"]} ofertas, cat {cat}, {n0} refs nombre)')
        creadas += 1
    print(f'Fichas nuevas: {creadas} creadas, {saltadas} saltadas')


if __name__ == '__main__':
    main()
