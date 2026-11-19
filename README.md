# News Image — 18 November 2026

[![make.fun bounty](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118)
[![make.fun rank](https://make.fun/badge/news-image-20261118/Dhikas182/news-image-18-nov/rank.svg)](https://make.fun/bounty/news-image-20261118)
[![make.fun reward](https://make.fun/badge/news-image-20261118/Dhikas182/news-image-18-nov/reward.svg)](https://make.fun/bounty/news-image-20261118)

A newspaper front page, "THE WORLD TODAY — WEDNESDAY 18 NOVEMBER 2026",
drawn by a single deterministic Python program. It sums up the world news
of 18 November 2026 in one 1024x1024 PNG.

The program uses only the Python 3.13 standard library (`math`, `os`,
`struct`, `sys`, `zlib`): no network, no clock, no randomness. It draws
every letter from a hand-written 5x7 bitmap font and every scene from
plain rectangles, lines, circles and polygons, then writes the PNG bytes
by hand. Running it three times gives three byte-identical files.
The output is about 23 KB, well under the 1 MiB limit.

## The six stories

- **Shenzhen — Diplomacy (lead):** Xi greets Trump in Shenzhen as APEC
  opens; three-way talks are set for Thursday, after Xi and Putin met
  first in the city.
- **The Gulf:** Iran hits Kuwait and Bahrain, after the US struck
  Qeshm first.
- **War in Ukraine:** the Kerch Bridge is hit for a second day; a span
  falls, and Kyiv hit back.
- **Washington — Politics:** Peltola wins the Alaska Senate race,
  56-44, the first Alaska Native in the seat; AP called it Tuesday night.
- **Space:** Voyager 1 is now one light-day away — 16.1 billion miles
  out, its signals taking a day to reach Earth, the farthest object ever.
- **Health:** America loses its measles-free status, with 5,412 cases
  in 2026, while Ebola in Congo tops 11,000; the status had held
  since 2000.

A ticker at the foot of the page adds four more items from the day:
Cyclone Akvan bearing down on India's Andhra coast, a Russian military
plane crashing in Siberia with 19 dead, the EU proposing a 45bn euro
loan for Ukraine in 2027, and Category 5 Cyclone Xavier hitting the
Cook Islands.

## Run it

```sh
python3 main.py [output-path]
```

With no argument it writes to `$MAKEFUN_OUTPUT_DIR/entry.png`,
or to `/output/entry.png` when that variable is not set.

## Licence

0BSD — see [LICENSE](LICENSE).
