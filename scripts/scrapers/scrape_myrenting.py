"""
scrape_myrenting.py — Scraper maestro Myrenting.es
Gestoras: Arval, Ayvens, Kinto, Alphabet, Quadis
Uso: python3 scrape_myrenting.py

Requisitos:
    pip install requests playwright beautifulsoup4
    playwright install chromium
"""

import asyncio
import json
import math
import os
import re
import time
import urllib3

import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

urllib3.disable_warnings()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_JSON = os.path.join(BASE_DIR, "ofertas_combinadas.json")
OUTPUT_HTML = os.path.join(BASE_DIR, "index.html")


# ─────────────────────────────────────────────────────────────────────────────
# ARVAL  (API Next.js, sin navegador)
# ─────────────────────────────────────────────────────────────────────────────

def arval_get_primera(overview_url):
    r = requests.get(
        f"https://www.arval.es/ofertas{overview_url}",
        headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"},
        timeout=30,
    )
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        r.text,
        re.DOTALL,
    )
    if not m:
        return [], 1
    data = json.loads(m.group(1))
    try:
        for block in data["props"]["pageProps"]["__TEMPLATE_QUERY_DATA__"]["page"]["blocks"]:
            if block.get("name") == "octopus/overview":
                offers = block["attributes"]["offers"]
                print(f"  Página 1: {len(offers['offerSummaries'])} ofertas ({offers['totalPages']} páginas)")
                return offers["offerSummaries"], offers["totalPages"]
    except Exception as e:
        print(f"  Error Arval: {e}")
    return [], 1


def arval_get_pagina(page, overview_url):
    url = (
        f"https://www.arval.es/ofertas/_next/api/offers/overview"
        f"?page={page}&size=12&sortBy=priceGridRental&sortDirection=asc"
        f"&minPrice=0&maxPrice=9999"
        f"&overviewUrl={overview_url.replace('/', '%2F')}&lang=es_ES"
    )
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    ofertas = r.json().get("offerSummaries", []) if r.status_code == 200 else []
    print(f"  Página {page}: {len(ofertas)} ofertas")
    return ofertas


def arval_norm(o, tipo):
    return {
        "fuente": "Arval",
        "tipo": tipo,
        "make": (o.get("makeName") or "").strip().upper(),
        "model": (o.get("modelName") or "").strip().upper(),
        "version": o.get("versionName") or o.get("vehicleCatalogName") or "",
        "fuel": o.get("fuelTypeName") or "",
        "precio_desde": float(o.get("leasePrice") or o.get("priceGridRental") or 0),
        "duracion": int(o.get("duration") or 36),
        "km": int(o.get("mileage") or 10000),
        "image": o.get("imagePath") or "",
        "url": "https://www.arval.es/ofertas" + (o.get("url") or ""),
        "category": o.get("modelCategoryName") or "",
    }


def scrape_arval():
    print("\n=== ARVAL ===")
    todas = []
    for tipo, path in [
        ("empresa", "/renting-empresas-largo-plazo"),
        ("particular", "/renting-particulares-largo-plazo"),
    ]:
        print(f"[{tipo}]")
        p1, total = arval_get_primera(path)
        for o in p1:
            todas.append(arval_norm(o, tipo))
        for page in range(2, total + 1):
            time.sleep(0.5)
            for o in arval_get_pagina(page, path):
                todas.append(arval_norm(o, tipo))
    print(f"Total Arval: {len(todas)}")
    return todas


# ─────────────────────────────────────────────────────────────────────────────
# AYVENS  (Bearer token via Playwright + API REST)
# ─────────────────────────────────────────────────────────────────────────────

async def ayvens_get_token():
    token = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        async def intercept(req):
            nonlocal token
            if "search_offers" in req.url:
                auth = req.headers.get("authorization", "")
                if auth and "Bearer" in auth:
                    token = auth.replace("Bearer ", "").strip()

        page.on("request", intercept)
        await page.goto(
            "https://ofertas-renting.ayvens.es/ofertas/",
            wait_until="networkidle",
            timeout=30000,
        )
        await page.wait_for_timeout(3000)
        await browser.close()
    return token


