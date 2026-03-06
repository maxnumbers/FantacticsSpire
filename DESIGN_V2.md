# Spire Tactics v2 — Design Spec

## Run Flow

```
DRAFT (pick 3 of 5 classes)
  │
  ▼
FLOOR 1 ──── 15 nodes, StS layout ──── BOSS 1
  │
FLOOR 2 ──── 15 nodes, harder ──────── BOSS 2
  │
FLOOR 3 ──── 15 nodes, hardest ─────── FINAL BOSS
  │
  ▼
VICTORY (or death anywhere = run over)
```

---

## The Draft

Run start: 5 of 6 base classes are offered. You pick 3.
Each unit gets a random name from: Aria, Kael, Lira, Voss, Rhen, Dahl, Mira, Thane.
Units start at tier 1 with their base class's 3 skills and base stats.

Why 5-of-6 and not 6-of-6: one class is always missing, so you
can't always build your ideal comp. Creates run identity from moment one.

---

## The 6 Base Classes

Design axis coverage:

| Axis        | Classes that cover it           |
|-------------|---------------------------------|
| Front melee | Squire, Brawler                 |
| Back ranged | Scout, Apprentice               |
| Support     | Acolyte, (Lancer partial)       |
| High HP     | Brawler, Squire                 |
| High SPD    | Scout, Apprentice               |
| High ATK    | Apprentice, Lancer              |
| AoE         | Apprentice→BLM, Brawler→Zerker |
| Single DPS  | Scout→Ranger, Lancer→Dragoon   |
| Healing     | Acolyte→Priest, Brawler→Monk   |
| Buffs       | Acolyte→Oracle, Lancer→Valk    |
| Debuffs     | Scout→Thief, Apprentice→TmMage |
| Tank/Prot   | Squire→Knight, Brawler→Monk    |

### Stats & Skills

Stats: HP, ATK, DEF, SPD. Skills scale off these.
Position preference: F=front (x=2), M=mid (x=1), B=back (x=0).

### ① SQUIRE — "The Reliable Starter"
Pos: F | HP:12 ATK:4 DEF:3 SPD:3

| Skill    | Type | Power | Range | CD | Effect |
|----------|------|-------|-------|----|--------|
| Slash    | atk  | 1.0×  | 1     | 0  | Basic melee hit |
| Guard    | buff | —     | self  | 3  | +50% DEF for 2 actions |
| Rally    | buff | —     | all   | 4  | +1 SPD to all allies for 3 actions |

**→ KNIGHT** (tank/protect)
HP:16 ATK:4 DEF:5 SPD:2

| Skill      | Type  | Power | Range | CD | Effect |
|------------|-------|-------|-------|----|--------|
| Shield Wall| buff  | —     | adj   | 3  | Adjacent allies take 50% damage, 2 actions |
| Taunt      | debuf | —     | all   | 4  | All enemies target this unit, 2 actions |
| Fortress   | buff  | —     | self  | 5  | +100% DEF for 3 actions, can't attack |

**→ SAMURAI** (burst damage)
HP:11 ATK:6 DEF:2 SPD:4

| Skill      | Type | Power | Range | CD | Effect |
|------------|------|-------|-------|----|--------|
| Iai Strike | atk  | 2.0×  | 1     | 3  | Double damage single hit |
| Blade Dance| atk  | 0.7×  | 1     | 3  | Hit ALL enemies in melee range |
| Focus      | buff | —     | self  | 4  | Next attack deals 3× damage |

---

### ② SCOUT — "The Fast Striker"
Pos: B | HP:8 ATK:3 DEF:1 SPD:6

| Skill  | Type  | Power | Range | CD | Effect |
|--------|-------|-------|-------|----|--------|
| Shot   | atk   | 1.0×  | 3     | 0  | Ranged physical hit |
| Dash   | buff  | —     | self  | 2  | +3 SPD for 2 actions |
| Mark   | debuf | —     | 3     | 3  | Target takes +50% damage, 2 actions |

