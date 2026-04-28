import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    todas = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        await page.goto("https://ofertas-renting.ayvens.es/ofertas/",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Obtener cookies del navegador
        cookies = await context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        
        total_paginas = 32
        pagina = 1
        
        while pagina <= total_paginas:
            print(f"Página {pagina}/{total_paginas}...")
            
            api_page = await context.new_page()
            await api_page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://ofertas-renting.ayvens.es/ofertas/"
            })
            
            response = await api_page.goto(
                f"https://ofertas-renting.ayvens.es/api/search_offers?page={pagina}",
                wait_until="networkidle"
            )
            
            content = await api_page.content()
            await api_page.close()
            
            try:
                # Extraer JSON del HTML
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                else:
                    print(f"  No JSON en página {pagina}")
                    break
                    
                ofertas = data["data"]
                total_paginas = data["meta"]["last_page"]
                
                for o in ofertas:
                    detail = o.get("offerDetail", {}) or {}
                    car = o.get("car", {}) or {}
                    brand = car.get("brand", {}) or {}
                    
                    oferta = {
                        "gestora": "Ayvens",
                        "tipoCliente": o.get("type", ""),
                        "marca": detail.get("make") or brand.get("name", ""),
                        "modeloLimpio": detail.get("model") or car.get("model", ""),
                        "version": detail.get("version") or "",
                        "precioNum": detail.get("monthFee") or round(o.get("price", 0) / 100),
                        "precio": f"{detail.get('monthFee') or round(o.get('price', 0) / 100)} €",
                        "duracionNum": detail.get("termInMonths") or 0,
                        "duracion": f"{detail.get('termInMonths') or 0} meses",
                        "kmNum": detail.get("yearKms") or 0,
                        "km": f"{detail.get('yearKms') or 0} km/año",
                        "combustible": car.get("fuelType", ""),
                        "imagen": detail.get("urlPhoto") or "",
                        "url": f"https://ofertas-renting.ayvens.es/ofertas/{car.get('slug', '')}",
                        "tipoVehiculo": detail.get("campaign_type", ""),
                    }
                    todas.append(oferta)
                
                print(f"  {len(todas)} ofertas acumuladas")
                pagina += 1
                
            except Exception as e:
                print(f"  Error: {e}")
                break
        
        await browser.close()
    
    empresas = [o for o in todas if o["tipoCliente"] == "empresa"]
    particulares = [o for o in todas if o["tipoCliente"] == "particular"]
    
    print(f"\nTotal: {len(todas)} ({len(empresas)} empresas + {len(particulares)} particulares)")
    
    with open("ayvens_definitivo.json", "w", encoding="utf-8") as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    print("Guardado en ayvens_definitivo.json")

asyncio.run(main())
