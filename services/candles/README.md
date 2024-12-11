# Candles Service App

Trades Service App → Candles Service App (Quix Streams Initialization) → Quix Streams Consumer Group → Set Up Candles Kafka (Redpanda) Topic →  Quix Streams Consumer Group (publishes the generated candles)

![candles](https://github.com/user-attachments/assets/3e4b6fd5-8a11-453c-9a77-a58aa0a8a59e)

## Steps

The "Candles Service App" serves as both a consumer (of the Trades topic) and a producer (for the Candles topic).

### Trades Service App → Quix Streams Consumer Group

- Consumes raw trade data from the Kafka Trades topic using Quix Streams.

- Aggregates this data into 60-second candles using a tumbling window approach.

### Set Up Candles Kafka (Redpanda) Topic

- A Kafka topic is set up in Redpanda to store and stream the candles data.

### Quix Streams Consumer Group → Write Data to Candles Kafka Topic

- After processing, the Quix Streams Consumer Group publishes the generated candles to the Kafka Candles topic in Redpanda.

## Partitions

While running both, trades and candles, each on a terminal, if you try to run candles on a separate one, it won't work and will stay idle. Then, if we stop the active candle topic, the idle terminal will automatically start running.

But doing partitions, will allow to scale up and down as kafka assigns consumers to partitions, so that the candles can run on 2 or more terminals (partitions).

## Set up your environment

To create a new environment for this service and create a lockfile, run the following command from the `services` folder:

    uv init --no-workspace candles
    cd candles
    source .venv/bin/activate

    # Install dependencies:
    uv add pip

    # Install `uv` optional dependencies:
    uv add pip --optional dev

    make req

The `.env` file contains env. variables. like consumer group, candle time frame and whether to use current() or final() depending on whether to emit the candles immediately or after each 60 seconds

    KAFKA_BROKER_ADDRESS=localhost:19092 # from redpanda.yml --advertise-kafka-addr external://localhost:19092 to connect to the broker
    KAFKA_INPUT_TOPIC=trades
    KAFKA_OUTPUT_TOPIC=candles
    KAFKA_CONSUMER_GROUP=candles_consumer_group
    CANDLE_SECONDS=60
    EMIT_INCOMPLETE_CANDLES=True

## Commands

From `docker-compose` folder:

    # Start single Redpanda broker and Redpanda Console
    make start-redpanda

    # Stop single Redpanda broker and Redpanda Console
    make stop-redpanda

From `service/candles` folder:

    # Start candles streaming service
    make run

After starting the streaming service with command `run-dev` (no Dockerfile), a `state` folder will be generated under the consumer group name and by restarting it will continue after the last state.

For other make commands run:

    # Command to run "make help"
    make

    # Output sample
    req                            Install requirements
    run                            Run Trades Service App
    ruff                           Run Ruff linter
    clean                          Clean up generated files
    help                           Display this help message

## Inspect docker network

    docker network ls

    docker network ls --filter driver=bridge

    docker network inspect redpanda_network

The inspect command shall give both containers as per `redpanda.yml` file under `Containers`:

    [
        {
            "Name": "redpanda_network",
            "Id": "2df92ed562932a5aff94dbcd7b7af97351fa83066071906335ffb1e88258b0d1",
            "Created": "2024-12-05T17:44:29.951934347Z",
            "Scope": "local",
            "Driver": "bridge",
            "EnableIPv6": false,
            "IPAM": {
                "Driver": "default",
                "Options": null,
                "Config": [
                    {
                        "Subnet": "172.19.0.0/16",
                        "Gateway": "172.19.0.1"
                    }
                ]
            },
            "Internal": false,
            "Attachable": false,
            "Ingress": false,
            "ConfigFrom": {
                "Network": ""
            },
            "ConfigOnly": false,
            "Containers": {
                "d3d485f40d717743cd0375bf69d5db0dd0c35222827551b75533a4c46fe3a2e5": {
                    "Name": "redpanda",
                    "EndpointID": "04de7ceb83bde185ce16b698f6fcabe0a1b7b86c54af5e1dbc2eff944d8bd151",
                    "MacAddress": "02:42:ac:13:00:02",
                    "IPv4Address": "172.19.0.2/16",
                    "IPv6Address": ""
                },
                "f836b1aab856e38ed5414c59bc32040a21d7612f5bfcb95c83c04389ecfa7893": {
                    "Name": "redpanda-console",
                    "EndpointID": "b2ef4bf48882ba6747a394aa792937351ea951211ef10605a3efb22f712083b5",
                    "MacAddress": "02:42:ac:13:00:03",
                    "IPv4Address": "172.19.0.3/16",
                    "IPv6Address": ""
                }
            },
            "Options": {},
            "Labels": {
                "com.docker.compose.network": "redpanda_network",
                "com.docker.compose.project": "redpanda-dev-cluster",
                "com.docker.compose.version": "2.30.3"
            }
        }
    ]

## Quixstreams

Once our pipeline works, we add a split between historical, live and test data. For that we need to add the following param in the application, `auto_offset_reset`: Consumer auto.offset.reset setting. Available values:

- "earliest" - automatically reset the offset to the smallest offset
- "latest" - automatically reset the offset to the largest offset
- "error" - trigger an error (ERR__AUTO_OFFSET_RESET) which is retrieved by consuming messages (used for testing)

`live`: start fetching data continuing where it stopped.
`earliest`: If test or historical, start fetching data from the beginning (first message in the topic)
