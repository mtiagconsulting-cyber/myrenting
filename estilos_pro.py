import os

HTML_PATH = '/Users/matthiasthomassen/Documents/Myrenting/index.html'

def aplicar_estilos_mejorados():
    if not os.path.exists(HTML_PATH):
        print("❌ Archivo no encontrado.")
        return

    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Definimos el nuevo look de las etiquetas
    nuevos_estilos = """
    /* --- Estilos de Badges Mejorados por Python --- */
    .fuel-badge {
        font-size: .75rem !important;
        font-weight: 800 !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        border: 1px solid transparent !important;
    }
    /* Si el texto es Económico, le damos look de CHOLLO */
    .fuel-badge:contains("Económico"), 
    .fuel-badge:contains("ECONÓMICO") {
        background: #e0faf1 !important;
        color: #00c47a !important;
        border-color: #00c47a !important;
    }
    /* Estilo general para resaltar */
    .model-card:hover .fuel-badge {
        transform: scale(1.05);
        transition: transform 0.2s;
    }
    """

    if '</style>' in content and '/* --- Estilos de Badges' not in content:
        content = content.replace('</style>', nuevos_estilos + '\n  </style>')
        print("✅ Estilos visuales inyectados en el CSS.")
    else:
        print("⚠️ Los estilos ya están o no se encontró la etiqueta style.")

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    aplicar_estilos_mejorados()