"""UI configuration for Astro Countdown."""

from __future__ import annotations

from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import (
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_TIME_ZONE,
)

from .const import DOMAIN


class AstroCountdownConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Configure independently for any observing site."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                ZoneInfo(user_input[CONF_TIME_ZONE])
            except (ZoneInfoNotFoundError, ValueError, KeyError):
                errors[CONF_TIME_ZONE] = "invalid_timezone"
            if not errors:
                lat = user_input[CONF_LATITUDE]
                lon = user_input[CONF_LONGITUDE]
                await self.async_set_unique_id(f"{lat:.5f}_{lon:.5f}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_NAME,
                    default=(user_input or {}).get(CONF_NAME, "Obserwatorium"),
                ): str,
                vol.Required(
                    CONF_LATITUDE,
                    default=(user_input or {}).get(
                        CONF_LATITUDE, self.hass.config.latitude
                    ),
                ): vol.All(vol.Coerce(float), vol.Range(min=-90, max=90)),
                vol.Required(
                    CONF_LONGITUDE,
                    default=(user_input or {}).get(
                        CONF_LONGITUDE, self.hass.config.longitude
                    ),
                ): vol.All(vol.Coerce(float), vol.Range(min=-180, max=180)),
                vol.Required(
                    CONF_ELEVATION,
                    default=(user_input or {}).get(
                        CONF_ELEVATION, self.hass.config.elevation
                    ),
                ): vol.Coerce(float),
                vol.Required(
                    CONF_TIME_ZONE,
                    default=(user_input or {}).get(
                        CONF_TIME_ZONE, self.hass.config.time_zone
                    ),
                ): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
