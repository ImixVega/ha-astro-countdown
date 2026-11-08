# Astro Countdown for Home Assistant

[![HACS](https://img.shields.io/badge/HACS-custom-41BDF5.svg)](https://hacs.xyz/)

Własna integracja Home Assistant pokazująca **czas do zdarzeń astronomicznych w formacie `HH:MM:SS`**, z aktualizacją co minutę, bez API i bez internetu. Obliczenia lokalne na podstawie Astral i współrzędnych ustawionych w HA.

## Cztery sensory

| Sensor | Kiedy odlicza |
| --- | --- |
| Do zachodu Słońca | Od wschodu do zachodu Słońca |
| Do początku nocy astronomicznej | Od wschodu do wieczornego przekroczenia wysokości Słońca **-18°** |
| Do końca nocy astronomicznej | Od początku nocy astronomicznej do porannego przekroczenia **-18°** |
| Do wschodu Słońca | Od zachodu do następnego wschodu |

Poza okresem działania licznik zwraca `00:00:00`. Sekundy są zawsze `00`; wynik jest **zaokrąglany w dół do pełnej minuty**, co przydaje się przy ustawianiu sesji ASIAIR. Każdy sensor udostępnia też atrybuty z datą/czasem zdarzenia i liczbą pozostałych minut.

## Instalacja przez HACS

1. HACS → trzy kropki → **Niestandardowe repozytoria**.
2. Dodaj `https://github.com/ImixVega/ha-astro-countdown` jako typ **Integracja**.
3. Zainstaluj, w razie potrzeby uruchom ponownie HA.
4. **Ustawienia → Urządzenia i usługi → Dodaj integrację → Astro Countdown**.
5. Podaj współrzędne, wysokość n.p.m. i strefę czasową.

Możliwa jest także instalacja ręczna przez `custom_components/astro_countdown/`.

## Karta dashboardu

```yaml
type: entities
title: 🌌 Odliczanie astronomiczne
entities:
  - entity: sensor.astro_countdown_sunset
    name: Zachód Słońca za
  - entity: sensor.astro_countdown_night_start
    name: Początek nocy astronomicznej za
  - entity: sensor.astro_countdown_night_end
    name: Koniec nocy astronomicznej za
  - entity: sensor.astro_countdown_sunrise
    name: Wschód Słońca za
```

Rzeczywiste identyfikatory encji mogą się różnić; sprawdź je w HA. Opcjonalnie wyklucz te sensory z Recorder, jeśli nie potrzebujesz historii liczników.

## Uwagi

- Astronomiczny zmierzch/świt to wysokość Słońca **-18°** (nie -6° ani -12°).
- Uwzględniana jest strefa czasowa i zmiany czasu.
- Dla lokalizacji, w których wybrane zjawisko nie występuje danego dnia (np. okolice polarne), brak aktywnego odliczania.
- Pierwsza wersja: testy logiki dla przejścia przez północ i granice zdarzeń; brak pełnych testów end-to-end w HA.

## License

MIT — see [LICENSE](LICENSE).
