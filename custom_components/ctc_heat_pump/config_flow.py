"""Config flow for the CTC Heat Pump integration."""

from __future__ import annotations

import socket
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import selector

from .const import (
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    CONF_SLAVE_ID,
    DEFAULT_MODEL,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    MIN_SCAN_INTERVAL,
    MODEL_OPTIONS,
)


def _model_selector() -> selector.SelectSelector:
    """Create a model dropdown with user-friendly labels."""
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
                {"value": model_key, "label": model_name}
                for model_key, model_name in MODEL_OPTIONS.items()
            ],
            mode=selector.SelectSelectorMode.DROPDOWN,
        )
    )

async def _validate_input(hass: HomeAssistant, data: dict[str, Any]) -> str:
    """Validate the user input allows us to connect."""
    await hass.async_add_executor_job(
        _test_tcp_connection,
        data[CONF_HOST],
        data[CONF_PORT],
    )
    model_name = MODEL_OPTIONS[data[CONF_MODEL]]
    return f"{model_name} ({data[CONF_HOST]})"


def _test_tcp_connection(host: str, port: int) -> None:
    """Test whether the Modbus TCP port accepts a socket connection."""
    with socket.create_connection((host, port), timeout=3):
        return


class CtcConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for CTC Heat Pump."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow for an existing heat pump."""
        return CtcOptionsFlow()

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Handle the initial setup step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}:{user_input[CONF_SLAVE_ID]}"
            )
            self._abort_if_unique_id_configured()

            try:
                title = await _validate_input(self.hass, user_input)
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default="192.168.0.222"): str,
                    vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                    vol.Optional(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(int, vol.Range(min=MIN_SCAN_INTERVAL)),
                    # Setup form
                    vol.Required(
                        CONF_MODEL,
                        default=DEFAULT_MODEL,
                    ): _model_selector(),
                    # Options form
                    vol.Required(
                        CONF_MODEL,
                        default=selected_model,
                    ): _model_selector(),
                }
            ),
            errors=errors,
        )


class CtcOptionsFlow(OptionsFlow):
    """Allow the selected CTC product family to be changed later."""

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Manage the selected model family."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        selected_model = self.config_entry.options.get(
            CONF_MODEL,
            self.config_entry.data.get(CONF_MODEL, DEFAULT_MODEL),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MODEL,
                        default=selected_model,
                    ): _model_selector(),
                }
            ),
        )
