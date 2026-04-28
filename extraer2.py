import json
from bs4 import BeautifulSoup

with open("arval_debug.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
script = soup.find("script", {"id": "__NEXT_DATA__"})
data = json.loads(script.string)

offers = data["props"]["pageProps"]["__TEMPLATE_QUERY_DATA__"]["page"]["blocksJSON"]
print(type(offers))
print(str(offers)[:200])
