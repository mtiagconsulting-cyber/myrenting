import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def analizar_arval():
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
        soup = BeautifulSoup(html, "html.parser")
        
        for tag in ["article", "div", "li", "section"]:
            items = soup.find_all(tag, class_=lambda c: c and any(x in c.lower() for x in ["card", "offer", "vehicle", "car", "product", "item"]))
            if items:
                print(f"\n<{tag}> con clases relevantes: {len(items)} encontrados")
                print(f"Ejemplo clase: {items[0].get('class')}")
                print(f"Texto muestra: {items[0].get_text()[:200]}")
        
        await browser.close()

asyncio.run(analizar_arval())
