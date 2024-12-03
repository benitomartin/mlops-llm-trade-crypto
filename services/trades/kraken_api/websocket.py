import json
from typing import List

import websockets
from loguru import logger

from .trade import Trade


class KrakenWebsocketAPI:

    URL = "wss://ws.kraken.com/v2"  # See Channel: https://docs.kraken.com/api/docs/websocket-v2/trade

    def __init__(self, pairs: List[str]):
        self.pairs = pairs
        self._ws_client = None

    async def _connect(self):
        """Asynchronously initializes the WebSocket connection and subscribes to the API."""
        try:
            logger.info("Connecting to Kraken WebSocket...")
            self._ws_client = await websockets.connect(self.URL)
            await self._subscribe()
            logger.info("Connected to Kraken WebSocket.")

        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            raise RuntimeError("WebSocket connection failed") from e

    async def get_trades(self) -> List[Trade]:
        """Fetches trades from the Kraken WebSocket asynchronously."""
        if self._ws_client is None:
            await self._connect()  # Ensure WebSocket is connected before fetching trades

        try:
            # Receive the data asynchronously from the WebSocket
            data = await self._ws_client.recv()

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
            await self.reconnect()  # Attempt reconnection if something goes wrong
            return []

    async def _subscribe(self):
        """Asynchronously subscribes to the Kraken WebSocket"""
        try:
            await self._ws_client.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": "trade",
                    "symbol": self.pairs,
                    "snapshot": True
                }
            }))
            # Wait for confirmation of subscription
            for _ in self.pairs:
                confirmation = await self._ws_client.recv()
                logger.debug(f"Subscription confirmation: {confirmation}")

        except Exception as e:
            logger.error(f"Error during WebSocket subscription: {e}")
            raise RuntimeError("WebSocket subscription failed") from e

    async def reconnect(self):
        """Asynchronously re-establishes the WebSocket connection and resubscribes."""
        if self._ws_client:
            try:
                logger.info("Attempting to reconnect to Kraken WebSocket...")
                await self._ws_client.close()
            except Exception as e:
                logger.warning(f"Error closing WebSocket: {e}")
        await self._connect()  # Attempt to reconnect
