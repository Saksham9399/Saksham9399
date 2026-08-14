# How this profile card is built

`README.md` is only a `<picture>` element. Everything visible is one of two SVGs,
picked by the viewer's colour scheme.

## The two halves of a card

**The ASCII portrait** (left column) is generated once, offline, from my GitHub
avatar. It is baked into both SVGs as literal `<tspan>` rows.

**The spec sheet** (right column) is mostly static text, plus nine fields that
GitHub Actions rewrites every day: uptime, repos, contributed repos, stars,
commits, followers, and the lines-of-code triple.

## Regenerating

Both SVGs are build artifacts — edit `tools/build_svg.py`, never the SVGs:

```sh
python3 -m venv .venv
.venv/bin/pip install pillow -r cache/requirements.txt
.venv/bin/python tools/build_svg.py
```

`build_svg.py` shells out to `tools/ascii_portrait.py` for the portrait, then
pads every row of the right column to exactly 60 monospace cells so the dot
leaders line up. It refuses to write anything if a row comes out the wrong width.

To retune the portrait on its own:

```sh
.venv/bin/python tools/ascii_portrait.py --contrast 4.2 --zoom 0.80 --y-bias 0.15
```

## The daily refresh

`.github/workflows/build.yaml` runs `today.py` on every push to `main`, daily at
04:00 UTC, and on demand via *Run workflow*. It needs two repository secrets:

| Secret | Value |
| --- | --- |
| `ACCESS_TOKEN` | A GitHub PAT with `repo` and `read:user` |
| `USER_NAME` | `Saksham9399` |

`today.py` walks every repository's commit history to count lines, so the first
run takes a few minutes and writes `cache/<sha256 of username>.txt`. Later runs
read that cache and finish quickly. Deleting the cache forces a full recount.

## Keeping the columns aligned

The dot leaders are sized in two places that must agree:

- `tools/build_svg.py` lays out the committed SVGs.
- `svg_overwrite()` in `today.py` re-pads the same fields on every run.

Both use the field widths listed in `svg_overwrite`. Change one, change the
other, then rebuild and check the diff is only in the `id`-tagged spans.

Two fields — `contrib_data` and `loc_add` — have no dot leader, so their rows
breathe by a cell or two as the numbers grow. `build_svg.py` accounts for this
via its `NOMINAL` table.
