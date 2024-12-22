from loguru import logger

from feature_reader import FeatureReader


def train(
    hopsworks_project_name: str,
    hopsworks_api_key: str,
    feature_view_name: str,
    feature_view_version: int,
    pair_to_predict: str,
    candle_seconds: int,
    pairs_as_features: list[str],
    prediction_seconds: int,
    llm_model_name_news_signals: str,
    days_back: int,
):
    """
    Does the following:
    1. Reads feature data from the Feature Store
    2. Splits the data into training and testing sets
    3. Trains a model on the training set
    4. Evaluates the model on the testing set
    5. Saves the model to the model registry

    Everything is instrumented with CometML.


    """
    logger.info('Hello from the ML model training job...')

    # 1. Read feature data from the Feature Store
    feature_reader = FeatureReader(
        hopsworks_project_name,
        hopsworks_api_key,
        feature_view_name,
        feature_view_version,
        pair_to_predict,
        candle_seconds,
        pairs_as_features,
        prediction_seconds,
        llm_model_name_news_signals,
    )
    logger.info(f'Reading feature data for {days_back} days back...')
    training_data = feature_reader.get_training_data(days_back=days_back)
    logger.info(f'Got {len(training_data)} rows')
    breakpoint()

    # 2. Split the data into training and testing sets

    # 3. Train a model on the training set

    # 4. Evaluate the model on the testing set

    # 5. Save the model to the model registry


if __name__ == '__main__':
    from config import hopsworks_credentials, training_config

    train(
        hopsworks_project_name=hopsworks_credentials.hopsworks_project_name,
        hopsworks_api_key=hopsworks_credentials.hopsworks_api_key,
        feature_view_name=training_config.feature_view_name,
        feature_view_version=training_config.feature_view_version,
        pair_to_predict=training_config.pair_to_predict,
        candle_seconds=training_config.candle_seconds,
        pairs_as_features=training_config.pairs_as_features,
        prediction_seconds=training_config.prediction_seconds,
        llm_model_name_news_signals=training_config.llm_model_name_news_signals,
        days_back=training_config.days_back,
    )
