"""Platform for Creality K1 numbers."""
import logging
from dataclasses import dataclass
from typing import Callable, Any, Awaitable

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.const import PERCENTAGE

from .const import DOMAIN
from .entity import CrealityK1Entity
from .coordinator import CrealityK1DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True)
class K1NumberEntityDescription(NumberEntityDescription):
    """Describes Creality K1 number entity."""
    value_fn: Callable[[dict[str, Any]], float | None] = None
    set_value_fn: Callable[[CrealityK1DataUpdateCoordinator, float], Awaitable[None]] | None = None

def get_int(data: dict, key: str) -> int | None:
    val = data.get(key)
    if val is None: return None
    try: return int(val)
    except (ValueError, TypeError): return None

NUMBER_TYPES: tuple[K1NumberEntityDescription, ...] = (
    K1NumberEntityDescription(
        key="feedrate_pct",
        translation_key="feedrate_pct",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:speedometer",
        native_min_value=10,
        native_max_value=300,
        native_step=1,
        mode=NumberMode.SLIDER,
        value_fn=lambda data: get_int(data, "curFeedratePct"),
        set_value_fn=lambda coordinator, value: coordinator.send_gcode_command(f"M220 S{int(value)}")
    ),
    K1NumberEntityDescription(
        key="flowrate_pct",
        translation_key="flowrate_pct",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:water-percent",
        native_min_value=10,
        native_max_value=300,
        native_step=1,
        mode=NumberMode.SLIDER,
        value_fn=lambda data: get_int(data, "curFlowratePct"),
        set_value_fn=lambda coordinator, value: coordinator.send_gcode_command(f"M221 S{int(value)}")
    ),
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Creality K1 numbers."""
    coordinator: CrealityK1DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        K1Number(coordinator, config_entry, description)
        for description in NUMBER_TYPES
    ]
    async_add_entities(entities)


class K1Number(CrealityK1Entity, NumberEntity):
    """Representation of a Creality K1 number."""

    entity_description: K1NumberEntityDescription

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: K1NumberEntityDescription,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, config_entry)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the state of the number."""
        if not self.coordinator.data or not self.coordinator.websocket.is_connected:
            return None
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        if self.entity_description.set_value_fn:
            await self.entity_description.set_value_fn(self.coordinator, value)
            # Optimistically update the state
            if self.entity_description.key == "feedrate_pct":
                self.coordinator.data["curFeedratePct"] = int(value)
            elif self.entity_description.key == "flowrate_pct":
                self.coordinator.data["curFlowratePct"] = int(value)
            self.async_write_ha_state()
