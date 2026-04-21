"""DataUpdateCoordinator for the Creality K1 integration."""
import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed
)

from .const import DOMAIN, HASS_UPDATE_INTERVAL, WS_OPERATION_TIMEOUT
from creality_k1_api import CrealityK1Client

_LOGGER = logging.getLogger(__name__)

class CrealityK1DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Creality K1."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=HASS_UPDATE_INTERVAL)
            )
        self.latest_data = {}  # Store the processed data
        printer_ip = config_entry.data.get(CONF_IP_ADDRESS)  # Get IP from config entry
        ws_url = f"ws://{printer_ip}:9999"
        self.websocket = CrealityK1Client(
            url=ws_url,
            new_data_callback=self.process_raw_data,
            )

    async def _async_update_data(self) -> dict:
        """Use this to ensure the Creality K1 is connected"""
        if not self.websocket.is_connected:
            _LOGGER.debug("Coordinator: WebSocket not connected, attempting connect.")
            await self.websocket.connect()
        if not self.websocket.is_connected:
            raise UpdateFailed("Creality K1 not connected") # Important to raise for retries
        return self.latest_data

    def process_raw_data(self, raw_data: dict) -> None:
        """Update latest data with raw data."""
        _LOGGER.debug(f"Coordinator: Fetched raw data: {raw_data}")
        if raw_data:
            self.latest_data.update(raw_data)  # Update latest data
            _LOGGER.debug(f"Coordinator: Processed data: {self.latest_data}")
            _LOGGER.debug(f"Coordinator: lightSw value in processed_data: {self.latest_data.get('lightSw')}")
            self.async_set_updated_data(self.latest_data)

    async def send_gcode_command(self, gcode: str) -> None:
        """Helper function to send GCODE commands."""
        command = {"method": "set", "params": {"gcodeCmd": gcode}}
        _LOGGER.debug(f"Sending gcode command: {command}")
        try:
            await self.websocket.send_message(command)
        except Exception as e:
            _LOGGER.error(f"Failed to send gcode command {command}: {e}")

    async def send_param_command(self, params: dict) -> None:
        """Helper function to send raw parameter commands."""
        command = {"method": "set", "params": params}
        _LOGGER.debug(f"Sending param command: {command}")
        try:
            await self.websocket.send_message(command)
        except Exception as e:
            _LOGGER.error(f"Failed to send param command {command}: {e}")