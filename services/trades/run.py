import asyncio
from loguru import logger
from quixstreams import Application

from kraken_api.websocket import KrakenWebsocketAPI
import signal
import sys

def signal_handler(sig, frame):
    logger.info("Shutting down trades service...")
    loop.stop()
    sys.exit(0)

# Set up signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

async def shutdown_with_timeout(app, kraken_api, timeout=10):
    """
    Gracefully shut down Quix application and Kraken WebSocket client with timeout.
    
    Args:
        app: Quix Streams application
        kraken_api: Kraken WebSocket API client
        timeout: Timeout in seconds for graceful shutdown (default: 10)
    """
    try:
        # Wait for app to close gracefully
        await asyncio.wait_for(app.close(), timeout)
    except asyncio.TimeoutError:
        logger.error("Timed out while closing Quix Streams application")

    try:
        # Close WebSocket client gracefully
        await asyncio.wait_for(kraken_api._ws_client.close(), timeout)
    except asyncio.TimeoutError:
        logger.error("Timed out while closing Kraken WebSocket client")


async def main(kafka_broker_address: str, kafka_topic: str, kraken_api: KrakenWebsocketAPI):
    """
    It does 2 things:
    1. Reads trades from the Kraken API and
    2. Pushes them to a Kafka topic.

    Args:
        kafka_broker_address: str
        kafka_topic: str
        kraken_api: KrakenWebsocketAPI

    Returns:
        None
    """

    logger.info("Start the trades service")
    
    # Initialize the Quix Streams application.
    # This class handles all the low-level details to connect to Kafka.
    # https://quix.io/docs/quix-streams/producer.html
    app = Application(broker_address=kafka_broker_address)
    topic = app.topic(name=kafka_topic, value_serializer='json')
    
    producer = app.get_producer()  # Get the producer without async context manager

    try:
        while True:
            trades = await kraken_api.get_trades()


            for trade in trades:
                try:
                    message = topic.serialize(
                        key=trade.pair,
                        value=trade.to_str(),
                    )

                    producer.produce(
                        topic=topic.name, value=message.value, key=message.key
                    )
                    logger.info(f"Pushed trade to Kafka: {trade}")
                
                except Exception as e:
                    logger.error(f"Error producing trade to Kafka: {e}")
    
    finally:
        # Gracefully shut down the producer and WebSocket client
        await shutdown_with_timeout(app, kraken_api)

        
if __name__ == "__main__":
    from config import config

    kraken_api = KrakenWebsocketAPI(pairs=config.pairs)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        main(
            kafka_broker_address=config.kafka_broker_address,
            kafka_topic=config.kafka_topic,
            kraken_api=kraken_api
        )
    )
