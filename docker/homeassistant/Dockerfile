FROM homeassistant/home-assistant:stable

# Update apk and upgrade installed packages
RUN apk update && apk upgrade \
    && apk add --no-cache build-base python3-dev libusb-1.0-0 \
    && pip3 install --no-binary :all: --ignore-installed --no-deps hid \
    && rm -rf /var/cache/apk/*

# Set the default shell to bash
SHELL ["/bin/bash", "-o", "pipefail", "-c"]