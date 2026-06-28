#!/usr/bin/env python3
"""
Agente de scraping de precios de renting — sin coste, sin APIs de pago.
Coordina múltiples scrapers y actualiza ofertas-db.json.
"""
import os, json, re, time, subprocess, sys
from datetime import datetime

OFERTAS_FILE = os.path.join(os.path.dirname(__file__), 'ofertas-db.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'agente_scraping.log')


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with open(LOG_FILE, 'a') as f:
        f.write(line + '\n')


def cargar_ofertas() -> list:
    try:
        with open(OFERTAS_FILE) as f:
            return json.load(f)
    except Exception:
        return []


def guardar_ofertas(ofertas: list):
    with open(OFERTAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(ofertas, f, ensure_ascii=False, separators=(',', ':'))
    log(f'Guardadas {len(ofertas)} ofertas en {OFERTAS_FILE}')


def scrape_arval() -> list:
    """Extrae ofertas de Arval via su API pública."""
    try:
        import urllib.request
        url = 'https://www.arval.es/api/v1/offers?locale=es_ES&page=1&per_page=200&offer_type=long_term'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; Myrenting/1.0)',
            'Accept': 'application/json',
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
        offers = data.get('offers', data) if isinstance(data, dict) else data
        result = []
        for o in offers:
            try:
                result.append({
                    'fuente': 'Arval',
                    'tipo': o.get('type', 'empresa'),
                    'make': o.get('brand', {}).get('name', '').upper(),
                    'model': o.get('model', {}).get('name', '').upper(),
                    'version': o.get('version', {}).get('name', ''),
                    'fuel': o.get('fuel_type', ''),
                    'precio_desde': float(o.get('price', {}).get('net', 0)),
                    'duracion': int(o.get('duration', 48)),
                    'km': int(o.get('mileage', 10000)),
                    'url': o.get('url', 'https://www.arval.es'),
                    'category': o.get('category', ''),
                    'image': o.get('image', {}).get('url', '') if isinstance(o.get('image'), dict) else o.get('image', ''),
                })
            except Exception:
                continue
        log(f'Arval: {len(result)} ofertas')
        return result
    except Exception as e:
        log(f'Arval error: {e}')
        return []


def scrape_ayvens() -> list:
    """Extrae ofertas de Ayvens buscando JSON embebido en la página."""
    try:
        import urllib.request
        url = 'https://www.ayvens.com/es-es/ofertas/'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; Myrenting/1.0)',
            'Accept': 'text/html,application/json',
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode('utf-8', errors='ignore')

        result = []

        # Intentar extraer precios del HTML con expresiones regulares
        price_pattern = re.findall(
            r'"brand"\s*:\s*"([^"]+)".*?"model"\s*:\s*"([^"]+)".*?"price"\s*:\s*([\d.]+)',
            raw, re.DOTALL
        )
        for brand, model, price in price_pattern[:100]:
            try:
                result.append({
                    'fuente': 'Ayvens',
                    'tipo': 'empresa',
                    'make': brand.upper(),
                    'model': model.upper(),
                    'version': '',
                    'fuel': '',
                    'precio_desde': float(price),
                    'duracion': 48,
                    'km': 10000,
                    'url': 'https://www.ayvens.com/es-es/ofertas/',
                    'category': '',
                    'image': '',
                })
            except Exception:
                continue

        log(f'Ayvens: {len(result)} ofertas')
        return result
    except Exception as e:
        log(f'Ayvens error: {e}')
        return []


def ejecutar_scraper_existente(nombre: str) -> list:
    """Ejecuta uno de los scrapers Python existentes si está disponible."""
    script_map = {
        'arval': 'scraper_arval_definitivo.py',
        'ayvens': 'scraper_ayvens_completo.py',
    }
    script = script_map.get(nombre)
    if not script:
        return []
    script_path = os.path.join(os.path.dirname(__file__), script)
    if not os.path.exists(script_path):
        return []
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=120,
            cwd=os.path.dirname(__file__)
        )
        if result.returncode == 0:
            for fname in ['ofertas_temp.json', f'{nombre}_data.json']:
                fpath = os.path.join(os.path.dirname(__file__), fname)
                if os.path.exists(fpath):
                    with open(fpath) as f:
                        data = json.load(f)
                    log(f'{nombre} via script: {len(data)} ofertas')
                    return data if isinstance(data, list) else []
    except Exception as e:
        log(f'{nombre} script error: {e}')
    return []


def analizar_calidad(ofertas: list) -> dict:
    """Análisis de calidad del dataset sin coste (Python puro)."""
    if not ofertas:
        return {'calidad': 0, 'problemas': ['Dataset vacío']}

    problemas = []
    sin_imagen = sum(1 for o in ofertas if not o.get('image'))
    sin_url = sum(1 for o in ofertas if not o.get('url'))
    sin_fuel = sum(1 for o in ofertas if not o.get('fuel'))
    precios_cero = sum(1 for o in ofertas if o.get('precio_desde', 0) <= 0)
    fuentes = list({o.get('fuente', '') for o in ofertas})

    if sin_imagen > len(ofertas) * 0.3:
        problemas.append(f'{sin_imagen} ofertas sin imagen ({round(sin_imagen/len(ofertas)*100)}%)')
    if sin_url > len(ofertas) * 0.1:
        problemas.append(f'{sin_url} ofertas sin URL')
    if precios_cero > 0:
        problemas.append(f'{precios_cero} ofertas con precio cero')
    if len(fuentes) < 2:
        problemas.append('Solo una gestora en el dataset')

    puntuacion = 10
    puntuacion -= len(problemas) * 2
    puntuacion -= round(sin_imagen / len(ofertas) * 3)
    puntuacion = max(0, min(10, puntuacion))

    return {
        'calidad': puntuacion,
        'total': len(ofertas),
        'fuentes': fuentes,
        'problemas': problemas,
        'precio_min': min((o.get('precio_desde', 9999) for o in ofertas), default=0),
        'precio_max': max((o.get('precio_desde', 0) for o in ofertas), default=0),
    }


