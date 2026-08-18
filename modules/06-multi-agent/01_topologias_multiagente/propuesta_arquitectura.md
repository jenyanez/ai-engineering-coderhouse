# Propuesta Arquitectónica: Sistema Multi-Agente Jerárquico para Atención al Cliente en E-Commerce (Twitter/X)

> **Programa:** AI Engineering — Coderhouse  
> **Módulo 6:** Sistemas Multi-Agente: Colaboración y Especialización  
> **Unidad 1:** Topologías Multi-Agente: Colaboración vs Jerarquía  
> **Patrón Arquitectónico:** Supervisor Jerárquico (*Supervisor Pattern*) en LangGraph  
> **Estado:** Aprobado / Versión Final de Entrega  

---

## 📌 Resumen Ejecutivo

> [!NOTE]
> El presente documento detalla el diseño técnico de un sistema multi-agente basado en una **topología jerárquica (Patrón Supervisor)** implementado sobre **LangGraph**. El sistema automatiza el triaje de quejas, la verificación del estado de pedidos en bases de datos y la redacción de respuestas personalizadas y seguras en la red social Twitter/X.

Al operar sobre un canal público de alta exposición, la arquitectura prioriza:
* **Control determinista y trazabilidad:** Cada decisión pasa por un nodo central de coordinación.
* **Compuerta de calidad (*Quality Gate*):** Validación estricta de políticas de marca y privacidad antes de publicar.
* **Aislamiento de responsabilidades:** Cada agente especialista opera bajo el principio de mínimo privilegio (*Least Privilege*).

---

## 1. Identificación y Definición de Roles

La arquitectura desacopla el razonamiento en un **nodo Supervisor central** y **tres agentes especialistas (Workers)**:

```text
┌─────────────────────────────────────────────────────────────────┐
│                      👑 SUPERVISOR AGENT                        │
│          (Orquestador Central & Compuerta de Calidad)           │
└───────────────┬─────────────────┬─────────────────┬─────────────┘
                │                 │                 │
        1. Infiere & Extrae       │         3. Redacta Borrador
                │       2. Consulta Logística       │
                ▼                 ▼                 ▼
        ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
        │  🎭 Agente 1  │ │  📦 Agente 2  │ │  ✍️ Agente 3   │
        │  Sentiment &  │ │    Order &    │ │  Response &   │
        │ Triage Agent  │ │Logistics Agent│ │Compliance Ag. │
        └───────────────┘ └───────────────┘ └───────────────┘
```

### 1.1. Supervisor Agent (Orquestador Central / Director de Tráfico)
* **Rol:** Cerebro coordinador del sistema. No ejecuta tareas operativas directamente (evitando el anti-patrón de *"Supervisor Todólogo"*), sino que analiza el estado global, determina qué especialista debe intervenir y audita la salida final.
* **Responsabilidades:**
  1. **Enrutamiento Dinámico:** Evalúa el estado conversacional y delega la ejecución mediante la variable de control `next_step`.
  2. **Evaluación de Suficiencia:** Verifica si la información recopilada es suficiente antes de avanzar a la siguiente etapa.
  3. **Compuerta de Calidad (*Quality Gate*):** Audita el borrador final (longitud, tono, PII) y autoriza la publicación o activa el escalamiento a un operador humano (*Human-in-the-Loop*).
* **Modelo Recomendado:** `GPT-4o` o `Claude 3.5 Sonnet` (alta capacidad de razonamiento y seguimiento de instrucciones).

### 1.2. Sentiment & Triage Agent (Analista de Sentimiento y Extracción)
* **Rol:** Especialista en Procesamiento de Lenguaje Natural (NLP) enfocado en entender la emoción del cliente, calcular la urgencia y extraer identificadores estructurados.
* **Responsabilidades:**
  1. Clasificar el sentimiento: `POSITIVO`, `NEUTRO`, `NEGATIVO_MODERADO`, `NEGATIVO_CRÍTICO`.
  2. Calcular el índice de urgencia (rango de `0.0` a `1.0`).
  3. Extraer entidades clave: identificador del pedido (`#ORD-XXXXX`), handle del cliente (`@usuario`) y categoría del reclamo.
