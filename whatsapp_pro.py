import os

HTML_PATH = '/Users/matthiasthomassen/Documents/Myrenting/index.html'
TU_TELEFONO = "34691766768"  # 👈 CAMBIA ESTO (Pon 34 + tu número sin espacios)

def inyectar_whatsapp():
    if not os.path.exists(HTML_PATH):
        print("❌ No se encuentra index.html")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Buscamos el botón de contacto en tu JavaScript
    # Tu código actual usa: <button class="btn-comparar" ...>Contactar</button>
    
    nuevo_boton = f"""<a href="https://wa.me/{TU_TELEFONO}?text=Hola!%20He%20visto%20el%20${{m.marca}}%20${{m.modelo}}%20en%20MiRenting%20y%20me%20gustaría%20información." 
           target="_blank" 
           class="btn-comparar" 
           style="background:#25D366; text-decoration:none; display:inline-block; text-align:center;">
           WhatsApp
        </a>"""

    # Localizamos el punto donde se genera el botón de contacto
    # Nota: He ajustado la búsqueda para que coincida con tu estructura de tarjetas
    old_btn = 'Contactar'
    
    if old_btn in content and 'wa.me' not in content:
        # Reemplazamos el texto del botón por la lógica de WhatsApp
        # Buscamos la etiqueta <button> que rodea a 'Contactar'
        content = content.replace('>Contactar</button>', f'>{nuevo_boton}')
        print("✅ Botones convertidos a WhatsApp dinámico.")
    else:
        print("⚠️ El botón ya es de WhatsApp o no se encontró el texto 'Contactar'.")

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    inyectar_whatsapp()