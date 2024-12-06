# Feature Store Service App

ADD IMAGE

## Steps

ADD STEPS

In many stream processing use cases the results need to be written to external destinations to be shared with other subsystems.

[Quix CSVSink](https://quix.io/docs/quix-streams/connectors/sinks/csv-sink.html) to write in external destinations.

## Set up your environment

To create a new environment for this service and create a lockfile, run the following command from the `services` folder:

    uv init --no-workspace to-feature-store
    cd to-feature-store 
    source .venv/bin/activate

    # Install dependencies:
    uv add pip

    # Install `uv` optional dependencies:
    uv add pip --optional dev

    make req

## Commands

From `docker-compose` folder:

    # Start single Redpanda broker and Redpanda Console
    make start-redpanda

    # Stop single Redpanda broker and Redpanda Console
    make stop-redpanda
