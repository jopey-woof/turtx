FROM homeassistant/home-assistant:stable

# Install build essentials, python headers, hidapi runtime library, and libusb development libraries
# Force pip to build hid from source to ensure proper linking
RUN apk add --no-cache build-base python3-dev hidapi libusb-dev \
    && pip3 install --no-binary :all: --ignore-installed --no-deps hid \
    && rm -rf /var/cache/apk/*

# Set the default shell to bash
SHELL ["/bin/bash", "-o", "pipefail", "-c"]