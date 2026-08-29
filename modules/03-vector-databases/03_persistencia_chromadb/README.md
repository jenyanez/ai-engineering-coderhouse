# Unidad 3 · Persistencia Local con ChromaDB: Operaciones CRUD

> **Programa:** AI Engineering — Coderhouse  
> **Módulo 3:** Bases de Datos Vectoriales y Embeddings  
> **Ejercicio:** Gestión de Memoria Vectorial y Operaciones CRUD Persistentes  
> **Autor:** Jen Yanez  

---

## 📌 Propósito del Ejercicio

En sistemas de agentes inteligentes y arquitecturas RAG, el conocimiento indexado debe **sobrevivir a los reinicios del servidor** y permitir actualizaciones continuas sin reindexar la base de datos desde cero.

Este ejercicio implementa la clase [`VectorMemoryManager`](./vector_memory_manager.py), que encapsula todas las operaciones **CRUD** (Create, Read, Update, Delete) sobre un cliente persistente local de **ChromaDB**:

* **Create / Update (`upsert_documents`):** Inserción o actualización atómica basada en identificadores deterministas. Si el ID ya existe, actualiza el vector y metadatos; de lo contrario, lo crea.
* **Read Exacto (`get_documents`):** Recuperación determinista por IDs o filtrado booleano por metadatos (equivalente a `SELECT WHERE`).
* **Read Semántico (`semantic_search`):** Recuperación basada en similitud de cosenos para preguntas en lenguaje natural.
* **Delete (`delete_documents`):** Eliminación selectiva de conocimiento obsoleto por IDs o metadatos.
* **Count (`count_documents`):** Conteo de registros vectorizados en la colección.

---

## 🏗️ Ciclo de Vida CRUD en el Espacio Vectorial

```
┌─────────────────────────────────────────────────────────────┐
│                    VectorMemoryManager                      │
└─────────────────────────────────────────────────────────────┘
          │
          ├──> [Create / Upsert] -> upsert_documents(ids, docs, metas)
          │                         Vectoriza y persiste en disco (.parquet)
          │
          ├──> [Read Exact]      -> get_documents(ids, where_filter)
          │                         Búsqueda por metadatos / IDs directos
          │
          ├──> [Read Semantic]   -> semantic_search(query_text, n_results)
          │                         Similitud de cosenos sobre embeddings
          │
          ├──> [Update]          -> upsert_documents(id_existente, new_doc)
          │                         Re-vectorización atómica sin duplicados
          │
          └──> [Delete]          -> delete_documents(ids, where_filter)
                                    Depuración de vectores obsoletos
```

---

## 🚀 Guía de Ejecución

### 1. Ejecutar Demostración CRUD
```bash
python vector_memory_manager.py
```

### 2. Ejecutar la Suite de Pruebas Automatizadas
```bash
python test_vector_memory.py
```

---

## 🧪 Casos de Prueba Verificados (`test_vector_memory.py`)

* ✅ **Inserción y Conteo:** Inserción de múltiples documentos con metadatos asociados.
* ✅ **Búsqueda Semántica:** Extracción de los $k$ documentos más cercanos con distancias de similitud.
* ✅ **Filtro por Metadatos:** Recuperación determinista usando condiciones `where`.
* ✅ **Idempotencia y Update:** Verificación de que `upsert` sobre un ID existente actualiza el registro sin duplicar.
* ✅ **Eliminación Segura:** Borrado por ID y validación de ausencia posterior.
* ✅ **Validaciones Defensivas:** Manejo de excepciones `ValueError` ante listas de diferente longitud.
