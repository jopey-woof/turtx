FROM homeassistant/home-assistant:stable

# Install build essentials, python headers, and hidapi runtime library
RUN apk add --no-cache build-base python3-dev hidapi \
    && pip3 install hid \
    && rm -rf /var/cache/apk/*

# Set the default shell to bash
SHELL ["/bin/bash", "-o", "pipefail", "-c"]