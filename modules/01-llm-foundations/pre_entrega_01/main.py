import asyncio
import os
import sys

from dotenv import load_dotenv

from manager import AsyncLLMManager
from schemas import ChatMessage, ModelConfig

# Cargar variables de entorno desde .env
load_dotenv()


async def run_tests(provider_name: str):
    print(f"\n{'='*60}")
    print(f"Iniciando pruebas con proveedor: {provider_name.upper()}")
    print(f"{'='*60}")

    # 1. Configuración validada por Pydantic
    try:
        config = ModelConfig(temperature=0.7, max_tokens=150)
    except Exception as e:
        print(f"Error de configuración: {e}")
        return

    # 2. Inicialización mediante el Factory
    try:
        client = AsyncLLMManager.create_client(provider=provider_name, config=config)
    except ValueError as e:
        print(f"Error inicializando cliente: {e}")
        return

    # 3. Definición del input
    messages = [
        ChatMessage(role="system", content="Eres un asistente experto en física."),
        ChatMessage(role="user", content="¿Qué es la entropía? Explícalo en 2 oraciones breves."),
    ]

    # --- PRUEBA 1: Generación Completa (Normal) ---
    print("\n--- 1. Generación Normal ---")
    print("Enviando petición y esperando respuesta completa...")
    
    response = await client.generate(messages)
    
    if response.finish_reason in ["rate_limit_error", "connection_error", "unknown_error"]:
        print(f"❌ Fallo controlado: {response.content}")
    else:
        print(f"✅ Respuesta ({response.model_used}):")
        print(f"   {response.content}")


    # --- PRUEBA 2: Generación en Streaming ---
    print("\n--- 2. Generación en Streaming ---")
    print("Recibiendo tokens en tiempo real:")
    
    try:
        async for chunk in client.stream(messages):
            # Imprime cada chunk directamente en la consola, sin salto de línea
            sys.stdout.write(chunk)
            sys.stdout.flush()
        print()  # Salto de línea final
    except Exception as e:
         print(f"\n❌ Error durante el streaming: {e}")


async def main():
    print("🚀 Iniciando cliente de LLM unificado...\n")
    
    # Probar OpenAI (requiere OPENAI_API_KEY en .env)
    if os.getenv("OPENAI_API_KEY"):
        await run_tests("openai")
    else:
        print("⚠️ OPENAI_API_KEY no configurada. Saltando pruebas de OpenAI.")
        
    # Probar Anthropic (requiere ANTHROPIC_API_KEY en .env)
    if os.getenv("ANTHROPIC_API_KEY"):
        await run_tests("anthropic")
    else:
        print("⚠️ ANTHROPIC_API_KEY no configurada. Saltando pruebas de Anthropic.")
        
    print("\n✅ Pruebas finalizadas.")


if __name__ == "__main__":
    asyncio.run(main())
