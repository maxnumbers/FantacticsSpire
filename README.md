# FantacticsSpire

PICO-8 roguelike auto-battler inspired by FFT: War of the Lions and Slay the Spire.

## Status

- **v1** (complete): Working auto-battler with 4 jobs, 6 skills, ATB combat, map navigation, campfires, relics, and enemy scaling. 53 automated tests passing.
- **v2** (in development): Major expansion to 18 classes, 54 skills, Slay the Spire-style map, accessories, potions, and class advancement system. See design docs below.

## Running Tests

```
pip install pytest
python3 -m pytest tests/ -v
```

## Design Documents

- `DESIGN_V2.md` — Complete v2 design specification
- `REVIEW.md` — Gap analysis between v1 and original design premise
- `WORKPLAN.md` — Ordered implementation plan for v2

## Project Structure

```
spire_tactics.p8          # The PICO-8 game cart
tests/                    # Python test harness
  p8_parser.py            # Cart parser (extracts Lua data from .p8)
  combat_sim.py           # Shadow combat simulator
  test_integrity.py       # Structural validation tests
  test_design.py          # Statistical balance tests
  test_anchors.py         # Drift detection tests
pico8-gamedev/            # PICO-8 development reference
  SKILL.md                # Game creation skill instructions
  references/pico8-api.md # PICO-8 API reference
Historical_Files/         # Archive of original development materials
```
