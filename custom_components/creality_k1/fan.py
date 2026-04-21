"""Platform for Creality K1 fans that support percentage control via GCODE."""

import logging
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, FAN_CONFIG
from .entity import CrealityK1Entity
from .coordinator import CrealityK1DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Creality K1 fans from a config entry."""
    coordinator: CrealityK1DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    fans = []
    icons = {
        "model_fan": "mdi:fan-speed-1",
        "case_fan": "mdi:fan-speed-2",
        "side_fan": "mdi:fan-speed-3",
    }
    for translation_key, (percent_key, toggle_key, p_index) in FAN_CONFIG.items():
        fans.append(
            K1Fan(
                coordinator,
                percent_key,
                toggle_key,
                p_index,
                config_entry,
                translation_key,
                icons.get(translation_key, "mdi:fan"),
            )
        )
    async_add_entities(fans)

class K1Fan(CrealityK1Entity, FanEntity):
    """Representation of a Creality K1 Fan using M106 GCODE."""

    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.TURN_ON | FanEntityFeature.TURN_OFF

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        percentage_key: str,
        toggle_key: str,
        p_index: int,
        config_entry: ConfigEntry,
        translation_key: str,
        icon: str,
    ) -> None:
        """Initialize the fan."""
        super().__init__(coordinator, config_entry)
        self._percentage_key = percentage_key
        self._toggle_key = toggle_key
        self._p_index = p_index
        self._attr_translation_key = translation_key
        self._attr_icon = icon
        self._attr_unique_id = f"{config_entry.entry_id}_fan_{toggle_key.lower()}"
        _LOGGER.debug(
            f"Initializing Fan: {self._attr_translation_key} ({self._attr_unique_id}) "
            f"using keys Pct='{self._percentage_key}', Toggle='{self._toggle_key}', GcodeP={self._p_index}"
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the fan is on (based on toggle key)."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            toggle_value = self.coordinator.data.get(self._toggle_key)
            if toggle_value is None:
                return None
            try:
                return int(toggle_value) == 1
            except (ValueError, TypeError):
                return None
        return None

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            current_is_on = self.is_on
            if current_is_on is False:
                return 0
            elif current_is_on is None:
                return None

            value = self.coordinator.data.get(self._percentage_key)
            if value is None:
                return None
            try:
                return max(0, min(100, int(value)))
            except (ValueError, TypeError):
                return None
        return None

    async def _send_m106_command(self, speed_0_255: int) -> None:
        """Helper function to send M106 S<speed> P<index> GCODE command."""
        safe_speed = max(0, min(255, speed_0_255))
        gcode = f"M106 P{self._p_index} S{safe_speed}"
        command = {"method": "set", "params": {"gcodeCmd": gcode}}
        _LOGGER.debug(f"Fan {self._attr_translation_key}: Sending command: {command}")
        try:
            await self.coordinator.websocket.send_message(command)
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Fan {self._attr_translation_key}: Failed to send M106 command: {e}")

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan using M106 S<0-255>."""
        _LOGGER.debug(f"Fan {self._attr_translation_key}: Setting percentage to {percentage}")
        if percentage < 0 or percentage > 100:
            _LOGGER.warning(f"Fan {self._attr_translation_key}: Invalid percentage {percentage} requested")
            return

        speed_0_255 = round(percentage / 100 * 255)
        await self._send_m106_command(speed_0_255)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan using M106."""
        _LOGGER.debug(f"Fan {self._attr_translation_key}: Turn on requested. Percentage={percentage}")
        if percentage is None:
            target_speed_0_255 = 255
            _LOGGER.debug(f"Fan {self._attr_translation_key}: No percentage specified, defaulting to 100% (S255)")
        else:
            target_percentage = max(1, min(100, percentage))
            target_speed_0_255 = round(target_percentage / 100 * 255)

        await self._send_m106_command(target_speed_0_255)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off using M106 S0."""
        _LOGGER.debug(f"Fan {self._attr_translation_key}: Turn off requested (M106 S0).")
        await self._send_m106_command(0)