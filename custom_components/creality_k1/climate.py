# Creality K1 Climate Module
#
# Copyright (C) 2025 Joshua Wherrett <thejoshw.code@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
from typing import Any
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.climate import ClimateEntity, ClimateEntityFeature, HVACMode
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .const import DOMAIN, CLIMATE_CONTROLS
from .coordinator import CrealityK1DataUpdateCoordinator
from .entity import CrealityK1Entity
from .helpers import to_float_or_none, get_hw_sw_versions

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    ) -> None:
    """Set up the Creality K1 climates from a config entry."""
    coordinator: CrealityK1DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id] # Get correct coordinator when having multiple printers
    climates = []
    for (heater_id, translation_key, current_temp_key, target_temp_key, max_temp_key) in CLIMATE_CONTROLS:
        climates.append(
            K1Climate(
                coordinator,
                config_entry,
                heater_id,
                translation_key,
                current_temp_key,
                target_temp_key,
                max_temp_key
            )
        )
    async_add_entities(climates)


class K1Climate(CrealityK1Entity, ClimateEntity):
    """Base class for Creality K1 heaters."""
    _attr_has_entity_name = True
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE |
        ClimateEntityFeature.TURN_OFF |
        ClimateEntityFeature.TURN_ON
    )
    _attr_min_temp = 0.0 # Adjust based on printer capabilities
    _attr_target_temperature_step = 1.0 # Set the step for temperature adjustments

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
        heater_id: str,
        translation_key: str,
        current_temp_key: str,
        target_temp_key: str,
        max_temp_key: str
        ) -> None:
        """
        Initialize the climate entity.
        :param coordinator: The PrinterManager coordinator instance.
        :param heater_id: The ID identifying the heater (e.g., 'bed0', 'nozzle0'), index must end with a number.
        :param name: The name of the heater (e.g., 'Bed Heater', 'Nozzle Heater').
        :param current_temp_key: The key in coordinator.data for the current temperature.
        :param target_temp_key: The key in coordinator.data for the target temperature.
        :param max_temp_key: The key in coordinator.data for the maximum temperature.
        """
        super().__init__(coordinator, config_entry)
        self._heater_id = heater_id
        self._attr_translation_key = translation_key
        self._current_temp_key = current_temp_key
        self._target_temp_key = target_temp_key
        self._max_temp_key = max_temp_key
        self._config_entry = config_entry
        self._attr_unique_id = f"{config_entry.entry_id}_{heater_id}_climate"



    @property
    def current_temperature(self) -> float | None:
        return to_float_or_none(self.coordinator.data, self._current_temp_key)

    @property
    def max_temp(self) -> float | None:
        return to_float_or_none(self.coordinator.data, self._max_temp_key)

    @property
    def target_temperature(self) -> float | None:
        return to_float_or_none(self.coordinator.data, self._target_temp_key)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        target = self.target_temperature
        if target is not None and target > 0.0:
            return HVACMode.HEAT
        return HVACMode.OFF

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            _LOGGER.debug(f"Turning off {self._heater_id} heater for {self._config_entry.entry_id}")
            # Command to turn off heater (set target temp to 0.0)
            await self.async_set_temperature(**{ATTR_TEMPERATURE: 0.0})
        elif hvac_mode == HVACMode.HEAT:
            # If turning on from off, set to a default heating temperature or the last known target.
            # For simplicity, if turning on, let's set a default target (e.g., 60 for bed, 200 for hotend)
            # or you might want to read the last target from coordinator.data or config.
            current_target = self.target_temperature
            if current_target is None or current_target == 0.0:
                default_target = 200.0 if self._heater_id.startswith("nozzle") else 60.0 # Example defaults for PLA
                _LOGGER.debug(f"Turning on {self._heater_id} heater for {self._config_entry.entry_id} to default {default_target}°C")
                await self.async_set_temperature(**{ATTR_TEMPERATURE: default_target})
            else:
                _LOGGER.debug(f"Setting HVAC mode to HEAT for {self._heater_id} heater, keeping current target {current_target}°C")
                # If already heating, no need to send command, but ensure state reflects HEAT
                self.async_write_ha_state()
        else:
            _LOGGER.warning(f"Unsupported HVAC mode: {hvac_mode}")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        _LOGGER.debug(f"Setting {self._heater_id} target temperature to {temperature}°C for {self._config_entry.entry_id}")
        rounded_temp_int = int(round(temperature))
        # Construct gcode based on bed or nozzle heater
        gcode = f"M104" if self._heater_id.startswith("nozzle") else f"M140" # M104 for nozzle, M140 for bed
        gcode += f" T" if self._heater_id.startswith("nozzle") else f" I" # T for nozzle, I for bed
        gcode += f"{self._heater_id[-1:]} S{rounded_temp_int}" # Heater ID must end with an index number
        await self.coordinator.websocket.send_message({"method": "set", "params": {"gcodeCmd": gcode}})

        # Optimistically update the state in Home Assistant
        # This helps the UI update immediately, then it will be corrected by next WS push
        if self.coordinator.data is not None:
            self.coordinator.data[self._target_temp_key] = temperature
            self.async_write_ha_state()