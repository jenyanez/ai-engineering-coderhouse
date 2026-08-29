import time
import requests

API_URL = "http://localhost:8000"


def simulate_client_polling():
    """Simula una consulta de usuario con patrón de Polling asíncrono."""
    print("=" * 60)
    print("🚀 [Cliente] Iniciando prueba de Escalabilidad Asíncrona")
    print("=" * 60)

    # 1. Enviar solicitud de procesamiento
    query = "¿Cuál es el impacto financiero del mercado de IA en 2025?"
    print(f"\n1. Enviando petición POST a /process...")
    print(f"   Query: '{query}'")

    start_time = time.time()
    try:
        response = requests.post(f"{API_URL}/process", json={"query": query})
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: No se pudo conectar con la API en {API_URL}.")
        print("   Asegúrate de que la API esté corriendo (`python main.py`).")
        return

    post_latency = time.time() - start_time
    data = response.json()
    job_id = data.get("job_id")

    print(f"   Status Code: {response.status_code} (Accepted)")
    print(f"   Respuesta inmediata en: {post_latency * 1000:.2f} ms")
    print(f"   Job ID recibido: {job_id}")
    print(f"   Estado inicial: {data.get('status')}")

    # 2. Polling periódico al endpoint /status/{job_id}
    print(f"\n2. Iniciando Polling sobre /status/{job_id}...")
    max_retries = 15
    for attempt in range(1, max_retries + 1):
        time.sleep(1)
        status_res = requests.get(f"{API_URL}/status/{job_id}")
        status_data = status_res.json()
        current_status = status_data.get("status")
        elapsed = time.time() - start_time

        print(f"   [Intento {attempt}] ({elapsed:.1f}s) Estado: {current_status}")

        if current_status == "completed":
            print("\n" + "=" * 60)
            print("🎉 TAREA COMPLETADA CON ÉXITO")
            print("=" * 60)
            print(f"Resultado final:")
            print(f"'{status_data.get('result')}'")
            print(f"Tiempo total transcurrido: {elapsed:.2f} segundos")
            return

    print("⚠️ Timeout: La tarea tardó más de lo esperado.")


if __name__ == "__main__":
    simulate_client_polling()
