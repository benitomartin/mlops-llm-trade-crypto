from typing import List
import json
from loguru import logger

from websocket import create_connection

from .trade import Trade

class KrakenWebsocketAPI:

    URL = "wss://ws.kraken.com/v2" # See Channel: https://docs.kraken.com/api/docs/websocket-v2/trade 

    def __init__(self, pairs: List[str]):
        self.pairs = pairs

        # create a websocket client
        self._ws_client = create_connection(self.URL)

        # subscribe to the websocket
        self._subscribe()

        # breakpoint()

    def get_trades(self) -> List[Trade]:
        """
        Fetches the trades fromm the Kraken Websocket APIs and returns them as a list of Trade objects.

        Returns:
            List[Trade]: A list of Trade objects.
        """
        # receive the data from the websocket
        data = self._ws_client.recv()

        if 'heartbeat' in data:
            logger.info("Heartbeat received")
            return []
        
        # transform raw string into a JSON object
        try:
            data = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON: {e}")
            return []

        try:
            trades_data = data['data']
        except KeyError as e:
            logger.error(f"No `data` field with trades in the message {e}")
            return []

        trades = [
            Trade.from_kraken_api_response(
                pair=trade['symbol'],
                price=trade['price'],
                volume=trade['qty'],
                timestamp=trade['timestamp'],
            ) for trade in trades_data
        ]
        
        # breakpoint()
        
        return trades

    def _subscribe(self):
        """
        Subscribes to the websocket and waits for the initial snapshot.
        """
        # Send a subscribe message to the websocket
        # json.dumps() function will convert a subset of Python objects into a json string
        # A string is required by the websocket
        # https://websocket-client.readthedocs.io/en/latest/examples.html#sending-connection-close-status-codes
        self._ws_client.send(json.dumps({
            "method": "subscribe",
            "params": {
                "channel": "trade",
                "symbol": self.pairs,
                "snapshot": True
            }
        }))
          
        # The first message is the subscription confirmation message 
        # The second message is the snapshot of the trades        
        for pair in self.pairs:
            _ = self._ws_client.recv()
            _ = self._ws_client.recv()


# def datestr2milliseconds(iso_time: str) -> int:
#     """
#     Convert ISO format datetime string to Unix milliseconds timestamp.
    
#     Args:
#         iso_time (str): ISO format datetime string (e.g. '2023-09-25T07:49:37.708706Z')
    
#     Returns:
#         int: Unix timestamp in milliseconds
#     """
#     from datetime import datetime
#     dt = datetime.strptime(iso_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    
#     return int(dt.timestamp() * 1000)