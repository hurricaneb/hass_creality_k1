# Creality K1 Button Module
#
# Copyright (C) 2025 Joshua Wherrett <thejoshw.code@gmail.com>
#
# This file may be distributed under the terms of the GNU GPLv3 license.
"""Platform for Creality K1 buttons."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, BUTTON_CONTROLS
from .entity import CrealityK1Entity
from .coordinator import CrealityK1DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Creality K1 buttons from a config entry."""
    coordinator: CrealityK1DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    buttons = []
    for (translation_key, params) in BUTTON_CONTROLS:
        buttons.append(
            K1Button(
                coordinator,
                config_entry,
                translation_key,
                params,
                translation_key
            )
        )
    async_add_entities(buttons)

class K1Button(CrealityK1Entity, ButtonEntity):
    """Base class for Creality K1 buttons."""

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
        translation_key: str,
        params: dict,
        unique_id_suffix: str | None = None
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, config_entry)
        self._attr_translation_key = translation_key
        self._params = params
        self._attr_unique_id = f"{config_entry.entry_id}_button"
        if unique_id_suffix:
            self._attr_unique_id += f"_{unique_id_suffix}"

    async def async_press(self):
        """Press the button."""
        await self._send_websocket_command()
        self.async_write_ha_state()

    async def _send_websocket_command(self) -> None:
        """Send the appropriate command to the printer via WebSocket."""
        command = {"method": "set", "params": self._params}
        _LOGGER.debug(f"Sending button command: {command}")
        await self.coordinator.websocket.send_message(command)