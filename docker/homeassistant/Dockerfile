FROM homeassistant/home-assistant:stable

# Update apk and upgrade installed packages
RUN ping -c 3 8.8.8.8 && \
    apk update && apk upgrade \
    && pip3 install hid \
    && rm -rf /var/cache/apk/*

# Set the default shell to bash
SHELL ["/bin/bash", "-o", "pipefail", "-c"]