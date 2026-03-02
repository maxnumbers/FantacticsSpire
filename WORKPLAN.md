# Spire Tactics v2 — Implementation Work Plan

## Project Summary

Spire Tactics is a PICO-8 roguelike auto-battler combining FFT-style
job progression with Slay the Spire map structure. Development started
2026-03-01 across 5 sessions: skill creation, initial game build,
test harness + balance tuning, balance finalization, and bug fixes.

The v1 cart (spire_tactics.p8) has a working auto-battle engine with
ATB, positioning, enemy AI, attrition, and basic map navigation. It
passes 53 automated tests covering structural integrity, balance
properties, and regression anchors.

v2 is a near-complete rewrite of the game systems built on the same
PICO-8 engine fundamentals. The auto-battle core survives but
everything around it changes.

---

## What's Being Built (v2 Design Summary)

**Draft → Map → Setup → Auto-Battle → Rewards → Repeat**

- **6 base classes**, each branching into 2 advanced classes (12 total)
- **Pick 3 of 5** offered classes at run start (one always missing)
- **Named units** that develop individually through the run
- **Class advancement** at elite nodes: pick a branch, keep 1 skill
- **Slay the Spire map**: 6 rows × 3-4 cols per floor, 3 floors
  - Pinch points force route commitment
  - Campfires, elites, shops, battles with structural guarantees
  - Full map visible and scrollable for route planning
- **Enemy preview** before battle: see enemy types + positions so
  player can plan unit placement with full information
- **Potions** (max 3 carried): player's only combat intervention
- **Accessories**: one per unit, FF-style stat/effect items
- **Auto-battle** with ATB, skill cooldowns, 11 effect handler types
- **AFK Arena-style UX**: ATB bars, skill name flashes, floating damage
- **Cross-run discovery**: tier-2 skill descriptions hidden until any
  run has reached that class (persisted via cartdata bitfield)

Full design spec: DESIGN_V2.md

---

## Work Breakdown

### Phase 1: Data Layer + Core Systems (~1500 tokens)

**W1.1 — Class & Skill Data Strings**
Encode all 18 classes (6 base + 12 advanced) with stats, and all 54
skills with effect type/power/range/cd into pipe-delimited strings.
Same pd() parser as v1.

Deliverable: Data strings verified by parser tests.

**W1.2 — Unit System Rewrite**
- Named units with per-unit fields: name, base_class, current_class,
  tier (1 or 2), kept_skill (nil or skill ref), accessory (nil or ref),
  alive, hp, mhp, atk, def, spd, x, y, atb, cd[], buffs[], debuffs[]
- mku() takes class_id, assigns random name from pool
- advance_unit(u, branch_id, kept_skill_idx) promotes tier and
  recalculates stats

Deliverable: Unit creation and advancement functions. Tests confirm
stat changes and skill loadout after advancement.

**W1.3 — Accessory & Potion Data**
12 accessories and 8 potions as data strings.
Accessory effects: stat bonuses applied at battle start, special
triggers checked during combat (counter ring, ward charm, etc).
Potion effects: applied via handler function during combat pause.

Deliverable: Data strings + accessor functions.

---

### Phase 2: Map System (~800 tokens)

**W2.1 — StS-Style Map Generator**
- 6 rows × 3-4 columns per floor
- Node types: battle(B), elite(E), campfire(C), shop(S), boss(X)
- Structural guarantees enforced:
  - ≥2 campfires per floor on different branches
  - ≥2 elites per floor
  - ≥1 shop per floor
  - Pinch points at rows 3 and 6 (2 nodes max)
  - Each node connects to 1-2 next-row nodes (sparse, not all)
- Connection algorithm: proximity-based with exclusivity constraint
  (if node A connects to B, neighboring node may not also reach B)

Deliverable: genmap() produces valid floors. Tests verify structural
guarantees (campfire count, elite count, path divergence, pinch points).

**W2.2 — Map Display + Scrolling**
- Vertical scroll: d-pad up/down moves viewport
- Node icons: sword(B), skull(E), flame(C), coin(S), crown(X)
- Lines drawn between connected nodes
- Current node highlighted, valid next nodes selectable
- Full floor visible by scrolling

Deliverable: Scrollable map renders correctly at 128×128.

**W2.3 — Enemy Preview on Battle Nodes**
- When cursor is on a battle/elite node: show enemy lineup
- Display enemy sprites, names, and HP values
- Player sees this BEFORE entering battle
- Allows informed placement decisions

Deliverable: Preview panel renders on node selection.

---

### Phase 3: Combat System Rewrite (~1300 tokens)

**W3.1 — Expanded ATB + Skill Effect System**
- Same ATB core: gauge fills by SPD, act at 100, reset
- 11 effect handlers: a(single dmg), A(AoE dmg), h(single heal),
  H(AoE heal), b(buff one), B(buff all), d(debuff one), D(debuff all),
  p(pierce), l(lifesteal), c(counter stance)
- Buff/debuff tracking: each unit has buffs[] and debuffs[] arrays
  with {stat, modifier, duration} entries, ticked down each action
- Skills scale off stats: damage = power × ATK, heals = power × ATK

Deliverable: Combat resolves correctly for all 11 effect types.
Tests validate each handler type independently.

**W3.2 — AI Targeting Rewrite**
- Role-based AI (encoded per-class):
  - DPS: highest damage skill → lowest HP enemy
  - Tank: protect/taunt if ally <50% HP, else nearest enemy
  - Healer: heal if ally <60% HP, else buff, else attack
  - Debuffer: debuff highest-ATK enemy, else attack
- Enemy AI per behavior flag (same as v1 but expanded)

Deliverable: AI makes sensible choices. Tests confirm healer heals,
tank taunts, DPS targets weak enemies.

