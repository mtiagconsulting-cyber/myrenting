import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    todas = []
    pagina_actual = {"num": 1, "total": 32}
    respuestas = {}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        async def capturar(response):
            if "search_offers" in response.url:
                try:
                    data = await response.json()
                    pagina = data["meta"]["current_page"]
                    pagina_actual["total"] = data["meta"]["last_page"]
                    respuestas[pagina] = data["data"]
                    print(f"  Capturada página {pagina}/{pagina_actual['total']} - {len(data['data'])} ofertas")
                except:
                    pass
        
        page.on("response", capturar)
        
        await page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        
        # Cargar primera página
        await page.goto("https://ofertas-renting.ayvens.es/ofertas/",
                       wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # Navegar por todas las páginas
        while pagina_actual["num"] < pagina_actual["total"]:
            pagina_actual["num"] += 1
            print(f"Navegando a página {pagina_actual['num']}...")
            await page.goto(
                f"https://ofertas-renting.ayvens.es/ofertas/?page={pagina_actual['num']}",
                wait_until="networkidle", timeout=30000
            )
            await page.wait_for_timeout(2000)
        
        await browser.close()
    
    # Procesar todas las respuestas capturadas
    for pagina in sorted(respuestas.keys()):
        for o in respuestas[pagina]:
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
    
    empresas = [o for o in todas if o["tipoCliente"] == "empresa"]
    particulares = [o for o in todas if o["tipoCliente"] == "particular"]
    
    print(f"\nTotal: {len(todas)} ({len(empresas)} empresas + {len(particulares)} particulares)")
    
    with open("ayvens_definitivo.json", "w", encoding="utf-8") as f:
        json.dump(todas, f, ensure_ascii=False, indent=2)
    print("Guardado en ayvens_definitivo.json")

asyncio.run(main())
