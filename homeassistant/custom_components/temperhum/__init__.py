"""The TEMPerHUM custom component for Home Assistant."""
DOMAIN = "temperhum"

def setup(hass, config):
    """Set up the TEMPerHUM component."""
    # This component does not have any global configuration.
    # All setup will be done in the sensor platform.
    return True
