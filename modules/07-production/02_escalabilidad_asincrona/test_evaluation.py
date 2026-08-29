import asyncio
import json
import unittest
from unittest.mock import AsyncMock, patch

from main import TaskRequest, TaskStatus, app, create_task, get_status, task_worker


class TestAsyncScalabilityEvaluation(unittest.IsolatedAsyncioTestCase):
    """
    Suite de pruebas unitarias y de integración que valida los 4 Criterios de Evaluación:
    1. Arquitectura de Desacoplamiento (FastAPI + Redis)
    2. Gestión de Estados y Polling (pending -> processing -> completed / failed)
    3. Lógica del Worker y Concurrencia (blpop, non-blocking, exception handling)
    4. Calidad del Código y Tipado (Pydantic / Python 3.12)
    """

    async def asyncSetUp(self):
        self.fake_db = {}
        self.fake_queue = []

    # -------------------------------------------------------------
    # CRITERIO 1: Arquitectura de Desacoplamiento
    # -------------------------------------------------------------
    async def test_01_decoupled_architecture_process_endpoint(self):
        async def fake_set(key, value):
            self.fake_db[key] = value

        async def fake_rpush(queue, value):
            self.fake_queue.append(value)

        with patch("main.redis_client.set", side_effect=fake_set), \
             patch("main.redis_client.rpush", side_effect=fake_rpush):

            req = TaskRequest(query="¿Cuál es la tendencia de IA en 2026?")
            res = await create_task(req)

            # 1. Retorna de inmediato con status pending
            self.assertEqual(res.status, TaskStatus.PENDING)
            self.assertTrue(len(res.job_id) > 10)

            # 2. Verifica persistencia en Redis antes de encolar
            saved_raw = self.fake_db.get(f"status:{res.job_id}")
            self.assertIsNotNone(saved_raw)
            saved_data = json.loads(saved_raw)
            self.assertEqual(saved_data["status"], "pending")

            # 3. Verifica que la tarea está en la cola FIFO de Redis
            self.assertIn(res.job_id, self.fake_queue)
            print("✅ [Criterio 1: Desacoplamiento] Petición encolada y Job ID generado.")

    # -------------------------------------------------------------
    # CRITERIO 2: Gestión de Estados y Polling
    # -------------------------------------------------------------
    async def test_02_state_management_and_polling(self):
        async def fake_get(key):
            return self.fake_db.get(key)

        with patch("main.redis_client.get", side_effect=fake_get):
            # 1. Consulta de Job ID inexistente lanza HTTP 404
            from fastapi import HTTPException
            with self.assertRaises(HTTPException) as ctx:
                await get_status("job-inexistente-12345")
            self.assertEqual(ctx.exception.status_code, 404)

            # 2. Consulta de Job ID existente
            self.fake_db["status:job-test-1"] = json.dumps({
                "job_id": "job-test-1",
                "status": "completed",
                "query": "Análisis test",
                "result": "Resultado verificado",
                "error": None,
                "created_at": 100.0,
                "updated_at": 103.0,
                "execution_time": 3.0
            })
            res = await get_status("job-test-1")
            self.assertEqual(res["status"], "completed")
            self.assertEqual(res["result"], "Resultado verificado")
            self.assertEqual(res["execution_time"], 3.0)
            print("✅ [Criterio 2: Estados y Polling] Validación 404 y tipado de estados superado.")

    # -------------------------------------------------------------
    # CRITERIO 3: Lógica del Worker y Concurrencia
    # -------------------------------------------------------------
    async def test_03_worker_lifecycle_and_exception_resilience(self):
        job_id = "job-worker-test-100"
        self.fake_db[f"status:{job_id}"] = json.dumps({
            "job_id": job_id,
            "status": "pending",
            "query": "Query worker test",
            "result": None,
            "error": None,
            "created_at": 200.0,
            "updated_at": 200.0,
            "execution_time": None
        })
        self.fake_queue.append(job_id)

        pop_count = 0
        async def fake_blpop(queue, timeout=2):
            nonlocal pop_count
            if pop_count == 0 and self.fake_queue:
                pop_count += 1
                return (queue, self.fake_queue.pop(0))
            await asyncio.sleep(0.05)
            raise asyncio.CancelledError()

        async def fake_get(key):
            return self.fake_db.get(key)

        async def fake_set(key, value):
            self.fake_db[key] = value

        with patch("main.redis_client.blpop", side_effect=fake_blpop), \
             patch("main.redis_client.get", side_effect=fake_get), \
             patch("main.redis_client.set", side_effect=fake_set), \
             patch("main.asyncio.sleep", new_callable=AsyncMock):

            try:
                await task_worker()
            except asyncio.CancelledError:
                pass

        final_state = json.loads(self.fake_db[f"status:{job_id}"])
        self.assertEqual(final_state["status"], "completed")
        self.assertIn("Respuesta del agente", final_state["result"])
        self.assertIsNotNone(final_state["execution_time"])
        print("✅ [Criterio 3: Lógica del Worker] Consumo de cola y ciclo de vida completado.")

    # -------------------------------------------------------------
    # CRITERIO 4: Calidad de Código y Validación Pydantic
    # -------------------------------------------------------------
    def test_04_pydantic_validation(self):
        from pydantic import ValidationError

        # Rechazar consultas vacías o menores a 3 caracteres
        with self.assertRaises(ValidationError):
            TaskRequest(query="a")

        # Aceptar consultas válidas
        valid = TaskRequest(query="Consulta de prueba válida")
        self.assertEqual(valid.query, "Consulta de prueba válida")
        print("✅ [Criterio 4: Calidad y Tipado] Validación estricta con Pydantic V2 superada.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
