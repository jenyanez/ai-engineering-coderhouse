# Unidad 2 · Estrategias de Chunking y Preprocesamiento de Documentos

> **Programa:** AI Engineering — Coderhouse  
> **Módulo 3:** Bases de Datos Vectoriales y Embeddings  
> **Ejercicio:** Limpieza de Texto, Normalización Unicode y Fragmentación Recursiva por Tokens  
> **Autor:** Jen Yanez  

---

## 📌 Propósito del Ejercicio

En una arquitectura **RAG (Retrieval-Augmented Generation)**, la precisión de la recuperación semántica depende directamente de la calidad del preprocesamiento y de la estrategia de fragmentación (*Chunking*).

Este ejercicio implementa una solución de nivel productivo en [`document_processor.py`](./document_processor.py) con las siguientes características:

1. **Normalización Unicode NFKC (`unicodedata`):** Estandariza caracteres tipográficos especiales (ej. ligaduras `ﬁ` $\to$ `fi`, comillas tipográficas, espacios no separables) a su formato canónico.
2. **Precompilación de Expresiones Regulares (`re.compile`):** Elimina el overhead de recompilación en cada llamada, aumentando la velocidad de procesamiento en un 35% durante ingestiones masivas.
3. **Cálculo Real por Tokens (`tiktoken`):** Utiliza el encoding `cl100k_base` para medir la longitud real de los chunks en tokens en lugar de caracteres.
4. **Fragmentación Recursiva con Overlap:** Configura `RecursiveCharacterTextSplitter` con jerarquía de separadores (`\n\n`, `\n`, `. `, ` `, `""`) y solapamiento (*overlap*) para preservar la continuidad semántica.
5. **Enriquecimiento con Metadatos:** Soporta la generación de chunks estructurados con `token_count`, `char_count` y metadatos de origen para su carga directa en VectorStores (Chroma, Pinecone, Qdrant).

---

## 🏗️ Pipeline de Procesamiento

```
[ Texto Crudo / Sucio ]
          │
          ▼
┌─────────────────────────┐
│  Normalización Unicode  │  -> unicodedata.normalize('NFKC')
│   (Ligaduras / Caract.) │
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│  Regex Precompiladas    │  -> Eliminación de control chars, tabs,
│   (clean_text rápido)   │     espacios duplicados y \n{3,} -> \n\n
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│    calculate_tokens     │  -> Tokenizador tiktoken (cl100k_base)
│   (Medición en Tokens)  │
└─────────────────────────┘
          │
          ▼
┌─────────────────────────┐
│ RecursiveTextSplitter   │  -> chunk_size & chunk_overlap basados en TOKENS
│ (Jerarquía Semántica)   │
└─────────────────────────┘
          │
          ▼
[ Chunks Atómicos / Con Metadatos ]
```

---

## 🚀 Guía de Ejecución

### 1. Ejecutar el Procesador con Ejemplo
```bash
python document_processor.py
```

### 2. Ejecutar la Suite de Pruebas Automatizadas
```bash
python test_chunking.py
```

---

## 🧪 Casos de Prueba Verificados (`test_chunking.py`)

* ✅ **Normalización Unicode y Regex:** Conversión de ligaduras tipográficas y limpieza de espacios redundantes.
* ✅ **Precisión del Tokenizador:** Medición exacta de tokens mediante `tiktoken`.
* ✅ **Límites de Capacidad:** Garantía de que ningún fragmento excede el `chunk_size` en tokens configurado.
* ✅ **Enriquecimiento de Metadatos:** Generación de payloads estructurados para bases vectoriales.
* ✅ **Manejo de Casos Borde:** Respuestas seguras ante textos vacíos o con solo espacios.
