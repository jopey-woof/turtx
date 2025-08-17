FROM homeassistant/home-assistant:stable

# Install libhidapi for HID device access (using apk for Alpine-based images)
RUN apk add --no-cache libhidapi-dev \
    && rm -rf /var/cache/apk/*

# Set the default shell to bash (if bash is installed, otherwise keep ash)
SHELL ["/bin/bash", "-o", "pipefail", "-c"]