"""The TEMPerHUM custom component for Home Assistant."""
import logging
from homeassistant.helpers import discovery

_LOGGER = logging.getLogger(__name__)

DOMAIN = "temperhum"


def setup(hass, config):
    """Set up the TEMPerHUM component."""
    _LOGGER.debug("Setting up TEMPerHUM custom component")

    # Load the sensor platform
    discovery.load_platform(hass, "sensor", DOMAIN, {}, config)

    return True
