import asyncio
import json
from playwright.async_api import async_playwright

async def buscar():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        async def capturar(response):
            url = response.url
            if "arval" in url and any(x in url for x in ["offer", "vehicle", "product", "catalog", "graphql", "search"]):
                print(f"\n>>> {url}")
                try:
                    body = await response.body()
                    if len(body) > 100:
                        text = body.decode("utf-8", errors="ignore")
                        if any(x in text.lower() for x in ["price", "precio", "make", "marca", "model"]):
                            print(f"    Tamaño: {len(body)} bytes - CONTIENE DATOS!")
                            with open("respuesta_api.json", "w") as f:
                                f.write(text)
                except:
                    pass
        
        page.on("response", capturar)
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        await page.goto("https://www.arval.es/ofertas/renting-empresas-largo-plazo",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(10000)
        
        await browser.close()

asyncio.run(buscar())
