from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Configuration for the news service.
    """

    model_config = SettingsConfigDict(env_file='settings.env')
    kafka_broker_address: str
    kafka_topic: str
    polling_interval_sec: Optional[int] = 10


config = Config()


class CryptopanicConfig(BaseSettings):
    """
    Configuration for the Cryptopanic API.
    """

    model_config = SettingsConfigDict(env_file='cryptopanic_credentials.env')
    api_key: str


cryptopanic_config = CryptopanicConfig()
