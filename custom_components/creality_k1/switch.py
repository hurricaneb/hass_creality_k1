"""Platform for Creality K1 switches."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import CrealityK1Entity
from .coordinator import CrealityK1DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Creality K1 switches."""
    coordinator: CrealityK1DataUpdateCoordinator = config_entry.runtime_data

    async_add_entities([
        K1LightSwitch(coordinator, config_entry),
        K1ParamSwitch(coordinator, config_entry, "aiDetection", "ai_detection", "mdi:brain"),
        K1ParamSwitch(coordinator, config_entry, "aiPausePrint", "ai_pause_print", "mdi:pause-octagon"),
        K1ParamSwitch(coordinator, config_entry, "aiFirstFloor", "ai_first_floor", "mdi:layers-search"),
    ])

class K1Switch(CrealityK1Entity, SwitchEntity):
    """Base class for Creality K1 switches."""

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
        translation_key: str,
        icon: str | None = None,
        unique_id_suffix: str | None = None,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, config_entry)
        self._attr_translation_key = translation_key
        self._attr_icon = icon
        self._state = False
        if unique_id_suffix:
            self._attr_unique_id = f"{config_entry.entry_id}_{unique_id_suffix}"

    async def async_turn_on(self, **kwargs: dict[str, Any]):
        """Turn the switch on."""
        await self._send_websocket_command(True)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: dict[str, Any]):
        """Turn the switch off."""
        await self._send_websocket_command(False)
        self.async_write_ha_state()

    async def _send_websocket_command(self, is_on: bool) -> None:
        """Send the appropriate command to the printer via WebSocket."""
        raise NotImplementedError

class K1LightSwitch(K1Switch):
    """Representation of a Creality K1 light switch."""

    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
    ) -> None:
        """Initialize the light switch."""
        super().__init__(
            coordinator,
            config_entry,
            translation_key="printer_light",
            unique_id_suffix="printer_light",
            icon="mdi:desk-lamp"
        )
        if coordinator.data:
            light_sw_value = coordinator.data.get("lightSw")
            _LOGGER.debug(f"Switch: Initial lightSw value: {light_sw_value}")

    async def _send_websocket_command(self, is_on: bool) -> None:
        """Send the command to turn the light on or off."""
        command = {"method": "set", "params": {"lightSw": 1 if is_on else 0}}
        _LOGGER.debug(f"Sending light command: {command}")
        await self.coordinator.websocket.send_message(command)

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            return self.coordinator.data.get("lightSw") == 1
        return None

class K1ParamSwitch(K1Switch):
    """Representation of a generic parameter switch."""

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
        param_key: str,
        translation_key: str,
        icon: str | None = None,
    ) -> None:
        """Initialize the switch."""
        super().__init__(
            coordinator,
            config_entry,
            translation_key=translation_key,
            unique_id_suffix=translation_key,
            icon=icon
        )
        self.param_key = param_key

    async def _send_websocket_command(self, is_on: bool) -> None:
        """Send the command to turn the param on or off."""
        await self.coordinator.send_param_command({self.param_key: 1 if is_on else 0})
        # Optimistically update the state
        self.coordinator.data[self.param_key] = 1 if is_on else 0

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            return self.coordinator.data.get(self.param_key) == 1
        return None