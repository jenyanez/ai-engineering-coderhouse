"""
Módulo 2 - Tarea: Refactorización a LCEL Asíncrono

Migración de la implementación imperativa (SDKs crudos del Módulo 1)
a una arquitectura declarativa usando LCEL (LangChain Expression Language).

Flujo: Input (dict) → ChatPromptTemplate → ChatOpenAI → StrOutputParser → str
"""

import asyncio
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Cargar variables de entorno desde .env
load_dotenv()


def build_chain():
    """
    Construye la cadena LCEL completa usando el operador pipe (|).

    Componentes:
    1. ChatPromptTemplate: Define los roles (system/human) y las variables de entrada.
    2. ChatOpenAI: Modelo de lenguaje configurado con gpt-4o-mini.
    3. StrOutputParser: Extrae el texto plano de la respuesta del modelo.
    """

    # --- Componente 1: Prompt con roles definidos ---
    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Eres un asistente experto en tecnología e ingeniería de software. "
            "Responde de forma clara, concisa y profesional."
        ),
        (
            "human",
            "{pregunta}"
        ),
    ])

    # --- Componente 2: Modelo de LangChain (reemplaza el SDK crudo del Módulo 1) ---
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
    )

    # --- Componente 3: Parser de salida ---
    parser = StrOutputParser()

    # --- Composición LCEL: prompt | model | parser ---
    chain = prompt | model | parser

    return chain


async def process_question(question: str) -> str:
    """
    Ejecuta la cadena LCEL de forma asíncrona.

    Args:
        question: La pregunta del usuario como texto.

    Returns:
        La respuesta del modelo como texto plano (str).
    """
    chain = build_chain()

    # Ejecución asíncrona con ainvoke
    result = await chain.ainvoke({"pregunta": question})

    return result


async def main():
    """Punto de entrada principal del programa."""

    print("=" * 60)
    print("Módulo 2 - Refactorización a LCEL Asíncrono")
    print("=" * 60)

    # Pregunta de ejemplo
    question = "¿Qué es LCEL en LangChain y cuáles son sus ventajas principales?"

    print(f"\nPregunta: {question}")
    print("-" * 60)

    try:
        response = await process_question(question)
        print(f"\nRespuesta:\n{response}")
    except Exception as e:
        print(f"\nError al ejecutar la cadena: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print("Ejecución finalizada.")


if __name__ == "__main__":
    asyncio.run(main())
