from loguru import logger

from kraken_api.mock import KrakenMockAPI


def main():
    """
    It does 2 things:
    1. Reads trades from the Kraken API and
    2. Pushes them to a Kafka topic.

    Args:
        kafka_broker_address: str
        kafka_topic: str
        kraken_api: Union[KrakenWebsocketAPI, KrakenMockAPI]

    Returns:
        None
    """

    logger.info('Start the trades service')

    # Initialize the Kraken API
    kraken_api = KrakenMockAPI(pair='BTC/USD')

    while True:
        trades = kraken_api.get_trades()

        for trade in trades:
            logger.info(f'Pushed trade to Kafka: {trade}')


if __name__ == '__main__':
    main()
