from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """
    Estructura validada de un mensaje de chat.
    """

    role: Literal["system", "user", "assistant"] = Field(
        ..., description="El rol del emisor del mensaje."
    )
    content: str = Field(..., description="El contenido de texto del mensaje.")


class ModelConfig(BaseModel):
    """
    Configuración base validada para cualquier modelo de lenguaje.
    """

    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Grado de aleatoriedad del modelo (0.0 a 2.0).",
    )
    max_tokens: int = Field(
        default=1024,
        gt=0,
        le=4096,
        description="Límite máximo de tokens a generar.",
    )
    top_p: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Límite de tokens considerados mediante nucleus sampling.",
    )


class ModelResponse(BaseModel):
    """
    Respuesta unificada de cualquier proveedor de modelo.
    """

    content: str = Field(..., description="El texto generado por el LLM.")
    provider: str = Field(..., description="El proveedor que generó la respuesta.")
    model_used: str = Field(..., description="El nombre exacto del modelo usado.")
    finish_reason: Optional[str] = Field(
        default=None, description="La razón por la que se detuvo la generación."
    )
