# Pre-entrega 3: Sistema de Recuperación Semántica Local (RAG)

Esta es la entrega correspondiente a la **Pre-entrega 3 del Módulo 3** del curso AI Engineering de Coderhouse. Implementa un flujo End-to-End de recuperación semántica local (RAG) que combina persistencia vectorial en **ChromaDB** con generación fundamentada (*grounded*) mediante **LangChain (LCEL)**, validada con **Pydantic** y ejecutada bajo una arquitectura **asíncrona**.

## Características Principales

Cumple strictly con la rúbrica del programa:
- **Ingesta y Fragmentación Estratégica**: Utiliza `RecursiveCharacterTextSplitter` con `from_tiktoken_encoder` (`chunk_size=500` tokens, `chunk_overlap=50`) sobre un dataset de IA aplicada a negocios en la carpeta `/data`.
- **Persistencia y Anti-Reindexado**: Almacena los vectores en `./vectorstore` con ChromaDB. Verifica la existencia e integridad del índice previo para evitar reindexaciones innecesarias, optimizando tiempo y costos.
- **Recuperación Semántica Reutilizable**: Configura un retriever con búsqueda por similitud (`k=4`) usando `sentence-transformers/all-MiniLM-L6-v2` de forma coherente tanto en la ingesta como en la consulta, con patrón *singleton* para acelerar la ejecución.
- **Generación Fundamentada (Grounded LCEL)**: Incorpora un prompt de sistema con "filtro de veracidad" estricto. Si la información no está en el contexto, el LLM responde exactamente: *"No tengo acceso a esa información en los documentos disponibles."*
- **Contratos Fuertes y Fuentes Verificables**: Mantiene esquemas Pydantic desacoplados (`RespuestaLLM` y `RAGResponse`). Las fuentes no son inventadas por el LLM, sino extraídas directamente de los metadatos reales de los documentos recuperados.
- **Arquitectura Asíncrona**: La función principal `get_rag_response(query)` ejecuta de forma asíncrona (`ainvoke`) tanto la búsqueda semántica como la invocación del LLM.

---

## Arquitectura

```
Pregunta → Retriever (ChromaDB) → Fragmentos Relevantes (k=4)
                                          ↓
                           ChatPromptTemplate (Filtro de Veracidad)
                                          ↓
                              ChatOpenAI (gpt-4o-mini)
                                          ↓
                           PydanticOutputParser → RAGResponse
```

---

## Estructura del Código

- `data/` — Dataset de ejemplo con 4 archivos `.txt` sobre IA aplicada a negocios.
- `schemas.py` — Modelos Pydantic `RespuestaLLM` y `RAGResponse` con contratos de datos estrictos.
- `ingesta.py` — Carga de documentos, fragmentación por tokens y persistencia en ChromaDB con chequeo anti-reindexado.
- `retriever.py` — Capa de recuperación semántica con caché de embeddings y formateador de contexto.
- `chain.py` — Cadena LCEL que compone el prompt con filtro de veracidad, `ChatOpenAI` y `PydanticOutputParser`.
- `main.py` — Orquestador asíncrono con `get_rag_response()` y suite de pruebas automáticas (pregunta positiva y pregunta trampa).

---

## Ejemplo de Salida

### Respuesta a pregunta presente en el contexto:
```json
{
  "respuesta": "La IA ayuda a predecir el abandono de clientes (churn) identificando a aquellos con alta probabilidad de abandonar el servicio... Los modelos de clasificación binaria como XGBoost, LightGBM y redes neuronales son los más utilizados...",
  "fuentes": [
    "data/analitica_predictiva_negocios.txt",
    "data/etica_ia_empresarial.txt"
  ],
  "fragmentos_recuperados": 4
}
```

### Respuesta a pregunta trampa (fuera del contexto):
```json
{
  "respuesta": "No tengo acceso a esa información en los documentos disponibles.",
  "fuentes": [
    "data/analitica_predictiva_negocios.txt",
    "data/automatizacion_procesos.txt",
    "data/estrategia_ia_ventas.txt",
    "data/etica_ia_empresarial.txt"
  ],
  "fragmentos_recuperados": 4
}
```

---

## Instrucciones de Ejecución

### 1. Entorno y Dependencias
Se recomienda utilizar un entorno virtual (`venv`) estándar de Python:
```bash
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual (Mac/Linux)
source .venv/bin/activate
# (En Windows usa: .venv\Scripts\activate)

# 3. Instalar dependencias
pip install -r requirements.txt
```

### 2. Variables de Entorno
Copia el archivo de ejemplo y agrega tu clave de API:
```bash
cp .env.example .env
```
Abre el archivo `.env` y configura tu `OPENAI_API_KEY`:
```
OPENAI_API_KEY=tu_api_key_aqui
```

### 3. Ejecutar
```bash
python main.py
```
El script ejecutará automáticamente la ingesta de documentos (si no existe el índice) y correrá la suite de pruebas validando tanto preguntas con respuesta como preguntas trampa.
