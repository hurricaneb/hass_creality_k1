"""Tests for the Creality K1 button platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_buttons(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the buttons."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        await setup_integration(hass, mock_config_entry)

        # Get all button entities
        buttons = hass.states.async_all("button")
        assert len(buttons) > 0

        # Assert that the state of each button matches the snapshot
        for button in buttons:
            assert button == snapshot(name=f"{button.entity_id}")


async def test_button_press(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the button press."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_refresh",
        return_value=True,
    ):
        await setup_integration(hass, mock_config_entry, data={})
        coordinator = mock_config_entry.runtime_data
        coordinator.websocket.send_message = AsyncMock()

        # Press the button
        await hass.services.async_call(
            "button",
            "press",
            {"entity_id": "button.mock_title_pause_print"},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"pause": 1}}
        )


from unittest.mock import AsyncMock

from homeassistant.helpers.update_coordinator import UpdateFailed


async def test_buttons_unavailable(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the buttons when the coordinator has no data."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator._async_update_data",
        side_effect=UpdateFailed("Test error"),
    ):
        await setup_integration(hass, mock_config_entry)

        # Get all button entities
        buttons = hass.states.async_all("button")
        assert len(buttons) > 0

        # Assert that all buttons are unavailable
        for button in buttons:
            assert button.state == "unavailable"
