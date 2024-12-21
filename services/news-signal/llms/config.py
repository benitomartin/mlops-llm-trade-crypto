from pydantic_settings import BaseSettings, SettingsConfigDict


class AnthropicConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='anthropic_credentials.env',
        env_file_encoding='utf-8',
    )
    llm_name: str
    api_key: str


# config = AnthropicConfig()


class OllamaConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='ollama.env',
        env_file_encoding='utf-8',
    )
    llm_name: str
    ollama_base_url: str
