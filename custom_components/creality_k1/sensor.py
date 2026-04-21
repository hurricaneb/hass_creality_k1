"""Platform for Creality K1 sensor."""
import logging

from homeassistant.const import UnitOfTemperature, PERCENTAGE
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, PRINTER_STATE_MAP, DEFAULT_PRINTER_STATE, SENSOR_NAME_BED_TEMP, SENSOR_NAME_BOX_TEMP, SENSOR_NAME_NOZZLE_TEMP, SENSOR_NAME_PRINT_PROGRESS, SENSOR_NAME_TOTAL_LAYER, SENSOR_NAME_WORKING_LAYER, SENSOR_NAME_USED_MATERIAL, SENSOR_NAME_TOTAL_PRINT_TIME, SENSOR_NAME_PRINT_JOB_LEFT, SENSOR_NAME_PRINT_STATE, DEVICE_MANUFACTURER, DEVICE_MODEL
from .coordinator import CrealityK1DataUpdateCoordinator  # DataUpdateCoordinator class from coordinator.py
from .helpers import get_hw_sw_versions

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Creality K1 sensors."""
    coordinator: CrealityK1DataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([
        K1NozzleTemperatureSensor(coordinator, config_entry),
        K1BedTemperatureSensor(coordinator, config_entry),
        K1BoxTemperatureSensor(coordinator, config_entry),
        K1PrintProgressSensor(coordinator, config_entry),
        K1TotalLayerSensor(coordinator, config_entry),
        K1WorkingLayerSensor(coordinator, config_entry),
        K1UsedMaterialSensor(coordinator, config_entry),
        K1PrintJobTimeSensor(coordinator, config_entry),
        K1PrintLeftTimeSensor(coordinator, config_entry),
        K1PrintState(coordinator, config_entry),
    ])


class K1Sensor(CoordinatorEntity, SensorEntity):
    """Base class for Creality K1 sensors."""
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
        translation_key: str,
        device_class: SensorDeviceClass | None = None,
        unit_of_measurement: str | None = None,
        state_class: SensorStateClass | None = None,
        icon: str | None = None,
        unique_id_suffix: str | None = None,  # Add unique_id here
        ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_translation_key = translation_key
        self._attr_device_class = device_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_state_class = state_class
        self._attr_icon = icon
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
        return (
            self.coordinator.websocket.is_connected
            and self.coordinator.data is not None
            and super().available
        )


class K1NozzleTemperatureSensor(K1Sensor):
    """Representation of a Creality K1 Nozzle Temperature sensor."""

    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the nozzle temperature sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="nozzle_temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            unique_id_suffix="nozzle_temperature", # Pass suffix
            icon="mdi:thermometer" # Optional: Explicitly set icon if needed
        )

    @property
    def native_value(self) -> float | None:
        """Return the current nozzle temperature."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            nozzle_temp = self.coordinator.data.get("nozzleTemp")
            if isinstance(nozzle_temp, str):
                try:
                    return float(nozzle_temp)
                except ValueError:
                    _LOGGER.warning(f"Invalid nozzleTemp value: {nozzle_temp}")
                    return None
            elif isinstance(nozzle_temp, (int, float)):
                return float(nozzle_temp)
        return None

    @property
    def extra_state_attributes(self):
        """Return the sensor attributes."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            return {
                "target": self.coordinator.data.get("targetNozzleTemp"),
                "max": self.coordinator.data.get("maxNozzleTemp"),
            }
        return {}


class K1BedTemperatureSensor(K1Sensor):
    """Representation of a Creality K1 Bed Temperature sensor."""

    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the bed temperature sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="bed_temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            unique_id_suffix="bed_temperature", # Pass suffix
            icon="mdi:thermometer" # Optional: Explicitly set icon if needed
        )

    @property
    def native_value(self) -> float | None:
        """Return the current bed temperature."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            bed_temp = self.coordinator.data.get("bedTemp0")
            if isinstance(bed_temp, str):
                try:
                    return float(bed_temp)
                except ValueError:
                    _LOGGER.warning(f"Invalid bedTemp0 value: {bed_temp}")
                    return None
            elif isinstance(bed_temp, (int, float)):
                return float(bed_temp)
        return None

    @property
    def extra_state_attributes(self):
        """Return the sensor attributes."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            return {
                "target": self.coordinator.data.get("targetBedTemp0"),
                "max": self.coordinator.data.get("maxBedTemp"),
            }
        return {}


class K1BoxTemperatureSensor(K1Sensor):
    """Representation of a Creality K1 Box Temperature sensor."""

    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the box temperature sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="box_temperature",
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=UnitOfTemperature.CELSIUS,
            unique_id_suffix="box_temperature", # Pass suffix
            icon="mdi:thermometer" # Optional: Explicitly set icon if needed
        )

    @property
    def native_value(self) -> float | None:
        """Return the current box temperature."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            box_temp = self.coordinator.data.get("boxTemp")
            if isinstance(box_temp, str):
                try:
                    return float(box_temp)
                except ValueError:
                    _LOGGER.warning(f"Invalid boxTemp value: {box_temp}")
                    return None
            elif isinstance(box_temp, (int, float)):
                return float(box_temp)
        return None


