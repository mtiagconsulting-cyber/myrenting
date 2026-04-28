import json
from bs4 import BeautifulSoup

with open("arval_debug.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
script = soup.find("script", {"id": "__NEXT_DATA__"})

if script:
    data = json.loads(script.string)
    ofertas = data["props"]["pageProps"]["__TEMPLATE_QUERY_DATA__"]["page"]["blocksJSON"]
    blocks = json.loads(ofertas)
    
    for block in blocks:
        if block.get("name") == "octopus/overview":
            offer_list = block["attributes"]["offers"]["offerSummaries"]
            print(f"Ofertas encontradas: {len(offer_list)}")
            for o in offer_list[:3]:
                print(f"  {o['makeName']} {o['modelName']} - {o['priceGridRental']}€/mes - {o['fuelTypeName']} - {o['duration']}m")
            
            with open("arval_ofertas.json", "w", encoding="utf-8") as f:
                json.dump(offer_list, f, ensure_ascii=False, indent=2)
            print("\nGuardado en arval_ofertas.json")
else:
    print("No encontrado")
