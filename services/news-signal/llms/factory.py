from typing import Literal

from .base import BaseNewsSignalExtractor
from .claude import ClaudeNewsSignalExtractor
from .ollama_model import OllamaNewsSignalExtractor


def get_llm(llm_name: Literal['anthropic', 'ollama']) -> BaseNewsSignalExtractor:
    """
    Returns the LLM we want for the news signal extractor

    Args:
        model_provider: The model provider to use

    Returns:
        The LLM we want for the news signal extractor
    """
    if llm_name == 'anthropic':
        from .config import AnthropicConfig

        config = AnthropicConfig()

        return ClaudeNewsSignalExtractor(
            llm_name=config.llm_name,
            api_key=config.api_key,
        )

    elif llm_name == 'ollama':
        from .config import OllamaConfig

        config = OllamaConfig()

        return OllamaNewsSignalExtractor(
            llm_name=config.llm_name,
            base_url=config.ollama_base_url,

        )

    else:
        raise ValueError(f'Unsupported model provider: {llm_name}')