class K1PrintProgressSensor(K1Sensor):
    """Representation of a Creality K1 Print Progress sensor."""

    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the print progress sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="print_progress",
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement=PERCENTAGE,
            unique_id_suffix="print_progress", # Pass suffix
            icon="mdi:percent" # Optional: Explicitly set icon if needed
        )

    @property
    def native_value(self) -> int | None:
        """Return the current print progress."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            progress = self.coordinator.data.get("printProgress")
            if isinstance(progress, str):
                try:
                    return int(progress)
                except ValueError:
                    _LOGGER.warning(f"Invalid printProgress value: {progress}")
                    return None
            elif isinstance(progress, int):
                return progress
        return None


class K1TotalLayerSensor(K1Sensor):
    """Representation of a Creality K1 Total Layer sensor."""

    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the total layer sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="total_layer",
            unique_id_suffix="total_layer_count", # Pass suffix
            icon="mdi:layers" # Optional: Explicitly set icon if needed
        )

    @property
    def native_value(self) -> int | None:
        """Return the total layer count."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            total_layer = self.coordinator.data.get("TotalLayer")
            if isinstance(total_layer, str):
                try:
                    return int(total_layer)
                except ValueError:
                    _LOGGER.warning(f"Invalid TotalLayer value: {total_layer}")
                    return None
            elif isinstance(total_layer, int):
                return total_layer
        return None


class K1WorkingLayerSensor(K1Sensor):
    """Representation of a Creality K1 Working Layer sensor."""

    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the working layer sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="working_layer",
            unique_id_suffix="working_layer_count", # Pass suffix
            icon="mdi:cube-outline" # Optional: Explicitly set icon if needed
        )

    @property
    def native_value(self) -> int | None:
        """Return the current working layer."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            layer = self.coordinator.data.get("layer")
            if isinstance(layer, str):
                try:
                    return int(layer)
                except ValueError:
                    _LOGGER.warning(f"Invalid layer value: {layer}")
                    return None
            elif isinstance(layer, int):
                return layer
        return None


class K1UsedMaterialSensor(K1Sensor):
    """Representation of a Creality K1 Used Material sensor."""

    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the used material sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="used_material",
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement="cm",
            unique_id_suffix="used_material_length", # Pass suffix
            icon="mdi:tape-measure" # Optional: Explicitly set icon if needed
        )

    @property
    def native_value(self) -> int | None:
        """Return the used material length."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            used_material = self.coordinator.data.get("usedMaterialLength")
            if isinstance(used_material, str):
                try:
                    return int(used_material)
                except ValueError:
                    _LOGGER.warning(f"Invalid usedMaterialLength value: {used_material}")
                    return None
            elif isinstance(used_material, int):
                return used_material
        return None
    
class K1PrintJobTimeSensor(K1Sensor):
    """K1 Print Job Time Sensor."""
    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the print job time sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="print_job_time",
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement="s",
            unique_id_suffix="print_job_time", # Pass suffix
            icon="mdi:timer-sand" # Optional: Explicitly set icon if needed
        )

    @property
    def native_value(self) -> int | None:
        """Return the print job time."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            print_job_time = self.coordinator.data.get("printJobTime")
            if isinstance(print_job_time, str):
                try:
                    return int(print_job_time)
                except ValueError:
                    _LOGGER.warning(f"Invalid printJobTime value: {print_job_time}")
                    return None
            elif isinstance(print_job_time, int):
                return print_job_time
        return None
    
class K1PrintLeftTimeSensor(K1Sensor):
    """K1 Print Job Left Sensor."""
    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the print job left sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="print_left_time",
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
            unit_of_measurement="s",
            unique_id_suffix="print_left_time", # Pass suffix
            icon="mdi:timer-sand" # Optional: Explicitly set icon if needed
        )

    @property
    def native_value(self) -> int | None:
        """Return the print left time."""
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            print_left_time = self.coordinator.data.get("printLeftTime")
            if isinstance(print_left_time, str):
                try:
                    return int(print_left_time)
                except ValueError:
                    _LOGGER.warning(f"Invalid printLeftTime value: {print_left_time}")
                    return None
            elif isinstance(print_left_time, int):
                return print_left_time
        return None
    
class K1PrintState(K1Sensor): 
    """K1 Print State Sensor"""
    def __init__(
        self, coordinator: CrealityK1DataUpdateCoordinator, config_entry: ConfigEntry
        ) -> None:
        """Initialize the print state Sensor."""
        super().__init__(
            coordinator=coordinator,
            config_entry=config_entry, # Pass entry
            translation_key="print_state",
            unique_id_suffix="print_state_sensor", # Pass suffix
            icon="mdi:printer-3d" # Optional: Explicitly set icon if needed
        )
    
    @property
    def native_value(self) -> str | None: 
        """Return The Printers State as a descriptive string."""
        raw_state_value = None
        if self.coordinator.data and self.coordinator.websocket.is_connected:
            raw_state_value = self.coordinator.data.get("state")

        int_state: int | None = None
        if isinstance(raw_state_value, (int, str)):
            try:
                int_state = int(raw_state_value)
            except (ValueError, TypeError):
                _LOGGER.warning(f"Invalid non-integer state value received: {raw_state_value}")
        elif raw_state_value is not None:
            _LOGGER.warning(f"Unexpected state value type: {type(raw_state_value)} ({raw_state_value})")

        if int_state is not None:
            return PRINTER_STATE_MAP.get(int_state, DEFAULT_PRINTER_STATE)

        return None