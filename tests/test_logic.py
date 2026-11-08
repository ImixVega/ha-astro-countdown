"""No HA needed: test the daylight/night phase transitions with synthetic events."""

import importlib.util
import sys
import types
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Astral is bundled with Home Assistant, but is not installed in the file-build
# environment. Stub imports so pure phase-calculation tests remain executable.
if "astral" not in sys.modules:
    astral = types.ModuleType("astral")
    astral.Observer = object
    astral_sun = types.ModuleType("astral.sun")
    for name in ("dawn", "dusk", "sunrise", "sunset"):
        setattr(astral_sun, name, lambda *args, **kwargs: None)
    sys.modules["astral"] = astral
    sys.modules["astral.sun"] = astral_sun

PATH = Path(__file__).parents[1] / "custom_components" / "astro_countdown" / "astronomy.py"
spec = importlib.util.spec_from_file_location("test_astronomy", PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["test_astronomy"] = mod
spec.loader.exec_module(mod)

TZ = ZoneInfo("Europe/Warsaw")


def day_events(day):
    def at(hour, minute=0):
        return datetime(day.year, day.month, day.day, hour, minute, tzinfo=TZ)

    return mod.SunEvents(at(7), at(16), at(5, 20), at(18, 10))


class TimerTests(unittest.TestCase):
    def setUp(self):
        self.current = datetime(2026, 11, 8, tzinfo=TZ)
        self.prev = day_events(self.current.date() - timedelta(days=1))
        self.today = day_events(self.current.date())
        self.next = day_events(self.current.date() + timedelta(days=1))

    def timers(self, hour, minute, second=0):
        now = self.current.replace(hour=hour, minute=minute, second=second)
        return mod.phase_countdowns(now, self.prev, self.today, self.next)

    def test_day_no_sunrise_countdown(self):
        ts = self.timers(12, 0)
        self.assertEqual(ts["sunrise"].remaining, "00:00:00")
        self.assertEqual(ts["night_end"].remaining, "00:00:00")
        self.assertEqual(ts["sunset"].remaining, "04:00:00")
        self.assertEqual(ts["night_start"].remaining, "06:10:00")

    def test_evening_after_sunset_before_dark(self):
        ts = self.timers(17, 0)
        self.assertEqual(ts["sunset"].remaining, "00:00:00")
        self.assertEqual(ts["night_start"].remaining, "01:10:00")
        self.assertEqual(ts["night_end"].remaining, "00:00:00")
        self.assertEqual(ts["sunrise"].remaining, "14:00:00")

    def test_deep_night(self):
        ts = self.timers(22, 0)
        self.assertEqual(ts["sunset"].remaining, "00:00:00")
        self.assertEqual(ts["night_start"].remaining, "00:00:00")
        self.assertEqual(ts["night_end"].remaining, "07:20:00")
        self.assertEqual(ts["sunrise"].remaining, "09:00:00")

    def test_after_midnight(self):
        ts = self.timers(2, 0)
        self.assertEqual(ts["sunset"].remaining, "00:00:00")
        self.assertEqual(ts["night_start"].remaining, "00:00:00")
        self.assertEqual(ts["night_end"].remaining, "03:20:00")
        self.assertEqual(ts["sunrise"].remaining, "05:00:00")

    def test_after_astro_dawn_before_sunrise(self):
        ts = self.timers(6, 0)
        self.assertEqual(ts["night_end"].remaining, "00:00:00")
        self.assertEqual(ts["sunrise"].remaining, "01:00:00")
        self.assertEqual(ts["sunset"].remaining, "00:00:00")

    def test_after_sunrise(self):
        ts = self.timers(7, 0)
        self.assertEqual(ts["sunrise"].remaining, "00:00:00")
        self.assertEqual(ts["sunset"].remaining, "09:00:00")

    def test_seconds_are_floored(self):
        ts = self.timers(12, 25, 42)
        self.assertEqual(ts["sunset"].remaining, "03:34:00")

    def test_boundary_exact_sunset(self):
        ts = self.timers(16, 0)
        self.assertEqual(ts["sunset"].remaining, "00:00:00")
        self.assertTrue(ts["sunrise"].active)

    def test_boundary_exact_astro_dusk(self):
        ts = self.timers(18, 10)
        self.assertEqual(ts["night_start"].remaining, "00:00:00")
        self.assertTrue(ts["night_end"].active)

    def test_boundary_exact_astro_dawn(self):
        ts = self.timers(5, 20)
        self.assertEqual(ts["night_end"].remaining, "00:00:00")
        self.assertTrue(ts["sunrise"].active)


if __name__ == "__main__":
    unittest.main()