**→ RANGER** (sustained ranged DPS)
HP:9 ATK:5 DEF:1 SPD:5

| Skill    | Type | Power | Range | CD | Effect |
|----------|------|-------|-------|----|--------|
| Volley   | atk  | 0.6×  | 3     | 3  | Hit ALL enemies (AoE) |
| Snipe    | atk  | 2.5×  | 3     | 4  | Massive single target, pierces DEF |
| Trap     | atk  | 1.5×  | 2     | 3  | Damages + slows target (-2 SPD, 3 actions) |

**→ THIEF** (debuff/disrupt)
HP:8 ATK:4 DEF:1 SPD:7

| Skill   | Type  | Power | Range | CD | Effect |
|---------|-------|-------|-------|----|--------|
| Poison  | debuf | 0.3×  | 2     | 2  | DoT: deals damage each tick, 4 ticks |
| Steal   | debuf | —     | 1     | 4  | Remove target's buff, apply to self |
| Ambush  | atk   | 2.0×  | 1     | 3  | Targets lowest-HP enemy, ignores DEF |

---

### ③ ACOLYTE — "The Healer Base"
Pos: B | HP:9 ATK:2 DEF:2 SPD:4

| Skill   | Type | Power | Range | CD | Effect |
|---------|------|-------|-------|----|--------|
| Mend    | heal | 1.5×  | 3     | 1  | Heal one ally (scales off own ATK) |
| Bless   | buff | —     | 3     | 3  | Target ally +30% ATK, 3 actions |
| Light   | atk  | 0.8×  | 2     | 0  | Weak ranged attack |

**→ PRIEST** (pure healer)
HP:10 ATK:3 DEF:3 SPD:3

| Skill    | Type | Power | Range | CD | Effect |
|----------|------|-------|-------|----|--------|
| Heal All | heal | 1.0×  | all   | 4  | Heal entire party |
| Revive   | heal | —     | 3     | 6  | Raise fallen ally at 30% HP |
| Holy     | atk  | 1.5×  | 3     | 3  | Light damage + heal self for same |

**→ ORACLE** (buff/ward specialist)
HP:9 ATK:2 DEF:2 SPD:5

| Skill     | Type | Power | Range | CD | Effect |
|-----------|------|-------|-------|----|--------|
| Haste     | buff | —     | 3     | 3  | Target +3 SPD, 3 actions |
| Shell     | buff | —     | 3     | 3  | Target absorbs next hit (up to 2× ATK) |
| Foresight | buff | —     | all   | 5  | All allies +30% DEF, 2 actions |

---

### ④ APPRENTICE — "The Glass Cannon"
Pos: B | HP:7 ATK:5 DEF:1 SPD:4

| Skill   | Type | Power | Range | CD | Effect |
|---------|------|-------|-------|----|--------|
| Fire    | atk  | 1.2×  | 3     | 1  | Ranged magic damage |
| Spark   | atk  | 0.7×  | 3     | 2  | Hit target + one adjacent enemy |
| Barrier | buff | —     | self  | 4  | Absorb next hit up to 1.5× ATK |

**→ BLACK MAGE** (AoE destruction)
HP:7 ATK:7 DEF:1 SPD:3

| Skill    | Type | Power | Range | CD | Effect |
|----------|------|-------|-------|----|--------|
| Firaga   | atk  | 1.0×  | 3     | 4  | Hit ALL enemies (AoE) |
| Thunder  | atk  | 1.5×  | 3     | 3  | Hit target + chain to 1 other |
| Drain    | atk  | 1.0×  | 2     | 3  | Damage + heal self for 50% dealt |

**→ TIME MAGE** (control/manipulation)
HP:8 ATK:4 DEF:1 SPD:5

| Skill   | Type  | Power | Range | CD | Effect |
|---------|-------|-------|-------|----|--------|
| Slow    | debuf | —     | 3     | 3  | Target -3 SPD, 3 actions |
| Quick   | buff  | —     | 3     | 3  | Target gets immediate extra action |
| Comet   | atk   | 2.0×  | 3     | 5  | Massive single-target damage |

