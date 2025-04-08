#!/bin/bash

# Set the environment variable for the password
PASSWORD="dummy_password"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Resolve config path relative to the script directory
CONFIG_PATH="$SCRIPT_DIR/server-config.yaml"

# Run Docker command
docker run -it \
    -e PASSWORD="$PASSWORD" \
    -v "$CONFIG_PATH:/config.yaml" \
    -p 46357:46357 \
    ghcr.io/agntcy/agp/gw:0.3.6 /gateway --config /config.yaml   