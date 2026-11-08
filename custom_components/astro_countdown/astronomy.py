"""Calculate local solar events and phase-aware countdowns.

Only sunrise/sunset or an astronomical -18 degree crossing can activate
its matching countdown. In particular, tomorrow's sunrise is NOT counted
during the day.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache
from zoneinfo import ZoneInfo

from astral import Observer
from astral.sun import dawn, dusk, sunrise, sunset


@dataclass(frozen=True)
class SunEvents:
    sunrise: datetime | None
    sunset: datetime | None
    astro_dawn: datetime | None
    astro_dusk: datetime | None


@dataclass(frozen=True)
class Countdown:
    remaining: str
    minutes: int
    target: datetime | None

    @property
    def active(self) -> bool:
        return self.target is not None


def _safe_event(fn, observer: Observer, day: date, tz: ZoneInfo, **kwargs):
    """Return None when the chosen event does not occur at this latitude/date."""
    try:
        return fn(observer, date=day, tzinfo=tz, **kwargs)
    except ValueError:
        return None


def _countdown(now: datetime, target: datetime | None) -> Countdown:
    if target is None or target <= now:
        return Countdown("00:00:00", 0, None)

    # Round DOWN to whole minutes, so a planned exposure never exceeds the
    # real time remaining before the astronomical boundary.
    minutes = max(0, int((target - now).total_seconds() // 60))
    hours, rest = divmod(minutes, 60)
    return Countdown(f"{hours:02d}:{rest:02d}:00", minutes, target)


def phase_countdowns(
    now: datetime, previous: SunEvents, today: SunEvents, following: SunEvents
) -> dict[str, Countdown]:
    """Return the four countdowns with zero outside their active phases.

    - Sunset / astronomical dusk: only after today's sunrise.
    - Sunrise: only after sunset, across midnight until sunrise.
    - Astronomical dawn: only after astronomical dusk, across midnight.
    """
    sunset_target = None
    if today.sunrise and today.sunset and today.sunrise <= now < today.sunset:
        sunset_target = today.sunset

    night_start_target = None
    if today.sunrise and today.astro_dusk and today.sunrise <= now < today.astro_dusk:
        night_start_target = today.astro_dusk

    sunrise_target = None
    if previous.sunset and today.sunrise and previous.sunset <= now < today.sunrise:
        sunrise_target = today.sunrise
    elif today.sunset and following.sunrise and today.sunset <= now < following.sunrise:
        sunrise_target = following.sunrise

    night_end_target = None
    if (
        previous.astro_dusk
        and today.astro_dawn
        and previous.astro_dusk <= now < today.astro_dawn
    ):
        night_end_target = today.astro_dawn
    elif (
        today.astro_dusk
        and following.astro_dawn
        and today.astro_dusk <= now < following.astro_dawn
    ):
        night_end_target = following.astro_dawn

    return {
        "sunset": _countdown(now, sunset_target),
        "night_start": _countdown(now, night_start_target),
        "night_end": _countdown(now, night_end_target),
        "sunrise": _countdown(now, sunrise_target),
    }


class AstronomyCalculator:
    """Cached astronomical event calculator for one geographic location."""

    def __init__(self, latitude: float, longitude: float, elevation: float, zone: str):
        self.observer = Observer(
            latitude=float(latitude), longitude=float(longitude), elevation=float(elevation)
        )
        self.tz = ZoneInfo(zone)

    @lru_cache(maxsize=8)
    def events_for(self, day: date) -> SunEvents:
        """Cache event calculations for the current three-day window."""
        observer = self.observer
        tz = self.tz
        return SunEvents(
            sunrise=_safe_event(sunrise, observer, day, tz),
            sunset=_safe_event(sunset, observer, day, tz),
            astro_dawn=_safe_event(dawn, observer, day, tz, depression=18.0),
            astro_dusk=_safe_event(dusk, observer, day, tz, depression=18.0),
        )

    def calculate(self, now: datetime) -> dict[str, Countdown]:
        """Compute counters in the configured time zone."""
        now = now.astimezone(self.tz)
        day = now.date()
        return phase_countdowns(
            now,
            self.events_for(day - timedelta(days=1)),
            self.events_for(day),
            self.events_for(day + timedelta(days=1)),
        )
