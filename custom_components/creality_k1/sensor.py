"""Platform for Creality K1 sensor."""
import logging
from dataclasses import dataclass
from typing import Callable, Any

from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, PRINTER_STATE_MAP, DEFAULT_PRINTER_STATE
from .entity import CrealityK1Entity
from .coordinator import CrealityK1DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True)
class K1SensorEntityDescription(SensorEntityDescription):
    """Describes Creality K1 sensor entity."""
    value_fn: Callable[[dict[str, Any]], Any] | None = None
    attributes_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None

def get_float(data: dict, key: str) -> float | None:
    val = data.get(key)
    if val is None: return None
    try: return float(val)
    except (ValueError, TypeError): return None

def get_int(data: dict, key: str) -> int | None:
    val = data.get(key)
    if val is None: return None
    try: return int(val)
    except (ValueError, TypeError): return None

def get_state(data: dict, key: str) -> str | None:
    val = data.get(key)
    if val is None: return None
    try: return PRINTER_STATE_MAP.get(int(val), DEFAULT_PRINTER_STATE)
    except (ValueError, TypeError): return None

SENSOR_TYPES: tuple[K1SensorEntityDescription, ...] = (
    K1SensorEntityDescription(
        key="nozzle_temperature",
        translation_key="nozzle_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        value_fn=lambda data: get_float(data, "nozzleTemp"),
        attributes_fn=lambda data: {"target": data.get("targetNozzleTemp"), "max": data.get("maxNozzleTemp")}
    ),
    K1SensorEntityDescription(
        key="bed_temperature",
        translation_key="bed_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        value_fn=lambda data: get_float(data, "bedTemp0"),
        attributes_fn=lambda data: {"target": data.get("targetBedTemp0"), "max": data.get("maxBedTemp")}
    ),
    K1SensorEntityDescription(
        key="box_temperature",
        translation_key="box_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        icon="mdi:thermometer",
        value_fn=lambda data: get_float(data, "boxTemp")
    ),
    K1SensorEntityDescription(
        key="print_progress",
        translation_key="print_progress",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:percent",
        value_fn=lambda data: get_int(data, "printProgress")
    ),
    K1SensorEntityDescription(
        key="total_layer",
        translation_key="total_layer",
        icon="mdi:layers",
        value_fn=lambda data: get_int(data, "TotalLayer")
    ),
    K1SensorEntityDescription(
        key="working_layer",
        translation_key="working_layer",
        icon="mdi:cube-outline",
        value_fn=lambda data: get_int(data, "layer")
    ),
    K1SensorEntityDescription(
        key="used_material",
        translation_key="used_material",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="cm",
        icon="mdi:tape-measure",
        value_fn=lambda data: get_int(data, "usedMaterialLength")
    ),
    K1SensorEntityDescription(
        key="print_job_time",
        translation_key="print_job_time",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="s",
        icon="mdi:timer-sand",
        value_fn=lambda data: get_int(data, "printJobTime")
    ),
    K1SensorEntityDescription(
        key="print_left_time",
        translation_key="print_left_time",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="s",
        icon="mdi:timer-sand",
        value_fn=lambda data: get_int(data, "printLeftTime")
    ),
    K1SensorEntityDescription(
        key="print_state",
        translation_key="print_state",
        icon="mdi:printer-3d",
        value_fn=lambda data: get_state(data, "state")
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Creality K1 sensors."""
    coordinator: CrealityK1DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        K1Sensor(coordinator, config_entry, description)
        for description in SENSOR_TYPES
    ]
    async_add_entities(entities)


class K1Sensor(CrealityK1Entity, SensorEntity):
    """Representation of a Creality K1 sensor."""

    entity_description: K1SensorEntityDescription

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
        description: K1SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, config_entry)
        self.entity_description = description
        self._attr_unique_id = f"{config_entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.websocket.is_connected:
            return None
        if self.entity_description.value_fn:
            return self.entity_description.value_fn(self.coordinator.data)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the sensor attributes."""
        if not self.coordinator.data or not self.coordinator.websocket.is_connected:
            return {}
        if self.entity_description.attributes_fn:
            return self.entity_description.attributes_fn(self.coordinator.data)
        return {}