---

### ⑤ BRAWLER — "The HP Wall"
Pos: F | HP:15 ATK:3 DEF:2 SPD:3

| Skill   | Type | Power | Range | CD | Effect |
|---------|------|-------|-------|----|--------|
| Pummel  | atk  | 1.0×  | 1     | 0  | Basic melee |
| Endure  | heal | —     | self  | 3  | Heal self 25% max HP |
| Roar    | debuf| —     | all   | 4  | All enemies -20% ATK, 2 actions |

**→ MONK** (counter/sustain)
HP:16 ATK:4 DEF:3 SPD:4

| Skill     | Type | Power | Range | CD | Effect |
|-----------|------|-------|-------|----|--------|
| Counter   | buff | —     | self  | 2  | Reflect 100% melee damage for 1 hit |
| Chi Wave  | heal | 1.0×  | all   | 4  | Heal all allies, damage all enemies for same |
| Iron Fist | atk  | 1.5×  | 1     | 2  | Pierces DEF entirely |

**→ BERSERKER** (lifesteal bruiser)
HP:14 ATK:5 DEF:1 SPD:3

| Skill      | Type | Power | Range | CD | Effect |
|------------|------|-------|-------|----|--------|
| Frenzy     | buff | —     | self  | 3  | +2 ATK permanently (stacks, resets on death) |
| Drain Strike| atk | 1.2×  | 1     | 2  | Damage + heal self for 50% dealt |
| Rampage    | atk  | 0.8×  | 1     | 4  | Hit ALL enemies in melee range |

---

### ⑥ LANCER — "The Versatile Reach Fighter"
Pos: M | HP:10 ATK:4 DEF:2 SPD:4

| Skill   | Type | Power | Range | CD | Effect |
|---------|------|-------|-------|----|--------|
| Thrust  | atk  | 1.0×  | 2     | 0  | Mid-range melee |
| Leap    | atk  | 1.3×  | 3     | 3  | Jump to target, deal damage |
| Inspire | buff | —     | adj   | 3  | Adjacent allies +20% ATK, 2 actions |

**→ DRAGOON** (burst pierce)
HP:11 ATK:6 DEF:2 SPD:3

| Skill       | Type | Power | Range | CD | Effect |
|-------------|------|-------|-------|----|--------|
| Jump        | atk  | 2.0×  | 3     | 4  | Become untargetable, crash next action |
| Lance Charge| atk  | 1.2×  | 2     | 2  | Pierce DEF, push target back |
| Rend        | atk  | 1.0×  | 2     | 2  | Damage + reduce target DEF 30%, 3 actions |

**→ VALKYRIE** (aura support fighter)
HP:10 ATK:4 DEF:3 SPD:4

| Skill     | Type | Power | Range | CD | Effect |
|-----------|------|-------|-------|----|--------|
| War Cry   | buff | —     | all   | 4  | All allies +30% ATK, 2 actions |
| Shield Bash| atk | 1.0×  | 1     | 2  | Damage + target skips next action |
| Aegis     | buff | —     | adj   | 3  | Adjacent allies +50% DEF, 2 actions |

---

## Advancement Mechanic

**When:** After an elite battle victory, ONE party member advances.
Player chooses which unit and which branch.

**The skill-keep decision:** You see all 3 of your current tier's
skills. You pick 1 to keep permanently. The other 2 are gone forever.
Then you gain access to your new tier's 3 skills.

**Post-advancement loadout:** 1 kept skill + 3 new skills = 4 active.

**Per-unit progression display:**
```
ARIA [Squire→Knight]
 Kept: Rally (from Squire)
 Active: Shield Wall, Taunt, Fortress
 Accessory: Counter Ring
```

**Floor pacing:** Floor 1 has 1-2 elites. Floor 2 has 2-3.
A typical run advances 2 units by the final boss.
One unit usually stays at base tier — this is fine, base skills
are viable, just less specialized.

---

## Accessories (12 total)