def ayvens_norm(o, tipo):
    detail = o.get("offerDetail") or {}
    car = o.get("car") or {}
    brand = car.get("brand") or {}
    make = detail.get("make") or brand.get("name") or ""
    model = detail.get("model") or car.get("model") or ""
    precio = detail.get("monthFee") or round((o.get("price") or 0) / 100)
    return {
        "fuente": "Ayvens",
        "tipo": tipo,
        "make": make.strip().upper(),
        "model": model.strip().upper(),
        "version": detail.get("version") or "",
        "fuel": car.get("fuelType") or "",
        "precio_desde": float(precio),
        "duracion": int(detail.get("termInMonths") or 36),
        "km": int(detail.get("yearKms") or 10000),
        "image": detail.get("urlPhoto") or "",
        "url": "https://ofertas-renting.ayvens.es/ofertas/" + (car.get("slug") or ""),
        "category": detail.get("campaign_type") or "",
    }


async def scrape_ayvens():
    print("\n=== AYVENS ===")
    token = await ayvens_get_token()
    if not token:
        print("ERROR: sin token Ayvens")
        return []
    print(f"Token: {token[:20]}...")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "Referer": "https://ofertas-renting.ayvens.es/ofertas/",
        "Origin": "https://ofertas-renting.ayvens.es",
    })

    todas = []
    for offer_type, tipo in [("enterprise", "empresa"), ("particular", "particular")]:
        print(f"[{tipo}]")
        payload = {
            "fuel": None, "brands": [], "models": [], "types": [],
            "minPrice": None, "maxPrice": None, "transmission": None,
            "delivery": False, "dgtLabel": None, "kms": [0, 128184],
            "offerType": offer_type, "order": "price_asc",
            "origin": None, "quality": None, "seats": None,
        }
        page = 1
        while True:
            r = session.post(
                f"https://ofertas-renting.ayvens.es/api/search_offers?page={page}",
                json=payload,
                timeout=30,
            )
            if r.status_code != 200:
                print(f"  Error {r.status_code}")
                break
            data = r.json()
            ofertas = data.get("data", [])
            last = data.get("meta", {}).get("last_page", 1)
            print(f"  Página {page}/{last}: {len(ofertas)} ofertas")
            for o in ofertas:
                todas.append(ayvens_norm(o, tipo))
            if page >= last:
                break
            page += 1
            time.sleep(0.5)

    print(f"Total Ayvens: {len(todas)}")
    return todas


# ─────────────────────────────────────────────────────────────────────────────
# KINTO  (Playwright + BeautifulSoup)
# ─────────────────────────────────────────────────────────────────────────────

