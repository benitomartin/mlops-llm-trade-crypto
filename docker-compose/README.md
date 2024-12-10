# Docker Command

Add one partition to the trades topic:

    docker compose -f redpanda.yml exec redpanda rpk topic add-partitions trades --num 1
