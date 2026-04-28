import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.goto("https://ofertas-renting.ayvens.es/ofertas/",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        api_page = await context.new_page()
        await api_page.set_extra_http_headers({
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://ofertas-renting.ayvens.es/ofertas/"
        })
        
        response = await api_page.goto(
            "https://ofertas-renting.ayvens.es/api/search_offers?page=1"
        )
        
        body = await response.body()
        print(f"Status: {response.status}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Primeros 500 chars:")
        print(body.decode("utf-8", errors="ignore")[:500])
        
        with open("ayvens_raw.txt", "wb") as f:
            f.write(body)
        
        await browser.close()

asyncio.run(main())
