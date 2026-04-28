import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_paginas(page, url, tipo_cliente):
    ofertas = []
    
    await page.goto(url, wait_until="networkidle", timeout=60000)
    await page.wait_for_timeout(4000)
    
    pagina = 1
    while True:
        print(f"  [{tipo_cliente}] Página {pagina}...")
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        script = soup.find("script", {"id": "__NEXT_DATA__"})
        
        if script:
            data = json.loads(script.string)
            blocks = data["props"]["pageProps"]["__TEMPLATE_QUERY_DATA__"]["page"]["blocks"]
            for block in blocks:
                if block.get("name") == "octopus/overview":
                    batch = block["attributes"]["offers"]["offerSummaries"]
                    total = block["attributes"]["offers"]["totalElements"]
                    for o in batch:
                        o["tipoCliente"] = tipo_cliente
                        o["gestora"] = "Arval"
                    ofertas.extend(batch)
                    print(f"    {len(ofertas)}/{total} ofertas")
                    
                    if len(ofertas) >= total:
                        print(f"    Completado!")
                        return ofertas
        
        # Buscar y clickar botón con scroll
        try:
            btn = await page.wait_for_selector("button.btn-primary span.btn-label", timeout=3000)
            texto = await btn.inner_text()
            if "DESCUBRE" in texto.upper():
                await btn.scroll_into_view_if_needed()
                await page.wait_for_timeout(1000)
                await btn.click()
                await page.wait_for_timeout(4000)
                pagina += 1
            else:
                break
        except:
            break
    
    return ofertas

async def main():
    print("Iniciando scraper Arval v2...")
    
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
    
    with open("arval_definitivo.json", "w", encoding="utf-8") as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    print("Guardado en arval_definitivo.json")

asyncio.run(main())
