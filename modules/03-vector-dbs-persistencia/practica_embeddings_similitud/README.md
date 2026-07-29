# Módulo 3 - Unidad 1: Evaluación de Embeddings y Similitud

Este proyecto contiene la evaluación práctica y empírica sobre la **Geometría del Lenguaje**, comparando modelos de **Embeddings densos** (`text-embedding-3-small` de OpenAI) frente a enfoques de **búsqueda léxica** (TF-IDF), utilizando la librería `scikit-learn` en Python para el cálculo de **Similitud Coseno**.

---

## Archivos del Proyecto

- `embeddings_eval.py` — Script modular que ejecuta la comparación empírica de similitud coseno entre la Query objetivo, 5 oraciones semánticamente equivalentes y 2 oraciones trampa.
- `generate_pdf.py` — Script que genera automáticamente el informe técnico entregable en formato PDF (`Evaluacion_Embeddings_Similitud.pdf`).
- `requirements.txt` — Dependencias del proyecto (`scikit-learn`, `openai`, `reportlab`, `python-dotenv`).
- `.env.example` — Plantilla para configurar la API key de OpenAI.

---

## Ejecución

```bash
# 1. Crear entorno virtual e instalar dependencias
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Configurar clave de API
cp .env.example .env
# Añadir la clave OPENAI_API_KEY en .env

# 3. Ejecutar la evaluación en consola
python embeddings_eval.py

# 4. Generar el documento PDF entregable
python generate_pdf.py
```

---

## Hallazgos Principales

1. **Captura Semántica:** Los Embeddings densos otorgan puntuaciones de similitud coseno altas (0.75 - 0.90) a oraciones con sinonimia léxica completa (sin compartir palabras clave con la consulta).
2. **Descarte de Trampas Léxicas:** Las oraciones trampa que comparten palabras clave como "servicio", "micro" o "despliegue", pero corresponden a dominios irrelevantes (limpieza comercial o flete marítimo), obtienen puntuaciones muy bajas (0.15 - 0.28) en Embeddings densos, mientras que con TF-IDF obtendrían falsos positivos elevados.
