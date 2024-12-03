from typing import List
import json
from loguru import logger

from websocket import create_connection

from .trade import Trade

class KrakenWebsocketAPI:

    URL = "wss://ws.kraken.com/v2" # See Channel: https://docs.kraken.com/api/docs/websocket-v2/trade 

    def __init__(self, pairs: List[str]):
        self.pairs = pairs
        self._connect()

    def _connect(self):
        """Initializes the WebSocket connection and subscribes to the API."""
        try:
            logger.info("Connecting to Kraken WebSocket...")
            self._ws_client = create_connection(self.URL)
            self._subscribe()
            logger.info("Connected to Kraken WebSocket.")
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            raise RuntimeError("WebSocket connection failed") from e

        # breakpoint()

    def get_trades(self) -> List[Trade]:
        """
        Fetches the trades from the Kraken WebSocket API and returns them as a list of Trade objects.
        """
        try:
            # Receive the data from the WebSocket
            data = self._ws_client.recv()

            if 'heartbeat' in data:
                logger.info("Heartbeat received")
                return []
            
            # Transform raw string into a JSON object
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

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return []

        except KeyError as e:
            logger.error(f"Missing expected key in WebSocket data: {e}")
            return []

        except Exception as e:
            logger.error(f"Unexpected error in WebSocket trade fetch: {e}")
            self.reconnect()
            return []


    def _subscribe(self):
        """
        Subscribes to the websocket and waits for the initial snapshot.
        """
        # Send a subscribe message to the websocket
        # json.dumps() function will convert a subset of Python objects into a json string
        # A string is required by the websocket
        # https://websocket-client.readthedocs.io/en/latest/examples.html#sending-connection-close-status-codes
        try:
            self._ws_client.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": "trade",
                    "symbol": self.pairs,
                    "snapshot": True
                }
            }))
            # Wait for confirmation of subscription
            for pair in self.pairs:
                confirmation = self._ws_client.recv()
                logger.debug(f"Subscription confirmation: {confirmation}")
                
        except Exception as e:
            logger.error(f"Error during WebSocket subscription: {e}")
            raise RuntimeError("WebSocket subscription failed") from e


    def reconnect(self):
        """Re-establishes the WebSocket connection and resubscribes."""
        try:
            logger.info("Attempting to reconnect to Kraken WebSocket...")
            self._ws_client.close()
        except Exception as e:
            logger.warning(f"Error closing WebSocket: {e}")

        self._connect()
