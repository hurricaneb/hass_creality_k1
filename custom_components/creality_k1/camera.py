"""Platform for Creality K1 camera."""

import logging

from homeassistant.components.mjpeg.camera import MjpegCamera
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
    """Set up the Creality K1 camera from a config entry."""
    coordinator: CrealityK1DataUpdateCoordinator = config_entry.runtime_data
    async_add_entities([K1Camera(coordinator, config_entry)])


class K1Camera(CrealityK1Entity, MjpegCamera):
    """Representation of a Creality K1 Camera."""

    def __init__(
        self,
        coordinator: CrealityK1DataUpdateCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the camera."""
        # Initialize CrealityK1Entity first
        CrealityK1Entity.__init__(self, coordinator, config_entry)
        
        # Initialize MjpegCamera
        mjpeg_url = f"http://{config_entry.data['ip_address']}:8080/?action=stream"
        
        MjpegCamera.__init__(
            self,
            mjpeg_url=mjpeg_url,
            still_image_url=None,
        )
        
        self._attr_translation_key = "camera"
        self._attr_unique_id = f"{config_entry.entry_id}_camera"

    @property
    def available(self) -> bool:
        """Return True if the camera is available."""
        if not self.coordinator.websocket.is_connected:
            return False
        if self.coordinator.data and self.coordinator.data.get("video") == 0:
            return False
        return super().available
