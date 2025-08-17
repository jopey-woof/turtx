FROM homeassistant/home-assistant:stable

# Install libhidapi-hidraw0 for HID device access
RUN apt-get update && apt-get install -y libhidapi-hidraw0 --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Set the default shell to bash
SHELL ["/bin/bash", "-o", "pipefail", "-c"]