"""
schemas.py — Contratos de datos Pydantic para el sistema RAG.

Define dos modelos:
- RespuestaLLM: lo que el LLM genera (parseado por PydanticOutputParser).
- RAGResponse: objeto final que combina la respuesta del LLM con metadata verificable.
"""

from typing import List

from pydantic import BaseModel, Field


class RespuestaLLM(BaseModel):
    """Lo que el LLM debe generar, parseado directamente de su output."""

    respuesta: str = Field(
        description=(
            "Respuesta a la pregunta del usuario, basada EXCLUSIVAMENTE "
            "en el CONTEXTO. Si la información no está en el contexto, "
            "decir explícitamente que no se cuenta con esa información."
        ),
    )


class RAGResponse(BaseModel):
    """
    Objeto final que devuelve get_rag_response.

    Combina el output del LLM con metadata verificable extraída
    de los metadatos reales de los documentos recuperados
    (no generada por el LLM, para evitar alucinación de fuentes).
    """

    respuesta: str = Field(
        description="Texto de la respuesta generada por el LLM.",
    )
    fuentes: List[str] = Field(
        description="Archivos de origen de los fragmentos usados como contexto.",
    )
    fragmentos_recuperados: int = Field(
        description="Cantidad de fragmentos recuperados del vectorstore.",
    )
