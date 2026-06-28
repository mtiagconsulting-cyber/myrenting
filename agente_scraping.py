#!/usr/bin/env python3
"""
Agente de scraping de precios de renting usando Claude API.
Coordina múltiples scrapers y actualiza ofertas-db.json.
"""
import os, json, re, time, subprocess, sys
from datetime import datetime
import anthropic

OFERTAS_FILE = os.path.join(os.path.dirname(__file__), 'ofertas-db.json')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'agente_scraping.log')

client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY', ''))


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
        import urllib.request, urllib.error
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
    """Extrae ofertas de Ayvens (ex-ALD)."""
    try:
        import urllib.request
        url = 'https://www.ayvens.com/es-es/ofertas/?format=json'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; Myrenting/1.0)',
            'Accept': 'application/json, text/html',
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode('utf-8', errors='ignore')
        # Buscar JSON embebido si no es API directa
        m = re.search(r'window\.__NUXT__\s*=\s*(\{.*?\})\s*;', raw, re.DOTALL)
        if not m:
            log('Ayvens: no JSON encontrado en página')
            return []
        data = json.loads(m.group(1))
        result = []
        # Navegación recursiva del JSON para encontrar ofertas
        def extract_offers(obj, depth=0):
            if depth > 8 or len(result) > 300:
                return
            if isinstance(obj, list):
                for item in obj:
                    extract_offers(item, depth+1)
            elif isinstance(obj, dict):
                if 'price' in obj and 'brand' in obj:
                    try:
                        result.append({
                            'fuente': 'Ayvens',
                            'tipo': obj.get('type', 'empresa'),
                            'make': str(obj.get('brand', '')).upper(),
                            'model': str(obj.get('model', '')).upper(),
                            'version': str(obj.get('version', '')),
                            'fuel': str(obj.get('fuel', '')),
                            'precio_desde': float(obj.get('price', 0)),
                            'duracion': int(obj.get('duration', 48)),
                            'km': int(obj.get('km', 10000)),
                            'url': obj.get('url', 'https://www.ayvens.com/es-es/ofertas/'),
                            'category': obj.get('category', ''),
                            'image': obj.get('image', ''),
                        })
                    except Exception:
                        pass
                for v in obj.values():
                    extract_offers(v, depth+1)
        extract_offers(data)
        log(f'Ayvens: {len(result)} ofertas')
        return result
    except Exception as e:
        log(f'Ayvens error: {e}')
        return []


def ejecutar_scraper_existente(nombre: str) -> list:
    """Ejecuta uno de los scrapers Python existentes y devuelve las ofertas."""
    script_map = {
        'arval': 'scraper_arval_definitivo.py',
        'ayvens': 'scraper_ayvens_completo.py',
        'kinto': 'scraper_kinto.py',
    }
    script = script_map.get(nombre)
    if not script:
        return []
    script_path = os.path.join(os.path.dirname(__file__), script)
    if not os.path.exists(script_path):
        log(f'Script no encontrado: {script_path}')
        return []
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True, timeout=120,
            cwd=os.path.dirname(__file__)
        )
        if result.returncode == 0:
            # Intentar leer el JSON producido
            for fname in ['ofertas_temp.json', f'{nombre}_data.json', 'output.json']:
                fpath = os.path.join(os.path.dirname(__file__), fname)
                if os.path.exists(fpath):
                    with open(fpath) as f:
                        data = json.load(f)
                    log(f'{nombre} via script: {len(data)} ofertas')
                    return data if isinstance(data, list) else []
        else:
            log(f'{nombre} script error: {result.stderr[:200]}')
    except subprocess.TimeoutExpired:
        log(f'{nombre} script timeout')
    except Exception as e:
        log(f'{nombre} script exception: {e}')
    return []


def analizar_calidad_claude(ofertas: list) -> dict:
    """Usa Claude para analizar la calidad del dataset y sugerir mejoras."""
    if not os.environ.get('ANTHROPIC_API_KEY'):
        return {}

    resumen = {
        'total': len(ofertas),
        'fuentes': list({o.get('fuente', '') for o in ofertas}),
        'marcas': list({o.get('make', '') for o in ofertas})[:20],
        'precio_min': min((o.get('precio_desde', 9999) for o in ofertas), default=0),
        'precio_max': max((o.get('precio_desde', 0) for o in ofertas), default=0),
        'sin_imagen': sum(1 for o in ofertas if not o.get('image')),
        'sin_url': sum(1 for o in ofertas if not o.get('url')),
    }

    try:
        message = client.messages.create(
            model='claude-haiku-4-5-20251001',
            max_tokens=512,
            messages=[{
                'role': 'user',
                'content': f"""Eres un analista de datos de renting de coches en España.
Analiza este resumen del dataset y responde en JSON con:
- "calidad": puntuación 0-10
- "problemas": lista de problemas encontrados
- "sugerencias": lista de mejoras

Dataset: {json.dumps(resumen, ensure_ascii=False)}"""
            }]
        )
        text = message.content[0].text
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception as e:
        log(f'Claude análisis error: {e}')
    return {}


