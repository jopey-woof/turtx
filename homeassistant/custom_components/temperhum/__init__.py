"""The TEMPerHUM custom component for Home Assistant."""
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "temperhum"

def setup(hass, config):
    """Set up the TEMPerHUM component."""
    _LOGGER.debug("Setting up TEMPerHUM custom component")
    # This component does not have any global configuration.
    # All setup will be done in the sensor platform.
    return True