Found at: shops (buy), elite rewards (pick 1 of 2), rare drops.
One per character. Can swap at campfire.

| # | Name         | Effect                              | Best On       |
|---|--------------|-------------------------------------|---------------|
| 1 | Power Glove  | +3 ATK                              | DPS classes   |
| 2 | Iron Shield  | +3 DEF                              | Tanks         |
| 3 | Sprint Shoes | +2 SPD                              | Anyone        |
| 4 | HP Bangle    | +5 Max HP                           | Fragile units |
| 5 | Counter Ring | Reflect 30% of melee damage taken   | Front-liners  |
| 6 | Healing Rod  | Heals restore +30%                  | Priest/Acolyte|
| 7 | Focus Band   | Skills deal +25% at full HP         | Glass cannons |
| 8 | Ward Charm   | Survive one lethal hit at 1 HP/battle| Anyone        |
| 9 | Haste Brooch | Start battle with ATB at 50%        | Slow units    |
|10 | Vampire Fang | Basic attacks heal 20% of damage    | Fast attackers|
|11 | Mage Ring    | Skill cooldowns reduced by 1        | Skill-heavy   |
|12 | Lucky Charm  | +15% gold from battles              | Economy       |

---

## Potions (8 types)

Party-wide inventory, max 3 potions carried.
Found at: shops, campfire (sometimes), battle drops (rare).
Used DURING auto-battle by pressing 🅾️ → select potion → select target.
This is the player's only combat interaction.

| # | Name        | Effect                                | Cost |
|---|-------------|---------------------------------------|------|
| 1 | Potion      | Heal one unit 50% max HP              | 30g  |
| 2 | Hi-Potion   | Heal one unit 100% max HP             | 60g  |
| 3 | Ether       | Reset all cooldowns for one unit      | 50g  |
| 4 | Haste Vial  | One unit: double SPD for 5 actions    | 40g  |
| 5 | Bomb        | Deal 8 damage to ALL enemies          | 45g  |
| 6 | Smoke Bomb  | All enemies lose their next action    | 55g  |
| 7 | Phoenix Down| Revive one fallen unit at 25% HP      | 75g  |
| 8 | Shield Tonic| One unit takes 50% damage, 3 actions  | 40g  |

---

## Map Structure (Slay the Spire baseline)

Each floor: 6 rows, 3-4 columns.
Paths branch and reconverge at rows 3 and 6 (pinch points).

```
Row 1:  [B] [B] [B]        ← 3 starting battles
         |\ /|\ /|
Row 2:  [B] [C] [E]        ← campfire + elite on diff paths
         |\ /|\ /|
Row 3:    [B] [B]          ← pinch: forces reconverge
          |\ /|\  |
Row 4:  [E] [S] [B]        ← elite, shop, battle
         |\ /|\ /|
Row 5:  [C] [B] [B]        ← another campfire opportunity
           \ | /
Row 6:     [BOSS]          ← single boss node
```

Node types:
- **B** = Battle (standard enemies, gold + small potion chance)
- **E** = Elite (hard fight, advance 1 unit OR accessory pick)
- **C** = Campfire (heal all to full OR swap accessories)
- **S** = Shop (buy potions, accessories, heal for gold)

**Structural guarantees:**
- At least 2 campfires per floor, on different branches
- At least 2 elites per floor
- At least 1 shop per floor
- Paths genuinely diverge: each node connects to 1-2 next nodes, NOT all
- Player can see the FULL floor map and scroll to plan route

**Pinch points** (rows 3 and 6) force reconvergence — you can't
cherry-pick every good node. "Do I path through the campfire, or
through the elite that would advance Aria to Knight?"

---

## Gold Economy

- Start run: 0 gold
- Battle reward: 15-25g + bonus for no deaths
- Elite reward: 30-50g + advancement OR accessory
- Gold spent at: shops (potions 30-75g, accessories 80-120g, heal 25g)
- Campfires are free (no gold cost for healing)

---

## Enemy Preview (Pre-Battle Intel)