* **Modelo Recomendado:** `GPT-4o-mini` (alta velocidad y bajo costo).

### 1.3. Order & Logistics Agent (Especialista en Órdenes y Logística)
* **Rol:** Especialista en integración transaccional con sistemas empresariales (ERP, base de datos de órdenes y APIs de couriers).
* **Responsabilidades:**
  1. Validar la existencia del pedido en la base de datos central.
  2. Obtener el estado operativo (`EN_PREPARACIÓN`, `EN_TRANSITO`, `RETRASADO`, `ENTREGADO`, `CANCELADO`).
  3. Consultar la API del operador logístico (DHL, FedEx, etc.) para recuperar el motivo de demoras y la nueva fecha estimada de entrega (ETA).
* **Modelo Recomendado:** `GPT-4o-mini`.

### 1.4. Response & Compliance Agent (Redactor y Cumplimiento de Políticas)
* **Rol:** Especialista en comunicación corporativa, tono de marca y protección de privacidad.
* **Responsabilidades:**
  1. Redactar una respuesta empática contextualizada con la emoción y los datos logísticos confirmados.
  2. Ajustar estrictamente el mensaje al límite de **280 caracteres** de Twitter/X.
  3. Enmascarar información personal identificable (PII) e invitar al usuario a mensaje directo (DM) si se requiere privacidad.
* **Modelo Recomendado:** `GPT-4o-mini`.

---

## 2. Definición de Herramientas Técnicas (Tooling Contract)

Cada especialista cuenta con herramientas dedicadas con contratos estrictos de entrada/salida tipados en Pydantic:

### 2.1. Herramientas del Sentiment & Triage Agent

#### 🛠️ `classify_sentiment_and_urgency`
* **Firma:** `classify_sentiment_and_urgency(tweet_text: str)`
* **Salida Estructurada:** `SentimentData(sentiment: str, urgency_score: float, category: str)`
* **Manejo de Errores:** Si el texto es ambiguo o spam, retorna categoría `"DESCONOCIDO"` con urgencia baja (`0.1`).

#### 🛠️ `extract_entities_pydantic`
* **Firma:** `extract_entities_pydantic(tweet_text: str)`
* **Salida Estructurada:** `EntitiesData(order_id: Optional[str], customer_handle: str)`
* **Manejo de Errores:** Si no se detecta número de orden, retorna `order_id = None` para que el redactor lo solicite por mensaje privado (DM).

---

### 2.2. Herramientas del Order & Logistics Agent

#### 🛠️ `query_order_db`
* **Firma:** `query_order_db(order_id: str)`
* **Salida Estructurada:** `OrderRecord(status: str, tracking_id: Optional[str], customer_id: str, order_exists: bool)`
* **Manejo de Errores:** Si el ID no existe en la base de datos, retorna `order_exists = False` sin interrumpir la ejecución.

#### 🛠️ `get_courier_tracking_info`
* **Firma:** `get_courier_tracking_info(tracking_id: str)`
* **Salida Estructurada:** `CourierStatus(carrier: str, location: str, eta: str, delay_reason: Optional[str])`
* **Manejo de Errores:** Ante caídas o timeout de API externa, aplica *Degradación Grácil* devolviendo la última fecha estimada en caché local.

---

### 2.3. Herramientas del Response & Compliance Agent

#### 🛠️ `twitter_length_formatter`
* **Firma:** `twitter_length_formatter(draft: str)`
* **Salida Estructurada:** `FormattedTweet(final_text: str, char_count: int, is_valid: bool)`
* **Manejo de Errores:** Si supera los 280 caracteres, trunca respetando límites de palabras e inserta llamada a DM.

#### 🛠️ `pii_sanitizer_filter`
* **Firma:** `pii_sanitizer_filter(text: str)`
* **Salida Estructurada:** `CleanText(sanitized_text: str, pii_detected: bool)`
* **Manejo de Errores:** Enmascara automáticamente números de tarjeta (`****-1234`), correos electrónicos y números de documento.

