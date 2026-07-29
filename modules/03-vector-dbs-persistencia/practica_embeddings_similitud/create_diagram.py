"""
create_diagram.py — Generador de diagrama de arquitectura minimalista de grado profesional.

Diseño neutro, elegante y técnico (estilo arquitectura de software / sistemas distribuidos).
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def generate_flow_diagram(output_filename: str = "diagrama_busqueda_semantica.png"):
    # Configuración de lienzo limpia con proporciones de arquitectura
    fig, ax = plt.subplots(figsize=(11, 4.8), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.8)
    ax.axis("off")

    # Encabezado Minimalista
    ax.text(
        0.5, 4.3,
        "PIPELINE DE BÚSQUEDA SEMÁNTICA & RECUPERACIÓN VEC (RAG)",
        ha="left", va="center", fontsize=11, fontweight="bold", color="#09090B", fontfamily="sans-serif"
    )
    ax.text(
        0.5, 4.0,
        "Arquitectura de flujo de datos: desde la consulta en lenguaje natural hasta la recuperación ponderada",
        ha="left", va="center", fontsize=8.5, color="#71717A", fontfamily="sans-serif"
    )

    # Línea divisoria superior
    ax.plot([0.5, 10.5], [3.8, 3.8], color="#E4E4E7", linewidth=1)

    # Definición de Nodos del Pipeline (Minimalista Neutral)
    nodes = [
        {
            "x": 0.5, "y": 1.6, "w": 1.7, "h": 1.7,
            "tag": "INPUT", "title": "1. Query Usuario",
            "desc": "Consulta en texto\nsin procesar\n(Lenguaje Natural)",
            "sub": "Ej. 'Despliegue de...'"
        },
        {
            "x": 2.5, "y": 1.6, "w": 1.8, "h": 1.7,
            "tag": "EMBEDDING", "title": "2. Modelo Vectorial",
            "desc": "Codificación densa\nOpenAI / Voyage\nDimensiones: 1536",
            "sub": "Vq ∈ ℝ¹⁵³⁶"
        },
        {
            "x": 4.6, "y": 1.6, "w": 1.8, "h": 1.7,
            "tag": "RETRIEVAL", "title": "3. Índice HNSW",
            "desc": "Búsqueda ANN por\ngrafo jerárquico en\nVector DB",
            "sub": "O(log N) Complejidad"
        },
        {
            "x": 6.7, "y": 1.6, "w": 1.8, "h": 1.7,
            "tag": "SCORING", "title": "4. Similitud Coseno",
            "desc": "Evaluación con\nscikit-learn\ncos(θ) = Q·D / ||Q||||D||",
            "sub": "Métrica de Orientación"
        },
        {
            "x": 8.8, "y": 1.6, "w": 1.7, "h": 1.7,
            "tag": "OUTPUT", "title": "5. Top-K Chunks",
            "desc": "Documentos de\nalta relevancia\nrecuperados",
            "sub": "Contexto para LLM"
        },
    ]

    # Dibujar Nodos Minimalistas
    for node in nodes:
        # Caja Principal
        rect = patches.FancyBboxPatch(
            (node["x"], node["y"]), node["w"], node["h"],
            boxstyle="round,pad=0,rounding_size=0.08",
            facecolor="#FAFAFA", edgecolor="#D4D4D8", linewidth=1.2
        )
        ax.add_patch(rect)

        # Etiqueta Superior (Pill Tag)
        tag_rect = patches.FancyBboxPatch(
            (node["x"] + 0.1, node["y"] + node["h"] - 0.32), node["w"] - 0.2, 0.24,
            boxstyle="round,pad=0,rounding_size=0.04",
            facecolor="#F4F4F5", edgecolor="#E4E4E7", linewidth=0.8
        )
        ax.add_patch(tag_rect)
        ax.text(
            node["x"] + node["w"]/2, node["y"] + node["h"] - 0.20,
            node["tag"], ha="center", va="center", fontsize=6.5, fontweight="bold", color="#71717A"
        )

        # Título
        ax.text(
            node["x"] + node["w"]/2, node["y"] + node["h"] - 0.55,
            node["title"], ha="center", va="center", fontsize=8.5, fontweight="bold", color="#09090B"
        )

        # Descripción
        ax.text(
            node["x"] + node["w"]/2, node["y"] + 0.65,
            node["desc"], ha="center", va="center", fontsize=7.5, color="#3F3F46", linespacing=1.2
        )

        # Subtexto Técnico
        ax.text(
            node["x"] + node["w"]/2, node["y"] + 0.2,
            node["sub"], ha="center", va="center", fontsize=6.5, fontweight="bold", color="#2563EB"
        )

    # Conectores Elegantes (Flechas entre Nodos)
    arrow_style = dict(arrowstyle="-|>", mutation_scale=12, lw=1.2, color="#71717A")

    ax.annotate("", xy=(2.45, 2.45), xytext=(2.25, 2.45), arrowprops=arrow_style)
    ax.annotate("", xy=(4.55, 2.45), xytext=(4.35, 2.45), arrowprops=arrow_style)
    ax.annotate("", xy=(6.65, 2.45), xytext=(6.45, 2.45), arrowprops=arrow_style)
    ax.annotate("", xy=(8.75, 2.45), xytext=(8.55, 2.45), arrowprops=arrow_style)

    # Pie de página técnico minimalista
    ax.plot([0.5, 10.5], [0.8, 0.8], color="#E4E4E7", linewidth=0.8)
    ax.text(
        0.5, 0.45,
        "Especificación Técnica: Vector Space Model (VSM) | Métrica: Cosine Distance | Framework: scikit-learn",
        ha="left", va="center", fontsize=7.5, color="#71717A"
    )

    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_filename)
    plt.savefig(output_path, bbox_inches="tight", dpi=300, facecolor="#FFFFFF")
    plt.close()
    return output_path


if __name__ == "__main__":
    img_path = generate_flow_diagram()
    print(f"✅ Diagrama de arquitectura minimalista generado en: {img_path}")