When the player selects a battle or elite node on the map, they see
the enemy lineup BEFORE committing. This shows:
- Enemy sprites and names
- Enemy HP and approximate ATK (shown as: ★ weak / ★★ med / ★★★ strong)
- Enemy positions on the right half of the grid (cols 3-5)

This is critical because class switching is no longer possible mid-run
(classes only advance at elites). Without the ability to respec, the
player needs information to make the ONLY decision they have left:
unit placement. Seeing a wolf pack (fast, targets weakest) tells you
to put your glass cannon behind your tank. Seeing an archer tells you
the back row isn't safe either.

The setup screen then shows the same enemy positions, so placement
is done with full knowledge of the matchup. This replaces the "class
switching as adaptation" mechanic from v1 with "placement as
adaptation."

---

## Combat (Auto-Battle + Potion Intervention)

### Grid
6 columns × 4 rows. Player places on cols 0-2, enemies on cols 3-5.

### ATB System
Each unit has an ATB gauge (0-100). Each tick: ATB += SPD.
At 100: unit acts, ATB resets to 0.
Action selection: AI picks highest-priority available skill.

### AI Priority (by role)
- **DPS**: Use highest-damage available skill on lowest-HP enemy
- **Tank**: Use taunt/protect if ally is low, else attack nearest
- **Healer**: Heal if any ally <60% HP, else buff, else attack
- **Debuffer**: Debuff highest-ATK enemy, else attack

### Skill Effect Types (code implementation)
Each skill maps to one of these handlers:

| Code | Effect                           | Params       |
|------|----------------------------------|--------------|
| `a`  | Single-target damage             | power, range |
| `A`  | AoE damage (all enemies)         | power, range |
| `h`  | Single-target heal               | power, range |
| `H`  | AoE heal (all allies)            | power        |
| `b`  | Buff one ally (stat + duration)  | stat, %, dur |
| `B`  | Buff all allies                  | stat, %, dur |
| `d`  | Debuff one enemy                 | stat, %, dur |
| `D`  | Debuff all enemies               | stat, %, dur |
| `p`  | Pierce attack (ignore DEF)       | power, range |
| `l`  | Lifesteal attack                 | power, range |
| `c`  | Counter stance (reflect next)    | %, dur       |

That's 11 handler types. Each skill is encoded as:
`name,effect_code,power,range,cd,extra_param`

This means 54 skills are 54 data strings but only ~11 code paths.

### Potion Intervention
During combat, 🅾️ pauses action and opens potion menu.
Player selects potion → selects target (if applicable) → confirm.
This is the "SDS champion card" moment.

### AFK Arena-Style UX
- Each unit has a small ATB fill bar beneath them
- When a unit acts: skill name flashes above for ~20 frames
- Damage numbers float upward from target
- Buffs/debuffs show small icon next to unit
- Potions: 🅾️ icon pulses in corner when potions available

---

## Enemy Design (15 enemy types, 3 bosses)

### Regular Enemies (floor 1-3, mixed)
| Name   | HP  | ATK | DEF | SPD | Behavior        |
|--------|-----|-----|-----|-----|-----------------|
| Slime  | 10  | 4   | 2   | 2   | Nearest target  |
| Goblin | 12  | 5   | 2   | 3   | Nearest target  |
| Wolf   | 9   | 5   | 1   | 6   | Lowest HP       |
| Archer | 8   | 4   | 1   | 4   | Back row first  |
| Mage   | 7   | 6   | 1   | 3   | AoE when 2+ grouped |
| Golem  | 18  | 3   | 5   | 1   | Nearest, slow   |
| Bandit | 10  | 5   | 2   | 5   | Highest ATK     |
| Bat    | 5   | 3   | 0   | 7   | Random target   |
| Orc    | 16  | 6   | 3   | 2   | Nearest target  |
| Snake  | 8   | 4   | 1   | 5   | Poison (DoT)    |

