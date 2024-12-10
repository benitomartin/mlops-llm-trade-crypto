import hopsworks
import pandas as pd
from quixstreams.sinks.base import BatchingSink, SinkBackpressureError, SinkBatch


class HopsworksFeatureStoreSink(BatchingSink):
    """
    Some sink writing data to a database
    """

    def __init__(
        self,
        api_key: str,
        project_name: str,
        feature_group_name: str,
        feature_group_version: int,
        feature_group_primary_keys: list[str],
        feature_group_event_time: str,
    ):
        """
        Establish a connection to the Hopsworks Feature Store
        """
        self.feature_group_name = feature_group_name
        self.feature_group_version = feature_group_version

        # Establish a connection to the Hopsworks Feature Store
        project = hopsworks.login(project=project_name, api_key_value=api_key)
        self._fs = project.get_feature_store()

        # Get the feature group
        self._feature_group = self._fs.get_or_create_feature_group(
            name=feature_group_name,
            version=feature_group_version,
            primary_key=feature_group_primary_keys,
            event_time=feature_group_event_time,
            online_enabled=True,
        )

        # Call the parent BatchingSink constructor to initialize the batches
        super().__init__()

    def write(self, batch: SinkBatch):
        # Transform the batch into a pandas DataFrame
        data = [item.value for item in batch]
        data = pd.DataFrame(data)

        # breakpoint()

        try:
            # Try to write data to the db
            self._feature_group.insert(data)
        except Exception as err:  # Capture the original exception
            # In case of timeout, tell the app to wait for 30s
            # and retry the writing later
            raise SinkBackpressureError(
                retry_after=30.0,
                topic=batch.topic,
                partition=batch.partition,
            ) from err  # Chain the exception
