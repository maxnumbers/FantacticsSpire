# FantacticsSpire Design Analysis & Recommended Changes

## Goal
Shape the game into a tighter fusion of **Slay the Spire** structure and **Final Fantasy Tactics: WotL** progression while improving:
- Balance
- Variety and replayability
- Mid/late-run progression satisfaction
- Strategic planning and identity per run

This proposal builds from the current v2 target design and known gaps.

---

## 1) High-Level Diagnosis

### What is already strong
- The game already has a strong auto-battle core with ATB, role-aware AI, and map node structure inspired by StS.
- Positioning is intended as the main tactical lever before battle.
- Attrition and pathing decisions already exist in concept and test strategy.

### What still limits depth
1. **Run identity is too class-centric, not character-centric.**
   - Class advancement is present, but units still need stronger personal build history and differentiation.
2. **Power spikes can become too binary.**
   - Some skills/relic interactions can produce runaway outcomes (especially speed, cooldown compression, and permanent scaling effects).
3. **Map decisions need stronger long-horizon planning pressure.**
   - StS-style map shape exists, but route planning can be deepened with more explicit risk/reward arcs and branch identity.
4. **Replayability is mostly content variance, not system variance.**
   - More enemy intents, mutators, and class/skill discovery layers are needed for a true roguelike mastery loop.

---

## 2) Core System Changes (Highest Impact)

## A. Add FFT-Style Job Mastery + Carryover Loadout Economy

### Recommendation
Introduce per-unit **JP/job mastery** and a constrained cross-job loadout model:
- Every unit has per-job mastery levels (0-5 suggested).
- Every mastered level unlocks either:
  - a passive node, or
  - one class skill for carryover pool.
- Combat loadout becomes:
  - 1 primary action set (current class)
  - 1 secondary skill slot (from mastered jobs)
  - 1 reaction slot (counter/guard-style)
  - 1 support slot (passive)

### Why this helps
- Creates real individual unit identity ("this is Aria, my tank with Time utility").
- Increases replayability through build expression, not just class choice.
- Better mirrors FFT while still fitting compact PICO-8 constraints.

### Balance rails
- Secondary skill slot only allows **one equipped active** at a time.
- Off-class skill cooldowns +1 turn baseline to limit degenerate burst chains.
- Disallow stacking equivalent effects (e.g., only strongest haste applies).

---

## B. Rebuild Advancement from Binary Promotion to Branching Mastery

### Recommendation
Replace one-time elite promotions with a 3-part growth loop:
1. **JP gain every battle** (small guaranteed amount).
2. **Elite node gives a promotion token** (fast-track unlock or branch access).
3. **Campfire can spend JP** on one mastery node (small but meaningful).

### Why this helps
- Smooth progression curve (less "dead run" when elite path missed).
- More strategic route tension: elite = tempo, campfire = refinement.
- Better mimics FFT's persistent growth feel in a run-based format.

### Suggested pacing targets
- Floor 1 end: each unit reaches 1-2 mastery thresholds.
- Floor 2 end: two units should have clear archetype branches.
- Floor 3: player should have 1 "carry" + 2 support specialists.

---

## C. Add StS-Like Macro Variety Layers Per Run

### Recommendation
Add two lightweight run-shaping layers:
1. **Act/Floor modifier** (one per floor): e.g., "Quickened Enemies" (+1 SPD) or "Arcane Flux" (magic +20%, physical -10%).
2. **Boss relic equivalents** after each floor boss: pick 1 of 3 high-impact global effects.

### Why this helps
- Forces adaptation across runs.
- Introduces macro-strategy beyond simple class drafting.
- Emulates StS run-defining relic moments.

### Design guardrails
- Keep modifiers orthogonal (avoid only stat inflation).
- Ensure at least one offered boss relic supports defense/consistency.

---

## 3) Balance Tuning Recommendations (Concrete)

## A. Speed/ATB Balance Controls

### Risks in current direction
- High SPD + cooldown reduction + immediate action effects can produce non-interactive loops.

### Changes
- Convert SPD to diminishing returns for ATB fill:
  - Example: `effective_spd = floor(spd * 100 / (spd + 6)) * 2` (or equivalent table).
- Cap turn-advantage effects:
  - "Quick" cannot target same unit twice in 3 actions.
- Cooldown floor rule:
  - No skill can go below CD 1 unless explicitly tagged "basic".

## B. Damage and Survivability Envelope

### Target combat length
- Normal fights: 8-14 unit actions total.
- Elite fights: 12-20 actions.
- Boss fights: 18-30 actions with at least one visible phase/mechanic shift.

### Changes
- Reduce multiplicative burst stack potential:
  - Mark/Foresight/War Cry style effects should use additive stacking categories.
