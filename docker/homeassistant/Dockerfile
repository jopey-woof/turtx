FROM homeassistant/home-assistant:stable

# Update apk and upgrade installed packages
RUN apk update && apk upgrade \
    #&& apk add --no-cache build-base python3-dev hidapi-dev hidapi libusb-dev libusb \
    && ldconfig \
    && pip3 install hid \
    && rm -rf /var/cache/apk/*

# Set the default shell to bash
SHELL ["/bin/bash", "-o", "pipefail", "-c"]