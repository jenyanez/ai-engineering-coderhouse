# Pre-Entrega 04 — Sistema RAG Escalable con Pinecone

Sistema de Retrieval-Augmented Generation (RAG) escalable en la nube utilizando **Pinecone Serverless** como base vectorial y un **recuperador híbrido** que combina búsqueda semántica (vectorial) con búsqueda léxica (BM25).

---

## 📁 Estructura del Proyecto

```text
pre_entrega_04/
├── .env.example          # Template de variables de entorno (sin secretos)
├── .gitignore            # Excluye .env, .venv, __pycache__
├── requirements.txt      # Dependencias del proyecto
├── README.md             # Este archivo
├── data/                 # Documentos fuente para la ingesta
│   ├── analitica_predictiva_negocios.txt
│   ├── automatizacion_procesos.txt
│   ├── estrategia_ia_ventas.txt
│   └── etica_ia_empresarial.txt
├── golden_set.json       # Benchmark de evaluación (5 preguntas)
├── config.py             # Inicialización de Pinecone + verificación del índice
├── ingesta.py            # Pipeline: carga → chunking → embeddings → upsert
├── retriever.py          # RAGSystem: EnsembleRetriever (BM25 + Pinecone)
├── evaluate.py           # Métricas: Precision@5 y Recall@5
└── main.py               # Orquestador: ingesta → consulta → evaluación
```

---

## 🚀 Cómo Replicar el Índice de Pinecone

### 1. Clonar el repositorio y configurar el entorno

```bash
cd pre_entrega_04
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar las variables de entorno

```bash
cp .env.example .env
# Editar .env con tus API keys reales
```

Variables requeridas:

| Variable | Descripción |
|---|---|
| `PINECONE_API_KEY` | API Key de tu cuenta de Pinecone |
| `OPENAI_API_KEY` | API Key de OpenAI |
| `INDEX_NAME` | Nombre del índice (default: `pre-entrega-04`) |

### 3. Crear el índice y ejecutar la ingesta

```bash
python ingesta.py
```

Esto:
- Verifica si el índice `pre-entrega-04` existe en Pinecone; si no, lo crea (Serverless, `us-east-1`, `cosine`, `dim=1536`).
- Carga los 4 documentos `.txt` de la carpeta `data/`.
- Fragmenta en chunks de ~500 tokens con solapamiento de 50.
- Genera embeddings con `text-embedding-3-small` y sube a Pinecone con namespace `documentos`.

### 4. Ejecutar la evaluación

```bash
python evaluate.py
```

### 5. Ejecutar el flujo completo

```bash
python main.py
```

---

## 🏗️ Arquitectura del Sistema (Senior Level Optimizations)

### 1. Ingesta Idempotente con Hashing SHA-256 (`ingesta.py`)
- **Control de cambios**: Cada chunk genera un hash SHA-256 único guardado en `.ingest_hashes.json`.
- **Eficiencia**: Si los archivos no han sido modificados, la ingesta omite el cálculo de embeddings y peticiones a OpenAI/Pinecone, ahorrando costos y tiempo.
- **Enriquecimiento de Metadatos**: `source`, `category`, `page`, `chunk_hash` y `text` almacenados directamente en Pinecone.

### 2. Recuperador Híbrido + Dynamic Metadata Filtering (`retriever.py`)
- **EnsembleRetriever**: Fusión de BM25 (búsqueda léxica) + PineconeVectorStore (búsqueda semántica).
- **Metadata Filtering**: Método `retrieve(query, filter_dict=...)` para aplicar estructuración de filtros vectoriales directo a Pinecone (ej: `{"category": {"$eq": "Estrategia Ia Ventas"}}`).

### 3. Evaluación Cuantitativa + LLM-as-a-Judge (`evaluate.py`)
- **Golden Set (30 preguntas)**: Evaluado sobre el corpus completo de documentos.
- **Métricas Tradicionales**: `Recall@5` y `Precision@5`.
- **Métrica Cualitativa (LLM-as-a-Judge)**: Muestra de consultas evaluadas en escala 1-5 por `gpt-4o-mini` para medir la relevencia semántica real del contexto recuperado (*Context Relevance*).

---

## 📊 Resultados de Evaluación Reales

```text
======================================================================
📈 RESULTADOS GLOBALES (30 PREGUNTAS EN BENCHMARK)
======================================================================
  Recall@5:           100.00% (30/30 preguntas con HIT perfecto)
  Precision@5:        58.00%  (promedio de precisión por consulta)
  Context Relevance:  5.00 / 5.00 (Puntuación perfecta LLM-as-a-Judge)
======================================================================
```

> **Conclusión del Benchmark**: El recuperador híbrido (`EnsembleRetriever`) demostró una cobertura del **100%** en localización de documentos relevantes para todo el corpus técnico.

---

## 🔧 Tecnologías Utilizadas

| Componente | Tecnología |
|---|---|
| Base Vectorial Cloud | Pinecone Serverless |
| Embeddings | OpenAI `text-embedding-3-small` (1536 dim) |
| Búsqueda Léxica | BM25 (`rank-bm25`) |
| Orquestación RAG | LangChain (`EnsembleRetriever`) |
| Validación de Datos | Pydantic v2 |
| Gestión de Secretos | `python-dotenv` + `.env` |
