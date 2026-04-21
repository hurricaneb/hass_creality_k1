"""Platform for Creality K1 switches."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, SWITCH_NAME_LIGHT, DEVICE_MANUFACTURER, DEVICE_MODEL
from .coordinator import CrealityK1DataUpdateCoordinator  # DataUpdateCoordinator
from .helpers import get_hw_sw_versions

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
    ) -> None:
    """Set up the Creality K1 switches."""
    coordinator: CrealityK1DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id] # Get correct coordinator when having multiple printers

    async_add_entities([
        K1LightSwitch(coordinator, config_entry),
    ])


class K1Switch(CoordinatorEntity, SwitchEntity):
    """Base class for Creality K1 switches."""
    _attr_has_entity_name = True
    _attr_name = None

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
        name: str,
        icon: str | None = None,
        unique_id_suffix: str | None = None,
        ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_icon = icon
        self._state = False  # Default state
        self._config_entry = config_entry
        if unique_id_suffix:
            self._attr_unique_id = f"{config_entry.entry_id}_{unique_id_suffix}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        if self.coordinator.data:
            (hw_version, sw_version) = get_hw_sw_versions(self.coordinator.data)
            return DeviceInfo(
                identifiers={(DOMAIN, self._config_entry.entry_id)},
                name=self.coordinator.data.get('hostname', self._config_entry.title),
                manufacturer=DEVICE_MANUFACTURER,
                model=self.coordinator.data.get('model', DEVICE_MODEL),
                hw_version=hw_version,
                sw_version=sw_version,
                via_device=(DOMAIN, self._config_entry.entry_id)
            )
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name=self._config_entry.title,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            via_device=(DOMAIN, self._config_entry.entry_id)
        )

    @property
    def available(self) -> bool:
        return self.coordinator.websocket.is_connected and super().available

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
        raise NotImplementedError  # To be implemented in subclasses


class K1LightSwitch(K1Switch):
    """Representation of a Creality K1 light switch."""

    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the light switch."""
        super().__init__(
        coordinator,
        config_entry,
        name=SWITCH_NAME_LIGHT,
        unique_id_suffix="printer_light",
        icon="mdi:desk-lamp"
        )
        # Initial state from data
        if coordinator.data:
            light_sw_value = coordinator.data.get("lightSw")
            _LOGGER.debug(f"Switch: Initial lightSw value: {light_sw_value}")  # Add this line

    async def _send_websocket_command(self, is_on: bool) -> None:
        """Send the command to turn the light on or off."""
        command = {"method": "set", "params": {"lightSw": 1 if is_on else 0}}
        _LOGGER.debug(f"Sending light command: {command}")  # Log the command
        await self.coordinator.websocket.send_message(command)

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        # If coordinator don't have data yet, return None
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            # Read direct from coordinator latest data
            return self.coordinator.data.get("lightSw") == 1
        return None