"""Platform for TEMPerHUM temperature and humidity sensors."""
import json
import logging
import os
import struct
import asyncio
import functools

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

async def init_and_read_temperhum(device_path: str) -> dict | None:
    """Initialize TEMPerHUM device and read data with accurate conversion"""
    _LOGGER.debug(f"Attempting to read from device: {device_path}")
    try:
        with open(device_path, 'rb+') as device:
            _LOGGER.debug(f"Device opened: {device_path}")
            # Send initialization sequence for TEMPerHUM - IMPORTANT for getting live data
            # Command 1: Send 'temp' command and read (discarding result as per temper.py's "magic")
            command1 = b'\x01\x80\x33\x01\x00\x00\x00\x00'
            device.write(command1)
            _LOGGER.debug(f"Sent command 1: {command1.hex()}")
            await asyncio.sleep(0.5) # Increased sleep to give device more time
            response1 = device.read(8) # Discard first read as per temper.py
            _LOGGER.debug(f"Received response 1 (discarded): {response1.hex()}")

            # Command 2: Send 'temp' command again and read actual data
            command2 = b'\x01\x80\x33\x01\x00\x00\x00\x00'
            device.write(command2)
            _LOGGER.debug(f"Sent command 2: {command2.hex()}")
            await asyncio.sleep(0.5) # Increased sleep for reliable data acquisition
            data = device.read(8) # This should be the actual sensor data
            
            # Log the raw data immediately after reading
            raw_hex_debug = ' '.join([f'{b:02x}' for b in data])
            _LOGGER.debug(f"READ RAW DATA from {device_path} (length {len(data)}): {raw_hex_debug}")
            
            if len(data) >= 8:
                # Based on temper.py for FM75 type devices (our TEMPerHUM 3553:a001)
                # Temperature is little-endian signed short at offset 2 (bytes 2 and 3)
                raw_temp = struct.unpack('<h', data[2:4])[0]
                temperature_celsius = float(raw_temp) / 256.0 # Explicitly cast to float

                # Humidity is little-endian unsigned short at offset 4 (bytes 4 and 5)
                raw_humidity = struct.unpack('<H', data[4:6])[0]
                
                # Based on temperhum_actual.py, the correct conversion for humidity is raw_humidity / 100.0
                humidity_percent = float(raw_humidity) / 100.0 # Explicitly cast to float

                _LOGGER.debug(f"Parsed - Temp Raw: {raw_temp}, Humidity Raw: {raw_humidity}")
                _LOGGER.debug(f"Converted - Temp C: {temperature_celsius:.2f}, Humidity %: {humidity_percent:.2f}") # Updated log message

                return {
                    "temperature_celsius": temperature_celsius,
                    "temperature_fahrenheit": (temperature_celsius * 1.8) + 32.0,
                    "humidity_percent": humidity_percent,
                    "status": "success",
                    "device": device_path,
                    "raw_temp": raw_temp,
                    "raw_humidity": raw_humidity,
                    "raw_data": raw_hex_debug
                }
            else:
                _LOGGER.warning(f"Insufficient data read from {device_path}: {len(data)} bytes. Expected 8. Data: {raw_hex_debug}") # Added data to warning
                return None
    except FileNotFoundError:
        _LOGGER.error(f"Device not found: {device_path}. Please ensure the device is connected and the path is correct.")
        return None
    except PermissionError:
        _LOGGER.error(f"Permission denied for {device_path}. Ensure Home Assistant has access to the device. Check udev rules.") # Added udev hint
        return None
    except Exception as e:
        _LOGGER.exception(f"Unexpected error with {device_path} while trying to read TEMPerHUM sensor: {e}")
        return None

async def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities,
    discovery_info: DiscoveryInfoType = None,
) -> None:
    """Set up the TEMPerHUM sensor platform."""
    name = config.get(CONF_NAME)
    device_path = config.get(CONF_DEVICE_PATH)
    _LOGGER.debug(f"Setting up TEMPerHUM platform for {name} at {device_path}")

    async def _async_update_data_for_coordinator():
        """Fetch data for coordinator."""
        return await init_and_read_temperhum(device_path)

    # Create a data coordinator to manage polling
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"TEMPerHUM {name}",
        update_method=_async_update_data_for_coordinator,
        update_interval=SCAN_INTERVAL,
    )

    # Fetch initial data so we have data when entities are added
    _LOGGER.debug(f"Fetching initial data for {name}...")
    await coordinator.async_refresh()
    _LOGGER.debug(f"Initial data fetched for {name}. Status: {coordinator.data.get('status') if coordinator.data else 'No Data'}")

    entities = [
        TemperhumTemperatureSensor(name, coordinator),
        TemperhumHumiditySensor(name, coordinator)
    ]
    add_entities(entities, True)

class TemperhumTemperatureSensor(CoordinatorEntity):
    """Representation of a TEMPerHUM temperature sensor."""

    def __init__(self, name: str, coordinator: DataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._name = f"{name} Temperature"
        self._state = None
        self._unit_of_measurement = UnitOfTemperature.CELSIUS

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return "mdi:thermometer"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get("status") == "success":
            value = self.coordinator.data["temperature_celsius"]
            _LOGGER.debug(f"Temperature sensor '{self._name}' native_value: {value}")
            return value
        _LOGGER.debug(f"Temperature sensor '{self._name}' native_value: None (data not successful or not yet fetched)")
        return None

class TemperhumHumiditySensor(CoordinatorEntity):
    """Representation of a TEMPerHUM humidity sensor."""

    def __init__(self, name: str, coordinator: DataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._name = f"{name} Humidity"
        self._state = None
        self._unit_of_measurement = "%"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return "mdi:water-percent"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get("status") == "success":
            value = self.coordinator.data["humidity_percent"]
            _LOGGER.debug(f"Humidity sensor '{self._name}' native_value: {value}")
            return value
        _LOGGER.debug(f"Humidity sensor '{self._name}' native_value: None (data not successful or not yet fetched)")
        return None
