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
            coordinator = mock_config_entry.runtime_data
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

async def test_binary_sensor_no_value_fn(hass: HomeAssistant) -> None:
    """Test binary sensor with no value_fn."""
    from custom_components.creality_k1.binary_sensor import K1BinarySensor, K1BinarySensorEntityDescription
    from unittest.mock import MagicMock
    mock_coordinator = MagicMock()
    mock_entry = MagicMock()
    desc = K1BinarySensorEntityDescription(key="test", value_fn=None)
    sensor = K1BinarySensor(mock_coordinator, mock_entry, desc)
    assert sensor.is_on is None
