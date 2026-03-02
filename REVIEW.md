# Spire Tactics: Premise vs Implementation Review

## The Original Vision (synthesized from design conversations)

Three design conversations established a game that would combine:

1. **FFT:WotL's job progression** — Units earn JP per battle in their
   *current* job. Reaching thresholds in one job unlocks adjacent jobs.
   Abilities learned in one job can be carried to another. Stat growth
   is permanently shaped by which job you level in. Each unit becomes a
   unique character through the player's investment choices.

2. **Slay the Spire's run structure** — Branching node map where every
   fork forces a tradeoff (heal vs loot vs shortcut). Information about
   what's ahead creates planning. Relics accumulate to define a run's
   identity. Difficulty narrows toward the boss.

3. **Autochess/TFT positioning** — Pre-battle placement is the primary
   decision. Once combat starts, units execute autonomously. The thinking
   happens *before* the fight, not during it.

4. **Aedis Eclipse / Revenant Wings** — Squad-based auto-combat where
   formation choice and unit-type matchups determine outcomes before the
   first blow lands.

The core fantasy: "I'm developing a team of unique individuals through
a gauntlet of escalating challenges, where every decision about who
they become shapes whether we survive."

---

## What the Current Implementation Has

### Working Well
- **Auto-battle with ATB**: Combat runs itself based on speed stats,
  skill cooldowns, and targeting AI. This is faithful to the premise.
- **Positioning matters**: Front-row units body-block for back-row
  units. Mage survival rate is 100% in back vs 25% in front. Validated
  by tests.
- **HP attrition across battles**: Damage carries between fights.
  Campfire choices (heal vs upgrade) create real tradeoffs. Validated.
- **Enemy behavior variety**: Wolves target lowest-HP (assassin AI),
  normal enemies target nearest. Creates matchup-dependent strategy.
- **Difficulty curve**: Floor 1 is welcoming, floor 3 is threatening.
  Smart compositions beat random ones by >10%. Validated.
- **Relics from elites**: Risk/reward for harder fights.
- **6 bugs fixed this session**: Placement bounds, tile collision, job
  switch cost, campfire heal-all, map constraints, enemy cap.

### The Gaps

---

## GAP 1: Units Have No Individual Identity

**Premise**: Each unit develops individually. "Two identical starting
Squires can become completely different units based on your job
leveling choices."

**Current state**: All 3 units are interchangeable. They share the
same job pool, have no names, no individual JP tracking that shapes
divergent paths, no memory of what jobs they've held. When you switch
a unit's job, it simply overwrites their stats with the new job's base
stats. There is no "Aria who trained as a Knight then became a Mage"
— there's just "unit slot 2 which is currently set to Mage."

**What's missing**:
- Units need names or at minimum distinct visual identities
- Per-unit JP tracking per job (not just a global JP counter)
- Job mastery levels that persist when switching away
- The feeling that unit #2 has a *history* of choices

---

## GAP 2: No Job Progression Tree

**Premise**: "Reaching specific levels (e.g., Squire Lvl 3) unlocks
adjacent jobs." Class unlock requirements are visible (perfect info),
but the skills each class brings are partially hidden (imperfect info).

**Current state**: Job switching is instant and free. The level gate
(`req_lv` in job data) exists in the data but was removed from the
code to fix the "JP cycling" bug. All 4 jobs are accessible from the
start if the unit meets the level requirement. There is no sense of
*unlocking* or *discovering* a job's capabilities.

**What's missing**:
- A visible job tree: "Squire → Knight (lv2) / Mage (lv2)"
- Per-unit tracking: "This unit has Squire lv3, Knight lv1"
- The unlock moment: earning access to a new job feels like a reward
- Skill discovery: you can see "Knight unlocks at Squire lv2" but
  you don't know Knight's skills until you try it
- The tension: do I keep leveling Squire for Squire lv4 abilities,
  or branch into Knight now?

---

## GAP 3: No Ability Inheritance / Cross-Job Skills

**Premise**: "Equipping abilities learned from other jobs with slot
limits." The genius of FFT is that a Knight who trained as a Mage can
use Fire. Ability mixing creates emergent builds.

**Current state**: Each job has exactly 2 hardcoded skills. When you
switch jobs, you get that job's skills. Period. No ability is ever
"learned" permanently. A unit that was a Mage, then became a Knight,
has zero memory of ever being a Mage.

**What's missing**:
- Skills learned permanently when a job reaches certain levels
- An equip slot for one cross-job skill (secondary ability)
- The build-crafting moment: "My Knight with Heal is uniquely valuable"

---

## GAP 4: Map Doesn't Force Meaningful Tradeoffs

**Premise**: Slay the Spire's map works because paths *diverge then
reconverge*, forcing you to choose between a campfire path and an
elite path — you can't have both.

**Current state**: The map has 5 rows with 1-3 nodes per row. Rows
0 and 4 are always single nodes (start and boss). Middle rows have
2-3 nodes but connections are semi-random. The problem:
- With 2-3 nodes and generous connections, most nodes are reachable
  from most positions — there's rarely an exclusive choice
