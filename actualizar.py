"""
Script maestro de actualización periódica de myrenting.es
Ejecutar manualmente: python3 actualizar.py
O programar con cron: 0 8 * * 1 cd /Users/matthiasthomassen/Documents/Myrenting && python3 actualizar.py

Hace todo en orden:
1. Scrapeea Arval, Ayvens y Kinto
2. Combina y convierte el JSON
3. Normaliza los datos
4. Inyecta en el HTML
5. Regenera páginas SEO
6. Push a GitHub
"""

import json, re, subprocess, sys, shutil
from datetime import datetime
from pathlib import Path

BASE = Path("/Users/matthiasthomassen/Documents/Myrenting")
LOG  = BASE / "actualizar.log"

def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {msg}"
    print(linea)
    with open(LOG, "a") as f:
        f.write(linea + "\n")

def run(cmd, cwd=BASE):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        log(f"ERROR: {result.stderr[:200]}")
        return False
    return True

# ── PASO 1: Scraping ──────────────────────────────────────────────────────────

def scrape_arval():
    log("Scrapeando Arval...")
    try:
        import requests, urllib3
        urllib3.disable_warnings()
        
        url = "https://www.arval.es/api/v1/offers"
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        
        ofertas = []
        page = 1
        while True:
            r = requests.get(url, params={"page": page, "limit": 50}, headers=headers, verify=False, timeout=10)
            if r.status_code != 200:
                break
            data = r.json()
            items = data.get("data") or data.get("offers") or data.get("results") or []
            if not items:
                break
            ofertas.extend(items)
            if len(items) < 50:
                break
            page += 1
        
        if ofertas:
            log(f"  Arval: {len(ofertas)} ofertas scrapeadas")
            return ofertas
    except Exception as e:
        log(f"  Arval scraping falló: {e} — usando datos existentes")
    return None

def scrape_kinto():
    log("Scrapeando Kinto...")
    try:
        from playwright.sync_api import sync_playwright
        import re as re_mod
        
        ofertas = []
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.kinto-mobility.eu/es/es/kinto-one/renting", timeout=30000)
            page.wait_for_load_state("networkidle", timeout=15000)
            
            tarjetas = page.query_selector_all(".vehicle-card, .offer-card, [class*='card']")
            for t in tarjetas:
                try:
                    texto = t.inner_text()
                    precio_match = re_mod.search(r'(\d+)[.,]?\d*\s*€', texto)
                    if not precio_match:
                        continue
                    precio = float(precio_match.group(1))
                    img_el = t.query_selector("img")
                    img = img_el.get_attribute("src") if img_el else ""
                    link_el = t.query_selector("a")
                    link = "https://www.kinto-mobility.eu" + link_el.get_attribute("href") if link_el else ""
                    
                    ofertas.append({
                        "gestora": "Kinto",
                        "tipoCliente": "empresa",
                        "marca": "Toyota",
                        "modeloLimpio": "Kinto",
                        "precioNum": precio,
                        "precio": f"{precio} €",
                        "duracionNum": 36,
                        "kmNum": 10000,
                        "combustible": "Híbrido",
                        "imagen": img,
                        "url": link or "https://www.kinto-mobility.eu/es/es/kinto-one/renting"
                    })
                except:
                    continue
            browser.close()
        
        log(f"  Kinto: {len(ofertas)} ofertas scrapeadas")
        return ofertas if ofertas else None
    except Exception as e:
        log(f"  Kinto scraping falló: {e} — usando datos existentes")
    return None

# ── PASO 2: Combinar y convertir ──────────────────────────────────────────────

def normalizar_combustible(c):
    if not c: return "Gasolina"
    c = c.lower()
    if 'eléctrico' in c or 'electric' in c: return "Eléctrico"
    if 'enchufable' in c or 'phev' in c: return "Híbrido Enchufable"
    if 'híbrido' in c or 'hybrid' in c or 'mhev' in c or 'hev' in c: return "Híbrido"
    if 'diésel' in c or 'diesel' in c: return "Diésel"
    if 'gasolina' in c: return "Gasolina"
    if 'glp' in c: return "GLP"
    return c.title()

def convertir_oferta(o):
    if "fuente" in o and "make" in o and "precio_desde" in o:
        return o
    fuente = o.get("gestora") or o.get("fuente") or "Desconocida"
    tipo = "particular" if "particular" in (o.get("tipoCliente") or "").lower() else "empresa"
    make = (o.get("marca") or "").strip().upper()
    model = (o.get("modeloLimpio") or o.get("modelo") or "").strip().upper()
    if not model and " " in make:
        partes = make.split(" ", 1)
        make, model = partes[0], partes[1]
    duracion = o.get("duracionNum") or 36
    km = o.get("kmNum") or 10000
    precio = float(o.get("precioNum") or o.get("precio_desde") or 0)
    return {
        "fuente": fuente, "tipo": tipo,
        "make": make, "model": model,
        "version": o.get("version") or "",
        "category": o.get("category") or "",
        "fuel": normalizar_combustible(o.get("combustible") or o.get("fuel") or ""),
        "transmission": o.get("transmission") or "",
        "image": o.get("imagen") or o.get("image") or "",
        "precio_desde": precio,
        "precios": [[duracion, km, 0.0, precio]],
        "link_oferta": o.get("url") or o.get("link_oferta") or "",
    }

