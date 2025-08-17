FROM homeassistant/home-assistant:stable

# Install build essentials, python headers, and hidapi runtime library
# Use hidapi-dev for development headers and hidapi for runtime library
# Force pip to build hid from source to ensure proper linking
RUN apk add --no-cache build-base python3-dev hidapi-dev hidapi \
    && pip3 install --no-binary :all: --ignore-installed --no-deps hid \
    && rm -rf /var/cache/apk/*

# Set the default shell to bash
SHELL ["/bin/bash", "-o", "pipefail", "-c"]