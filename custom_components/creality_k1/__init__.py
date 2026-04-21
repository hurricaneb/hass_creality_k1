"""Creality K1 Integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import CrealityK1DataUpdateCoordinator  # DataUpdateCoordinator class from coordinator.py

_LOGGER = logging.getLogger(__name__)

type CrealityK1ConfigEntry = ConfigEntry[CrealityK1DataUpdateCoordinator]

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

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Reload config entry."""
    return await hass.config_entries.async_reload(config_entry.entry_id)

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Running migration of config entry")
    return True