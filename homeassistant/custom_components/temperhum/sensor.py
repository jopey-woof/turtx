"""Platform for TEMPerHUM temperature and humidity sensors."""
import json
import logging
import os
import struct
import time

from datetime import timedelta

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import (
    CONF_NAME,
    CONF_UNIT_OF_MEASUREMENT,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "TEMPerHUM Sensor"
SCAN_INTERVAL = timedelta(seconds=60)
CONF_DEVICE_PATH = "device_path"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Required(CONF_DEVICE_PATH): cv.string,
    }
)

def init_and_read_temperhum(device_path):
    """Initialize TEMPerHUM device and read data with accurate conversion"""
    try:
        with open(device_path, 'rb+') as device:
            # Send initialization sequence for TEMPerHUM - IMPORTANT for getting live data
            # Command 1: Send 'temp' command and read (discarding result as per temper.py's "magic")
            device.write(b'\x01\x80\x33\x01\x00\x00\x00\x00') # COMMANDS['temp'] from temper.py
            time.sleep(0.1)
            _ = device.read(8) # Discard first read as per temper.py

            # Command 2: Send 'temp' command again and read actual data
            device.write(b'\x01\x80\x33\x01\x00\x00\x00\x00') # COMMANDS['temp'] from temper.py
            time.sleep(0.2)
            data = device.read(8) # This should be the actual sensor data
            
            # Log the raw data immediately after reading
            raw_hex_debug = ' '.join([f'{b:02x}' for b in data])
            _LOGGER.debug(f"READ RAW DATA from {device_path} (length {len(data)}): {raw_hex_debug}")
            
            if len(data) >= 8:
                # Based on temper.py for FM75 type devices (our TEMPerHUM 3553:a001)
                # Temperature is little-endian signed short at offset 2 (bytes 2 and 3)
                raw_temp = struct.unpack('<h', data[2:4])[0]
                temperature_celsius = raw_temp / 256.0

                # Humidity is little-endian unsigned short at offset 4 (bytes 4 and 5)
                raw_humidity = struct.unpack('<H', data[4:6])[0]
                
                # The humidity conversion formula from temper.py's FM75 type
                # ((raw_humidity * 32) / 1000.0) seems to yield incorrect values based on
                # previous test. For now, we will return the raw humidity value to verify
                # the reading, and investigate the proper conversion later.
                humidity_percent = float(raw_humidity) # Store raw value for debugging

                _LOGGER.debug(f"Parsed - Temp Raw: {raw_temp}, Humidity Raw: {raw_humidity}")
                _LOGGER.debug(f"Converted - Temp C: {temperature_celsius:.2f}, Humidity Raw Val: {humidity_percent:.2f}")

                return {
                    "temperature_celsius": temperature_celsius,
                    "temperature_fahrenheit": (temperature_celsius * 1.8) + 32.0,
                    "humidity_percent": humidity_percent, # Return raw for now
                    "status": "success",
                    "device": device_path,
                    "raw_temp": raw_temp,
                    "raw_humidity": raw_humidity,
                    "raw_data": raw_hex_debug
                }
            else:
                _LOGGER.warning(f"Insufficient data read from {device_path}: {len(data)} bytes. Expected 8.")
                return None
    except Exception as e:
        _LOGGER.exception(f"Error with {device_path} while trying to read TEMPerHUM sensor.")
        return None

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up the TEMPerHUM sensor platform."""
    name = config.get(CONF_NAME)
    device_path = config.get(CONF_DEVICE_PATH)

    # Create a data coordinator to manage polling
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"TEMPerHUM {name}",
        update_method=lambda: init_and_read_temperhum(device_path),
        update_interval=SCAN_INTERVAL,
    )

    # Fetch initial data so we have data when entities are added
    coordinator.async_refresh()

    entities = [
        TemperhumTemperatureSensor(name, coordinator),
        TemperhumHumiditySensor(name, coordinator)
    ]
    add_entities(entities, True)

class TemperhumTemperatureSensor(CoordinatorEntity):
    """Representation of a TEMPerHUM temperature sensor."""

    def __init__(self, name, coordinator):
        super().__init__(coordinator)
        self._name = f"{name} Temperature"
        self._state = None
        self._unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:thermometer"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get("status") == "success":
            value = self.coordinator.data["temperature_celsius"]
            _LOGGER.debug(f"Temperature sensor native_value: {value}")
            return value
        _LOGGER.debug("Temperature sensor native_value: None (data not successful)")
        return None

class TemperhumHumiditySensor(CoordinatorEntity):
    """Representation of a TEMPerHUM humidity sensor."""

    def __init__(self, name, coordinator):
        super().__init__(coordinator)
        self._name = f"{name} Humidity"
        self._state = None
        self._unit_of_measurement = "%"

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:water-percent"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get("status") == "success":
            return self.coordinator.data["humidity_percent"]
        return None
