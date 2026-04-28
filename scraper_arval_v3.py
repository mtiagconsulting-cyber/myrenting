import asyncio
import json
from playwright.async_api import async_playwright

async def scrape_paginas(page, url, tipo_cliente):
    ofertas = []
    
    await page.goto(url, wait_until="networkidle", timeout=60000)
    await page.wait_for_timeout(4000)
    
    # Hacer clic en "DESCUBRE MÁS" hasta que desaparezca
    while True:
        try:
            btn = page.locator("button.btn-primary:has-text('DESCUBRE')")
            count = await btn.count()
            if count == 0:
                break
            await btn.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)
            await btn.click()
            await page.wait_for_timeout(3000)
            print(f"  [{tipo_cliente}] Cargando más...")
        except:
            break
    
    # Extraer todas las tarjetas del DOM
    cards = await page.query_selector_all(".offer-card-vehicle")
    print(f"  [{tipo_cliente}] Total tarjetas en DOM: {len(cards)}")
    
    for card in cards:
        try:
            marca = await card.query_selector("h4.title")
            version = await card.query_selector("p.text-text-xs")
            precio = await card.query_selector(".offer-card__new-price")
            combustible = await card.query_selector(".offer-card__spec p")
            duracion = await card.query_selector_all(".offer-card-vehicle__price-box-text")
            imagen = await card.query_selector("img.offer-card__image")
            enlace = await card.query_selector("a.btn-secondary")
            
            oferta = {
                "gestora": "Arval",
                "tipoCliente": tipo_cliente,
                "marca": await marca.inner_text() if marca else "",
                "version": await version.inner_text() if version else "",
                "precio": await precio.inner_text() if precio else "",
                "combustible": await combustible.inner_text() if combustible else "",
                "duracion": await duracion[0].inner_text() if duracion else "",
                "km": await duracion[1].inner_text() if len(duracion) > 1 else "",
                "imagen": await imagen.get_attribute("src") if imagen else "",
                "url": await enlace.get_attribute("href") if enlace else "",
            }
            ofertas.append(oferta)
        except Exception as e:
            pass
    
    return ofertas

async def main():
    print("Iniciando scraper Arval v3...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        empresas = await scrape_paginas(page, "https://www.arval.es/ofertas/renting-empresas-largo-plazo", "empresa")
        particulares = await scrape_paginas(page, "https://www.arval.es/ofertas/renting-particulares-largo-plazo", "particular")
        
        await browser.close()
    
    todas = empresas + particulares
    print(f"\nTotal: {len(todas)} ({len(empresas)} empresas + {len(particulares)} particulares)")
    
    if todas:
        print("\nEjemplo:")
        print(json.dumps(todas[0], ensure_ascii=False, indent=2))
    
    with open("arval_definitivo.json", "w", encoding="utf-8") as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    print("\nGuardado en arval_definitivo.json")

asyncio.run(main())
