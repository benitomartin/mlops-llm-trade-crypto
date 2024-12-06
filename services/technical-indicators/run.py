from candle import update_candles
from loguru import logger
from quixstreams import Application


def main(
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_consumer_group: str,
    # max_candles_in_state: int,
):
    logger.info('Hello from technical-indicators!')

    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
    )

    # Define the input and output topics of our streaming application
    input_topic = app.topic(
        name=kafka_input_topic,
        value_deserializer='json',
    )
    output_topic = app.topic(
        name=kafka_output_topic,
        value_serializer='json',
    )

    # Create a Streaming DataFrame so we can start transforming data in real time
    sdf = app.dataframe(topic=input_topic)

    # # Update the list of candles in the state
    sdf = sdf.apply(update_candles, stateful=True)

    # # Compute the technical indicators from the candles in the state
    # sdf = sdf.apply(compute_indicators, stateful=True)

    sdf = sdf.update(lambda value: logger.debug(f'Final message: {value}'))

    # Send the final messages to the output topic
    sdf = sdf.to_topic(output_topic)

    app.run()


if __name__ == '__main__':
    from config import config

    main(
        kafka_broker_address=config.kafka_broker_address,
        kafka_input_topic=config.kafka_input_topic,
        kafka_output_topic=config.kafka_output_topic,
        kafka_consumer_group=config.kafka_consumer_group,
        # max_candles_in_state=config.max_candles_in_state,
    )
