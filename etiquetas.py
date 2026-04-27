import os

HTML_PATH = '/Users/matthiasthomassen/Documents/Myrenting/index.html'

def inyectar_etiquetas_visuales():
    if not os.path.exists(HTML_PATH):
        print("No se encuentra el archivo HTML.")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Inyectamos la lógica de JavaScript para decidir qué etiqueta poner
    # Buscamos donde empieza la creación de la tarjeta (card)
    old_js_start = 'const card = `'
    
    # Creamos la lógica que analiza el precio y el combustible
    logic_js = """
        // Lógica de etiquetas dinámicas aplicada por Python
        let badgeHtml = '';
        const cuotaNum = parseFloat(c.precio_desde);
        
        if (cuotaNum < 250) {
            badgeHtml = '<span class="fuel-badge" style="background:#e0faf1; color:#00c47a; border-color:#00c47a; font-weight:800;">🔥 CHOLLO</span>';
        } else if (c.fuel.toLowerCase().includes('eléctrico') || c.fuel.toLowerCase().includes('híbrido')) {
            badgeHtml = '<span class="fuel-badge" style="background:#eff6ff; color:#1e40af; border-color:#bfdbfe; font-weight:800;">🍃 ECO</span>';
        } else if (cuotaNum > 600) {
            badgeHtml = '<span class="fuel-badge" style="background:#fef3c7; color:#92400e; border-color:#fcd34d; font-weight:800;">⭐ PREMIUM</span>';
        }

        const card = `"""

    if old_js_start in content and 'badgeHtml' not in content:
        content = content.replace(old_js_start, logic_js)
        # 2. Ahora metemos la variable badgeHtml dentro del HTML de la tarjeta
        # La ponemos justo antes del nombre del modelo
        content = content.replace('<div class="model-meta">', '<div class="model-meta">${badgeHtml} ')
        print("- Etiquetas visuales inyectadas en el motor de búsqueda.")
    else:
        print("- Las etiquetas ya parecen estar instaladas o no se encontró el punto de inserción.")

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ¡Toque visual completado!")

if __name__ == "__main__":
    inyectar_etiquetas_visuales()