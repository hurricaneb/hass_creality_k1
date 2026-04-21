"""Tests for the Creality K1 switch platform."""
from unittest.mock import patch
import pytest

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_switches(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the switches."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        await setup_integration(hass, mock_config_entry)

        # Get all switch entities
        switches = hass.states.async_all("switch")
        assert len(switches) > 0

        # Assert that the state of each switch matches the snapshot
        for switch in switches:
            assert switch == snapshot(name=f"{switch.entity_id}")


async def test_switch_services(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the switch services."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_refresh",
        return_value=True,
    ):
        await setup_integration(hass, mock_config_entry, data={"lightSw": 0})
        coordinator = mock_config_entry.runtime_data
        coordinator.websocket.send_message = AsyncMock()

        # Turn on the switch
        await hass.services.async_call(
            "switch",
            "turn_on",
            {"entity_id": "switch.mock_title_printer_light"},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"lightSw": 1}}
        )

        # Turn off the switch
        await hass.services.async_call(
            "switch",
            "turn_off",
            {"entity_id": "switch.mock_title_printer_light"},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"lightSw": 0}}
        )


from unittest.mock import AsyncMock

from homeassistant.helpers.update_coordinator import UpdateFailed


async def test_switches_unavailable(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the switches when the coordinator has no data."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator._async_update_data",
        side_effect=UpdateFailed("Test error"),
    ):
        await setup_integration(hass, mock_config_entry)

        # Get all switch entities
        switches = hass.states.async_all("switch")
        assert len(switches) > 0

        # Assert that all switches are unavailable
        for switch in switches:
            assert switch.state == "unavailable"


async def test_param_switches(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the generic parameter switches."""
    await setup_integration(hass, mock_config_entry, data={"aiDetection": 0})
    coordinator = mock_config_entry.runtime_data
    coordinator.websocket.send_message = AsyncMock()

    # Turn on AI Detection
    await hass.services.async_call(
        "switch",
        "turn_on",
        {"entity_id": "switch.mock_title_ai_detection"},
        blocking=True,
    )
    # Check if correct param command was sent
    # Note: K1ParamSwitch uses coordinator.send_param_command which sends {"method": "set", "params": {key: val}}
    coordinator.websocket.send_message.assert_called_with(
        {"method": "set", "params": {"aiDetection": 1}}
    )
    # Check optimistic update
    assert coordinator.data["aiDetection"] == 1

    # Test NotImplementedError in base class (covers line 62/63)
    from custom_components.creality_k1.switch import K1Switch
    switch = K1Switch(coordinator, mock_config_entry, "test")
    with pytest.raises(NotImplementedError):
        await switch._send_websocket_command(True)


