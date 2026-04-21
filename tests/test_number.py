"""Tests for the Creality K1 number platform."""
from unittest.mock import patch, AsyncMock

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion
from homeassistant.components.number import DOMAIN as NUMBER_DOMAIN, SERVICE_SET_VALUE

from . import setup_integration

async def test_numbers(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the creation and values of the numbers."""
    with patch("custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_config_entry_first_refresh") as mock_refresh:
        async def mock_first_refresh():
            coordinator = hass.data["creality_k1"][mock_config_entry.entry_id]
            coordinator.data = {
                "curFeedratePct": 100,
                "curFlowratePct": 95,
            }
        mock_refresh.side_effect = mock_first_refresh

        await setup_integration(hass, mock_config_entry)

        entities = hass.states.async_all(NUMBER_DOMAIN)
        assert len(entities) > 0

        for entity in entities:
            assert entity == snapshot(name=f"{entity.entity_id}")

async def test_set_number(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test setting number value."""
    with patch("custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_config_entry_first_refresh") as mock_refresh:
        async def mock_first_refresh():
            coordinator = hass.data["creality_k1"][mock_config_entry.entry_id]
            coordinator.data = {
                "curFeedratePct": 100,
            }
        mock_refresh.side_effect = mock_first_refresh

        await setup_integration(hass, mock_config_entry)

        with patch("custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.send_gcode_command", new_callable=AsyncMock) as mock_send:
            await hass.services.async_call(
                NUMBER_DOMAIN,
                SERVICE_SET_VALUE,
                {"entity_id": "number.mock_title_print_speed", "value": 150},
                blocking=True,
            )
            mock_send.assert_called_once_with("M220 S150")
            
            state = hass.states.get("number.mock_title_print_speed")
            assert float(state.state) == 150.0
