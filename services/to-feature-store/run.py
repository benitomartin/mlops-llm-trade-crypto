from loguru import logger
from quixstreams import Application
from quixstreams.sinks.core.csv import CSVSink


def main(
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_consumer_group: str,
    feature_group_name: str,
    feature_group_version: int,
):
    """
    2 things:
    1. Read messages from Kafka topic
    2. Push messages to Feature Store

    """
    logger.info('Hello from to-feature-store!')

    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
    )
    input_topic = app.topic(kafka_input_topic, value_deserializer='json')

    # Push messages to Feature Store
    # TODO: Implement
    # Initialize a CSV sink with a file path
    csv_sink = CSVSink(path='technical_indicators.csv')

    sdf = app.dataframe(input_topic)

    # Do some processing here ...
    # We need to extract the features we want to push to the feature store
    # TODO: Implement
    # Sink data to a CSV file
    sdf.sink(csv_sink)

    app.run()


if __name__ == '__main__':
    from config import config

    main(
        kafka_broker_address=config.kafka_broker_address,
        kafka_input_topic=config.kafka_input_topic,
        kafka_consumer_group=config.kafka_consumer_group,
        feature_group_name=config.feature_group_name,
        feature_group_version=config.feature_group_version,
    )
