# Docker Command

Add one partition to the trades topic:

    docker compose -f redpanda.yml exec redpanda rpk topic add-partitions trades --num 1

This file `technical-indicators-pipeline.yml` runs all Dockerfile from the different services together.