**W3.3 — Potion Intervention System**
- 🅾️ during combat opens potion overlay
- Pause ATB ticking while menu is open
- Select potion → select target → apply effect → resume
- Potion consumed from party inventory

Deliverable: Potion UI works, combat pauses/resumes cleanly.

**W3.4 — Combat UX (AFK Arena style)**
- ATB fill bars beneath each unit sprite
- Skill name text flash above unit on action (~20 frames)
- Floating damage numbers (drift up, fade)
- Buff/debuff small icon indicators
- Potion-available indicator pulsing in corner

Deliverable: Visual feedback is readable at 128×128.

---

### Phase 4: Game Flow Screens (~1000 tokens)

**W4.1 — Draft Screen**
- Show 5 class cards with name, role icon, base stats
- Player picks 3 (highlight + confirm)
- Each pick assigns a random name from pool
- Transition to floor 1 map

**W4.2 — Setup Screen (Pre-Battle)**
- Top: 6×4 battle grid with enemy positions shown (from preview)
- Player places 3 units on cols 0-2 using cursor
- Bottom: selected unit's stats, skills, accessory
- Collision check (no stacking)
- Confirm → battle starts

**W4.3 — Reward Screen**
- Battle: gold amount, chance of potion drop
- Elite: choice of "Advance a unit" OR "Pick an accessory (1 of 2)"
  - Advance: pick unit → pick branch → pick 1 skill to keep
  - Accessory: pick 1 of 2 offered, assign to a unit

**W4.4 — Campfire Screen**
- Option 1: Rest (heal all to full HP)
- Option 2: Reforge (rearrange accessories between units)

**W4.5 — Shop Screen**
- List potions with prices, buy with gold
- 2 random accessories for sale (80-120g)
- Heal all (25g)
- Skill viewer: inspect any unit's full skill descriptions

**W4.6 — Skill Viewer / Info Screen**
- Accessible from shop, campfire, setup
- Per-unit: show name, class path, all active skills with descriptions
- Tier-2 classes not yet discovered: show "???" for skill descriptions
- Discovery bitfield persisted in cartdata()

**W4.7 — Boss Intro + Victory/Defeat**
- Boss node: brief name + sprite display before combat
- Victory: "Floor cleared!" → next floor or run victory
- Defeat: "Run over" → show stats → return to title

---

### Phase 5: Test Harness Rewrite (~separate from token budget)

**W5.1 — Parser Update**
Rewrite p8_parser.py to extract v2 data structures (18 classes,
54 skills, 12 accessories, 8 potions, 15 enemies, 3 bosses).

**W5.2 — Combat Simulator Update**
Rewrite combat_sim.py to handle:
- 11 effect types
- Buff/debuff duration tracking
- Potion usage (simulated as optimal timing)
- Accessory effects
- Boss mechanics (summon, multi-hit, drain)

**W5.3 — Integrity Tests**
- All 18 classes parseable with valid stats
- All 54 skills reference valid effect types
- All accessories and potions parseable
- Map generator produces valid structure (guaranteed nodes)
- Skill viewer discovery bitfield fits in cartdata

**W5.4 — Design Tests**
- Draft variance: removing 1 of 6 classes creates meaningfully
  different optimal comps
- Floor 1 winrate ≥80% with base-tier party
- Floor 3 boss winrate 30-70% with advanced party
- Potion usage improves winrate by ≥10%
- Accessory impact: equipped vs naked shows stat difference
- Smart placement beats random by ≥15%
- Campfire heal impact measurable across multi-battle sequences
- All 11 effect types trigger correctly in simulation

**W5.5 — Anchor Tests**
Snapshot all class stats, skill params, enemy stats, accessory values.
Detect any unintended drift from balance tuning.

---

## Implementation Order (Suggested)

```
1. W1.1 Data strings (foundation everything else builds on)
2. W1.2 Unit system (needed for all gameplay)
3. W1.3 Accessories + potions data
4. W5.1 Parser update (validate data immediately)
5. W3.1 Combat engine + effect handlers
6. W3.2 AI targeting
7. W5.2 Simulator update (validate combat)
8. W5.3 Integrity tests (lock down data correctness)
9. W2.1 Map generator
10. W4.1 Draft screen
11. W4.2 Setup screen + enemy preview (W2.3)
12. W4.3 Reward screen + advancement
13. W3.3 Potion system
14. W4.4-W4.5 Campfire + Shop
15. W3.4 Combat UX polish
16. W4.6 Skill viewer + discovery persistence
17. W4.7 Boss + endgame
18. W5.4-W5.5 Design + anchor tests
19. Balance tuning pass
```

Steps 1-8 can be validated without any UI. Steps 9-13 form the
playable core. Steps 14-18 are polish and verification.

---

## Files in This Archive

### Game
- `spire_tactics.p8` — v1 cart (working, 53 tests passing)

### Design
- `DESIGN_V2.md` — Complete v2 design specification
- `REVIEW.md` — Gap analysis: v1 vs original premise
- `WORKPLAN.md` — This file

### Test Harness
- `tests/p8_parser.py` — Cart parser (extracts Lua data from .p8)
- `tests/combat_sim.py` — Shadow combat simulator
- `tests/test_integrity.py` — 24 structural validation tests
- `tests/test_design.py` — 16 statistical balance tests
- `tests/test_anchors.py` — 9 drift detection tests

### PICO-8 Skill
- `pico8-gamedev/SKILL.md` — Game creation skill instructions
- `pico8-gamedev/references/pico8-api.md` — PICO-8 API reference

### History
- `journal.txt` — Index of all session transcripts
- `transcripts/` — 5 session transcripts (skill creation, review,
  test harness, balance tuning, bug fixes)
