#!/usr/bin/env bash

source .venv/bin/activate
poetry export --with dev -f requirements.txt --output aiiabox/requirements.txt
docker compose up --remove-orphans --build --force-recreate -d

trap 'echo -e "\nEnter dc stop to stop containers."' SIGINT
docker compose logs -f
