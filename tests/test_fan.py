"""Tests for the Creality K1 fan platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_fans(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the fans."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        await setup_integration(hass, mock_config_entry)

        # Get all fan entities
        fans = hass.states.async_all("fan")
        assert len(fans) > 0

        # Assert that the state of each fan matches the snapshot
        for fan in fans:
            assert fan == snapshot(name=f"{fan.entity_id}")


async def test_fan_services(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the fan services."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_refresh",
        return_value=True,
    ):
        await setup_integration(
            hass,
            mock_config_entry,
            data={"fan_speed_1": 0, "fan_speed_2": 0, "fan_speed_3": 0},
        )
        coordinator = mock_config_entry.runtime_data
        coordinator.websocket.send_message = AsyncMock()

        # Turn on the fan
        await hass.services.async_call(
            "fan",
            "turn_on",
            {"entity_id": "fan.mock_title_model_fan", "percentage": 50},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"gcodeCmd": "M106 P0 S128"}}
        )

        # Turn off the fan
        await hass.services.async_call(
            "fan",
            "turn_off",
            {"entity_id": "fan.mock_title_model_fan"},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"gcodeCmd": "M106 P0 S0"}}
        )

        # Set speed
        await hass.services.async_call(
            "fan",
            "set_percentage",
            {"entity_id": "fan.mock_title_model_fan", "percentage": 75},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"gcodeCmd": "M106 P0 S191"}}
        )


from unittest.mock import AsyncMock

from homeassistant.helpers.update_coordinator import UpdateFailed


async def test_fans_unavailable(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the fans when the coordinator has no data."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator._async_update_data",
        side_effect=UpdateFailed("Test error"),
    ):
        await setup_integration(hass, mock_config_entry)

        # Get all fan entities
        fans = hass.states.async_all("fan")
        assert len(fans) > 0

        # Assert that all fans are unavailable
        for fan in fans:
            assert fan.state == "unavailable"


async def test_fan_error_cases(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the fan error cases for coverage."""
    await setup_integration(hass, mock_config_entry, data={"fan": "invalid", "modelFanPct": None})
    coordinator = mock_config_entry.runtime_data
    coordinator.websocket.send_message = AsyncMock()
    from custom_components.creality_k1.fan import K1Fan

    # Create instance directly for full coverage of properties
    fan_entity = K1Fan(coordinator, "modelFanPct", "fan", 0, mock_config_entry, "model_fan", "mdi:fan")
    
    # Test is_on ValueError (covers line 81-82)
    coordinator.data["fan"] = "invalid"
    assert fan_entity.is_on is None
    
    # Test percentage with is_on = None (covers line 92-93)
    coordinator.data["fan"] = None
    assert fan_entity.percentage is None

    # Test percentage with value = None (covers line 96-97)
    coordinator.data["fan"] = 1
    coordinator.data["modelFanPct"] = None
    assert fan_entity.percentage is None

    # Test percentage with invalid value (covers line 100-101)
    coordinator.data["modelFanPct"] = "invalid"
    assert fan_entity.percentage is None

    # Test disconnected (covers line 102)
    coordinator.websocket.is_connected = False
    assert fan_entity.percentage is None

    # Test fan is off (covers line 92)
    coordinator.websocket.is_connected = True
    coordinator.data["fan"] = 0
    assert fan_entity.percentage == 0

    # Test invalid percentage (covers line 121-122)
    await fan_entity.async_set_percentage(150)
    coordinator.websocket.send_message.assert_not_called()

    # Test turn on without percentage (covers line 136-137)
    await fan_entity.async_turn_on()
    coordinator.websocket.send_message.assert_called_with(
        {"method": "set", "params": {"gcodeCmd": "M106 P0 S255"}}
    )

    # Test command failure (covers line 114-115)
    coordinator.websocket.send_message.side_effect = Exception("error")
    await fan_entity.async_turn_off()
    # Should log error and not crash





