import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        async def capturar(response):
            url = response.url
            try:
                body = await response.body()
                if len(body) > 500:
                    text = body.decode("utf-8", errors="ignore")
                    if any(x in text.lower() for x in ["precio", "price", "cuota", "marca", "model"]):
                        if any(x in url for x in ["api", "json", "graphql", "search", "offer", "vehicle"]):
                            print(f"\n>>> {url[:120]}")
                            print(f"    {len(body)} bytes")
                            with open("ayvens_api_raw.txt", "a") as f:
                                f.write(f"\n\n=== {url} ===\n{text[:2000]}")
            except:
                pass
        
        page.on("response", capturar)
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        await page.goto("https://ofertas-renting.ayvens.es/ofertas/",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(8000)
        
        html = await page.content()
        with open("ayvens_debug2.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"\nHTML: {len(html)} chars")
        
        await browser.close()

asyncio.run(main())
