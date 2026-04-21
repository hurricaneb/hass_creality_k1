"""Platform for Creality K1 binary sensors."""
import logging
from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
    BinarySensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import CrealityK1Entity
from .coordinator import CrealityK1DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
PARALLEL_UPDATES = 0

@dataclass(frozen=True)
class K1BinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes Creality K1 binary sensor entity."""
    value_fn: Callable[[dict[str, Any]], bool | None] = None


BINARY_SENSOR_TYPES: tuple[K1BinarySensorEntityDescription, ...] = (
    K1BinarySensorEntityDescription(
        key="material_detect",
        translation_key="material_detect",
        icon="mdi:printer-3d-nozzle",
        value_fn=lambda data: data.get("materialDetect") == 1 if data.get("materialDetect") is not None else None,
    ),
    K1BinarySensorEntityDescription(
        key="tf_card",
        translation_key="tf_card",
        icon="mdi:sd",
        value_fn=lambda data: data.get("tfCard") == 1 if data.get("tfCard") is not None else None,
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Creality K1 binary sensors."""
    coordinator: CrealityK1DataUpdateCoordinator = config_entry.runtime_data
    
    entities = [
        K1BinarySensor(coordinator, config_entry, description)
        for description in BINARY_SENSOR_TYPES
    ]
    async_add_entities(entities)


class K1BinarySensor(CrealityK1Entity, BinarySensorEntity):
    """Representation of a Creality K1 binary sensor."""

    entity_description: K1BinarySensorEntityDescription

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: K1BinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, config_entry)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return True if the binary sensor is on."""
        if not self.coordinator.data or not self.coordinator.websocket.is_connected:
            return None
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None
