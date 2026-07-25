"""
main.py — Mini-script de prueba asíncrono para el pipeline de extracción.

Ejecuta process_text() con múltiples textos de prueba y valida
que la salida sea un objeto EntityExtraction correcto.
"""

import asyncio

from chain import process_text
from schemas import EntityExtraction


# Textos de prueba para validar el pipeline
TEST_CASES = [
    {
        "nombre": "Descripción de arquitectura",
        "texto": (
            "Nuestra API está construida con FastAPI y utiliza Redis como capa de "
            "caché para sesiones. La persistencia principal es PostgreSQL con "
            "conexiones manejadas por SQLAlchemy. En picos de tráfico, detectamos "
            "un cuello de botella en las conexiones concurrentes que saturan el "
            "pool de la base de datos, provocando timeouts de hasta 30 segundos."
        ),
    },
    {
        "nombre": "Log de error en producción",
        "texto": (
            "ERROR 2024-03-15 14:22:01 [kubernetes] Pod 'payment-service-7b4d' "
            "reiniciado 5 veces en los últimos 10 minutos. OOMKilled detectado. "
            "El contenedor Docker consume 2.1GB de RAM con un límite de 1GB. "
            "El servicio usa Node.js 20 con Express y se conecta a MongoDB Atlas "
            "mediante Mongoose. La cola de mensajes en RabbitMQ acumula 50k mensajes."
        ),
    },
    {
        "nombre": "Texto ambiguo (prueba de estrés)",
        "texto": (
            "El equipo está evaluando migrar parte del sistema legacy. Se menciona "
            "que Java podría reemplazarse por algo más moderno, pero no hay consenso. "
            "La base de datos actual funciona correctamente y no hay incidencias graves."
        ),
    },
]


async def main():
    """Ejecuta la batería de pruebas del pipeline."""

    print("=" * 60)
    print("Pre-entrega 2 — Pipeline de Extracción de Entidades Técnicas")
    print("=" * 60)

    passed = 0
    failed = 0

    for i, case in enumerate(TEST_CASES, 1):
        print(f"\n{'─' * 60}")
        print(f"Prueba {i}/{len(TEST_CASES)}: {case['nombre']}")
        print(f"{'─' * 60}")

        try:
            result = await process_text(case["texto"])

            # Verificaciones de integridad
            assert isinstance(result, EntityExtraction), (
                f"Se esperaba EntityExtraction, se obtuvo {type(result).__name__}"
            )
            assert len(result.tecnologias) >= 1, "La lista de tecnologías está vacía"
            assert result.nivel_de_criticidad in ("baja", "media", "alta"), (
                f"Nivel de criticidad inválido: {result.nivel_de_criticidad}"
            )

            # Impresión del resultado como JSON
            print(f"\nResultado (JSON):\n{result.model_dump_json(indent=2)}")
            print(f"\n✅ Prueba {i} superada")
            passed += 1

        except Exception as e:
            print(f"\n❌ Prueba {i} fallida — {type(e).__name__}: {e}")
            failed += 1

    # Resumen final
    print(f"\n{'=' * 60}")
    print(f"Resultado: {passed}/{len(TEST_CASES)} pruebas superadas")
    if failed == 0:
        print("✅ Todas las pruebas pasaron correctamente.")
    else:
        print(f"⚠️ {failed} prueba(s) fallida(s).")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
