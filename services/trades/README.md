# Trades Workflow

Kraken API → WebSocket → Trades Service App (Quix Streams Initialization) → Set Up Trades Kafka (Redpanda) Topic → Quix Streams Producer (write serialized data)

<p align="center">

<img width="623" alt="Captura de pantalla 2024-12-03 124748" src="https://github.com/user-attachments/assets/53765778-4ece-4a05-bed3-fb45f7d9cc55">

</p>

## Steps

### Kraken API → WebSocket

- The Kraken WebSocket API is used to subscribe to real-time trade data streams. This allows the system to receive trade updates as they occur on the Kraken exchange.

### WebSocket → Trades Service App (Quix Streams Initialization)

- The Trades Service App connects to the Kraken WebSocket, fetches trade updates, and initializes Quix Streams Application for further processing. The app prepares the connection to the Kafka broker (Redpanda) and the trade data for streaming.

### Set Up Trades Kafka (Redpanda) Topic

- A Kafka topic is set up in Redpanda to store and stream the trade data. This allows the system to manage the trade data efficiently, with high throughput and low latency.

### Quix Streams Producer → Write Serialized Data to Kafka Topic

- The Quix Streams Producer writes serialized trade data (in JSON format) to the Kafka topic in Redpanda. This serialized data includes trade details such as price, volume, timestamp, etc.

- Quix Streams ensures the smooth publishing of data to Kafka, and it handles the serialization process (e.g., turning Python objects into JSON or binary format) before writing to the Kafka topic.

## Kraken API

The Kraken API provides programmatic access to the Kraken cryptocurrency exchange, enabling the retrieval of real-time market data and trade activity.

- WebSocket API: Use this for receiving real-time updates on trades, price changes, and other events.

[Kraken WebSocket API (Trade) Documentation](https://docs.kraken.com/api/docs/websocket-v2/trade)

Example of trade data received via the WebSocket API:

    # Sample data

    {
        "channel": "trade",
        "type": "update",
        "data": [
            {
                "symbol": "MATIC/USD",
                "side": "sell",
                "price": 0.5117,
                "qty": 40.0,
                "ord_type": "market",
                "trade_id": 4665906,
                "timestamp": "2023-09-25T07:49:37.708706Z"
            }
        ]
    }

## WebSocket

The WebSocket protocol enables efficient, real-time, full-duplex communication between clients and servers. It provides access to low-level APIs, such as Kraken's WebSocket API, allowing for continuous data streams, which is ideal for real-time applications like cryptocurrency trading.

- Efficient Real-Time Communication: WebSocket maintains an open connection, allowing for constant data transmission, reducing the overhead of establishing multiple connections.

- Low Latency: Enables immediate updates as soon as data is available (e.g., trade updates).

- Two-Way Communication: Both the client and server can send and receive messages at any time during the connection.

[WebSocket Documentation](https://websocket-client.readthedocs.io/en/latest/examples.html#)

## Redpanda

Redpanda is a high-performance, Kafka-compatible event streaming platform designed for low-latency data ingestion and processing. It serves as the backbone for capturing and streaming real-time trade data.

Key Features:

- Kafka-Compatible: Drop-in replacement for Apache Kafka.
- High Performance: Optimized for low-latency and high-throughput workloads.
- Real-Time Streaming: Produce (write) and consume (read) streams of data in real time.
- Scalability: Handles high volumes of data ingestion and partitioning.

[Redpanda Documentation](https://www.redpanda.com/)

### Trades Service with Redpanda

The Trades Service fetches real-time trade data using the Kraken WebSocket API and publishes it to a Redpanda topic.

1. Fetch Data:
   - Connect to the Kraken WebSocket API to receive real-time trade updates.

2. Publish Data:
   - Stream raw trade data to a designated Redpanda topic.

## Quix Streams

Quix Streams simplifies building Kafka-based producer and consumer applications, offering a developer-friendly SDK for stream processing. It integrates with Redpanda to enable real-time processing of trade data or creation of event-driven systems.

Key Features:

- Stream Processing: Apply real-time transformations, filtering, or aggregations on data streams.
- ML-Friendly: Use Python SDK to connect streams to machine learning pipelines.
- Kafka-Compatible: Seamlessly connects to Redpanda topics as a producer or consumer.
- Time-Series Insights: Capture data as time-series for storage or advanced analytics.

[Quix Streams Documentation](https://quix.io/docs/quix-streams/producer.html)
