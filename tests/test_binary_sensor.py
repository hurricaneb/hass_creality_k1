"""Tests for the Creality K1 binary sensor platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration

async def test_binary_sensors(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the creation and values of the binary sensors."""
    with patch("custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_config_entry_first_refresh") as mock_refresh:
        async def mock_first_refresh():
            coordinator = hass.data["creality_k1"][mock_config_entry.entry_id]
            coordinator.data = {
                "materialDetect": 1,
                "tfCard": 0,
            }
        mock_refresh.side_effect = mock_first_refresh

        await setup_integration(hass, mock_config_entry)

        # Get all binary sensor entities
        entities = hass.states.async_all("binary_sensor")
        assert len(entities) > 0

        for entity in entities:
            assert entity == snapshot(name=f"{entity.entity_id}")
