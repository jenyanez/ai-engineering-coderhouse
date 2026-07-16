# Pre-entrega 1: Cliente de LLM Robusto y Asíncrono

Esta es la entrega correspondiente a la **Pre-entrega 1 del Módulo 1** del curso AI Engineering de Coderhouse. Contiene una capa de abstracción asíncrona para interactuar con modelos de lenguaje, implementada usando `Python 3.12+`.

## Características Principales

Cumple estrictamente con la rúbrica del programa:
- **Abstracción y Factory Pattern**: La clase `AsyncLLMManager` permite instanciar transparentemente proveedores (OpenAI o Anthropic) sin acoplar la lógica de negocio.
- **Concurrencia y Streaming**: Utiliza `AsyncOpenAI` y `AsyncAnthropic` con generadores asíncronos (`yield`) que devuelven los tokens en tiempo real sin bloquear el *Event Loop*.
- **Contratos Fuertes (Pydantic)**: Se validan tanto los parámetros de configuración (ej. temperatura) como los esquemas de mensajes de entrada (`ChatMessage`) garantizando la integridad.
- **Resiliencia**: Captura proactiva de errores de red o cuotas de API (`RateLimitError`) devolviendo una respuesta estructurada que no rompe la ejecución del sistema.

## Estructura del Código

- `schemas.py`: Modelos de validación.
- `clients/base.py`: Clase abstracta de la que heredan los SDKs.
- `clients/openai_client.py`: Wrapper para OpenAI.
- `clients/anthropic_client.py`: Wrapper para Anthropic.
- `manager.py`: Inicializador.
- `main.py`: Script de ejecución de pruebas.

---

## Instrucciones de Ejecución

### 1. Entorno y Dependencias
Se recomienda utilizar un entorno virtual (venv) estándar de Python:
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
Copia el archivo de ejemplo y agrega tus credenciales:
```bash
cp .env.example .env
```
Abre el archivo `.env` y coloca al menos una clave de API válida (OpenAI o Anthropic). El script probará automáticamente las que encuentre.

### 3. Ejecutar
```bash
python main.py
```
Verás la respuesta completa y luego la respuesta transmitida en *streaming* token a token en tu consola.
