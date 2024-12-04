import json
from typing import List

from loguru import logger
from websocket import WebSocketConnectionClosedException, create_connection

from .trade import Trade


class KrakenWebsocketAPI:
    URL = 'wss://ws.kraken.com/v2'  # See Channel: https://docs.kraken.com/api/docs/websocket-v2/trade

    def __init__(self, pairs: List[str]):
        self.pairs = pairs
        self._ws_client = None
        self._connect()

    def _connect(self):
        """Initializes the WebSocket connection and subscribes to the API."""
        try:
            logger.info('Connecting to Kraken WebSocket...')
            self._ws_client = create_connection(self.URL)
            self._subscribe()
            logger.info('Connected to Kraken WebSocket.')
        except Exception as e:
            logger.error(f'Failed to connect to WebSocket: {e}')
            raise RuntimeError('WebSocket connection failed') from e

    def get_trades(self) -> List[Trade]:
        """Fetches trades from the Kraken WebSocket."""
        try:
            data = self._ws_client.recv()

            if 'heartbeat' in data:
                logger.info('Heartbeat received')
                return []

            data = json.loads(data)
            trades_data = data.get('data', [])

            trades = [
                Trade.from_kraken_api_response(
                    pair=trade['symbol'],
                    price=trade['price'],
                    volume=trade['qty'],
                    timestamp=trade['timestamp'],
                )
                for trade in trades_data
            ]
            return trades
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f'Error decoding WebSocket data: {e}')
            return []
        except WebSocketConnectionClosedException:
            logger.warning('WebSocket connection closed; reconnecting...')
            self._connect()
            return []
        except Exception as e:
            logger.error(f'Unexpected error in WebSocket connection: {e}')
            raise  # Exception propagate to terminate the app

    def _subscribe(self):
        """Subscribes to the Kraken WebSocket."""
        try:
            subscription_message = json.dumps(
                {
                    'method': 'subscribe',
                    'params': {
                        'channel': 'trade',
                        'symbol': self.pairs,
                        'snapshot': True,
                    },
                }
            )
            self._ws_client.send(subscription_message)

            for _ in self.pairs:
                confirmation = self._ws_client.recv()
                logger.debug(f'Subscription confirmation: {confirmation}')
        except Exception as e:
            logger.error(f'Error during WebSocket subscription: {e}')
            raise RuntimeError('WebSocket subscription failed') from e

    def close(self):
        """Closes the WebSocket connection."""
        if self._ws_client:
            try:
                self._ws_client.close()
                logger.info('WebSocket connection closed.')
            except Exception as e:
                logger.warning(f'Error closing WebSocket: {e}')
