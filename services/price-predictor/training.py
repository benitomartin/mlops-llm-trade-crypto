import pandas as pd
from loguru import logger
from sklearn.metrics import mean_absolute_error

from feature_reader import FeatureReader
from models.dummy_model import DummyModel


def train_test_split(
    data: pd.DataFrame,
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split the given `data` into 2 dataframes based on the `timestamp_ms` column
    such that
    > the first dataframe contains the first `train_size` rows
    > the second dataframe contains the remaining rows
    """
    train_size = int(len(data) * (1 - test_size))
    logger.info(f'train_size: {train_size}')

    train_df = data.iloc[:train_size]
    test_df = data.iloc[train_size:]

    logger.info(f'train_df: {train_df}')
    logger.info(f'test_df: {test_df}')

    return train_df, test_df


def train(
    hopsworks_project_name: str,
    hopsworks_api_key: str,
    feature_view_name: str,
    feature_view_version: int,
    pair_to_predict: str,
    candle_seconds: int,
    pairs_as_features: list[str],
    technical_indicators_as_features: list[str],
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
        technical_indicators_as_features,
        prediction_seconds,
        llm_model_name_news_signals,
    )

    logger.info(f'Reading feature data for {days_back} days back...')
    features_and_target = feature_reader.get_training_data(days_back=days_back)
    logger.info(f'Got {len(features_and_target)} rows')

    # breakpoint()

    # 2. Split the data into training and testing sets
    train_df, test_df = train_test_split(features_and_target, test_size=0.2)

    # 3. Split into features and target
    X_train = train_df.drop(columns=['target'])
    y_train = train_df['target']
    X_test = test_df.drop(columns=['target'])
    y_test = test_df['target']

    # experiment.log_parameters(
    #     {
    #         'X_train': X_train.shape,
    #         'y_train': y_train.shape,
    #         'X_test': X_test.shape,
    #         'y_test': y_test.shape,
    #     }
    # )

    # 3. Evaluate quick baseline models

    # Dummy model based on current close price
    # on the test set
    y_test_pred = DummyModel(from_feature='close').predict(X_test)
    mae_dummy_model = mean_absolute_error(y_test, y_test_pred)
    logger.info(f'MAE of dummy model based on close price: {mae_dummy_model}')
    # experiment.log_metric('mae_dummy_model', mae_dummy_model)
    # on the training set
    y_train_pred = DummyModel(from_feature='close').predict(X_train)
    mae_dummy_model_train = mean_absolute_error(y_train, y_train_pred)
    logger.info(
        f'MAE of dummy model based on close price on training set: {mae_dummy_model_train}'
    )
    # experiment.log_metric('mae_train_dummy_model', mae_dummy_model_train)

    # Dummy model based on sma_7
    if 'sma_7' in technical_indicators_as_features:
        y_test_pred = DummyModel(from_feature='sma_7').predict(X_test)
        mae_dummy_model = mean_absolute_error(y_test, y_test_pred)
        logger.info(f'MAE of dummy model based on sma_7: {mae_dummy_model}')
        # experiment.log_metric('mae_dummy_model_sma_7', mae_dummy_model)

    # Dummy model based on sma_14
    if 'sma_14' in technical_indicators_as_features:
        y_test_pred = DummyModel(from_feature='sma_14').predict(X_test)
        mae_dummy_model = mean_absolute_error(y_test, y_test_pred)
        logger.info(f'MAE of dummy model based on sma_14: {mae_dummy_model}')
        # experiment.log_metric('mae_dummy_model_sma_14', mae_dummy_model)


def main():
    from config import (
        # comet_ml_credentials,
        hopsworks_credentials,
        training_config,
    )

    train(
        hopsworks_project_name=hopsworks_credentials.hopsworks_project_name,
        hopsworks_api_key=hopsworks_credentials.hopsworks_api_key,
        feature_view_name=training_config.feature_view_name,
        feature_view_version=training_config.feature_view_version,
        pair_to_predict=training_config.pair_to_predict,
        candle_seconds=training_config.candle_seconds,
        pairs_as_features=training_config.pairs_as_features,
        technical_indicators_as_features=training_config.technical_indicators_as_features,
        prediction_seconds=training_config.prediction_seconds,
        llm_model_name_news_signals=training_config.llm_model_name_news_signals,
        days_back=training_config.days_back,
        # comet_ml_api_key=comet_ml_credentials.api_key,
        # comet_ml_project_name=comet_ml_credentials.project_name,
        # hyperparameter_tuning_search_trials=training_config.hyperparameter_tuning_search_trials,
        # hyperparameter_tuning_n_splits=training_config.hyperparameter_tuning_n_splits,
        # model_status=training_config.model_status,
    )


if __name__ == '__main__':
    main()
