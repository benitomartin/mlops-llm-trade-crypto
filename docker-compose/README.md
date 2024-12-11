# Commands

From `docker-compose` folder:

    # Start single Redpanda broker and Redpanda Console
    make start-redpanda

    # Stop single Redpanda broker and Redpanda Console
    make stop-redpanda

Add one partition to the trades topic:

    docker compose -f redpanda.yml exec redpanda rpk topic add-partitions trades --num 1

This file `technical-indicators-live.yml` and `technical-indicators-historical.yml` runs all Dockerfile from the different services together.

## Errors

If the backfill pipeline cannot be run, update "credsStore" to "credStore" in the docker config

    code ~/.docker/config.json
