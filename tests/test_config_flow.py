"""Test the Creality K1 config flow."""
from unittest.mock import patch, AsyncMock

import pytest
from homeassistant import config_entries, setup
from homeassistant.const import CONF_IP_ADDRESS
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.creality_k1.config_flow import CannotConnect
from custom_components.creality_k1.const import DOMAIN


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert not result["errors"]

    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        return_value=None,
    ) as mock_validate_connection:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.4",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.CREATE_ENTRY
    assert result2["title"] == "Creality K1"
    assert result2["data"] == {
        CONF_IP_ADDRESS: "1.2.3.4",
    }
    assert len(mock_validate_connection.mock_calls) == 1


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        side_effect=CannotConnect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.4",
            },
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_duplicate_error(hass: HomeAssistant) -> None:
    """Test we handle duplicate entries."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_IP_ADDRESS: "1.2.3.4"},
        unique_id="1.2.3.4",
    )
    entry.add_to_hass(hass)
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        return_value=None,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.4",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "already_configured"


async def test_reconfigure(hass: HomeAssistant, mock_config_entry) -> None:
    """Test reconfiguration flow."""
    mock_config_entry.add_to_hass(hass)
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": mock_config_entry.entry_id,
        },
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        return_value=None,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.5",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.ABORT
    assert result2["reason"] == "reconfigure_successful"
    assert mock_config_entry.data[CONF_IP_ADDRESS] == "1.2.3.5"

async def test_reconfigure_failure(hass: HomeAssistant, mock_config_entry) -> None:
    """Test reconfiguration flow failure."""
    mock_config_entry.add_to_hass(hass)
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": mock_config_entry.entry_id,
        },
    )

    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        side_effect=CannotConnect,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.5",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_unknown_error(hass: HomeAssistant) -> None:
    """Test we handle unknown errors."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        side_effect=Exception("Unknown"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.4",
            },
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}


async def test_reconfigure_unknown_error(hass: HomeAssistant, mock_config_entry) -> None:
    """Test reconfiguration flow unknown error."""
    mock_config_entry.add_to_hass(hass)
    
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={
            "source": config_entries.SOURCE_RECONFIGURE,
            "entry_id": mock_config_entry.entry_id,
        },
    )

    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        side_effect=Exception("Unknown"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_IP_ADDRESS: "1.2.3.5",
            },
        )

    assert result2["type"] is FlowResultType.FORM
    assert result2["errors"] == {"base": "unknown"}



async def test_import(hass: HomeAssistant) -> None:
    """Test import step."""
    with patch(
        "custom_components.creality_k1.config_flow.validate_connection",
        return_value=None,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data={CONF_IP_ADDRESS: "1.2.3.4"},
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_validate_connection(hass: HomeAssistant) -> None:
    """Test validate_connection helper."""
    from custom_components.creality_k1.config_flow import validate_connection, CannotConnect
    
    with patch("custom_components.creality_k1.config_flow.CrealityK1Client") as mock_client:
        instance = mock_client.return_value
        instance.connect = AsyncMock()
        instance.disconnect = AsyncMock()
        
        # Success
        instance.is_connected = True
        await validate_connection("1.2.3.4")
        
        # Failure: not connected
        instance.is_connected = False
        with pytest.raises(CannotConnect):
            await validate_connection("1.2.3.4")
            
        # Failure: exception
        instance.connect.side_effect = Exception("error")
        with pytest.raises(CannotConnect):
            await validate_connection("1.2.3.4")