### Elite Enemies (stronger versions + boss minions)
| Name     | HP  | ATK | DEF | SPD | Special            |
|----------|-----|-----|-----|-----|--------------------|
| Champion | 22  | 7   | 4   | 3   | Cleave (hit 2)     |
| Assassin | 14  | 8   | 1   | 6   | Targets lowest HP  |
| Shaman   | 16  | 5   | 2   | 4   | Heals ally enemies |
| Ogre     | 28  | 8   | 3   | 2   | Hits hardest       |
| Drake    | 20  | 7   | 4   | 3   | AoE breath attack  |

### Bosses
| Floor | Name       | HP  | ATK | DEF | SPD | Mechanic          |
|-------|------------|-----|-----|-----|-----|-------------------|
| 1     | Warlord    | 35  | 7   | 4   | 3   | Summons 1 Goblin every 3 actions |
| 2     | Hydra      | 50  | 8   | 3   | 4   | Attacks 2 targets at once |
| 3     | Lich King  | 60  | 10  | 5   | 3   | AoE curse (-SPD) + drain heal |

Bosses appear with 1-2 adds. Boss fights are 3v3 or 3v4.

---

## Floor Scaling
Enemy stats scale per floor:
- Floor 1: base stats
- Floor 2: ×1.3 HP, ×1.2 ATK
- Floor 3: ×1.6 HP, ×1.4 ATK

Player power scales via: advancement (stat gains), accessories,
potion stockpile, and the kept-skill from tier 1.

---

## Campfire Options
1. **Rest**: Heal all units to full HP
2. **Reforge**: Swap accessories between units (free rearrange)

Simple. The choice is: do I path through the campfire at all,
or do I take the elite path instead?

---

## Shop
- Buy potions (listed with prices)
- Buy 1 of 2 random accessories (80-120g)
- Heal all units to full (25g)
- View all unit stats and skills (free, info only)

The shop also serves as the "read about skills" interface —
you can inspect any unit's full skill list with descriptions.

---

## Skill Description Viewer

Accessible from: shop (always), campfire, pre-battle setup.
Shows each unit's current skills with full text descriptions.
For tier-2 classes the unit hasn't reached yet: shows class name
and stat changes only, skills listed as "???" until discovered.

"Discovered" = any unit in any run has ever been that class.
This persists across runs as a simple bitfield in cartdata().

---

## Token Budget Estimate

| System                        | Est. Tokens |
|-------------------------------|-------------|
| Data parsing + helpers        | 200         |
| Class/skill/enemy data strings| 0 (free)    |
| Unit creation + advancement   | 300         |
| Map generation + display      | 600         |
| Map scrolling + navigation    | 200         |
| Setup screen (placement)      | 300         |
| Combat engine (ATB + AI)      | 800         |
| Skill effect handlers (11)    | 500         |
| Potion system + UI            | 300         |
| Accessory system              | 150         |
| Shop + skill viewer           | 400         |
| Drawing routines (all screens)| 1200        |
| Draft screen                  | 200         |
| Title, game over, save        | 200         |
| **TOTAL**                     | **~5350**   |

Buffer: ~2800 tokens. Comfortable.

---

## What This Design Achieves vs Premise

| Premise Element                 | How It's Addressed           |
|---------------------------------|------------------------------|
| Individual unit identity        | Names + per-unit class path + kept skill + accessory |
| Job tree with unlocks           | Tier 1 → pick branch → Tier 2 (leafing tree) |
| Perfect info unlock req         | You see: "Squire → Knight or Samurai" always |
| Hidden skill details            | Tier 2 skills are "???" until discovered in any run |
| Ability inheritance             | Keep 1 skill from tier 1 when advancing |
| Map forces tradeoffs            | StS-style diverging paths with pinch points |
| Skill scales off stats          | All powers are multipliers of ATK, not flat |
| Player combat interaction       | Potions during auto-battle |
| Items/accessories               | FF-style, one per character |
| Slay the Spire pacing           | 6 rows, 3-4 cols, campfire/elite/shop/battle |
| Replayability                   | Draft variance + path choice + class discovery |
