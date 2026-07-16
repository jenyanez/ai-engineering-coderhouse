from typing import AsyncGenerator, List

import anthropic
from anthropic import AsyncAnthropic

from clients.base import BaseLLMClient
from schemas import ChatMessage, ModelResponse


class AnthropicClient(BaseLLMClient):
    """
    Implementación del cliente para la API de Anthropic.
    """

    def __init__(self, api_key: str, model_name: str = "claude-3-5-sonnet-20241022", config=None):
        super().__init__(api_key, model_name, config)
        # Inicializa el cliente oficial asíncrono
        self.client = AsyncAnthropic(api_key=self.api_key)

    def _format_messages(self, messages: List[ChatMessage]):
        """
        Anthropic maneja el 'system' prompt aparte de los mensajes de la conversación.
        """
        system_prompt = ""
        conversation = []
        
        for msg in messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                conversation.append({"role": msg.role, "content": msg.content})
                
        return system_prompt, conversation

    async def generate(self, messages: List[ChatMessage]) -> ModelResponse:
        system, formatted_messages = self._format_messages(messages)
        
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                system=system,
                messages=formatted_messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
            )
            
            return ModelResponse(
                content=response.content[0].text,
                provider="anthropic",
                model_used=self.model_name,
                finish_reason=response.stop_reason,
            )

        except anthropic.RateLimitError as e:
            return ModelResponse(
                content=f"[Error de Anthropic] Rate limit excedido: {str(e)}",
                provider="anthropic",
                model_used=self.model_name,
                finish_reason="rate_limit_error"
            )
        except anthropic.APIConnectionError as e:
            return ModelResponse(
                content=f"[Error de red] Problema conectando a Anthropic: {str(e)}",
                provider="anthropic",
                model_used=self.model_name,
                finish_reason="connection_error"
            )
        except Exception as e:
            return ModelResponse(
                content=f"[Error inesperado] {str(e)}",
                provider="anthropic",
                model_used=self.model_name,
                finish_reason="unknown_error"
            )

    async def stream(self, messages: List[ChatMessage]) -> AsyncGenerator[str, None]:
        system, formatted_messages = self._format_messages(messages)
        
        try:
            async with self.client.messages.stream(
                model=self.model_name,
                system=system,
                messages=formatted_messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
            ) as stream:
                async for text_chunk in stream.text_stream:
                    yield text_chunk

        except anthropic.RateLimitError as e:
            yield f"\n[Stream interrumpido: Rate limit de Anthropic -> {str(e)}]"
        except Exception as e:
            yield f"\n[Stream interrumpido: Error inesperado -> {str(e)}]"