def normalizar_oferta(o: dict) -> dict:
    """Normaliza y limpia una oferta."""
    MAKE_CORRECTIONS = {
        'VW': 'VOLKSWAGEN', 'CITROËN': 'CITROEN', 'CITROÃ\x83Â‰N': 'CITROEN',
        'MERCEDES-BENZ': 'MERCEDES', 'BMW GROUP': 'BMW',
        'KIA MOTORS': 'KIA', 'HYUNDAI MOTOR': 'HYUNDAI',
    }
    FUEL_MAP = {
        'GASOLINA': 'Gasolina', 'PETROL': 'Gasolina',
        'DIESEL': 'Diesel', 'GASOIL': 'Diesel',
        'ELECTRICO': 'Electrico', 'ELECTRIC': 'Electrico', 'BEV': 'Electrico',
        'HIBRIDO': 'Hibrido', 'HYBRID': 'Hibrido', 'HEV': 'Hibrido',
        'PHEV': 'Hibrido enchufable', 'PLUG-IN': 'Hibrido enchufable',
        'MICRO': 'Micro hibrido', 'MHEV': 'Micro hibrido',
    }

    make = str(o.get('make', '')).strip().upper()
    make = MAKE_CORRECTIONS.get(make, make)

    fuel = str(o.get('fuel', '')).strip()
    for k, v in FUEL_MAP.items():
        if k in fuel.upper():
            fuel = v
            break

    return {
        'fuente': o.get('fuente', ''),
        'tipo': o.get('tipo', 'empresa'),
        'make': make,
        'model': str(o.get('model', '')).strip().upper(),
        'version': str(o.get('version', '')).strip()[:120],
        'fuel': fuel,
        'precio_desde': round(float(o.get('precio_desde', 0)), 2),
        'duracion': int(o.get('duracion', 48)),
        'km': int(o.get('km', 10000)),
        'url': str(o.get('url', '')),
        'category': str(o.get('category', '')),
        'image': str(o.get('image', '')),
    }


def deduplicar(ofertas: list) -> list:
    seen = {}
    for o in ofertas:
        key = f"{o['fuente']}|{o['make']}|{o['model']}|{o['duracion']}|{o['km']}"
        if key not in seen or o['precio_desde'] < seen[key]['precio_desde']:
            seen[key] = o
    return list(seen.values())


def main():
    log('=== Agente de Scraping iniciado (coste cero) ===')

    ofertas_existentes = cargar_ofertas()
    log(f'Ofertas existentes: {len(ofertas_existentes)}')

    nuevas = []

    # 1. Scrapers directos (gratuitos)
    nuevas.extend(scrape_arval())
    time.sleep(2)
    nuevas.extend(scrape_ayvens())

    # 2. Scripts existentes como fallback
    if len(nuevas) < 50:
        log('Pocas ofertas nuevas, ejecutando scripts existentes...')
        for fuente in ['arval', 'ayvens']:
            nuevas.extend(ejecutar_scraper_existente(fuente))

    if not nuevas:
        log('Sin ofertas nuevas. Manteniendo dataset existente.')
        return

    # 3. Normalizar y deduplicar
    normalizadas = [normalizar_oferta(o) for o in nuevas if o.get('make') and o.get('precio_desde', 0) > 0]
    normalizadas = deduplicar(normalizadas)
    log(f'Normalizadas: {len(normalizadas)}')

    # 4. Mezclar con fuentes no scrapeadas en esta ejecución
    fuentes_nuevas = {o['fuente'] for o in normalizadas}
    otras = [o for o in ofertas_existentes if o.get('fuente') not in fuentes_nuevas]
    final = deduplicar(normalizadas + otras)
    final.sort(key=lambda o: o.get('precio_desde', 9999))

    # 5. Análisis de calidad (Python puro, sin coste)
    analisis = analizar_calidad(final)
    log(f'Calidad dataset: {analisis["calidad"]}/10 · {analisis["total"]} ofertas · fuentes: {analisis["fuentes"]}')
    for p in analisis.get('problemas', []):
        log(f'  Advertencia: {p}')

    # 6. Guardar
    guardar_ofertas(final)

    # 7. Regenerar páginas SEO
    for script in ['inyectar_ofertas.py', 'generar_seo.py', 'generar_categorias.py']:
        ruta = os.path.join(os.path.dirname(__file__), script)
        if os.path.exists(ruta):
            log(f'Ejecutando {script}...')
            subprocess.run([sys.executable, ruta], cwd=os.path.dirname(__file__), timeout=300)

    log('=== Agente completado ===')


if __name__ == '__main__':
    main()
