import asyncio
import json
import requests

def scrape_arval():
    print("Scrapeando Arval via API...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.arval.es/ofertas/renting-empresas-largo-plazo"
    }
    
    # Empresas
    url_empresas = "https://www.arval.es/ofertas/_next/api/offers/filters?searchText=&overviewUrl=%2Frenting-empresas-largo-plazo&lang=es_ES"
    
    r = requests.get(url_empresas, headers=headers)
    print(f"Status: {r.status_code}")
    
    data = r.json()
    print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
    
    with open("arval_api.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\nGuardado en arval_api.json")

scrape_arval()
