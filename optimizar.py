import os

# Ruta a tu archivo HTML
HTML_PATH = '/Users/matthiasthomassen/Documents/Myrenting/index.html'

def aplicar_mejoras():
    if not os.path.exists(HTML_PATH):
        print(f"Error: No se encuentra el archivo en {HTML_PATH}")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Optimizar ALT de imágenes
    old_img = '<img src="${c.image}"'
    new_img = '<img src="${c.image}" alt="Renting de ${c.make} ${c.model} - Oferta MiRenting"'
    if old_img in content:
        content = content.replace(old_img, new_img)
        print("- Alts de imágenes optimizados.")

    # 2. Inyectar SEO Footer (solo si no existe ya)
    seo_footer = """
        <div class="footer-links-col">
          <h4>Categorías Populares</h4>
          <a href="#modelos" onclick="document.getElementById('search-text').value='SUV'; applyFilters();">Renting de SUV</a>
          <a href="#modelos" onclick="document.getElementById('search-text').value='Híbrido'; applyFilters();">Renting Eco/Híbrido</a>
          <a href="#modelos" onclick="document.getElementById('filter-cuota').value='300'; applyFilters();">Renting menos de 300€</a>
        </div>"""
    
    if 'Categorías Populares' not in content and '<div class="footer-links-col">' in content:
        content = content.replace('<div class="footer-links-col">', seo_footer + '\n        <div class="footer-links-col">', 1)
        print("- Footer SEO inyectado.")

    # 3. Mejora de Calculadora
    old_calc = 'const totalRenting = cuota * duracion;'
    new_calc = """const totalRenting = cuota * duracion;
        const ahorroFiscal = perfil === 'autonomo' ? (totalRenting * 0.21) : 0;
        const ahorroMantenimiento = (duracion / 12) * 600;
        const ahorroTotalEfectivo = ahorroFiscal + ahorroMantenimiento;"""
    
    if old_calc in content and 'ahorroFiscal' not in content:
        content = content.replace(old_calc, new_calc)
        print("- Lógica de calculadora mejorada.")

    # 4. Meta Description
    if 'content="Compara más de 900 ofertas' in content:
        content = content.replace('content="Compara más de 900 ofertas', 'content="Ofertas de Renting desde 199€/mes. Compara +900 coches')
        print("- Meta description actualizada.")

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ ¡Proceso completado con éxito!")

if __name__ == "__main__":
    aplicar_mejoras()