---

## 3. Esquema de Estado y Flujo Lógico

### 3.1. Esquema del Estado Global (`CustomerSupportState`)

Para evitar condiciones de carrera (*Race Conditions*) y sobreescrituras accidentales, cada agente posee un espacio de escritura aislado en el estado compartido:

```python
from typing import Annotated, Literal, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

# 1. Contratos de Datos Validados con Pydantic
class SentimentPayload(BaseModel):
    sentiment: Literal["POSITIVO", "NEUTRO", "NEGATIVO_MODERADO", "NEGATIVO_CRÍTICO"]
    urgency_score: float = Field(ge=0.0, le=1.0)
    category: str
    order_id: Optional[str] = None
    customer_handle: str

class LogisticsPayload(BaseModel):
    order_exists: bool
    status: str
    tracking_url: Optional[str] = None
    delay_reason: Optional[str] = None
    estimated_delivery: Optional[str] = None

class ResponsePayload(BaseModel):
    tweet_text: str
    char_count: int
    invites_to_dm: bool
    requires_human_approval: bool

# 2. Estado Central del Grafo en LangGraph
class CustomerSupportState(TypedDict):
    # Historial acumulativo de mensajes
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Canales de datos aislados por agente
    raw_tweet: str
    sentiment_data: Optional[SentimentPayload]
    logistics_data: Optional[LogisticsPayload]
    response_data: Optional[ResponsePayload]
    
    # Variables de control y enrutamiento del Supervisor
    next_step: Literal[
        "triage_agent", 
        "logistics_agent", 
        "response_agent", 
        "publish_tweet", 
        "human_escalation", 
        "END"
    ]
    iteration_count: int
    is_escalated: bool
```

---

### 3.2. Diagrama de Flujo del Grafo en LangGraph

```text
[▶ Webhook: Tweet Entrante]
            │
            ▼
    ┌───────────────┐
    │ 👑 Supervisor │ ◄───────────────────────────┐
    └───────┬───────┘                             │
            │                                     │ (Retorna Estado)
     ¿next_step?                                  │
            ├─► [🎭 Sentiment & Triage Agent] ────┤
            ├─► [📦 Order & Logistics Agent] ─────┤
            ├─► [✍️ Response & Compliance Agent] ─┘
            │
    Decisión de Salida:
            ├─► [🚀 Publicador Twitter/X] ──► [⏹️ END: Tweet Publicado]
            └─► [🚨 Escalamiento Humano]  ──► [⏹️ END: Ticket Creado]
```

---

### 3.3. Secuencia Paso a Paso de Transferencia de Estado

A continuación se detalla cómo muta iterativamente el estado global a lo largo del flujo:

#### Paso 1: Ingesta del Tweet (`START` → `Supervisor`)
* **Entrada cruda:**  
  `"¡Una vergüenza @TiendaOnline! Hace 5 días espero mi pedido #ORD-4491 y nadie responde. ¡Son unos estafadores!"`
* **Acción:** El Supervisor inicializa el estado y enruta al analista: `next_step = "triage_agent"`.

#### Paso 2: Análisis Emocional y Extracción (`Triage Agent`)
* **Ejecución:** Corre `classify_sentiment_and_urgency` y `extract_entities_pydantic`.
* **Mutación del Estado:**
  ```json
  "sentiment_data": {
    "sentiment": "NEGATIVO_CRÍTICO",
    "urgency_score": 0.95,
    "category": "Envío Demorado",
    "order_id": "ORD-4491",
    "customer_handle": "@cliente_enojado"
  }
  ```
* **Retorno:** El control regresa al Supervisor.

#### Paso 3: Decisión Intermedia del Supervisor
* **Evaluación:** El Supervisor verifica que `sentiment_data` está completo y contiene `order_id = "ORD-4491"`.
* **Acción:** Enruta a consulta logística: `next_step = "logistics_agent"`.

