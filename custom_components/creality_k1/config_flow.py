"""Config flow to configure Creality K1 integration."""
import logging
import json
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import (
    CONF_IP_ADDRESS
)
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from creality_k1_api import CrealityK1Client
from .const import DOMAIN, DEVICE_MANUFACTURER, DEVICE_MODEL

_LOGGER = logging.getLogger(__name__)

class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

async def validate_connection(ip_address: str) -> None:
    """Validate the connection to the Creality K1."""
    ws_url = f"ws://{ip_address}:9999"
    
    try:
        client = CrealityK1Client(url=ws_url, new_data_callback=lambda x: None)
        await client.connect()
        
        if client.is_connected:
            await client.disconnect()
            return
        else:
            raise CannotConnect
    except Exception as e:
        _LOGGER.error(f"Could not connect to {ws_url}: {e}")
        raise CannotConnect from e

class CrealityK1ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Creality K1."""

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            ip_address = user_input.get(CONF_IP_ADDRESS)
            try:
                await validate_connection(ip_address)
                return self.async_create_entry(title=f'{DEVICE_MANUFACTURER} {DEVICE_MODEL}', data=user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # General error handling
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_IP_ADDRESS): str}),
            errors=errors,
        )

    async def async_step_reconfigure(self, user_input: dict | None = None) -> FlowResult:
        """Handle reconfiguration of the integration."""
        errors = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])

        if user_input is not None:
            ip_address = user_input.get(CONF_IP_ADDRESS)
            try:
                await validate_connection(ip_address)
                return self.async_update_reload_and_abort(
                    entry,
                    data={**entry.data, **user_input},
                    reason="reconfigure_successful",
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {vol.Required(CONF_IP_ADDRESS, default=entry.data.get(CONF_IP_ADDRESS)): str}
            ),
            errors=errors,
        )

    async def async_step_import(self, user_input: dict) -> FlowResult:
        """Handle import from config."""
        return await self.async_step_user(user_input)