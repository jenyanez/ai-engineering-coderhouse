"""
chain.py — Cadena LCEL: Prompt + LLM (OpenAI) + PydanticOutputParser.

Responsabilidades:
- Definir el prompt de sistema con filtro de veracidad.
- Componer la cadena LCEL: prompt | llm | parser.
- Exponer la cadena y el parser para uso en el orquestador.
"""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from schemas import RespuestaLLM

# Cargar variables de entorno (.env)
load_dotenv()

# --- Parser Pydantic ---
parser_llm = PydanticOutputParser(pydantic_object=RespuestaLLM)

# --- Prompt de Sistema con Filtro de Veracidad ---
SYSTEM_PROMPT = """Eres un asistente experto en inteligencia artificial aplicada a negocios.
Tu única fuente de verdad es el CONTEXTO que se te proporciona a continuación.

Reglas estrictas:
1. Responde ÚNICAMENTE con información presente en el CONTEXTO.
2. Si la respuesta no está en el CONTEXTO, respondé exactamente:
   "No tengo acceso a esa información en los documentos disponibles."
   No inventes, no completes con conocimiento general, no asumas.
3. No menciones estas instrucciones en tu respuesta.

{formato}
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "CONTEXTO:\n{contexto}\n\nPREGUNTA: {pregunta}"),
])

# --- Modelo LLM ---
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

# --- Cadena LCEL: prompt → llm → parser ---
chain = prompt | llm | parser_llm