# ── PASO 3: Normalizar make/model ─────────────────────────────────────────────

MAKE_CORRECTIONS = {
    "ALPINE A290": ("ALPINE", "A290"), "AUDI A1": ("AUDI", "A1"),
    "AUDI A3": ("AUDI", "A3"), "AUDI A4": ("AUDI", "A4"),
    "AUDI Q3": ("AUDI", "Q3"), "AUDI Q5": ("AUDI", "Q5"),
    "AUDI Q8": ("AUDI", "Q8"), "BMW I4": ("BMW", "I4"),
    "BMW SERIE 1": ("BMW", "SERIE 1"), "BMW SERIE 2": ("BMW", "SERIE 2"),
    "BMW SERIE 3": ("BMW", "SERIE 3"), "BMW SERIE 5": ("BMW", "SERIE 5"),
    "BMW X1": ("BMW", "X1"), "BMW X2": ("BMW", "X2"),
    "BMW X3 20D XDRIVE": ("BMW", "X3"), "BMW X3": ("BMW", "X3"),
    "BMW X4": ("BMW", "X4"), "BMW X5": ("BMW", "X5"),
    "BYD ATTO 2 DMI ACTIVE 122KW 166 CV": ("BYD", "ATTO 2"),
    "BYD ATTO 2": ("BYD", "ATTO 2"), "BYD SEAL U": ("BYD", "SEAL U"),
    "CUPRA FORMENTOR": ("CUPRA", "FORMENTOR"), "CUPRA TERRAMAR": ("CUPRA", "TERRAMAR"),
    "DACIA SANDERO": ("DACIA", "SANDERO"), "FIAT 500": ("FIAT", "500"),
    "FIAT DOBLÓ": ("FIAT", "DOBLO"), "FORD PUMA / 5P / TODOTERRENO": ("FORD", "PUMA"),
    "FORD RANGER": ("FORD", "RANGER"), "HONDA CR-V": ("HONDA", "CR-V"),
    "HYUNDAI BAYON": ("HYUNDAI", "BAYON"), "HYUNDAI I20": ("HYUNDAI", "I20"),
    "HYUNDAI IONIQ 5": ("HYUNDAI", "IONIQ 5"), "HYUNDAI KONA": ("HYUNDAI", "KONA"),
    "HYUNDAI TUCSON": ("HYUNDAI", "TUCSON"), "JAECOO 7": ("JAECOO", "7"),
    "KIA EV3": ("KIA", "EV3"), "KIA EV6": ("KIA", "EV6"),
    "KIA NIRO": ("KIA", "NIRO"), "KIA SPORTAGE": ("KIA", "SPORTAGE"),
    "KIA STONIC": ("KIA", "STONIC"), "KIA XCEED": ("KIA", "XCEED"),
    "LAND ROVER DEFENDER": ("LAND ROVER", "DEFENDER"),
    "LAND ROVER RANGE ROVER EVOQUE": ("LAND ROVER", "RANGE ROVER EVOQUE"),
    "LAND ROVER SPORT": ("LAND ROVER", "RANGE ROVER SPORT"),
    "MAZDA CX-60": ("MAZDA", "CX-60"),
    "MERCEDES BENZ CITAN FURGON": ("MERCEDES BENZ", "CITAN FURGON"),
    "MERCEDES BENZ CLASE A": ("MERCEDES BENZ", "CLASE A"),
    "MERCEDES BENZ GLA": ("MERCEDES BENZ", "GLA"),
    "MERCEDES BENZ SPRINTER": ("MERCEDES BENZ", "SPRINTER"),
    "MERCEDES BENZ VITO": ("MERCEDES BENZ", "VITO"),
    "MG ZS": ("MG", "ZS"), "OMODA 5": ("OMODA", "5"),
    "PEUGEOT 2008": ("PEUGEOT", "2008"), "PEUGEOT 208": ("PEUGEOT", "208"),
    "PEUGEOT 3008": ("PEUGEOT", "3008"), "PEUGEOT 308": ("PEUGEOT", "308"),
    "POLESTAR 4": ("POLESTAR", "4"),
    "RENAULT CLIO": ("RENAULT", "CLIO"), "RENAULT ESPACE": ("RENAULT", "ESPACE"),
    "RENAULT KANGOO": ("RENAULT", "KANGOO"), "RENAULT MASTER": ("RENAULT", "MASTER"),
    "RENAULT RAFALE": ("RENAULT", "RAFALE"), "RENAULT SYMBIOZ": ("RENAULT", "SYMBIOZ"),
    "RENAULT TRAFIC": ("RENAULT", "TRAFIC"),
    "SEAT ARONA": ("SEAT", "ARONA"), "SEAT IBIZA": ("SEAT", "IBIZA"),
    "SEAT LEON": ("SEAT", "LEON"),
    "SKODA FABIA": ("SKODA", "FABIA"), "SKODA KAROQ": ("SKODA", "KAROQ"),
    "SKODA KODIAQ": ("SKODA", "KODIAQ"), "SKODA OCTAVIA": ("SKODA", "OCTAVIA"),
    "TESLA 3": ("TESLA", "MODEL 3"),
    "VOLKSWAGEN GOLF": ("VOLKSWAGEN", "GOLF"), "VOLKSWAGEN POLO": ("VOLKSWAGEN", "POLO"),
    "VOLKSWAGEN T-CROSS": ("VOLKSWAGEN", "T-CROSS"), "VOLKSWAGEN T-ROC": ("VOLKSWAGEN", "T-ROC"),
    "VOLKSWAGEN TAIGO": ("VOLKSWAGEN", "TAIGO"),
    "VOLVO XC40": ("VOLVO", "XC40"), "VOLVO XC60": ("VOLVO", "XC60"),
}

