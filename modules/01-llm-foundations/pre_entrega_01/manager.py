import os
from typing import Literal

from clients.anthropic_client import AnthropicClient
from clients.base import BaseLLMClient
from clients.openai_client import OpenAIClient
from schemas import ModelConfig


class AsyncLLMManager:
    """
    Factory que inicializa y devuelve el cliente correcto (OpenAI o Anthropic)
    basado en la configuración proporcionada.
    """

    @staticmethod
    def create_client(
        provider: Literal["openai", "anthropic"],
        config: ModelConfig = None
    ) -> BaseLLMClient:
        """
        Crea e inicializa el cliente asíncrono solicitado.
        """
        if config is None:
            config = ModelConfig()

        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY no encontrada en las variables de entorno.")
            # Permite usar un modelo específico si se desea, o usar el por defecto del cliente
            return OpenAIClient(api_key=api_key, config=config)

        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY no encontrada en las variables de entorno.")
            return AnthropicClient(api_key=api_key, config=config)

        else:
            raise ValueError(f"Proveedor '{provider}' no soportado. Usa 'openai' o 'anthropic'.")
