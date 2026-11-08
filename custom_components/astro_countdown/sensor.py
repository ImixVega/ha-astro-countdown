"""Four user-friendly textual HH:MM:SS countdown sensors."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import COUNTERS, DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    runtime = hass.data[DOMAIN][entry.entry_id]
    sensors = [AstroCountdownSensor(entry, runtime, key) for key in COUNTERS]
    async_add_entities(sensors)
    runtime.entities.extend(sensors)


class AstroCountdownSensor(SensorEntity):
    """Countdown string; no numeric unit/statistics are advertised."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, runtime, key: str) -> None:
        self.runtime = runtime
        self.key = key
        title, icon, _label = COUNTERS[key]
        self._attr_name = title
        self._attr_icon = icon
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_suggested_object_id = f"astro_countdown_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Astro Countdown – {entry.title}",
            manufacturer="Lokalne obliczenia",
            model="Astronomical Countdown",
        )

    @property
    def native_value(self) -> str:
        return self.runtime.states[self.key].remaining

    @property
    def extra_state_attributes(self) -> dict:
        snap = self.runtime.states[self.key]
        return {
            "aktywne_odliczanie": snap.active,
            "pozostalo_minut": snap.minutes,
            "zdarzenie": COUNTERS[self.key][2],
            "godzina_zdarzenia": snap.target.strftime("%H:%M:%S") if snap.target else None,
            "data_zdarzenia": snap.target.isoformat() if snap.target else None,
        }
