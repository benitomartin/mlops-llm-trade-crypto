from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TrainingConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file='training.settings.env')

    feature_view_name: str = Field(description='The name of the feature view')
    feature_view_version: int = Field(description='The version of the feature view')
    pair_to_predict: str = Field(description='The pair to train the model on')
    candle_seconds: int = Field(description='The number of seconds per candle')
    prediction_seconds: int = Field(
        description='The number of seconds into the future to predict'
    )

    pairs_as_features: list[str] = Field(
        description='The pairs to use for the features'
    )

    technical_indicators_as_features: list[str] = Field(
        description='The technical indicators to use for from the technical_indicators feature group'
    )

    days_back: int = Field(
        description='The number of days to consider for the historical data'
    )

    llm_model_name_news_signals: str = Field(
        description='The name of the LLM model to use for the news signals'
    )


training_config = TrainingConfig()


class HopsworksCredentials(BaseSettings):
    model_config = SettingsConfigDict(env_file='hops_credentials.env')
    hopsworks_api_key: str
    hopsworks_project_name: str


hopsworks_credentials = HopsworksCredentials()
