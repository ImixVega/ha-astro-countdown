"""Astro Countdown: local once-per-minute astronomical timers."""

from __future__ import annotations

from datetime import datetime

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ELEVATION, CONF_LATITUDE, CONF_LONGITUDE, CONF_TIME_ZONE, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_change
from homeassistant.util import dt as dt_util

from .astronomy import AstronomyCalculator
from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]


class AstroCountdownRuntime:
    """One computation shared by four sensors and one minute tick."""

    def __init__(self, entry: ConfigEntry):
        self.calculator = AstronomyCalculator(
            latitude=entry.data[CONF_LATITUDE],
            longitude=entry.data[CONF_LONGITUDE],
            elevation=entry.data[CONF_ELEVATION],
            zone=entry.data[CONF_TIME_ZONE],
        )
        self.states = self.calculator.calculate(dt_util.utcnow())
        self.entities = []

    @callback
    def refresh(self, _when: datetime | None = None) -> None:
        """Recalculate after the HA minute boundary and notify listeners."""
        self.states = self.calculator.calculate(dt_util.utcnow())
        for entity in self.entities:
            entity.async_write_ha_state()


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Initialize config entry and schedule one refresh per minute."""
    runtime = AstroCountdownRuntime(entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(
        async_track_time_change(hass, runtime.refresh, second=0)
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Stop timer and unload entities."""
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        entry.async_unload_callbacks()
        hass.data[DOMAIN].pop(entry.entry_id, None)
        return True
    return False
