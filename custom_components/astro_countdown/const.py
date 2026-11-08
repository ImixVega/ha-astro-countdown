"""Constants for the Astro Countdown integration."""

DOMAIN = "astro_countdown"

COUNTERS = {
    "sunset": ("Do zachodu Słońca", "mdi:weather-sunset-down", "Zachód Słońca"),
    "night_start": (
        "Do początku nocy astronomicznej",
        "mdi:weather-night",
        "Początek nocy astronomicznej",
    ),
    "night_end": (
        "Do końca nocy astronomicznej",
        "mdi:weather-sunset-up",
        "Koniec nocy astronomicznej",
    ),
    "sunrise": ("Do wschodu Słońca", "mdi:weather-sunny", "Wschód Słońca"),
}
