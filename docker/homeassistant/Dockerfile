FROM homeassistant/home-assistant:stable

# Install bash and libhidapi for HID device access
RUN apk add --no-cache bash hidapi \
    && rm -rf /var/cache/apk/*

# Set the default shell to bash
SHELL ["/bin/bash", "-o", "pipefail", "-c"]