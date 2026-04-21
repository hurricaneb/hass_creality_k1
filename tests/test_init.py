"""Tests for the Creality K1 integration."""

from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from custom_components.creality_k1.const import DOMAIN


from unittest.mock import patch


async def test_load_unload_integration(hass, mock_config_entry):
    """Test loading and unloading the integration."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1Client", autospec=True
    ) as mock_client:
        client = mock_client.return_value
        client.is_connected = True
        client.disconnect.return_value = True

        mock_config_entry.add_to_hass(hass)

        # Load the integration
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.LOADED
        assert mock_config_entry.runtime_data is not None

        # Unload the integration
        unload_ok = await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    assert unload_ok
    assert mock_config_entry.state is ConfigEntryState.NOT_LOADED


async def test_reload_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test reloading the config entry."""
    from custom_components.creality_k1 import async_reload_entry
    with patch("homeassistant.config_entries.ConfigEntries.async_reload", return_value=True):
        assert await async_reload_entry(hass, mock_config_entry)



async def test_migrate_entry(hass: HomeAssistant, mock_config_entry) -> None:
    """Test migrating the config entry."""
    from custom_components.creality_k1 import async_migrate_entry
    assert await async_migrate_entry(hass, mock_config_entry)
