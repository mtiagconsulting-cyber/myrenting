import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        async def capturar(response):
            url = response.url
            if "ayvens" in url.lower():
                print(url[:120])
        
        page.on("response", capturar)
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        await page.goto("https://www.ayvens.com/es-es/ofertas/",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(8000)
        
        await browser.close()

asyncio.run(main())
