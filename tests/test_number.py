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
            coordinator = mock_config_entry.runtime_data
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
            coordinator = mock_config_entry.runtime_data
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


async def test_number_error_cases(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the number error cases."""
    from custom_components.creality_k1.number import get_int, K1Number, K1NumberEntityDescription
    from unittest.mock import MagicMock

    # Test get_int with invalid data (covers lines 33)
    assert get_int({"key": "invalid"}, "key") is None
    
    # Test number with no value_fn (covers line 100)
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    desc = K1NumberEntityDescription(key="test", value_fn=None)
    number = K1Number(mock_coordinator, mock_entry, desc)
    assert number.native_value is None

    # Test flow rate optimistic update (covers line 110)
    await setup_integration(hass, mock_config_entry, data={"curFlowratePct": 100})
    coordinator = mock_config_entry.runtime_data
    coordinator.websocket.send_message = AsyncMock()

    await hass.services.async_call(
        NUMBER_DOMAIN,
        SERVICE_SET_VALUE,
        {"entity_id": "number.mock_title_flow_rate", "value": 110},
        blocking=True,
    )
    assert coordinator.data["curFlowratePct"] == 110

