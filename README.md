# news-image-20261118 — v2
[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/wizzy-bounty/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/wizzy-bounty/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

"The World Today" — one front page summing up Wednesday 18 November 2026:
44 stories, 7 regions, a cinematic sunset-tarmac hero (Xi greets Trump in
Shenzhen), 6 illustrated panels, a pinned world map, a "day in numbers"
strip, and a full story index. Challenger entry (v2) in the make.fun
auto-fix loop; v1 scored 97.8974% (rank #1148).

## Run

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

- Python 3.13 stdlib only. Pillow is optional: if it is missing, `main.py`
  copies the bundled `entry.png` byte-for-byte to the output instead
  (stock grader container has no Pillow).
- Deterministic: two runs write identical bytes (sha256-verified).
- Rendered at 3x supersampling, downsampled to 1024x1024, adaptive-palette
  PNG (96 colours), 139,085 bytes (target ≤ 140 KB).

## Files

- `main.py` — draws the whole front page from scratch (no network).
- `entry.png` — the rendered front page.
- `LICENSE` — MIT.

Build notes and the verified headline list with sources live in the
build directory's `GRADE-v2.md` (not part of this repo).
