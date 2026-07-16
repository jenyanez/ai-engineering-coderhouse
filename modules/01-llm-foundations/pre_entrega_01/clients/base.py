from abc import ABC, abstractmethod
from typing import AsyncGenerator, List

from schemas import ChatMessage, ModelConfig, ModelResponse


class BaseLLMClient(ABC):
    """
    Clase base abstracta que define el contrato (interfaz) para
    cualquier cliente de modelo de lenguaje.
    """

    def __init__(self, api_key: str, model_name: str, config: ModelConfig = None):
        self.api_key = api_key
        self.model_name = model_name
        self.config = config or ModelConfig()

    @abstractmethod
    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        """
        Genera una respuesta completa de una sola vez de forma asíncrona.
        """
        pass

    @abstractmethod
    async def stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        """
        Genera una respuesta como un flujo (stream) de tokens asíncrono.
        """
        pass
