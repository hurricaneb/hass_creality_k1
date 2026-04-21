"""Tests for the Creality K1 data update coordinator."""
from unittest.mock import AsyncMock, patch, PropertyMock

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.creality_k1.coordinator import CrealityK1DataUpdateCoordinator


async def test_coordinator_connection(hass: HomeAssistant, mock_config_entry):
    """Test the coordinator's connection logic."""
    coordinator = CrealityK1DataUpdateCoordinator(hass, mock_config_entry)

    with patch.object(
        coordinator.websocket, "connect", AsyncMock()
    ) as mock_connect, patch.object(
        type(coordinator.websocket), "is_connected", new_callable=PropertyMock
    ) as mock_is_connected:
        # Test successful connection
        mock_is_connected.return_value = True
        await coordinator._async_update_data()
        mock_connect.assert_not_called()

        # Test connection failure
        mock_is_connected.return_value = False
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        mock_connect.assert_called_once()


async def test_coordinator_data_processing(hass: HomeAssistant, mock_config_entry):
    """Test the coordinator's data processing logic."""
    coordinator = CrealityK1DataUpdateCoordinator(hass, mock_config_entry)
    test_data = {"test_key": "test_value"}

    with patch.object(coordinator, "async_set_updated_data") as mock_set_updated_data:
        coordinator.process_raw_data(test_data)
        mock_set_updated_data.assert_called_once_with(test_data)
        assert coordinator.latest_data == test_data

async def test_coordinator_commands(hass: HomeAssistant, mock_config_entry):
    """Test the coordinator's command functions."""
    coordinator = CrealityK1DataUpdateCoordinator(hass, mock_config_entry)
    coordinator.websocket.send_message = AsyncMock()

    # Test send_gcode_command
    await coordinator.send_gcode_command("M106 P1 S255")
    coordinator.websocket.send_message.assert_called_once_with(
        {"method": "set", "params": {"gcodeCmd": "M106 P1 S255"}}
    )

    # Test send_param_command
    coordinator.websocket.send_message.reset_mock()
    await coordinator.send_param_command({"aiDetection": 1})
    coordinator.websocket.send_message.assert_called_once_with(
        {"method": "set", "params": {"aiDetection": 1}}
    )

    # Test error handling in commands
    coordinator.websocket.send_message.side_effect = Exception("Send failed")
    await coordinator.send_gcode_command("ERROR")
    await coordinator.send_param_command({"error": 1})
    # Should not raise exception but log error

async def test_coordinator_log_once(hass: HomeAssistant, mock_config_entry):
    """Test the log-once-on-failure logic."""
    coordinator = CrealityK1DataUpdateCoordinator(hass, mock_config_entry)
    
    with patch.object(coordinator.websocket, "connect", AsyncMock()), \
         patch.object(type(coordinator.websocket), "is_connected", new_callable=PropertyMock) as mock_is_connected, \
         patch("custom_components.creality_k1.coordinator._LOGGER") as mock_logger:
        
        # Initial state: connected
        mock_is_connected.return_value = True
        await coordinator._async_update_data()
        assert coordinator._was_available is True
        
        # Disconnect: Should log ERROR
        mock_is_connected.return_value = False
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        assert coordinator._was_available is False
        mock_logger.error.assert_called_once()
        
        # Still disconnected: Should NOT log ERROR again
        mock_logger.error.reset_mock()
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()
        mock_logger.error.assert_not_called()
        
        # Reconnect: Should log INFO
        mock_is_connected.return_value = True
        await coordinator._async_update_data()
        assert coordinator._was_available is True
        mock_logger.info.assert_called_once()

