# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/bingx12/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/bingx12/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

THE WORLD TODAY — a pure-stdlib Python program that draws Tuesday 24 November 2026's world news as a one-page newspaper front page and writes it to `/output/entry.png` (1024×1024 PNG, under 1 MiB, byte-identical on every run).

## Run it

```sh
python3 main.py
```

No network, no clock, no randomness: `main.py` renders everything itself from bitmap glyphs in `font_data.py` (DejaVu Sans Book and Bold at one 64px base size, scaled at runtime) and encodes the PNG with `zlib`.

## The day's stories

Every story on the page happened or was first reported on Tuesday 24 November 2026 (Reuters, AP, BBC, Al Jazeera):

- **Lead — Huang is back.** Nvidia's board unanimously reinstates Jensen Huang as president and CEO, 11 days after he resigned; the shares soar 31% in a day, adding about $1 trillion of market value, while the Nasdaq jumps 6.9% and the S&P 500 rises 5%. President Trump claims credit: "I made the deal."
- **Diplomacy.** Canada and Qatar sign a foreign-investment protection deal at the two countries' first strategic dialogue — a step towards unlocking Qatari investment pledged in January.
- **Europe.** Volodymyr Zelenskiy addresses the German parliament in Berlin, pressing allies for more air defences as Russia keeps striking Ukrainian cities and power plants.
- **The Gulf.** Iran vows to use "all available tools" to confront the US naval blockade, as oil keeps moving through the Strait of Hormuz.
- **Commodities.** DR Congo, the world's top cobalt producer, suspends all cobalt exports from 30 November to fight oversupply and weak prices.
- **Aid.** The UN World Food Programme warns that fighting is jeopardising aid for more than seven million more people.
- **Also today.** Kilauea's 57th eruption lights up Hawaii; a Belgium cost-of-living strike grounds flights; search and rescue after a Nigeria boat tragedy; Kenya and DR Congo agree to restore ties.

---

<sub>Entered on [make.fun](https://make.fun/?ref=k6eq9xtw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
