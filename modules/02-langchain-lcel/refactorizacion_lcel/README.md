# Tarea Módulo 2: Refactorización a LCEL Asíncrono

Migración de la implementación imperativa del Módulo 1 (SDKs crudos de OpenAI/Anthropic) a una arquitectura declarativa usando **LCEL (LangChain Expression Language)**.

## Flujo de la Cadena

```
Input (dict) → ChatPromptTemplate → ChatOpenAI (gpt-4o-mini) → StrOutputParser → str
```

## Características

- **Sintaxis LCEL**: Composición de la cadena usando el operador pipe (`|`).
- **Ejecución asíncrona**: Uso de `await chain.ainvoke({...})` para no bloquear el Event Loop.
- **Prompting con roles**: `ChatPromptTemplate` con roles `system` y `human`.
- **Post-procesamiento**: `StrOutputParser` para obtener texto plano (no objetos `AIMessage`).

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
