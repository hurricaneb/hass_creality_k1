"""Base entity for Creality K1."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL
from .coordinator import CrealityK1DataUpdateCoordinator
from .helpers import get_hw_sw_versions


class CrealityK1Entity(CoordinatorEntity[CrealityK1DataUpdateCoordinator]):
    """Base class for Creality K1 entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._config_entry = config_entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        if self.coordinator.data:
            (hw_version, sw_version) = get_hw_sw_versions(self.coordinator.data)
            return DeviceInfo(
                identifiers={(DOMAIN, self._config_entry.entry_id)},
                name=self.coordinator.data.get("hostname", self._config_entry.title),
                manufacturer=DEVICE_MANUFACTURER,
                model=self.coordinator.data.get("model", DEVICE_MODEL),
                hw_version=hw_version,
                sw_version=sw_version,
            )
        return DeviceInfo(
            identifiers={(DOMAIN, self._config_entry.entry_id)},
            name=self._config_entry.title,
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
        )

    @property
    def available(self) -> bool:
        """Return true if the printer is connected."""
        return (
            self.coordinator.websocket.is_connected
            and super().available
        )
