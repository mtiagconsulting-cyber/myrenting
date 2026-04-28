import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        await page.goto("https://www.ayvens.com/es-es/ofertas/", 
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000)
        
        html = await page.content()
        print(f"Tamaño HTML: {len(html)} caracteres")
        
        with open("ayvens_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Guardado en ayvens_debug.html")
        
        await browser.close()

asyncio.run(main())
