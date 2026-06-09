#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de sitemap.xml y robots.txt — ZONA FOTOGRAFIA (zonafotografia.com)

Recorre la carpeta del sitio, busca TODOS los archivos .html y genera un
sitemap.xml correcto, mas el robots.txt. No hay que editar nada a mano.

USO (doble clic, o desde la carpeta del proyecto):
    python generar_sitemap.py

No requiere instalar nada extra: solo Python (ya instalado).
"""

import os
import datetime

# ---------------------------------------------------------------------------
# CONFIGURACION (lo unico que podrias necesitar tocar algun dia)
# ---------------------------------------------------------------------------
DOMINIO = "https://zonafotografia.com"

# Idiomas alternativos que se anaden a cada URL (hreflang)
IDIOMAS = ["es", "en"]

# Archivos .html que NO deben aparecer en el sitemap (plantillas, borradores...)
EXCLUIR = {"404.html", "google.html"}

# Prioridad y frecuencia segun el archivo. Si no esta en la lista, usa POR_DEFECTO.
REGLAS = {
    "index.html":      (1.0, "monthly"),
    "privacidad.html": (0.3, "yearly"),
}
POR_DEFECTO = (0.8, "monthly")

# ---------------------------------------------------------------------------
# No suele hacer falta tocar nada por debajo de esta linea
# ---------------------------------------------------------------------------
RAIZ = os.path.dirname(os.path.abspath(__file__))


def fecha_modificacion(ruta):
    """Devuelve la fecha de ultima modificacion del archivo (AAAA-MM-DD)."""
    ts = os.path.getmtime(ruta)
    return datetime.date.fromtimestamp(ts).isoformat()


def buscar_htmls():
    """Lista todas las rutas relativas .html, con '/' como separador."""
    encontrados = []
    for carpeta, _subcarpetas, archivos in os.walk(RAIZ):
        # Ignorar carpetas internas que no son web
        if ".git" in carpeta or "\\." in carpeta.replace(RAIZ, ""):
            continue
        for nombre in archivos:
            if nombre.lower().endswith(".html") and nombre not in EXCLUIR:
                completa = os.path.join(carpeta, nombre)
                rel = os.path.relpath(completa, RAIZ).replace("\\", "/")
                encontrados.append((rel, completa))
    return encontrados


def url_publica(rel):
    """Convierte 'index.html' en '/' y el resto en '/ruta.html'."""
    if rel == "index.html":
        return DOMINIO + "/"
    return DOMINIO + "/" + rel


def orden(rel):
    """index primero, luego alfabetico."""
    return (0 if rel == "index.html" else 1, rel)


def construir_sitemap(paginas):
    lineas = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
        '',
    ]
    for rel, completa in sorted(paginas, key=lambda x: orden(x[0])):
        loc = url_publica(rel)
        prioridad, frecuencia = REGLAS.get(rel, POR_DEFECTO)
        lineas.append('  <url>')
        lineas.append(f'    <loc>{loc}</loc>')
        lineas.append(f'    <lastmod>{fecha_modificacion(completa)}</lastmod>')
        lineas.append(f'    <changefreq>{frecuencia}</changefreq>')
        lineas.append(f'    <priority>{prioridad}</priority>')
        for idioma in IDIOMAS:
            lineas.append(
                f'    <xhtml:link rel="alternate" hreflang="{idioma}" href="{loc}"/>'
            )
        lineas.append('  </url>')
        lineas.append('')
    lineas.append('</urlset>')
    return "\n".join(lineas) + "\n"


def construir_robots():
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "\n"
        f"Sitemap: {DOMINIO}/sitemap.xml\n"
    )


def main():
    paginas = buscar_htmls()
    sitemap = construir_sitemap(paginas)
    robots = construir_robots()

    with open(os.path.join(RAIZ, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap)
    with open(os.path.join(RAIZ, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots)

    print("OK - ZONA FOTOGRAFIA")
    print(f"  Paginas incluidas en el sitemap: {len(paginas)}")
    for rel, _ in sorted(paginas, key=lambda x: orden(x[0])):
        print(f"    - {url_publica(rel)}")
    print("  Archivos actualizados: sitemap.xml, robots.txt")
    print("\nAhora sube los cambios a GitHub (o pideselo a Cline).")


if __name__ == "__main__":
    main()