- Add soft anti-burst protection:
  - First hit taken by each unit each round gains +X temporary DEF (small value).
- Ensure tank viability:
  - Guard/protect effects should also increase aggro weight.

## C. Healing and Sustain

### Risk
- Teamwide healing + sustain accessories can stall fights or trivialize attrition.

### Changes
- Introduce **healing fatigue** per unit per battle:
  - Repeated incoming healing reduced by 10% per heal (resets next battle).
- Let support builds bypass fatigue partially via mastery node (build payoff).
- Revive should apply "Weakened" debuff for 1 action to avoid immediate snowball recovery.

---

## 4) Variety & Replayability Expansion

## A. Enemy Intent & Formation System

### Recommendation
Borrow StS intent readability and FFT formation identity:
- Before battle, show enemy **intent icons** for first action.
- Enemy squads should have named archetypes (e.g., "Hunter Pack", "Bulwark Line", "Hex Cell").
- Formation-level passives (small):
  - Hunter Pack: +1 SPD if 2+ wolves alive.
  - Bulwark Line: front enemies grant +DEF to backline.

### Benefit
- Better pre-battle puzzle quality.
- Higher variety without huge content count increase.

## B. Add Events and Tactical Contracts

### Recommendation
Introduce non-combat nodes with tactical tradeoffs:
- **Event nodes** (risk/reward narrative choices).
- **Contracts** before battle (optional handicap for extra reward), e.g.:
  - "No potion use" → +35g and rare accessory chance.
  - "Win in <12 actions" → mastery bonus.

### Benefit
- Creates run texture, player-authored challenge, and stronger replay value.

## C. Expand Discoverability Meta-Progression (Lightweight)

### Recommendation
Persist codex-like unlock knowledge across runs:
- Discovered class skills (already planned) + enemy intent glossary + relic synergy hints.
- Meta unlocks are informational, not raw power, to preserve roguelike fairness.

---

## 5) Progression Model: "StS x FFT" Fusion Blueprint

Implement this 6-step loop:
1. **Draft** 3 of 5 classes (run seed identity).
2. **Path planning** on visible floor with pinch points and known node distribution.
3. **Battle prep** with enemy intent preview + placement puzzle.
4. **Battle execution** mostly auto, limited intervention via potions.
5. **Growth decision** after combat (JP spend, loot, relic, promotion token).
6. **Compounding build expression** through cross-job slots and mastery tree.

This gives StS's route tension + FFT's character authorship.

---

## 6) Prioritized Implementation Roadmap

## Phase 1 — Must Have (Foundation)
1. Per-unit mastery tables + JP earn/spend.
2. Secondary skill slot + reaction/support slot stubs.
3. Speed/cooldown guardrails (diminishing returns + CD floor).
4. Enemy intent preview v1.

## Phase 2 — Core Replayability
1. Floor modifiers.
2. Boss relic choices.
3. Event/contract nodes.
4. Formation-based enemy archetypes.

## Phase 3 — Content Scaling
1. Extra branch-specific mastery nodes per class.
2. Additional potion archetypes (tempo, cleanse, reposition).
3. More boss phase mechanics.

---

## 7) Design KPIs to Validate the Changes

Track these during simulation and playtests:
- **Comp diversity:** top 10 winrate comps should represent >=4 different class cores.
- **Run identity divergence:** two runs with same opening draft should still diverge in >=2 major build choices by floor 2.
- **Action readability:** player can correctly predict likely outcome of placement in >=70% of test scenarios.
- **Pacing:** average full run length stable within target minutes while adding decision depth.
- **Retention proxy:** number of voluntarily started new runs after a defeat should increase.

---

## 8) Practical Tuning Defaults (Starting Numbers)

Use these as first-pass values:
- JP gain: 2 per normal battle, 4 per elite, 5 per boss.
- Mastery threshold ladder: 4 / 8 / 14 / 22 / 32 JP.
- Secondary skill off-class penalty: +1 cooldown.
- Healing fatigue: -10% per received heal this battle (cap -40%).
- Floor modifier intensity: equivalent to ~8-12% power swing.
- Boss relic strength: equivalent to ~15-20% power swing.

These ranges are large enough to be felt but small enough to prevent instant breakage.

---

## 9) Final Recommendation

If only **three** changes can be made now, do these first:
1. **Per-unit mastery + cross-job slotting** (FFT soul).
2. **Floor modifiers + boss relic choices** (StS run identity).
3. **Speed/cooldown/healing guardrails** (balance stability for all future content).

Together, they provide the biggest increase in strategic depth, replayability, and player-authored progression while preserving the current auto-battle strengths.
