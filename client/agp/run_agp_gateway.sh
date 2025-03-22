# Set the environment variable for the password
PASSWORD="dummy_password"

# Resolve config path
CONFIG_PATH=$(realpath .server-config.yaml)

# Run Docker command
docker run -it \
    -e PASSWORD="$PASSWORD" \
    -v "$CONFIG_PATH:/config.yaml" \
    -p 46357:46357 \
    ghcr.io/agntcy/agp/gw:0.3.6 /gateway --config /config.yaml   