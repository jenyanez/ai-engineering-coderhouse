"""
schemas.py — Contrato de datos Pydantic para la extracción de entidades técnicas.

Define la estructura validada que el LLM debe devolver,
garantizando integridad de tipos y reglas de negocio.
"""

from typing import List, Literal

from pydantic import BaseModel, Field


class EntityExtraction(BaseModel):
    """
    Esquema de salida para la extracción de entidades técnicas.

    El LLM debe poblar cada campo a partir del análisis
    de un párrafo de texto sin procesar.
    """

    tecnologias: List[str] = Field(
        ...,
        min_length=1,
        description=(
            "Lista de tecnologías, frameworks, lenguajes o herramientas "
            "mencionadas en el texto. No puede estar vacía."
        ),
    )

    nivel_de_criticidad: Literal["baja", "media", "alta"] = Field(
        ...,
        description=(
            "Nivel de criticidad del escenario descrito. "
            "Valores permitidos: 'baja', 'media' o 'alta'."
        ),
    )

    resumen_tecnico: str = Field(
        ...,
        min_length=10,
        description=(
            "Resumen técnico conciso (1-2 oraciones) que capture "
            "el problema o la arquitectura descrita en el texto."
        ),
    )
