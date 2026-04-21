"""Tests for the Creality K1 integration."""

from custom_components.creality_k1.const import DOMAIN
from homeassistant.config_entries import ConfigEntryState


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
        assert DOMAIN in hass.data
        assert mock_config_entry.entry_id in hass.data[DOMAIN]

        # Unload the integration
        assert await hass.config_entries.async_unload(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        assert mock_config_entry.state is ConfigEntryState.NOT_LOADED
        assert not hass.data.get(DOMAIN)
