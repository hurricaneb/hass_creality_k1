"""Tests for the Creality K1 sensor platform."""
from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_sensors(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the sensors."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        entry = await setup_integration(hass, mock_config_entry)

        # Get all sensor entities
        sensors = hass.states.async_all("sensor")
        assert len(sensors) > 0  # Ensure some sensors were created

        # Assert that the state of each sensor matches the snapshot
        for sensor in sensors:
            assert sensor == snapshot(name=f"{sensor.entity_id}")


from homeassistant.helpers.update_coordinator import UpdateFailed


async def test_sensors_unavailable(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the sensors when the coordinator has no data."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator._async_update_data",
        side_effect=UpdateFailed("Test error"),
    ):
        await setup_integration(hass, mock_config_entry)

        # Get all sensor entities
        sensors = hass.states.async_all("sensor")
        assert len(sensors) > 0

        # Assert that all sensors are unavailable
        for sensor in sensors:
            assert sensor.state == "unavailable"


async def test_sensor_helper_error_cases(
    hass: HomeAssistant,
) -> None:
    """Test the sensor helper functions with invalid data."""
    from custom_components.creality_k1.sensor import get_float, get_int, get_state
    
    # Test get_float with invalid data
    assert get_float({"key": "invalid"}, "key") is None
    assert get_float({"key": None}, "key") is None
    
    # Test get_int with invalid data
    assert get_int({"key": "invalid"}, "key") is None
    assert get_int({"key": None}, "key") is None
    
    # Test get_state with invalid data
    assert get_state({"key": "invalid"}, "key") is None
    assert get_state({"key": None}, "key") is None
    
    # Test sensor with no value_fn (covers line 185)
    from custom_components.creality_k1.sensor import K1Sensor, K1SensorEntityDescription
    from unittest.mock import MagicMock
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    desc = K1SensorEntityDescription(key="test", value_fn=None)
    sensor = K1Sensor(mock_coordinator, mock_entry, desc)
    assert sensor.native_value is None

    # Test get_hw_sw_versions with invalid data (covers helpers.py)
    from custom_components.creality_k1.helpers import get_hw_sw_versions, to_float_or_none
    assert get_hw_sw_versions({"modelVersion": "invalid"}) == (None, None)
    assert get_hw_sw_versions(None) == (None, None)
    assert to_float_or_none({"key": "invalid"}, "key") is None
    assert to_float_or_none("invalid", "key") is None


async def test_timelapses_sensor(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the timelapses sensor and automatic update on completion."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1Client", autospec=True
    ) as mock_client:
        client = mock_client.return_value
        client.is_connected = True
        client.disconnect.return_value = True

        # Mock the timelapse list
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

        # The sensor should be created and show 1 timelapse initially
        sensor_state = hass.states.get("sensor.mock_title_timelapses")
        assert sensor_state is not None
        assert sensor_state.state == "1"
        assert sensor_state.attributes["videos"] == mock_timelapses

        # Reset mock
        client.get_timelapses.reset_mock()

        # Test state transition to Completed (2)
        coordinator = mock_config_entry.runtime_data
        
        # Initial state is 1 (Printing)
        coordinator.latest_data["state"] = 1
        
        # Update mock response for the completed print
        updated_timelapses = mock_timelapses + [
            {
                "gcode": "cube.gcode",
                "url": "http://1.2.3.4/downloads/video/1764699999.mp4",
                "timestamp": 1764699999,
                "start_time": "2025-11-20T12:45:00+00:00",
            }
        ]
        client.get_timelapses.return_value = updated_timelapses

        # Simulate incoming websocket message with state = 2 (Complete)
        coordinator.process_raw_data({"state": 2})
        await hass.async_block_till_done()

        # Check that get_timelapses was called again
        client.get_timelapses.assert_called_once()
        
        # Verify the sensor updated
        sensor_state = hass.states.get("sensor.mock_title_timelapses")
        assert sensor_state.state == "2"
        assert len(sensor_state.attributes["videos"]) == 2


async def test_timelapses_sensor_error_handling(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test error handling in coordinator for timelapses."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1Client", autospec=True
    ) as mock_client:
        client = mock_client.return_value
        client.is_connected = True
        client.disconnect.return_value = True
        client.get_timelapses.return_value = []

        mock_config_entry.add_to_hass(hass)
        await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

        coordinator = mock_config_entry.runtime_data

        # 1. Test get_timelapses raising an exception in _async_fetch_timelapses_and_update
        client.get_timelapses.side_effect = Exception("Websocket failure")
        coordinator.latest_data["state"] = 1
        coordinator.process_raw_data({"state": 2})
        await hass.async_block_till_done()
        assert client.get_timelapses.called

        # 2. Test ValueError/TypeError in state transition
        client.get_timelapses.reset_mock()
        client.get_timelapses.side_effect = None
        client.get_timelapses.return_value = []
        coordinator.latest_data["state"] = "invalid_state"
        coordinator.process_raw_data({"state": 2})
        await hass.async_block_till_done()
        assert not client.get_timelapses.called
