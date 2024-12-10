import signal
import sys

from loguru import logger
from quixstreams import Application

from kraken_api.base import TradesAPI
from kraken_api.mock import KrakenMockAPI
from kraken_api.rest import KrakenRestAPI
from kraken_api.websocket import KrakenWebsocketAPI


def signal_handler(sig, frame):
    logger.info('Shutting down trades service...')
    sys.exit(0)


# Set up signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)


def main(kafka_broker_address: str, kafka_topic: str, trades_api: TradesAPI):
    """
    Reads trade data from the Kraken WebSocket API and publishes it to a Kafka topic.

    Args:
        kafka_broker_address (str): The address of the Kafka broker (e.g., 'localhost:9092').
        kafka_topic (str): The name of the Kafka topic to which trade data will be published.
        trades_api(TradesAPI): The Kraken API object with 2 methods: get_trades and is_done
    """

    logger.info('Starting the trades service')

    # Initialize the Quix Streams application.
    # This class handles all the low-level details to connect to Kafka.
    # https://quix.io/docs/quix-streams/producer.html
    app = Application(broker_address=kafka_broker_address)
    topic = app.topic(name=kafka_topic, value_serializer='json')
    producer = app.get_producer()

    try:
        while not trades_api.is_done():

            trades = trades_api.get_trades()

            for trade in trades:
                try:
                    message = topic.serialize(
                        key=trade.pair.replace(
                            '/', '-'
                        ),  # Slashes might git problems in Kafka
                        value=trade.to_dict(),
                    )
                    producer.produce(
                        topic=topic.name, value=message.value, key=message.key
                    )
                    logger.info(f'Pushed trade to Kafka: {trade}')

                except Exception as e:
                    logger.error(f'Error producing trade to Kafka: {e}')

    except KeyboardInterrupt:
        logger.info('Shutting down due to KeyboardInterrupt')
    finally:
        logger.info('Shutting down Quix Streams application')
        app.stop()
        # trades_api.close()


if __name__ == '__main__':
    from config import config

    # Initialize the Kraken API depending on the data source
    if config.data_source == 'live':
        kraken_api = KrakenWebsocketAPI(pairs=config.pairs)
    elif config.data_source == 'historical':
        kraken_api = KrakenRestAPI(pairs=config.pairs, last_n_days=config.last_n_days)

        # # TODO: remove this once we are done debugging the KrakenRestAPISinglePair
        # from kraken_api.rest import KrakenRestAPISinglePair
        # kraken_api = KrakenRestAPISinglePair(
        #     pair=config.pairs[0],
        #     last_n_days=config.last_n_days,
        # )

    elif config.data_source == 'test':
        kraken_api = KrakenMockAPI(pairs=config.pairs)
    else:
        raise ValueError(f'Invalid data source: {config.data_source}')

    try:
        main(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic=config.kafka_topic,
            trades_api=kraken_api,
        )
    except Exception as e:
        logger.error(f'Fatal error in main: {e}')