async def scrape_kinto():
    print("\n=== KINTO ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(
            "https://www.kinto-mobility.eu/es/es/kinto-one/renting",
            wait_until="networkidle",
            timeout=30000,
        )
        await page.wait_for_timeout(3000)
        html = await page.content()
        await browser.close()

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(".cmp-caroverview__list a[href*='/renting/']")
    print(f"Cards: {len(cards)}")

    ofertas = []
    for card in cards:
        # Precio
        precio_el = card.select_one(".cmp-caroverview__car-price span")
        precio_num = float(re.sub(r"[^\d.]", "", precio_el.text)) if precio_el else 0

        # Nombre → marca y modelo
        nombre_el = card.select_one(".cmp-caroverview__car-name")
        nombre = nombre_el.text.strip() if nombre_el else ""
        palabras = nombre.split()
        make = palabras[0].upper() if palabras else ""
        model_words = palabras[1:] if len(palabras) > 1 else []
        if model_words and model_words[0].upper() == make:
            model_words = model_words[1:]
        model = " ".join(model_words).upper()

        # Duración y km
        duracion_el = card.select_one(".cmp-caroverview__car-duration")
        duracion_raw = duracion_el.text.strip() if duracion_el else ""
        duracion_m = re.search(r"(\d+)\s*[Mm]es", duracion_raw)
        km_m = re.search(r"([\d,.]+)\s*km", duracion_raw)
        duracion = int(duracion_m.group(1)) if duracion_m else 36
        km = int(re.sub(r"[,.]", "", km_m.group(1))) if km_m else 10000

        # Entrada
        meses_el = card.select_one(".cmp-caroverview__car-lease-months")
        meses_raw = meses_el.text.strip() if meses_el else ""
        entrada = 0
        m = re.search(r"€([\d,.]+)\s*Entrada", meses_raw)
        if m:
            entrada = float(re.sub(r"[,.](?=\d{3})", "", m.group(1)))

        # Combustible desde aria-label
        aria = card.get("aria-label", "")
        partes = aria.split(" - ")
        combustible = partes[1].split()[0] if len(partes) > 1 else ""

        # Imagen
        img_el = card.select_one("img")
        imagen = img_el.get("src", "") if img_el else ""

        ofertas.append({
            "fuente": "Kinto",
            "tipo": "empresa",
            "make": make,
            "model": model,
            "version": aria.replace(" - view details", "").strip(),
            "fuel": combustible,
            "precio_desde": precio_num,
            "duracion": duracion,
            "km": km,
            "entrada": entrada,
            "image": imagen,
            "url": "https://www.kinto-mobility.eu" + card.get("href", ""),
            "category": "",
        })

    print(f"Total Kinto: {len(ofertas)}")
    return ofertas


# ─────────────────────────────────────────────────────────────────────────────
# ALPHABET  (API Base64, sin navegador)
# ─────────────────────────────────────────────────────────────────────────────

def alphabet_call_api(payload_dict):
    import base64
    payload = base64.b64encode(json.dumps(payload_dict).encode()).decode()
    r = requests.post(
        "https://crm-colectivosb2e.alphabet.es/colectivosb2eadmin/callColecApi",
        data=payload,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "text/plain",
            "Referer": "https://www.ofertas-renting.alphabet.es/",
        },
        verify=False,
        timeout=30,
    )
    import base64 as b64
    return json.loads(b64.b64decode(r.json()["data"]).decode())


def alphabet_norm(o):
    precio = float(o.get("precioformat") or o.get("precio", "0").replace(",", ".") or 0)
    return {
        "fuente": "Alphabet",
        "tipo": "empresa",
        "make": (o.get("dsmarca") or "").strip().upper(),
        "model": (o.get("modelo") or "").strip().upper(),
        "version": o.get("descripcion") or "",
        "fuel": o.get("dscombustible") or "",
        "precio_desde": precio,
        "duracion": int(o.get("plazo") or 36),
        "km": int((o.get("kilometros") or "10000").replace(".", "").replace(",", "")),
        "image": o.get("imgVeh") or "",
        "url": f"https://www.ofertas-renting.alphabet.es/ofertas-renting/{o.get('modeloEnc', '')}",
        "category": o.get("dscarroceria") or "",
    }


def scrape_alphabet():
    print("\n=== ALPHABET ===")
    data = alphabet_call_api({
        "accion": "searchInit",
        "entidad": "2",
        "from": "colectbe",
        "executeApi": "BuscadorAPI",
    })
    ofertas = [alphabet_norm(o) for o in data.get("listDatos", [])]
    print(f"Total Alphabet: {len(ofertas)}")
    return ofertas


# ─────────────────────────────────────────────────────────────────────────────
# QUADIS  (API HTML + BeautifulSoup, sin navegador)
# ─────────────────────────────────────────────────────────────────────────────

