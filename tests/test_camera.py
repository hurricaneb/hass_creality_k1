"""Tests for the Creality K1 camera platform."""
from unittest.mock import patch

from homeassistant.core import HomeAssistant
from syrupy.assertion import SnapshotAssertion

from . import setup_integration


async def test_camera(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    mock_config_entry,
) -> None:
    """Test the camera."""
    with patch("custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_config_entry_first_refresh") as mock_refresh:
        async def mock_first_refresh():
            coordinator = mock_config_entry.runtime_data
            coordinator.data = {"video": 1}
        mock_refresh.side_effect = mock_first_refresh

        await setup_integration(hass, mock_config_entry)

        # Get all camera entities
        cameras = hass.states.async_all("camera")
        assert len(cameras) > 0

        # Assert that the state of each camera matches the snapshot, ignoring dynamic tokens
        for camera in cameras:
            camera_dict = {
                "entity_id": camera.entity_id,
                "state": camera.state,
                "attributes": dict(camera.attributes),
            }
            # Mask dynamic attributes
            for key in ["access_token", "entity_picture"]:
                camera_dict["attributes"].pop(key, None)
            
            assert camera_dict == snapshot(name=f"{camera.entity_id}")




async def test_camera_unavailable_when_video_zero(
    hass: HomeAssistant,
    mock_config_entry,
) -> None:
    """Test that camera is unavailable if video is 0."""
    with patch("custom_components.creality_k1.coordinator.CrealityK1DataUpdateCoordinator.async_config_entry_first_refresh") as mock_refresh:
        async def mock_first_refresh():
            coordinator = mock_config_entry.runtime_data
            coordinator.data = {"video": 0}
        mock_refresh.side_effect = mock_first_refresh

        await setup_integration(hass, mock_config_entry)

        cameras = hass.states.async_all("camera")
        assert len(cameras) == 1
        assert cameras[0].state == "unavailable"
