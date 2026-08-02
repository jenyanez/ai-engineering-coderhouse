# Pre-entrega 3: Sistema de Recuperación Semántica Local (RAG)

Sistema RAG (Retrieval-Augmented Generation) End-to-End que integra memoria vectorial local con generación fundamentada. El sistema recibe consultas sobre **IA aplicada a negocios**, busca información relevante en una base vectorial ChromaDB y genera respuestas basadas exclusivamente en el contexto recuperado.

## Arquitectura

```
Pregunta → Retriever (ChromaDB) → Fragmentos relevantes (k=4)
                                          ↓
                           ChatPromptTemplate (filtro de veracidad)
                                          ↓
                              ChatOpenAI (gpt-4o-mini)
                                          ↓
                           PydanticOutputParser → RAGResponse
```

## Estructura del Código

```
pre_entrega_03/
├── data/                              # Dataset: IA aplicada a negocios
│   ├── estrategia_ia_ventas.txt       # Lead scoring, personalización, chatbots
│   ├── automatizacion_procesos.txt    # IDP, atención al cliente, supply chain
│   ├── analitica_predictiva_negocios.txt  # Churn, pricing, riesgo crediticio
│   └── etica_ia_empresarial.txt       # Sesgo, transparencia, gobernanza
├── schemas.py                         # Modelos Pydantic (RespuestaLLM, RAGResponse)
├── ingesta.py                         # Carga + chunking + ChromaDB persistente
├── retriever.py                       # Recuperación semántica (similarity, k=4)
├── chain.py                           # Cadena LCEL: prompt → LLM → parser
├── main.py                            # Orquestador: get_rag_response() + pruebas
├── .env.example                       # Template de variables de entorno
├── .gitignore                         # Excluye .env, vectorstore/, .venv/
└── requirements.txt                   # Dependencias del proyecto
```

## Ejemplo de Salida

```json
{
  "respuesta": "La IA ayuda a predecir el churn mediante modelos de clasificación binaria como XGBoost y LightGBM, que combinan variables transaccionales con datos de comportamiento...",
  "fuentes": ["data/analitica_predictiva_negocios.txt"],
  "fragmentos_recuperados": 4
}
```

## Ejecución

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env y agregar tu API key de OpenAI

# 4. Ejecutar (ingesta + pruebas automáticas)
python main.py
```

## Decisiones Técnicas

| Componente | Decisión | Razón |
|---|---|---|
| **Embeddings** | HuggingFace `all-MiniLM-L6-v2` | Local, gratuito, mismo modelo para indexar y consultar |
| **Vector DB** | ChromaDB persistente | Prototipado local sin latencia de red |
| **Chunking** | 500 tokens / 50 overlap (tiktoken) | Medido en tokens reales del modelo, no caracteres |
| **LLM** | OpenAI `gpt-4o-mini` | Balance costo/calidad para generación |
| **Validación** | PydanticOutputParser | Salida estructurada con tipado estricto |
