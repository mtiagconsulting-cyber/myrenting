import json, re, shutil
from datetime import datetime
from pathlib import Path

BASE = Path("/Users/matthiasthomassen/Documents/Myrenting")
JSON_PATH = BASE / "ofertas_para_html.json"
HTML_PATH = BASE / "index.html"
BACKUP_PATH = BASE / f"index_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

shutil.copy2(HTML_PATH, BACKUP_PATH)
print(f"Backup: {BACKUP_PATH.name}")

with open(JSON_PATH, "r", encoding="utf-8") as f:
    ofertas = json.load(f)
print(f"Ofertas: {len(ofertas)}")

json_str = json.dumps(ofertas, ensure_ascii=False, separators=(",", ":"))
html = HTML_PATH.read_text(encoding="utf-8")
patron = r'(const _OFERTAS\s*=\s*)\[.*?\];'
html_nuevo, n = re.subn(patron, rf'\g<1>{json_str};', html, count=1, flags=re.DOTALL)

if n == 0:
    print("ERROR: No se encontro _OFERTAS en el HTML")
else:
    HTML_PATH.write_text(html_nuevo, encoding="utf-8")
    print(f"OK: index.html actualizado con {len(ofertas)} ofertas")
