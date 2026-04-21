"""Tests for the Creality K1 climate platform."""
from unittest.mock import patch, MagicMock, AsyncMock

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_climates(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the climates."""
    with patch("custom_components.creality_k1.CrealityK1DataUpdateCoordinator.async_refresh", return_value=True):
        await setup_integration(hass, mock_config_entry)

        # Get all climate entities
        climates = hass.states.async_all("climate")
        assert len(climates) > 0

        # Assert that the state of each climate matches the snapshot
        for climate in climates:
            assert climate == snapshot(name=f"{climate.entity_id}")


async def test_climate_services(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the climate services."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_refresh",
        return_value=True,
    ):
        await setup_integration(
            hass,
            mock_config_entry,
            data={"targetNozzleTemp": 0, "maxNozzleTemp": 300},
        )
        coordinator = mock_config_entry.runtime_data
        coordinator.websocket.send_message = AsyncMock()

        # Set temperature
        await hass.services.async_call(
            "climate",
            "set_temperature",
            {"entity_id": "climate.mock_title_nozzle_heater", "temperature": 220},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"gcodeCmd": "M104 T0 S220"}}
        )

        # Turn off
        await hass.services.async_call(
            "climate",
            "set_hvac_mode",
            {"entity_id": "climate.mock_title_nozzle_heater", "hvac_mode": "off"},
            blocking=True,
        )
        coordinator.websocket.send_message.assert_called_with(
            {"method": "set", "params": {"gcodeCmd": "M104 T0 S0"}}
        )


from unittest.mock import AsyncMock

from homeassistant.helpers.update_coordinator import UpdateFailed


async def test_climates_unavailable(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test the climates when the coordinator has no data."""
    with patch(
        "custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator._async_update_data",
        side_effect=UpdateFailed("Test error"),
    ):
        await setup_integration(hass, mock_config_entry)

        # Get all climate entities
        climates = hass.states.async_all("climate")
        assert len(climates) > 0

        # Assert that all climates are unavailable
        for climate in climates:
            assert climate.state == "unavailable"


async def test_climate_extra_coverage(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test extra coverage for climate platform."""
    await setup_integration(hass, mock_config_entry, data={"targetBedTemp0": 0})
    coordinator = mock_config_entry.runtime_data
    coordinator.websocket.send_message = AsyncMock()
    from custom_components.creality_k1.climate import K1Climate
    climate = K1Climate(coordinator, mock_config_entry, "bed0", "test", "bedTemp0", "targetBedTemp0", "maxBedTemp")
    climate.hass = hass
    climate.async_write_ha_state = MagicMock()


    # Test set_hvac_mode HEAT (covers line 115-128)
    await climate.async_set_hvac_mode("heat")
    # Check if correct default temp was set (60.0 for bed)
    coordinator.websocket.send_message.assert_called_with(
        {"method": "set", "params": {"gcodeCmd": "M140 I0 S60"}}
    )

    # Test set_hvac_mode HEAT when already heating (covers line 124-127)
    coordinator.data["targetBedTemp0"] = 50.0
    await climate.async_set_hvac_mode("heat")
    
    # Test set_hvac_mode OFF (covers line 111-114)
    await climate.async_set_hvac_mode("off")
    coordinator.websocket.send_message.assert_called_with(
        {"method": "set", "params": {"gcodeCmd": "M140 I0 S0"}}
    )

    # Test set_temperature with None (covers line 135)
    await climate.async_set_temperature(**{"temperature": None})
    
    # Test Unsupported HVAC mode (covers line 129)
    await climate.async_set_hvac_mode("unsupported")


