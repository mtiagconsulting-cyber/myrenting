import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    todas = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        # Cargar la web para obtener cookies
        await page.goto("https://ofertas-renting.ayvens.es/ofertas/",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Scraper todas las páginas via API
        pagina = 1
        total_paginas = 32
        
        while pagina <= total_paginas:
            print(f"Página {pagina}/{total_paginas}...")
            
            response = await page.evaluate(f"""
                async () => {{
                    const r = await fetch('/api/search_offers?page={pagina}');
                    return await r.json();
                }}
            """)
            
            if not response or "data" not in response:
                print(f"  Sin datos en página {pagina}")
                break
            
            ofertas = response["data"]
            total_paginas = response["meta"]["last_page"]
            
            for o in ofertas:
                detail = o.get("offerDetail", {}) or {}
                car = o.get("car", {}) or {}
                brand = car.get("brand", {}) or {}
                
                oferta = {
                    "gestora": "Ayvens",
                    "tipoCliente": o.get("type", ""),
                    "marca": detail.get("make") or brand.get("name", ""),
                    "modeloLimpio": detail.get("model") or car.get("model", ""),
                    "version": detail.get("version") or car.get("version", ""),
                    "precioNum": detail.get("monthFee") or round(o.get("price", 0) / 100),
                    "precio": f"{detail.get('monthFee') or round(o.get('price', 0) / 100)} €",
                    "duracionNum": detail.get("termInMonths") or 0,
                    "duracion": f"{detail.get('termInMonths') or 0} meses",
                    "kmNum": detail.get("yearKms") or 0,
                    "km": f"{detail.get('yearKms') or 0} km/año",
                    "combustible": car.get("fuelType", ""),
                    "imagen": detail.get("urlPhoto") or (car.get("images", [{}])[0].get("url") if car.get("images") else ""),
                    "url": f"https://ofertas-renting.ayvens.es/ofertas/{car.get('slug', '')}",
                    "tipoVehiculo": detail.get("campaign_type", ""),
                }
                todas.append(oferta)
            
            print(f"  {len(todas)} ofertas acumuladas")
            pagina += 1
            await page.wait_for_timeout(500)
        
        await browser.close()
    
    empresas = [o for o in todas if o["tipoCliente"] == "empresa"]
    particulares = [o for o in todas if o["tipoCliente"] == "particular"]
    
    print(f"\nTotal: {len(todas)} ({len(empresas)} empresas + {len(particulares)} particulares)")
    
    with open("ayvens_definitivo.json", "w", encoding="utf-8") as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    print("Guardado en ayvens_definitivo.json")

asyncio.run(main())
