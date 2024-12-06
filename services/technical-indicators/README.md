# Technical Indicators Service App

Candles Service App → Technical Indicators Service App (Quix Streams Initialization) → Quix Streams Consumer Group → Set Up Technical Indicators Kafka (Redpanda) Topic →  Quix Streams Consumer Group (publishes the generated 60 candles history)

<p align="center">
<img width="623" height="300" alt="ti" src="https://github.com/user-attachments/assets/2628638e-a507-4458-8cdf-ba19cd6d2ac5">
</p>

## Stateful Applications

### How State Relates to Kafka Message Keys?

The most important concept to understand with state is that it depends on the message key due to how Kafka topic partitioning works.

Every Kafka message key's state is independent and inaccessible from all others; it is accessible only while it is the currently active message key.

Each key may belong to different Kafka topic partitions, and partitions are automatically assigned and re-assigned by Kafka broker to consumer apps in the same consumer group.

[Quix Documentation Stateful Processing](https://quix.io/docs/quix-streams/advanced/stateful-processing.html#state-guarantees)

## Steps

The "Technical Indicators Service App" serves as both a consumer (of the Candles topic) and a producer (for the Technical Indicators topic).

### Candles Service App → Quix Streams Consumer Group

- Consumes candles data from the Kafka Candles topic using Quix Streams.

- Collects the emitted candles into a stateful history.

- This state acts as an in-memory cache of the last `MAX_CANDLES_IN_STATE` candles variable (e.g., 60 candles).

### Set Up Technical Indicators  Kafka (Redpanda) Topic

- A Kafka topic is set up in Redpanda to store and stream the stateful history.

### Quix Streams Consumer Group → Write Data to Technical Indicators Kafka Topic

- After processing, the Quix Streams Consumer Group publishes the generated 60 candles history to the Kafka Technical Indicators topic in Redpanda.

## Set Up

It requires the installation of the TA-lib library. As it is a C library it must be installed first as per this [repository](https://github.com/TA-Lib/ta-lib-python)

    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib
    ./configure --prefix=/usr
    make
    sudo make install

Then add it to the `pyproject.toml` file

    uv add ta-lib

[TA Lib Python Documentation](https://ta-lib.github.io/ta-lib-python/)

## Commands

From `docker-compose` folder:

    # Start single Redpanda broker and Redpanda Console
    make start-redpanda

    # Stop single Redpanda broker and Redpanda Console
    make stop-redpanda

From `service/technical-indicators` folder:

    # Start technical indicators streaming service
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
