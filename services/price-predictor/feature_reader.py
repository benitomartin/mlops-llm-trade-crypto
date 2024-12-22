from datetime import datetime, timedelta
from typing import Optional

import hopsworks
from hsfs.feature_group import FeatureGroup
from hsfs.feature_store import FeatureStore
from hsfs.feature_view import FeatureView
from loguru import logger


class FeatureReader:
    """
    Reads features from our 2 features groups
    - technical_indicators
    - news_signals
    and preprocess it so that it has the format (features, target) we need for
    training and for inference.
    """

    def __init__(
        self,
        hopsworks_project_name: str,
        hopsworks_api_key: str,
        feature_view_name: str,
        feature_view_version: int,
        pair_to_predict: str,
        candle_seconds: int,
        pairs_as_features: list[str],
        prediction_seconds: int,
        llm_model_name_news_signals: str,
        # Optional. Only required if the feature view above does not exist and needs
        # to be created
        technical_indicators_feature_group_name: Optional[str] = None,
        technical_indicators_feature_group_version: Optional[int] = None,
        news_signals_feature_group_name: Optional[str] = None,
        news_signals_feature_group_version: Optional[int] = None,
    ):
        """ """
        self.pair_to_predict = pair_to_predict
        self.candle_seconds = candle_seconds
        self.pairs_as_features = pairs_as_features
        self.prediction_seconds = prediction_seconds
        self.llm_model_name_news_signals = llm_model_name_news_signals

        # connect to the Hopsworks Feature Store
        self._feature_store = self._get_feature_store(
            hopsworks_project_name,
            hopsworks_api_key,
        )

        if technical_indicators_feature_group_name is not None:
            logger.info(
                f'Attempt to create the feature view {feature_view_name}-{feature_view_version}'
            )
            self._feature_view = self._create_feature_view(
                feature_view_name,
                feature_view_version,
                technical_indicators_feature_group_name,
                technical_indicators_feature_group_version,
                news_signals_feature_group_name,
                news_signals_feature_group_version,
            )
        else:
            self._feature_view = self._get_feature_view(
                feature_view_name,
                feature_view_version,
            )

    def _get_feature_group(self, name: str, version: int) -> FeatureGroup:
        """
        Returns a feature group object given its name and version.
        """
        return self._feature_store.get_feature_group(
            name=name,
            version=version,
        )

    def _create_feature_view(
        self,
        feature_view_name: str,
        feature_view_version: int,
        technical_indicators_feature_group_name: str,
        technical_indicators_feature_group_version: int,
        news_signals_feature_group_name: str,
        news_signals_feature_group_version: int,
    ) -> FeatureView:
        # we get the 2 features groups we need to join
        technical_indicators_fg = self._get_feature_group(
            technical_indicators_feature_group_name,
            technical_indicators_feature_group_version,
        )
        print(f"A: {technical_indicators_fg}")

        news_signals_fg = self._get_feature_group(
            news_signals_feature_group_name,
            news_signals_feature_group_version,
        )
        print(f"B: {news_signals_fg}")


        # # Query in 3-steps
        # # Step 1. Filter rows from news_signals_fg for the model_name we need and drop the model_name column
        # news_signal_query = news_signals_fg \
        #     .select_all() \
        #     .filter(news_signals_fg.model_name == self.llm_model_name_news_signals)

        # # Step 2. Filter rows from technical_indicators_fg for the candle_seconds we need
        # technical_indicators_query = technical_indicators_fg \
        #     .select_all() \
        #     .filter(technical_indicators_fg.candle_seconds == self.candle_seconds) \

        # # Step 3. Join the 2 queries on the `coin` column
        # query = technical_indicators_query.join(
        #     news_signal_query,
        #     on=["coin"],
        #     join_type="left",
        #     prefix='news_signals_',
        # )

        # # Attempt to create the feature view in one query
        # query = technical_indicators_fg.select_all() \
        #     .join(
        #         news_signals_fg.select_all(),
        #         on=["coin"],
        #         join_type="left",
        #         prefix='news_signals_',
            # ) \
            # .filter(
            #     (technical_indicators_fg.candle_seconds == self.candle_seconds) & \
            #     (news_signals_fg.model_name == self.llm_model_name_news_signals)
            # )

        # # TODO: remove this once we have the correct query
        query = technical_indicators_fg.select_all().filter(
            technical_indicators_fg.candle_seconds == self.candle_seconds
        )

        # # This query works
        # query = technical_indicators_fg \
        #     .select_all(
        #         ["pair", "timestamp_ms", "close", "candle_seconds"]
        #     )

        # attempt to create the feature view
        feature_view = self._feature_store.create_feature_view(
            name=feature_view_name,
            version=feature_view_version,
            query=query,
            logging_enabled=True,
        )
        logger.info(f'Feature view {feature_view_name}-{feature_view_version} created')

        return feature_view

    def _get_feature_view(
        self, feature_view_name: str, feature_view_version: int
    ) -> FeatureView:
        """
        Returns a feature view object given its name and version.
        """
        # raise NotImplementedError('Feature view creation is not supported yet')
        return self._feature_store.get_feature_view(
            name=feature_view_name,
            version=feature_view_version,
        )

    def _get_feature_store(self, project_name: str, api_key: str) -> FeatureStore:
        """
        Returns a feature store object.
        """
        logger.info('Getting feature store')
        project = hopsworks.login(project=project_name, api_key_value=api_key)
        fs = project.get_feature_store()
        print(f"fs: {fs}")
        return fs

    def get_training_data(self, days_back: int):
        """
        Use the self._feature_view to get the training data going back `days_back` days.
        """
        logger.info(f'Getting training data going back {days_back} days')
        return self._feature_view.get_batch_data(
            start_time=datetime.now() - timedelta(days=days_back),
            end_time=datetime.now(),
        )

    #     # TODO: split these features into groups of `pairs` and then stack them
    #     # horizontally
    #     # On Monday

    # def get_inference_data(self):
    #     pass


if __name__ == '__main__':
    from config import hopsworks_credentials

    print(hopsworks_credentials)

    feature_reader = FeatureReader(
        hopsworks_project_name=hopsworks_credentials.hopsworks_project_name,
        hopsworks_api_key=hopsworks_credentials.hopsworks_api_key,
        feature_view_name='price_predictor',
        feature_view_version=1,
        pair_to_predict='BTC/USD',
        candle_seconds=60,
        pairs_as_features=['BTC/USD', 'ETH/USD'],
        prediction_seconds=60 * 5,
        llm_model_name_news_signals='dummy',
        # Optional. Only required if the feature view above does not exist and needs
        # to be created
        technical_indicators_feature_group_name='technical_indicators',
        technical_indicators_feature_group_version=1,
        news_signals_feature_group_name='news_signals',
        news_signals_feature_group_version=1,
    )


    training_data = feature_reader.get_training_data(days_back=1000)
    print(training_data)
    # breakpoint()
