# Technical Indicators Service App

It requires the installation of the TA-lib library. As it is a C library it must be installed first as per this [repository](https://github.com/TA-Lib/ta-lib-python)

    wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
    tar -xzf ta-lib-0.4.0-src.tar.gz
    cd ta-lib
    ./configure --prefix=/usr
    make
    sudo make install

Then add it to the `pyproject.toml` file

    uv add ta-lib


## Stateful Applications

### How State Relates to Kafka Message Keys?

The most important concept to understand with state is that it depends on the message key due to how Kafka topic partitioning works.

Every Kafka message key's state is independent and inaccessible from all others; it is accessible only while it is the currently active message key.

Each key may belong to different Kafka topic partitions, and partitions are automatically assigned and re-assigned by Kafka broker to consumer apps in the same consumer group.

[Quix Documentation Stateful Processing](https://quix.io/docs/quix-streams/advanced/stateful-processing.html#state-guarantees)