def scrape_quadis():
    print("\n=== QUADIS ===")
    BASE = "https://www.quadis.es/api-vehicles/coches-renting"
    HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    r = requests.get(f"{BASE}?page=1&limit=14", headers=HEADERS, timeout=30)
    data = r.json()
    total = int(data.get("total_count", 0))
    total_pages = math.ceil(total / 14)
    print(f"Total: {total} vehículos, {total_pages} páginas")

    all_html = data.get("html", "")
    for page in range(2, total_pages + 1):
        r = requests.get(f"{BASE}?page={page}&limit=14", headers=HEADERS, timeout=30)
        all_html += r.json().get("html", "")
        time.sleep(0.5)

    soup = BeautifulSoup(all_html, "html.parser")
    cards = soup.select(".car-card")
    print(f"Cards encontradas: {len(cards)}")

    ofertas = []
    for card in cards:
        link = card.select_one("a[href*='/coches-renting/']")
        url = "https://www.quadis.es" + link.get("href", "") if link else ""
        img = card.select_one("img.car-card-img-1")
        imagen = img.get("src", "") if img else ""
        precio_el = card.select_one("[class*='price'], [class*='precio']")
        precio_raw = precio_el.text.strip() if precio_el else ""
        precio_num = float(re.sub(r"[^\d]", "", precio_raw)) if re.search(r"\d", precio_raw) else 0
        parts = url.replace("https://www.quadis.es/coches-renting/", "").split("/")
        make = parts[0].upper() if parts else ""
        model = parts[1].upper() if len(parts) > 1 else ""
        version_el = card.select_one("h2, h3, .car-card-title, [class*='title']")
        version = version_el.text.strip() if version_el else ""
        if not make:
            continue
        ofertas.append({
            "fuente": "Quadis",
            "tipo": "empresa",
            "make": make,
            "model": model,
            "version": version,
            "fuel": "",
            "precio_desde": precio_num,
            "duracion": 36,
            "km": 10000,
            "image": imagen,
            "url": url,
            "category": "",
        })

    print(f"Total Quadis: {len(ofertas)}")
    return ofertas


# ─────────────────────────────────────────────────────────────────────────────
# INYECTAR JSON EN INDEX.HTML
# ─────────────────────────────────────────────────────────────────────────────

def inyectar_en_html(ofertas):
    with open(OUTPUT_HTML, encoding="utf-8") as f:
        html = f.read()

    start = html.find("const _OFERTAS = [")
    end = html.find("];", start) + 2
    if start == -1:
        print("⚠️  No se encontró const _OFERTAS en index.html")
        return

    nuevo_json = json.dumps(ofertas, ensure_ascii=False, separators=(",", ":"))
    nuevo_html = html[:start] + f"const _OFERTAS = {nuevo_json};" + html[end:]

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(nuevo_html)
    print(f"✅ {len(ofertas)} ofertas inyectadas en index.html")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

async def main():
    print("╔══════════════════════════════════════╗")
    print("║   SCRAPER MYRENTING.ES               ║")
    print("╚══════════════════════════════════════╝")

    arval    = scrape_arval()
    ayvens   = await scrape_ayvens()
    kinto    = await scrape_kinto()
    alphabet = scrape_alphabet()
    quadis   = scrape_quadis()

    todas = arval + ayvens + kinto + alphabet + quadis

    print("\n─── RESUMEN ─────────────────────────────")
    print(f"Arval:    {len(arval):>4} ofertas")
    print(f"Ayvens:   {len(ayvens):>4} ofertas")
    print(f"Kinto:    {len(kinto):>4} ofertas")
    print(f"Alphabet: {len(alphabet):>4} ofertas")
    print(f"Quadis:   {len(quadis):>4} ofertas")
    print(f"TOTAL:    {len(todas):>4} ofertas")

    # Guardar JSON combinado
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Guardado en ofertas_combinadas.json")

    # Inyectar en index.html
    inyectar_en_html(todas)

    print("\n🚀 Listo. Ahora ejecuta:")
    print(f"   cd {BASE_DIR}")
    print("   git add index.html ofertas_combinadas.json")
    print('   git commit -m "Update ofertas scraping"')
    print("   git push")


if __name__ == "__main__":
    asyncio.run(main())