- Campfire appearance is random, so some runs have none reachable
- You can't see more than one step ahead to plan a route
- Paths don't converge at pinch points that force commitment

**What's missing**:
- Wider maps (3-4 nodes per row) with sparser connections so paths
  truly diverge
- Guaranteed campfire on at least one path per floor
- Visible full map so the player can plan ahead
- Pinch-point structure: wide → narrow → wide forces tradeoffs

---

## GAP 5: No Skill/Ability Growth Within a Run

**Premise**: "Skill Cards gain XP and level up through repeated use
in successful battles." Using Cleave makes Cleave better. This creates
investment in a playstyle.

**Current state**: Skills are static. Slash always does power=3. There
is no concept of a skill improving through use.

**What's missing**:
- Skills gaining XP from use
- Level thresholds that improve power, range, or cooldown
- The feeling of commitment: "I've invested in Fire, switching to
  Knight now means that investment is partially wasted"

---

## GAP 6: First Battle Has No Real Choice

**Premise**: Every encounter should involve a decision. The player
should always be thinking.

**Current state**: The first battle starts with 3 Squires. Job
switching is free but all units are identical Squires with identical
skills. The only choice is positioning, which for 3 identical melee
units against 2 weak enemies is trivial.

**What's missing**:
- Differentiated starting conditions (different starting jobs, or
  a draft/choice at the start of a run)
- Or: the first node could be a "recruitment" event where you pick
  your 3 units from a pool of 5 with varied starting jobs

---

## GAP 7: Combat Lacks Readable Feedback

**Premise**: "Floating damage numbers and simple particle effects
communicate actions."

**Current state**: Combat has damage text and particles, but the
auto-battle runs quickly and it's hard to tell *why* things happened.
There's no indication of which skill was used, whether it was a basic
attack or a special, or why a unit chose its target.

**What's missing**:
- Brief skill name flash when a unit acts
- Visual distinction between basic attacks and skills
- Some indication of cooldown state visible during combat

---

## Summary Scorecard

| Design Pillar                    | Premise | Current | Gap   |
|----------------------------------|---------|---------|-------|
| Auto-battle with ATB             | ✓       | ✓       | —     |
| Positioning matters              | ✓       | ✓       | —     |
| HP attrition / permadeath        | ✓       | ✓       | —     |
| Enemy variety + matchups         | ✓       | ✓       | —     |
| Difficulty curve                 | ✓       | ✓       | —     |
| Relic system                     | ✓       | Partial | Minor |
| Individual unit identity         | ✓       | ✗       | MAJOR |
| Job tree with unlocks            | ✓       | ✗       | MAJOR |
| Ability inheritance              | ✓       | ✗       | MAJOR |
| Map forces tradeoffs             | ✓       | ✗       | MAJOR |
| Skill growth through use         | ✓       | ✗       | Major |
| Perfect info unlock / hidden skills | ✓    | ✗       | MAJOR |
| Meaningful first choice          | ✓       | ✗       | Major |
| Combat readability               | ✓       | Partial | Minor |

The auto-battler *chassis* is solid. The progression *soul* — the
thing that makes FFT's loop addictive — is almost entirely absent.

---

## The Core Problem

The current game is a **positioning puzzle with attrition management**.
That's a valid game, but it's not what was designed. What was designed
is a **character development roguelike** where the central tension is:

> "How do I grow these 3 specific individuals through a gauntlet,
> making irreversible investment decisions that compound into unique
> builds, while the map forces me to choose between safety and power?"

Right now there are no irreversible decisions. No investment that
compounds. No individual identity. No discovery. The game plays the
same on run 5 as on run 1 because nothing about the party *develops*
within a run — you just pick a job at setup time and place units.

---

## What Would Fix It (within PICO-8 token budget)

The three highest-impact changes, roughly in priority order:

### 1. Per-Unit Job Mastery + Unlock Tree
Each unit tracks JP separately per job. Battling as Squire earns
Squire JP for *that unit*. At Squire lv2, that unit unlocks Knight
and Mage. At Knight lv2, that unit unlocks Paladin (or similar).
The tree is visible. The skills are not (until you try the job).

Token cost: ~200-300 (per-unit mastery table, unlock check function)

### 2. Secondary Skill Slot (Ability Inheritance)
When a unit reaches job lv2, they permanently learn that job's first
skill. They can equip one "secondary" skill from any job they've
mastered. This single slot creates enormous build variety:
- Knight with Heal
- Mage with Block
- Priest with Cleave

Token cost: ~100-150 (one extra field per unit, skill lookup)

### 3. Map Restructure for Real Tradeoffs
Wider map (3-4 columns), sparser connections (each node connects to
1-2 next nodes, not all of them). Guarantee at least one campfire
and one elite per floor. Show the full floor map so the player can
plan a route.

Token cost: ~50-100 (tighter connection logic, campfire guarantee)

These three changes would transform the game from "pick a job each
fight" into "develop unique characters through a branching gauntlet
where every path choice and every JP investment matters."
