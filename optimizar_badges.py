import os

HTML_PATH = '/Users/matthiasthomassen/Documents/Myrenting/index.html'

def aplicar_super_badges():
    if not os.path.exists(HTML_PATH):
        print("❌ Error: No encuentro el archivo index.html")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Definimos la lógica de las etiquetas
    # Esta lógica se insertará justo antes de que se cree el HTML de la tarjeta
    logica_badges = """
        // --- Lógica de Badges Dinámicos ---
        let badgeHtml = '';
        const precioNum = parseFloat(m.precio_desde);
        const fuelLower = m.fuel.toLowerCase();

        if (precioNum < 260) {
            badgeHtml = '<span class="fuel-badge" style="background:#e0faf1; color:#00c47a; border-color:#00c47a; font-weight:800; margin-right:5px;">🔥 CHOLLO</span>';
        } else if (fuelLower.includes('eléctrico') || fuelLower.includes('híbrido') || fuelLower.includes('eco')) {
            badgeHtml = '<span class="fuel-badge" style="background:#eff6ff; color:#1e40af; border-color:#bfdbfe; font-weight:800; margin-right:5px;">🍃 ECO</span>';
        } else if (precioNum > 600) {
            badgeHtml = '<span class="fuel-badge" style="background:#fef3c7; color:#92400e; border-color:#fcd34d; font-weight:800; margin-right:5px;">⭐ PREMIUM</span>';
        }
        // --- Fin Lógica ---
    """

    # 2. Buscamos el punto de inyección en tu JS
    # Buscamos donde empieza el template literal de la card
    punto_busqueda = "const card = `"
    
    if punto_busqueda in content and 'badgeHtml' not in content:
        # Insertamos la lógica justo antes de la definición de 'card'
        content = content.replace(punto_busqueda, logica_badges + "\n        const card = `")
        
        # 3. Insertamos el badge dentro del HTML de la meta-información
        # Buscamos <div class="model-meta"> y le pegamos el ${badgeHtml}
        content = content.replace('<div class="model-meta">', '<div class="model-meta">${badgeHtml}')
        
        print("✅ Lógica de etiquetas (CHOLLO/ECO) inyectada correctamente.")
    else:
        print("⚠️ El script ya estaba aplicado o no se encontró el punto exacto.")

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    aplicar_super_badges()