#### Paso 4: Consulta de Pedido y Tracking (`Logistics Agent`)
* **Ejecución:** Corre `query_order_db("ORD-4491")` y `get_courier_tracking_info`.
* **Mutación del Estado:**
  ```json
  "logistics_data": {
    "order_exists": true,
    "status": "RETRASADO",
    "delay_reason": "Bloqueo vial en centro logístico regional",
    "estimated_delivery": "Mañana antes de las 14:00hs",
    "tracking_url": "https://courier.com/track/TRK-9921"
  }
  ```
* **Retorno:** El control regresa al Supervisor.

#### Paso 5: Redacción y Cumplimiento (`Compliance Agent`)
* **Evaluación del Supervisor:** Cuenta con contexto emocional y datos logísticos. Enruta: `next_step = "response_agent"`.
* **Ejecución:** Redacta borrador, valida longitud (≤ 280 caracteres) y sanitiza PII.
* **Mutación del Estado:**
  ```json
  "response_data": {
    "tweet_text": "Hola @cliente_enojado, lamentamos mucho la demora. Tu pedido #ORD-4491 tuvo un retraso y llegará mañana antes de las 14:00hs. Te enviamos DM con cupón y tracking. 📦",
    "char_count": 168,
    "invites_to_dm": true,
    "requires_human_approval": false
  }
  ```

#### Paso 6: Quality Gate y Publicación (`Supervisor Final` → `Publicador`)
* **Auditoría:** El Supervisor valida que el tweet cumple con el límite de caracteres, tono empático y no expone datos privados.
* **Mutación Final:** `next_step = "publish_tweet"`.
* **Cierre:** El nodo publicador invoca la API de Twitter/X y concluye el grafo (`END`).

---

## 4. Justificación Arquitectónica: Jerarquía vs Cooperación

En atención al cliente sobre redes públicas, la topología jerárquica es técnicamente superior a una red colaborativa entre pares (P2P):

### Comparativa por Dimensiones Técnicas:

#### 1. Mitigación de Riesgos de Marca y Reputación
* **Topología Cooperativa (P2P):** Descentralizada. Cualquier agente puede publicar directamente en la red social sin filtro previo.
* **Topología Jerárquica (Supervisor):** **Centralizada.** El Supervisor actúa como *Quality Gate* obligatorio antes de cualquier emisión externa.
* **Impacto en E-Commerce:** En Twitter/X, un mensaje agresivo o una alucinación daña la reputación pública de la empresa en minutos.

#### 2. Determinismo y Auditoría del Flujo
* **Topología Cooperativa (P2P):** Emergente y reactivo. El orden de ejecución entre agentes es impredecible.
* **Topología Jerárquica (Supervisor):** **Secuencial y Protocolar:** Triaje → Logística → Redacción → Validación.
* **Impacto en E-Commerce:** No tiene sentido redactar una respuesta antes de confirmar si el pedido realmente existe en la base de datos.

#### 3. Control de Bucles Infinitos (Anti-Loop)
* **Topología Cooperativa (P2P):** Alto riesgo de ciclos recursivos no controlados entre pares (discusiones sin fin entre redactor y analista).
* **Topología Jerárquica (Supervisor):** **Garantizado.** El Supervisor gestiona un contador de iteraciones y límite de recursión estricto.
* **Impacto en E-Commerce:** Evita el consumo descontrolado de tokens y garantiza tiempos de respuesta acotados.

#### 4. Eficiencia de Costos y Tokens
* **Topología Cooperativa (P2P):** Exige modelos de gama alta en todos los nodos para que puedan auto-coordinarse.
* **Topología Jerárquica (Supervisor):** **Modelos Heterogéneos:** `GPT-4o` en el Supervisor + `GPT-4o-mini` en los Workers.
* **Impacto en E-Commerce:** **Ahorro de costos superior al 70%** delegando tareas atómicas en modelos ligeros.

#### 5. Principio de Mínimo Privilegio (Seguridad)
* **Topología Cooperativa (P2P):** Contexto global compartido donde todos los agentes tienen acceso a todas las herramientas y datos.
* **Topología Jerárquica (Supervisor):** **Aislamiento Estricto:** Cada especialista solo accede a su canal de datos asignado.
* **Impacto en E-Commerce:** El agente redactor jamás tiene permisos para consultar ni modificar la base de datos de pedidos.

