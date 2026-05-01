#!/usr/bin/env python3
"""
deploy_legal.py
Sube index.html + páginas legales al repo mtiagconsulting-cyber/myrenting (rama main)
Uso: python3 deploy_legal.py
"""

import subprocess
import sys
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────────────────────
REPO_DIR   = Path("/Users/matthiasthomassen/Documents/Myrenting")
RAMA       = "main"

# Archivos a subir (deben estar en REPO_DIR)
ARCHIVOS = [
    "index.html",
    "aviso-legal.html",
    "politica-privacidad.html",
    "politica-cookies.html",
]
# ──────────────────────────────────────────────────────────────────────────────


def run(cmd: list[str], cwd: Path) -> str:
    """Ejecuta un comando y devuelve stdout. Lanza excepción si falla."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def check_archivos():
    """Verifica que todos los archivos existen antes de hacer nada."""
    faltantes = [f for f in ARCHIVOS if not (REPO_DIR / f).exists()]
    if faltantes:
        print("❌ Archivos no encontrados en", REPO_DIR)
        for f in faltantes:
            print(f"   · {f}")
        print("\n👉 Copia los archivos generados al directorio del proyecto y vuelve a ejecutar.")
        sys.exit(1)
    print(f"✓ {len(ARCHIVOS)} archivos encontrados")


def git_status():
    """Muestra un resumen del estado actual del repo."""
    out = run(["git", "status", "--short"], REPO_DIR)
    return out


def deploy():
    print("=" * 55)
    print("  MiRenting · Deploy páginas legales → GitHub")
    print("=" * 55)
    print(f"  Repo:  {REPO_DIR}")
    print(f"  Rama:  {RAMA}")
    print(f"  Files: {', '.join(ARCHIVOS)}")
    print("=" * 55)

    # 1. Verificar archivos
    check_archivos()

    # 2. Verificar que es un repo git válido
    try:
        run(["git", "rev-parse", "--git-dir"], REPO_DIR)
    except RuntimeError:
        print(f"❌ {REPO_DIR} no es un repositorio Git.")
        sys.exit(1)

    # 3. Asegurarse de estar en la rama correcta
    rama_actual = run(["git", "branch", "--show-current"], REPO_DIR)
    if rama_actual != RAMA:
        print(f"⚠️  Rama actual: '{rama_actual}'. Cambiando a '{RAMA}'...")
        run(["git", "checkout", RAMA], REPO_DIR)
        print(f"✓ En rama '{RAMA}'")
    else:
        print(f"✓ Rama correcta: '{RAMA}'")

    # 4. Pull para evitar conflictos
    print("↓ git pull...")
    try:
        out = run(["git", "pull", "origin", RAMA], REPO_DIR)
        print(f"  {out.splitlines()[0] if out else 'Already up to date.'}")
    except RuntimeError as e:
        print(f"⚠️  Pull con advertencia: {e}")

    # 5. git add de los archivos legales
    print(f"\n+ git add {' '.join(ARCHIVOS)}")
    run(["git", "add"] + ARCHIVOS, REPO_DIR)

    # 6. Comprobar si hay cambios reales para commitear
    status = run(["git", "diff", "--cached", "--name-only"], REPO_DIR)
    if not status:
        print("\n✅ Sin cambios nuevos que subir. Todo ya está actualizado en GitHub.")
        return

    print("  Archivos en el commit:")
    for f in status.splitlines():
        print(f"    · {f}")

    # 7. Commit
    mensaje = "feat: añadir páginas legales (Aviso Legal, Privacidad, Cookies) y actualizar footer/banner index.html"
    print(f"\n● git commit: \"{mensaje}\"")
    run(["git", "commit", "-m", mensaje], REPO_DIR)
    print("✓ Commit creado")

    # 8. Push
    print(f"↑ git push origin {RAMA}...")
    out = run(["git", "push", "origin", RAMA], REPO_DIR)
    print("✓ Push completado")

    # 9. Resumen final
    ultimo_commit = run(["git", "log", "--oneline", "-1"], REPO_DIR)
    print("\n" + "=" * 55)
    print("  ✅ Deploy completado con éxito")
    print(f"  Commit: {ultimo_commit}")
    print(f"  URL:    https://github.com/mtiagconsulting-cyber/myrenting")
    print("=" * 55)


if __name__ == "__main__":
    try:
        deploy()
    except RuntimeError as e:
        print(f"\n❌ Error Git: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️  Cancelado por el usuario.")
        sys.exit(0)
