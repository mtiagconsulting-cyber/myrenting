import asyncio
import json
from playwright.async_api import async_playwright

async def interceptar():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        llamadas_api = []
        
        async def capturar_respuesta(response):
            if any(x in response.url for x in ["api", "ofertas", "vehicles", "cars", "products", "catalog"]):
                print(f"API encontrada: {response.url}")
                llamadas_api.append(response.url)
        
        page.on("response", capturar_respuesta)
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        await page.goto("https://www.arval.es/ofertas/renting-empresas-largo-plazo",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(8000)
        
        print(f"\nTotal llamadas API capturadas: {len(llamadas_api)}")
        for url in llamadas_api:
            print(url)
        
        await browser.close()

asyncio.run(interceptar())
