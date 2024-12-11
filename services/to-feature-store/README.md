# Feature Store Service App

ADD IMAGE

## Steps

ADD STEPS

In many stream processing use cases the results need to be written to external destinations to be shared with other subsystems.

[Quix CSVSink](https://quix.io/docs/quix-streams/connectors/sinks/csv-sink.html) to write in external destinations.
[Custom Sink (Batch)](https://quix.io/docs/quix-streams/connectors/sinks/custom-sinks.html#backpressure-handling)

## Hopsworks

Tutorials for online and batch and API:

[Tutorials](https://docs.hopsworks.ai/latest/tutorials/)

 [API](https://docs.hopsworks.ai/feature-store-api/latest/generated/api/feature_group_api/)

Warnings on the "online table".

Set a time to see the job in the feature store using `materialization_job`

    FEATURE_GROUP_MATERIALIZATION_INTERVAL_MINUTES=15

In Hopsworks, under ingestions in the features store, you can see the materialization jobs.

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

Check logs last minute:

    docker logs -f --since 1m <CONTAINER_ID>
