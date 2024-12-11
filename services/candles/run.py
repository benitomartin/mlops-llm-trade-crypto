from datetime import timedelta
from typing import Any, List, Literal, Optional, Tuple

from loguru import logger
from quixstreams import Application
from quixstreams.models import TimestampType


# Timestamp extractor must always return timestamp as an integer in milliseconds.
# https://quix.io/docs/quix-streams/windowing.html#updating-window-definitions
def custom_ts_extractor(
    value: Any,
    headers: Optional[List[Tuple[str, bytes]]],
    timestamp: float,
    timestamp_type: TimestampType,
) -> int:
    """
    Specifying a custom timestamp extractor to use the timestamp from the message payload instead of Kafka timestamp.
    """
    return value['timestamp_ms']


def init_candle(trade: dict) -> dict:
    """
    Initialize a candle with the first trade
    """
    return {
        'open': trade['price'],
        'high': trade['price'],
        'low': trade['price'],
        'close': trade['price'],
        'volume': trade['volume'],
        'timestamp_ms': trade['timestamp_ms'],
        'pair': trade['pair'],
    }


def update_candle(candle: dict, trade: dict) -> dict:
    """
    Update the candle with the latest trade
    """
    candle['close'] = trade['price']
    candle['high'] = max(
        candle['high'], trade['price']
    )  # Max of the candle high (current high of the candle) and new received trade price.
    candle['low'] = min(
        candle['low'], trade['price']
    )  # Max of the candle low (current low of the candle) and new received trade price.
    candle['volume'] += trade[
        'volume'
    ]  # Sum of the candle volume (current volume of the candle) and new received trade volume.
    candle['timestamp_ms'] = trade['timestamp_ms']
    candle['pair'] = trade['pair']
    return candle


def main(
    kafka_broker_address: str,
    kafka_input_topic: str,
    kafka_output_topic: str,
    kafka_consumer_group: str,
    candle_seconds: int,
    emit_incomplete_candles: bool,
    data_source: Literal['live', 'historical', 'test'],
):
    """
    3 steps:
    1. Ingests trades from Kafka
    2. Generates candles using tumbling windows and
    3. Outputs candles to Kafka

    Args:
        kafka_broker_address (str): Kafka broker address
        kafka_input_topic (str): Kafka input topic
        kafka_output_topic (str): Kafka output topic
        kafka_consumer_group (str): Kafka consumer group
        candle_seconds (int): Candle seconds
        emit_incomplete_candles (bool): Emit incomplete candles or just the final one
        data_source (Literal['live', 'historical', 'test']): Data source

    Returns:
        None
    """
    logger.info('Starting the candles service!')

    # Consuming data from Kafka
    # https://quix.io/docs/quix-streams/quickstart.html#getting-help
    # Initialize the Quix Streams application
    app = Application(
        broker_address=kafka_broker_address,
        consumer_group=kafka_consumer_group,
        auto_offset_reset='latest'
        if data_source == 'live'
        else 'earliest',  # If test or historical, start fetching data from the beginning (first message in the topic)
    )

    # Define the input and output topics
    input_topic = app.topic(
        name=kafka_input_topic,
        value_deserializer='json',
        timestamp_extractor=custom_ts_extractor,  # To use the "timestamp_ms" in window aggregations
    )

    output_topic = app.topic(
        name=kafka_output_topic,
        value_serializer='json',
    )

    # Create a Streaming DataFrame from the input topic
    sdf = app.dataframe(topic=input_topic)

    sdf = (
        # Define a tumbling window of 10 minutes
        sdf.tumbling_window(timedelta(seconds=candle_seconds))
        # Create a "reduce" aggregation with "reducer" and "initializer" functions
        .reduce(reducer=update_candle, initializer=init_candle)
    )

    if emit_incomplete_candles:
        # Emit all intermediate candles to make the system more responsive
        sdf = sdf.current()
    else:
        # Emit only the final candle
        sdf = sdf.final()

    # Extract open, high, low, close, volume, timestamp_ms, pair from the dataframe
    # to make them keys and not being nested in the value
    sdf['open'] = sdf['value']['open']
    sdf['high'] = sdf['value']['high']
    sdf['low'] = sdf['value']['low']
    sdf['close'] = sdf['value']['close']
    sdf['volume'] = sdf['value']['volume']
    sdf['timestamp_ms'] = sdf['value']['timestamp_ms']
    sdf['pair'] = sdf['value']['pair']

    # Extract window start and end timestamps
    sdf['window_start_ms'] = sdf['start']
    sdf['window_end_ms'] = sdf['end']

    # Keep only the relevant columns
    sdf = sdf[
        [
            'pair',
            'timestamp_ms',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'window_start_ms',
            'window_end_ms',
        ]
    ]

    # We add the candle_seconds to the dataframe
    sdf['candle_seconds'] = candle_seconds

    # With the following line, we can see the candle values in the logs
    # Otherwise you only see them in the output topic in Redpanda
    sdf = sdf.update(lambda value: logger.info(f'Candle: {value}'))
    # sdf = sdf.update(lambda value: breakpoint()) # Set to current() instead of final() above to see the candle values in the logs

    # Push the candle to the output topic
    sdf = sdf.to_topic(topic=output_topic)

    # Start the application
    app.run()


if __name__ == '__main__':
    from config import config

    main(
        kafka_broker_address=config.kafka_broker_address,
        kafka_input_topic=config.kafka_input_topic,
        kafka_output_topic=config.kafka_output_topic,
        kafka_consumer_group=config.kafka_consumer_group,
        candle_seconds=config.candle_seconds,
        emit_incomplete_candles=config.emit_incomplete_candles,
        data_source=config.data_source,
    )