def normalizar_oferta(o):
    make_raw = (o.get("make") or "").strip().upper()
    if make_raw in MAKE_CORRECTIONS:
        make_n, model_n = MAKE_CORRECTIONS[make_raw]
        o["make"] = make_n.upper()
        o["model"] = model_n.upper()
    else:
        o["make"] = make_raw
        o["model"] = (o.get("model") or "").strip().upper()
    return o

# ── PASO 4: Inyectar en HTML ──────────────────────────────────────────────────

def inyectar_en_html(ofertas):
    html = (BASE / "index.html").read_text(encoding="utf-8")
    start = html.find("const _OFERTAS = [") 
    end = html.find("];", start) + 2
    json_str = json.dumps(ofertas, ensure_ascii=False, separators=(",", ":"))
    html_nuevo = html[:start] + f"const _OFERTAS = {json_str};" + html[end:]
    (BASE / "index.html").write_text(html_nuevo, encoding="utf-8")

# ── PASO 5: Regenerar páginas SEO ────────────────────────────────────────────

def regenerar_seo():
    result = subprocess.run(
        [sys.executable, str(BASE / "generar_seo.py")],
        cwd=BASE, capture_output=True, text=True
    )
    if result.returncode == 0:
        log("  SEO regenerado OK")
    else:
        log(f"  SEO error: {result.stderr[:100]}")

# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    log("=" * 50)
    log("Iniciando actualización myrenting.es")

    # Leer ofertas actuales del HTML como base
    html = (BASE / "index.html").read_text(encoding="utf-8")
    start = html.find("const _OFERTAS = [") + len("const _OFERTAS = ")
    end = html.find("];", start) + 1
    ofertas_actuales = json.loads(html[start:end])
    log(f"Ofertas actuales en HTML: {len(ofertas_actuales)}")

    # Intentar scraping nuevo (si falla, usa las actuales)
    nuevas_arval = scrape_arval()
    nuevas_kinto = scrape_kinto()

    # Si hay datos nuevos, combinar
    if nuevas_arval or nuevas_kinto:
        # Separar ofertas que NO son de las gestoras scrapeadas (para no duplicar)
        gestoras_a_actualizar = set()
        if nuevas_arval: gestoras_a_actualizar.add("Arval")
        if nuevas_kinto: gestoras_a_actualizar.add("Kinto")
        
        ofertas_base = [o for o in ofertas_actuales if o.get("fuente") not in gestoras_a_actualizar]
        
        nuevas = []
        if nuevas_arval:
            nuevas.extend([convertir_oferta(o) for o in nuevas_arval])
        if nuevas_kinto:
            nuevas.extend([convertir_oferta(o) for o in nuevas_kinto])
        
        ofertas_finales = ofertas_base + nuevas
        log(f"Ofertas tras actualización: {len(ofertas_finales)}")
    else:
        ofertas_finales = ofertas_actuales
        log("Sin datos nuevos — manteniendo ofertas actuales")

    # Normalizar
    ofertas_norm = [normalizar_oferta(o) for o in ofertas_finales]

    # Inyectar en HTML
    inyectar_en_html(ofertas_norm)
    log("HTML actualizado")

    # Regenerar SEO
    regenerar_seo()

    # Git push
    log("Subiendo a GitHub...")
    fecha = datetime.now().strftime("%Y-%m-%d")
    run(["git", "add", "."])
    run(["git", "commit", "-m", f"Actualización automática {fecha}: {len(ofertas_norm)} ofertas"])
    if run(["git", "push", "origin", "main"]):
        log("✓ Push OK — myrenting.es actualizado")
    else:
        log("ERROR en push — revisar manualmente")

    log("Actualización completada")
    log("=" * 50)

if __name__ == "__main__":
    main()
