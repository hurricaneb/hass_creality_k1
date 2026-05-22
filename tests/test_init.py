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


async def test_get_timelapses_service(hass: HomeAssistant, mock_config_entry) -> None:
    """Test get_timelapses service registration and invocation."""
    import pytest
    import voluptuous as vol

    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1Client", autospec=True
    ) as mock_client:
        client = mock_client.return_value
        client.is_connected = True
        client.disconnect.return_value = True

        # Mock the new get_timelapses api method
        mock_timelapses = [
            {
                "gcode": "benchy.gcode",
                "url": "http://1.2.3.4/downloads/video/1764698892.mp4",
                "timestamp": 1764698892,
                "start_time": "2025-11-20T12:34:52+00:00",
            }
        ]
        client.get_timelapses.return_value = mock_timelapses

        mock_config_entry.add_to_hass(hass)

        # Load integration
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        # Check that the service is registered
        assert hass.services.has_service(DOMAIN, "get_timelapses")

        # Call the service
        response = await hass.services.async_call(
            DOMAIN,
            "get_timelapses",
            {"config_entry_id": mock_config_entry.entry_id},
            blocking=True,
            return_response=True,
        )

        assert response == {"timelapses": mock_timelapses}
        assert client.get_timelapses.call_count == 2

        # Test with invalid config entry id
        with pytest.raises(vol.Invalid):
            await hass.services.async_call(
                DOMAIN,
                "get_timelapses",
                {"config_entry_id": "invalid_id"},
                blocking=True,
                return_response=True,
            )

