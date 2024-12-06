import signal
import sys

from loguru import logger
from quixstreams import Application

from kraken_api.websocket import KrakenWebsocketAPI


def signal_handler(sig, frame):
    logger.info('Shutting down trades service...')
    sys.exit(0)


# Set up signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
# signal.signal(signal.SIGTERM, signal_handler)


def main(kafka_broker_address: str, kafka_topic: str, kraken_api: KrakenWebsocketAPI):
    """
    Reads trade data from the Kraken WebSocket API and publishes it to a Kafka topic.

    Args:
        kafka_broker_address (str): The address of the Kafka broker (e.g., 'localhost:9092').
        kafka_topic (str): The name of the Kafka topic to which trade data will be published.
        kraken_api (KrakenWebsocketAPI): An instance of the KrakenWebsocketAPI class used to fetch trade data.
    """

    logger.info('Starting the trades service')

    # Initialize the Quix Streams application.
    # This class handles all the low-level details to connect to Kafka.
    # https://quix.io/docs/quix-streams/producer.html
    app = Application(broker_address=kafka_broker_address)
    topic = app.topic(name=kafka_topic, value_serializer='json')
    producer = app.get_producer()

    try:
        while True:
            trades = kraken_api.get_trades()

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
        kraken_api.close()


if __name__ == '__main__':
    from config import config

    kraken_api = KrakenWebsocketAPI(pairs=config.pairs)

    try:
        main(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic=config.kafka_topic,
            kraken_api=kraken_api,
        )
    except Exception as e:
        logger.error(f'Fatal error in main: {e}')
