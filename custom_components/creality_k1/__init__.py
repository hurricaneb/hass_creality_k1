"""Creality K1 Integration."""
import logging

from homeassistant.config_entries import ConfigEntry, ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall, ServiceResponse, SupportsResponse
from homeassistant.helpers import config_validation as cv
import voluptuous as vol

from .const import DOMAIN, PLATFORMS
from .coordinator import CrealityK1DataUpdateCoordinator  # DataUpdateCoordinator class from coordinator.py

_LOGGER = logging.getLogger(__name__)

type CrealityK1ConfigEntry = ConfigEntry[CrealityK1DataUpdateCoordinator]

# Define service schema
GET_TIMELAPSES_SCHEMA = vol.Schema(
    {
        vol.Required("config_entry_id"): cv.string,
    }
)

async def async_setup_entry(hass: HomeAssistant, config_entry: CrealityK1ConfigEntry) -> bool:
    """Set up Creality K1 from a config entry."""

    # Store coordinator instance per entry for platform access
    coordinator = CrealityK1DataUpdateCoordinator(hass, config_entry)
    config_entry.runtime_data = coordinator

    # Trigger initial connection
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as e:
        _LOGGER.warning(f"Initial connection to printer failed: {e}")

    # Register the get_timelapses service/action
    async def handle_get_timelapses(call: ServiceCall) -> ServiceResponse:
        entry_id = call.data["config_entry_id"]
        # Find matching config entry and coordinator
        entry = hass.config_entries.async_get_entry(entry_id)
        if not entry or entry.domain != DOMAIN:
            raise vol.Invalid("Invalid config entry ID")
        
        coord: CrealityK1DataUpdateCoordinator = entry.runtime_data
        
        # Fetch the timelapses using the new api method
        timelapses = await coord.websocket.get_timelapses()
        return {"timelapses": timelapses}

    if not hass.services.has_service(DOMAIN, "get_timelapses"):
        hass.services.async_register(
            DOMAIN,
            "get_timelapses",
            handle_get_timelapses,
            schema=GET_TIMELAPSES_SCHEMA,
            supports_response=SupportsResponse.ONLY,
        )

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: CrealityK1ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms first
    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS) # Use PLATFORMS

    if unload_ok:
        # Get the specific websocket instance and close it.
        coordinator = config_entry.runtime_data
        await coordinator.websocket.disconnect()

        # Remove service if this is the last entry being unloaded
        current_entries = hass.config_entries.async_entries(DOMAIN)
        loaded_entries = [
            entry
            for entry in current_entries
            if entry.state == ConfigEntryState.LOADED and entry.entry_id != config_entry.entry_id
        ]
        if not loaded_entries and hass.services.has_service(DOMAIN, "get_timelapses"):
            hass.services.async_remove(DOMAIN, "get_timelapses")

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Reload config entry."""
    return await hass.config_entries.async_reload(config_entry.entry_id)

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Running migration of config entry")
    return True