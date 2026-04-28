import json
from bs4 import BeautifulSoup

with open("arval_debug.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
script = soup.find("script", {"id": "__NEXT_DATA__"})
data = json.loads(script.string)

def buscar_ofertas(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "offerSummaries":
                print(f"ENCONTRADO en: {path}.{k}")
                print(f"Total ofertas: {len(v)}")
                for o in v[:3]:
                    print(f"  {o.get('makeName')} {o.get('modelName')} - {o.get('priceGridRental')}€")
                with open("arval_ofertas.json", "w") as f:
                    json.dump(v, f, ensure_ascii=False, indent=2)
                print("Guardado en arval_ofertas.json")
                return
            buscar_ofertas(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            buscar_ofertas(v, f"{path}[{i}]")

buscar_ofertas(data)
