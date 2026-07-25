"""
chain.py — Cadena LCEL con salida estructurada y resiliencia.

Compone: ChatPromptTemplate | ChatOpenAI.with_structured_output() | .with_retry()
Expone: process_text(text) para ejecución asíncrona.
"""

import logging
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from schemas import EntityExtraction

# Cargar variables de entorno
load_dotenv()

# Configuración de logging para observar el flujo de validación y reintentos
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def build_chain():
    """
    Construye la cadena LCEL completa con salida estructurada y resiliencia.

    Componentes:
    1. ChatPromptTemplate: Instrucciones para extraer entidades técnicas.
    2. ChatOpenAI + .with_structured_output(): Fuerza salida Pydantic validada.
    3. .with_retry(): Reintento automático ante errores transitorios o JSON mal formado.
    """

    # --- Componente 1: Prompt con roles definidos ---
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un analista experto en arquitectura de software e infraestructura. "
            "Tu tarea es extraer entidades técnicas de un texto proporcionado. "
            "Debes identificar las tecnologías mencionadas, evaluar el nivel de "
            "criticidad del escenario descrito y generar un resumen técnico conciso. "
            "Para el nivel de criticidad, usa exclusivamente: 'baja', 'media' o 'alta'."
        ),
        (
            "human",
            "{texto}"
        ),
    ])

    # --- Componente 2: Modelo con salida estructurada ---
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )

    # .with_structured_output() fuerza al modelo a devolver un objeto Pydantic válido
    structured_model = model.with_structured_output(EntityExtraction)

    # --- Componente 3: Resiliencia con reintentos ---
    # Reintenta hasta 3 veces con backoff exponencial ante errores de red o rate limits
    resilient_model = structured_model.with_retry(
        stop_after_attempt=3,
        wait_exponential_jitter=True,
    )

    # --- Composición LCEL ---
    chain = prompt | resilient_model

    return chain


async def process_text(text: str) -> EntityExtraction:
    """
    Ejecuta la cadena LCEL de forma asíncrona y devuelve un objeto validado.

    Args:
        text: Párrafo de texto sin procesar (descripción técnica o log de error).

    Returns:
        EntityExtraction: Objeto Pydantic validado con las entidades extraídas.
    """
    logger.info("Iniciando extracción de entidades...")
    logger.info("Texto de entrada: %s", text[:80] + "..." if len(text) > 80 else text)

    chain = build_chain()

    # Ejecución asíncrona
    result = await chain.ainvoke({"texto": text})

    # Log de validación exitosa
    logger.info("Extracción completada exitosamente.")
    logger.info("Tecnologías detectadas: %s", result.tecnologias)
    logger.info("Nivel de criticidad: %s", result.nivel_de_criticidad)
    logger.info("Resumen: %s", result.resumen_tecnico)

    return result