---

## 5. Matriz de Casos Borde y Resiliencia (*Edge Cases*)

```text
[📥 Evento Entrante] ──► [Evaluación de Casos Borde]
                                │
    ┌───────────────────────────┼───────────────────────────┐
    ▼                           ▼                           ▼
[Sin #PedidoID]       [Crisis / Amenaza Legal]     [Timeout API Courier]
    │                           │                           │
    ▼                           ▼                           ▼
(Bypass Logística:      (Bypass Agéntico:           (Degradación Grácil:
Solicitar por DM)       Escalar a Humano)           Usar caché local)
```

### Detalle de Escenarios de Contingencia:

#### ⚡ Caso Borde 1: Queja sin Número de Pedido
* **Detección:** `Sentiment & Triage Agent` retorna `order_id = None`.
* **Comportamiento:** El Supervisor **saltea el nodo logístico** y ordena al redactor emitir un tweet empático solicitando el ID por mensaje directo (DM).

#### ⚡ Caso Borde 2: Crisis de Marca o Amenaza Legal
* **Detección:** `Sentiment & Triage Agent` detecta lenguaje litigioso o insultos graves (`urgency_score = 1.0`).
* **Comportamiento:** **Bypass total.** El Supervisor aborta la respuesta automática y enruta inmediatamente a `human_escalation` (crea ticket prioritario en Zendesk/Slack para el equipo legal/PR).

#### ⚡ Caso Borde 3: Caída o Timeout de API de Paquetería
* **Detección:** `get_courier_tracking_info` arroja excepción HTTP 5xx o Timeout.
* **Comportamiento:** **Degradación Grácil (*Graceful Degradation*):** Se recupera la última fecha estimada almacenada en la base de datos interna con aviso de actualización en curso.

#### ⚡ Caso Borde 4: Pedido Inexistente o Inválido
* **Detección:** `query_order_db` retorna `order_exists = False`.
* **Comportamiento:** El redactor genera un mensaje amable informando que el código no figura en sistema y ofrece un enlace seguro de asistencia.

---

## 6. Observabilidad, Guardrails y Mitigación de Cuellos de Botella

### 6.1. Guardrails Anti-Loop y Mitigación de Cuello de Botella
* **Tope de Recursión (`recursion_limit = 4`):** Si en 4 turnos el Supervisor no logra un estado de resolución válido, el flujo aborta automáticamente y escala a un humano.
* **Mitigación de Latencia en Supervisor:** Para evitar que el Supervisor centralizado sea un cuello de botella (*Bottleneck*), se aplican tres técnicas:
  1. *Prompt Caching* en el Supervisor para no re-procesar el system prompt completo en cada turno.
  2. Llamadas a herramientas con esquemas estructurados (*Structured Outputs*) de baja latencia.
  3. Ejecución asíncrona de las llamadas a bases de datos y couriers.

### 6.2. Estrategia de Observabilidad con LangSmith
* **Jerarquía de Spans:** Cada ejecución genera un árbol de observabilidad:  
  `Trace (Tweet ID) → Span: Supervisor → Span: Worker → Span: Tool Call`
* **SLOs (Service Level Objectives) de Producción:**
  * **Time to First Response (TTFR):** ≤ 45 segundos desde la recepción del webhook.
  * **Tasa de Aprobación de Quality Gate:** ≥ 90% en la primera iteración.
  * **Costo Promedio por Reclamo:** ≤ $0.003 USD por interacción resuelta.

---

## 7. Conclusión

La **Topología Jerárquica con Patrón Supervisor** es el estándar de ingeniería idóneo para atención al cliente automatizada en redes sociales públicas. Garantiza el equilibrio óptimo entre **especialización operativa, contención de costos, determinismo en el flujo y control estricto de reputación de marca**.

Este diseño representa la arquitectura base para la implementación funcional con LangGraph en las siguientes unidades del programa.
