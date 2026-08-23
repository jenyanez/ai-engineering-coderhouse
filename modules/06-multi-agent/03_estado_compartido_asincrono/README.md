# Ejercicio: Estado Compartido y Comunicación Asíncrona (Concurrencia Real)

> **Programa:** AI Engineering — Coderhouse  
> **Módulo 6:** Sistemas Multi-Agente: Colaboración y Especialización  
> **Unidad 3:** Manejo de Estado Inmutable, Pydantic V2 y Concurrencia con `asyncio.gather`  

---

## 📌 Descripción del Ejercicio

Implementación de un pipeline multi-agente asíncrono en **LangGraph** optimizado con **concurrencia real (`asyncio.gather`)** y validación estricta de esquemas mediante **Pydantic V2** (`ResearchArtifact` y `ReviewArtifact`).

---

## ⚡ Concurrencia Real con `asyncio.gather`

Para minimizar la latencia total del sistema, los sub-procesos independientes se ejecutan en paralelo:

1. **Nodo Investigador:**
   - Consulta simultánea de fuentes académicas (`fetch_academic_papers`) y benchmarks industriales (`fetch_industry_benchmarks`) con `asyncio.gather`.
   - **Ahorro de tiempo:** En lugar de ejecución secuencial (0.3s + 0.3s = 0.6s), se resuelve en paralelo en ~0.3s.

2. **Nodo Revisor:**
   - Evaluación simultánea de compliance (`verify_policy_compliance`) y profundidad técnica (`evaluate_technical_depth`) con `asyncio.gather`.
   - **Ahorro de tiempo:** Resuelto en paralelo en ~0.2s en lugar de 0.4s.

**Tiempo Total:** Reducción del tiempo de pipeline de 1.0s a **~0.5s** (reducción del 50% de latencia en I/O).

---

## 🏗️ Topología del Grafo

```text
[▶ Inicio: {"topic": "..."}]
             │
             ▼
    ┌─────────────────┐
    │ 🔬 Investigador │ ◄── [asyncio.gather: Fuentes Académicas + Benchmarks]
    └────────┬────────┘
             │ {"researcher_output": {...}}
             ▼
    ┌─────────────────┐
    │   🔍 Revisor    │ ◄── [asyncio.gather: Compliance + Calidad Técnica]
    └────────┬────────┘
             │ {"reviewer_output": {...}}
             ▼
         [⏹️ END]
```

---

## 🚀 Guía de Ejecución

```bash
python estado_compartido_asincrono.py
```
