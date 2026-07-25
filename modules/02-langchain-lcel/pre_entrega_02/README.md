# Pre-entrega 2: Pipeline de Procesamiento Validado

Pipeline de extracción de entidades técnicas que recibe un párrafo de texto sin procesar y devuelve un objeto Pydantic validado, utilizando **LangChain (LCEL)** con salida estructurada y lógica de resiliencia.

## Arquitectura

```
Texto (dict) → ChatPromptTemplate → ChatOpenAI.with_structured_output() → EntityExtraction (Pydantic)
                                         ↑
                                   .with_retry(3)
```

## Estructura del Código

- `schemas.py` — Modelo Pydantic `EntityExtraction` con validaciones estrictas.
- `chain.py` — Cadena LCEL con `.with_structured_output()`, `.with_retry()` y logs.
- `main.py` — Mini-script de prueba asíncrono con 3 casos de prueba.

## Ejemplo de Salida

```json
{
  "tecnologias": ["FastAPI", "Redis", "PostgreSQL"],
  "nivel_de_criticidad": "alta",
  "resumen_tecnico": "API con caché en Redis y persistencia en PostgreSQL; cuello de botella en conexiones concurrentes."
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

# 4. Ejecutar
python main.py
```