def normalizar_oferta(o: dict) -> dict:
    """Normaliza y limpia una oferta."""
    MAKE_CORRECTIONS = {
        'VW': 'VOLKSWAGEN', 'CITROËN': 'CITROEN', 'CITROÃN': 'CITROEN',
        'MERCEDES-BENZ': 'MERCEDES', 'BMW GROUP': 'BMW', 'KIA MOTORS': 'KIA',
        'HYUNDAI MOTOR': 'HYUNDAI',
    }
    make = str(o.get('make', '')).strip().upper()
    make = MAKE_CORRECTIONS.get(make, make)

    fuel = str(o.get('fuel', '')).strip()
    FUEL_MAP = {
        'GASOLINA': 'Gasolina', 'PETROL': 'Gasolina', 'BENZIN': 'Gasolina',
        'DIESEL': 'Diesel', 'GASOIL': 'Diesel',
        'ELECTRICO': 'Electrico', 'ELECTRIC': 'Electrico', 'BEV': 'Electrico',
        'HIBRIDO': 'Hibrido', 'HYBRID': 'Hibrido', 'HEV': 'Hibrido',
        'PHEV': 'Hibrido enchufable', 'PLUG-IN': 'Hibrido enchufable',
        'MICRO': 'Micro hibrido', 'MHEV': 'Micro hibrido',
    }
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
    """Elimina duplicados manteniendo el de menor precio."""
    seen = {}
    for o in ofertas:
        key = f"{o['fuente']}|{o['make']}|{o['model']}|{o['duracion']}|{o['km']}"
        if key not in seen or o['precio_desde'] < seen[key]['precio_desde']:
            seen[key] = o
    return list(seen.values())


def main():
    log('=== Agente de Scraping iniciado ===')

    # Cargar ofertas existentes como fallback
    ofertas_existentes = cargar_ofertas()
    log(f'Ofertas existentes: {len(ofertas_existentes)}')

    nuevas_ofertas = []

    # 1. Scrapers directos
    log('--- Ejecutando scrapers ---')
    nuevas_ofertas.extend(scrape_arval())
    time.sleep(2)
    nuevas_ofertas.extend(scrape_ayvens())

    # 2. Scripts existentes como fallback
    if len(nuevas_ofertas) < 50:
        log('Pocas ofertas nuevas, ejecutando scripts existentes...')
        for fuente in ['arval', 'ayvens']:
            nuevas_ofertas.extend(ejecutar_scraper_existente(fuente))

    # 3. Si no hay nada nuevo, mantener las existentes
    if not nuevas_ofertas:
        log('Sin ofertas nuevas. Manteniendo dataset existente.')
        return

    # 4. Normalizar y deduplicar
    log('--- Normalizando ---')
    nuevas_normalizadas = [normalizar_oferta(o) for o in nuevas_ofertas if o.get('make') and o.get('precio_desde', 0) > 0]
    nuevas_normalizadas = deduplicar(nuevas_normalizadas)
    log(f'Después de normalizar/dedup: {len(nuevas_normalizadas)}')

    # 5. Mezclar con existentes (priorizar nuevas, mantener fuentes no scrapeadas)
    fuentes_nuevas = {o['fuente'] for o in nuevas_normalizadas}
    existentes_otras_fuentes = [o for o in ofertas_existentes if o.get('fuente') not in fuentes_nuevas]
    final = nuevas_normalizadas + existentes_otras_fuentes
    final = deduplicar(final)
    final.sort(key=lambda o: o.get('precio_desde', 9999))

    log(f'Dataset final: {len(final)} ofertas')

    # 6. Análisis de calidad con Claude
    analisis = analizar_calidad_claude(final)
    if analisis:
        log(f'Calidad dataset: {analisis.get("calidad", "N/D")}/10')
        for p in analisis.get('problemas', []):
            log(f'  Problema: {p}')

    # 7. Guardar
    guardar_ofertas(final)

    # 8. Regenerar páginas SEO
    generar_seo = os.path.join(os.path.dirname(__file__), 'generar_seo.py')
    if os.path.exists(generar_seo):
        log('Regenerando páginas SEO...')
        subprocess.run([sys.executable, generar_seo], cwd=os.path.dirname(__file__), timeout=300)

    # 9. Inyectar en index.html
    inyectar = os.path.join(os.path.dirname(__file__), 'inyectar_ofertas.py')
    if os.path.exists(inyectar):
        log('Inyectando ofertas en index.html...')
        subprocess.run([sys.executable, inyectar], cwd=os.path.dirname(__file__), timeout=60)

    log('=== Agente completado ===')


if __name__ == '__main__':
    main()
