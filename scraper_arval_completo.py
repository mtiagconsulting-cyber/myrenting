import asyncio
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_arval():
    print("Iniciando scraper Arval completo...")
    todas_ofertas = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        await page.goto("https://www.arval.es/ofertas/renting-empresas-largo-plazo",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        pagina = 1
        while True:
            print(f"Extrayendo página {pagina}...")
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            script = soup.find("script", {"id": "__NEXT_DATA__"})
            
            if script:
                data = json.loads(script.string)
                blocks = data["props"]["pageProps"]["__TEMPLATE_QUERY_DATA__"]["page"]["blocks"]
                for block in blocks:
                    if block.get("name") == "octopus/overview":
                        ofertas = block["attributes"]["offers"]["offerSummaries"]
                        todas_ofertas.extend(ofertas)
                        print(f"  {len(ofertas)} ofertas extraídas")
            
            # Intentar cargar más
            btn = await page.query_selector("button.btn-primary")
            if btn:
                texto = await btn.inner_text()
                if "DESCUBRE" in texto.upper():
                    await btn.click()
                    await page.wait_for_timeout(3000)
                    pagina += 1
                else:
                    break
            else:
                break
        
        await browser.close()
    
    print(f"\nTotal ofertas Arval: {len(todas_ofertas)}")
    with open("arval_todas.json", "w", encoding="utf-8") as f:
        json.dump(todas_ofertas, f, ensure_ascii=False, indent=2)
    print("Guardado en arval_todas.json")

asyncio.run(scrape_arval())
