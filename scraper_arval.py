import asyncio
import json
from playwright.async_api import async_playwright

async def scrape_arval():
    print("Iniciando scraper Arval...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        await page.goto("https://www.arval.es/ofertas/renting-empresas-largo-plazo", 
                       wait_until="networkidle", timeout=60000)
        
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        print(f"Página cargada: {len(html)} caracteres")
        
        with open("arval_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("HTML guardado en arval_debug.html")
        
        await browser.close()

asyncio.run(scrape_arval())