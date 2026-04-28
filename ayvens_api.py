import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    todas = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        async def capturar(response):
            if "search_offers" in response.url:
                try:
                    data = await response.json()
                    print(f"API: {response.url}")
                    print(f"Claves: {list(data.keys())}")
                    for k, v in data.items():
                        if isinstance(v, list) and len(v) > 0:
                            print(f"  {k}: {len(v)} elementos")
                            print(f"  Ejemplo: {json.dumps(v[0], ensure_ascii=False)[:300]}")
                    with open("ayvens_api_data.json", "w") as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Error: {e}")
        
        page.on("response", capturar)
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        await page.goto("https://ofertas-renting.ayvens.es/ofertas/",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(8000)
        
        await browser.close()

asyncio.run(main())
