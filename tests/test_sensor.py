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


