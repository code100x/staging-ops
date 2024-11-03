#!/bin/bash

DOCKER_COMPOSE_DIR="$(pwd)"

DOCKER_CMD="$(which docker)"

# create the cron job
(crontab -l; echo "0 0 * * * cd $DOCKER_COMPOSE_DIR && $DOCKER_CMD compose up >> $DOCKER_COMPOSE_DIR/log.txt 2>&1") | crontab -
