"""
combat_sim.py — Shadow simulator for Spire Tactics combat.

Reimplements the ATB combat loop, AI targeting, damage formulas, and
skill execution in Python. Uses data extracted from the .p8 source
via p8_parser.py (no hardcoded copies).

This simulator serves as the DESIGN SPECIFICATION. The Lua implementation
should match its behavior. Drift is detected by anchor tests.

v2: 11 effect handlers (a/A/h/H/b/B/d/D/p/l/c), buff/debuff tracking,
    taunt, counter, poison DoT, mark, stun, revive, secondary effects.
"""

import os
import random
from dataclasses import dataclass, field
from typing import Optional
from tests.p8_parser import P8Cart, load_cart


@dataclass
class Buff:
    st: str   # stat: a=atk, d=def, s=spd, t=taunt, c=counter, etc.
    val: int  # modifier value
    dur: int  # remaining duration (0 = permanent)


@dataclass
class Unit:
    name: str
    job_id: int  # 1-indexed (0 = no job, e.g. enemies)
    hp: int
    max_hp: int
    atk: int
    def_: int
    spd: int
    x: int = 0
    y: int = 0
    atb: float = 0
    alive: bool = True
    team: int = 1  # 1=player, 2=enemy
    cooldowns: dict = field(default_factory=lambda: {})
    sprite: int = 0
    behavior: int = 0  # 0=nearest, 1=lowest HP, 2=backrow, etc.
    buffs: list = field(default_factory=list)
    debuffs: list = field(default_factory=list)

    def copy(self):
        u = Unit(
            name=self.name, job_id=self.job_id, hp=self.hp,
            max_hp=self.max_hp, atk=self.atk, def_=self.def_,
            spd=self.spd, x=self.x, y=self.y, atb=self.atb,
            alive=self.alive, team=self.team,
            cooldowns=dict(self.cooldowns), sprite=self.sprite,
            behavior=self.behavior,
            buffs=[Buff(b.st, b.val, b.dur) for b in self.buffs],
            debuffs=[Buff(d.st, d.val, d.dur) for d in self.debuffs]
        )
        return u


class CombatSim:
    """Simulates a single auto-battle encounter."""

    def __init__(self, cart: P8Cart, relics=None, rng_seed=None):
        self.cart = cart
        self.jobs = cart.jobs
        self.skills = cart.skills
        self.relics = relics or []
        self.log = []
        if rng_seed is not None:
            random.seed(rng_seed)

    def relic_bonus(self, stat_key, team=1):
        """Sum accessory bonuses for a stat. Only applies to player team."""
        if team != 1:
            return 0
        total = 0
        for r in self.relics:
            key = r.get("stat_key", r.get("stat", ""))
            if key == stat_key[0]:
                total += r.get("bonus", 0)
        return total

    @staticmethod
    def bufmod(unit, stat):
        """Sum of buff/debuff modifiers for a stat."""
        m = 0
        for b in unit.buffs:
            if b.st == stat:
                m += b.val
        for d in unit.debuffs:
            if d.st == stat:
                m -= d.val
        return m

    @staticmethod
    def bfval(caster, target, skill):
        """Compute buff/debuff value from skill data."""
        pw = skill["power"]
        x = skill.get("xtra", "0")
        if x == "s":
            return pw
        if x == "a":
            if pw <= 5:
                return pw
            return max(1, int(pw * target.atk / 100))
        if x == "d":
            return max(1, int(pw * target.def_ / 100))
        return pw

    def tick_buffs(self, unit):
        """Tick down buff/debuff durations. Handle poison DoT."""
        # Tick buffs (iterate backwards for safe removal)
        for b in list(unit.buffs):
            if b.dur > 0:
                b.dur -= 1
                if b.dur <= 0:
                    unit.buffs.remove(b)
        # Tick debuffs + poison
        for d in list(unit.debuffs):
            if d.st == "p":
                unit.hp -= d.val
                if unit.hp <= 0:
                    unit.alive = False
            if d.dur > 0:
                d.dur -= 1
                if d.dur <= 0:
                    unit.debuffs.remove(d)

    def make_player_unit(self, job_id, level=1, x=0, y=0):
        """Create a player unit from job data."""
        j = self.jobs[job_id - 1]
        hp = j["hp"] + level * 2 if level > 1 else j["hp"]
        atk = j["atk"] + (level - 1) // 2
        def_ = j["def_"] + (level - 1) // 2
        return Unit(
            name=j["name"], job_id=job_id,
            hp=hp, max_hp=hp, atk=atk, def_=def_, spd=j["spd"],
            x=x, y=y, team=1
        )

    def make_enemy(self, enemy_id, x=4, y=0, floor=1):
        """Create an enemy unit from enemy data with floor scaling."""
        e = self.cart.enemies[enemy_id - 1]
        hp = int(e["hp"] * (1 + floor * 0.2))
        atk = int(e["atk"] * (1 + floor * 0.1))
        def_ = e.get("def_", 1)
        behavior = e.get("behavior", 0)
        return Unit(
            name=e["name"], job_id=0,
            hp=hp, max_hp=hp, atk=atk, def_=def_, spd=e["spd"],
            x=x, y=y, team=2, sprite=e["spr"],
            behavior=behavior
        )

    def get_skills_for(self, unit):
        """Get skills available for a unit's current job."""
        if unit.job_id == 0:
            return []
        return [s for s in self.skills if s["job_id"] == unit.job_id]

    def manhattan(self, a, b):
        return abs(a.x - b.x) + abs(a.y - b.y)

    def calc_damage(self, attacker, defender, power=0, pierce=False):
        """Damage formula matching v2 Lua calcdmg().

        v2: max(1, pw*atk/10 + atk_bonus + bufmod(atk) - (def + bufmod(def)) ± 1)
        Mark debuff: +50% damage.
        """
        atk_bonus = self.relic_bonus("atk", attacker.team)
        atk_mod = self.bufmod(attacker, "a")
        base = int(power * attacker.atk / 10) + atk_bonus + atk_mod
        if not pierce:
            def_mod = self.bufmod(defender, "d")
            base -= (defender.def_ + def_mod)
        # Mark: +50% damage
        for d in defender.debuffs:
            if d.st == "m":
                base = int(base * 1.5)
                break
        varied = base + random.randint(-1, 1)
        return max(1, varied)

    def do_action(self, unit, all_units):
        """Execute one unit's turn. Mirrors doact() in Lua."""
        self.tick_buffs(unit)

        # Stun check
        for d in list(unit.debuffs):
            if d.st == "n":
                unit.debuffs.remove(d)
                self.log.append(f"{unit.name} stunned")
                return

        friends = [u for u in all_units if u.alive and u.team == unit.team]
        foes = [u for u in all_units if u.alive and u.team != unit.team]
        if not foes:
            return

        skills = self.get_skills_for(unit)

        # 1) Heal check (h, H + revive)
        for i, sk in enumerate(skills):
            sk_key = sk["name"]
            if sk["type"] in ("h", "H") and unit.cooldowns.get(sk_key, 0) == 0:
                # Revive
                if sk.get("xtra") == "r":
                    pool = [u for u in all_units
                            if not u.alive and u.team == unit.team]
                    if pool:
                        dead = pool[0]
                        dead.alive = True
                        dead.hp = max(1, int(dead.max_hp * sk["power"] / 100))
                        unit.cooldowns[sk_key] = sk["cd"]
                        self.log.append(f"{unit.name} revives {dead.name}")
                        return

                target = None
                for f in friends:
                    if f.hp < f.max_hp * 0.5:
                        if target is None or f.hp < target.hp:
                            target = f
                if target or sk["type"] == "H":
                    power = int(sk["power"] * unit.atk / 10)
                    if sk["type"] == "H":
                        for f in friends:
                            f.hp = min(f.max_hp, f.hp + power)
                    elif target:
                        target.hp = min(target.max_hp, target.hp + power)
                    unit.cooldowns[sk_key] = sk["cd"]
                    self.log.append(f"{unit.name} heals for {power}")
                    return

        # 2) Find target (taunt + behavior)
        nearest = None
        nearest_dist = 999
        bf = unit.behavior

        # Taunt override
        for f in foes:
            for b in f.buffs:
                if b.st == "t":
                    nearest = f
                    nearest_dist = self.manhattan(unit, f)

        if nearest is None:
            target_pool = foes
            if bf == 0 and unit.team == 2 and len(foes) > 1:
                max_x = max(f.x for f in foes)
                front = [f for f in foes if f.x == max_x]
                if front:
                    target_pool = front

            for f in target_pool:
                d = self.manhattan(unit, f)
                if bf == 1:
                    if (nearest is None or f.hp < nearest.hp
                            or (f.hp == nearest.hp and d < nearest_dist)):
                        nearest = f
                        nearest_dist = d
                elif bf == 2:
                    if (nearest is None or f.x < nearest.x
                            or (f.x == nearest.x and d < nearest_dist)):
                        nearest = f
                        nearest_dist = d
                else:
                    if d < nearest_dist:
                        nearest = f
                        nearest_dist = d

        if nearest:
            nearest_dist = self.manhattan(unit, nearest)

        # 3) Debuff check (d, D)
        for i, sk in enumerate(skills):
            sk_key = sk["name"]
            tp = sk["type"]
            if tp in ("d", "D") and unit.cooldowns.get(sk_key, 0) == 0:
                xtra = sk.get("xtra", "0")
                dur = sk.get("dur", 0)
                if tp == "D":
                    if xtra == "t":
                        # Taunt: buff self
                        unit.buffs.append(Buff("t", 0, dur))
                    else:
                        for f in foes:
                            val = self.bfval(unit, f, sk)
                            f.debuffs.append(Buff(xtra, val, dur))
                    unit.cooldowns[sk_key] = sk["cd"]
                    self.log.append(f"{unit.name} uses {sk['name']}")
                    return
                elif nearest_dist <= sk["range"] and nearest:
                    if xtra == "0" and sk["power"] == 0:
                        # Steal
                        if nearest.buffs:
                            stolen = nearest.buffs[0]
                            nearest.buffs.remove(stolen)
                            unit.buffs.append(stolen)
                            self.log.append(f"{unit.name} stole buff")
                    else:
                        val = self.bfval(unit, nearest, sk)
                        nearest.debuffs.append(Buff(xtra, val, dur))
                        self.log.append(
                            f"{unit.name} uses {sk['name']} on {nearest.name}")
                    unit.cooldowns[sk_key] = sk["cd"]
                    return

        # 4) Buff check (b, B, c)
        for i, sk in enumerate(skills):
            sk_key = sk["name"]
            tp = sk["type"]
            if tp in ("b", "B", "c") and unit.cooldowns.get(sk_key, 0) == 0:
                xtra = sk.get("xtra", "0")
                dur = sk.get("dur", 0)
                if tp == "c":
                    unit.buffs.append(Buff("c", sk["power"], dur))
                    self.log.append(f"{unit.name} uses {sk['name']} counter")
                elif tp == "B":
                    for f in friends:
                        val = self.bfval(unit, f, sk)
                        f.buffs.append(Buff(xtra, val, dur))
                    self.log.append(f"{unit.name} uses {sk['name']} all")
                else:
                    # Single target buff
                    btgt = unit
                    rng = sk["range"]
                    if rng > 0:
                        for f in friends:
                            if f is not unit and self.manhattan(unit, f) <= rng:
                                btgt = f
                                break
                    val = self.bfval(unit, btgt, sk)
                    btgt.buffs.append(Buff(xtra, val, dur))
                    self.log.append(
                        f"{unit.name} uses {sk['name']} +{val}")
                unit.cooldowns[sk_key] = sk["cd"]
                return

        # 5) Attack skills (a, A, p, l)
        for i, sk in enumerate(skills):
            sk_key = sk["name"]
            tp = sk["type"]
            if tp in ("a", "A", "p", "l") and unit.cooldowns.get(sk_key, 0) == 0:
                if tp == "A":
                    dmg = self.calc_damage(unit, foes[0], sk["power"])
                    for f in foes:
                        f.hp -= dmg
                        if f.hp <= 0:
                            f.alive = False
                    unit.cooldowns[sk_key] = sk["cd"]
                    self.log.append(
                        f"{unit.name} uses {sk['name']} AoE for {dmg}")
                    return
                elif nearest_dist <= sk["range"]:
                    pierce = (tp == "p")
                    dmg = self.calc_damage(
                        unit, nearest, sk["power"], pierce=pierce)
                    # Counter check (melee only)
                    countered = False
                    if nearest_dist <= 1:
                        for b in list(nearest.buffs):
                            if b.st == "c":
                                ref = int(dmg * b.val / 100)
                                unit.hp -= ref
                                if unit.hp <= 0:
                                    unit.alive = False
                                nearest.buffs.remove(b)
                                countered = True
                                self.log.append(
                                    f"{nearest.name} counters for {ref}")
                                break
                    if not countered:
                        nearest.hp -= dmg
                        # Xtra effects
                        xtra = sk.get("xtra", "0")
                        dur = sk.get("dur", 0)
                        if xtra != "0" and dur > 0:
                            val = self.bfval(unit, nearest, sk)
                            nearest.debuffs.append(Buff(xtra, val, dur))
                        if xtra == "k":
                            unit.hp = min(unit.max_hp, unit.hp + dmg)
                        if xtra == "n":
                            nearest.debuffs.append(Buff("n", 0, 1))
                    if tp == "l" and not countered:
                        unit.hp = min(unit.max_hp, unit.hp + dmg // 2)
                    if not countered and nearest.hp <= 0:
                        nearest.alive = False
                    unit.cooldowns[sk_key] = sk["cd"]
                    self.log.append(
                        f"{unit.name} uses {sk['name']} on {nearest.name} "
                        f"for {dmg} dmg (hp: {nearest.hp})")
                    return

        # 6) Move or basic attack
        if nearest_dist > 1:
            if nearest.x > unit.x:
                unit.x += 1
            elif nearest.x < unit.x:
                unit.x -= 1
            elif nearest.y > unit.y:
                unit.y += 1
            elif nearest.y < unit.y:
                unit.y -= 1
            self.log.append(f"{unit.name} moves to ({unit.x},{unit.y})")
        else:
            # Basic attack with bufmod
            a = unit.atk + self.relic_bonus("atk", unit.team) + self.bufmod(unit, "a")
            d = nearest.def_ + self.bufmod(nearest, "d")
            dmg = max(1, a - d + random.randint(-1, 1))
            # Counter check
            countered = False
            for b in list(nearest.buffs):
                if b.st == "c":
                    unit.hp -= int(dmg * b.val / 100)
                    if unit.hp <= 0:
                        unit.alive = False
                    nearest.buffs.remove(b)
                    countered = True
                    self.log.append(f"{nearest.name} counters for {dmg}")
                    break
            if not countered:
                nearest.hp -= dmg
                if nearest.hp <= 0:
                    nearest.alive = False
            self.log.append(
                f"{unit.name} attacks {nearest.name} for {dmg} dmg "
                f"(hp: {nearest.hp})")

    def tick_cooldowns(self, unit):
        """Reduce all cooldowns by 1."""
        for key in list(unit.cooldowns.keys()):
            if unit.cooldowns[key] > 0:
                unit.cooldowns[key] -= 1

    def run(self, party, enemies, max_ticks=2000):
        """Run a full combat encounter. Returns CombatResult."""
        all_units = party + enemies
        self.log = []
        ticks = 0

        while ticks < max_ticks:
            ticks += 1
            # Check win/loss
            p_alive = any(u.alive for u in party)
            e_alive = any(u.alive for u in enemies)
            if not e_alive:
                return CombatResult(
                    won=True, ticks=ticks, log=self.log,
                    party=party, enemies=enemies,
                    surviving_party=[u for u in party if u.alive]
                )
            if not p_alive:
                return CombatResult(
                    won=False, ticks=ticks, log=self.log,
                    party=party, enemies=enemies,
                    surviving_party=[]
                )

            # Tick ATB for all alive units
            for u in all_units:
                if not u.alive:
                    continue
                spd_bonus = self.relic_bonus("spd", u.team)
                spd_mod = self.bufmod(u, "s")
                u.atb += max(1, u.spd + spd_bonus + spd_mod)
                if u.atb >= 100:
                    u.atb = 0
                    self.do_action(u, all_units)
                    self.tick_cooldowns(u)
                    break  # One action per tick, matches Lua behavior

        # Timeout — treat as loss
        return CombatResult(
            won=False, ticks=ticks, log=self.log,
            party=party, enemies=enemies,
            surviving_party=[u for u in party if u.alive]
        )


@dataclass
class CombatResult:
    won: bool
    ticks: int
    log: list
    party: list
    enemies: list
    surviving_party: list

    @property
    def party_hp_pct(self):
        """Average HP percentage of surviving party members."""
        if not self.surviving_party:
            return 0.0
        return sum(u.hp / u.max_hp for u in self.surviving_party) / len(
            self.surviving_party
        )

    @property
    def total_party_damage_taken(self):
        """Total damage taken across all party members."""
        return sum(u.max_hp - u.hp for u in self.party)


def run_batch(cart, setup_fn, n=500, seed_base=0):
    """Run n simulations with a setup function.

    setup_fn(sim, i) -> (party_list, enemy_list)
    Returns list of CombatResults.
    """
    results = []
    for i in range(n):
        sim = CombatSim(cart, rng_seed=seed_base + i)
        party, enemies = setup_fn(sim, i)
        result = sim.run(party, enemies)
        results.append(result)
    return results


def win_rate(results):
    """Calculate win rate from a batch of CombatResults."""
    if not results:
        return 0.0
    return sum(1 for r in results if r.won) / len(results)


def avg_ticks(results):
    """Average combat duration in ticks."""
    if not results:
        return 0
    return sum(r.ticks for r in results) / len(results)


def avg_surviving_hp_pct(results):
    """Average surviving party HP% across wins only."""
    wins = [r for r in results if r.won]
    if not wins:
        return 0.0
    return sum(r.party_hp_pct for r in wins) / len(wins)


if __name__ == "__main__":
    cart = load_cart(os.path.join(os.path.dirname(__file__), "..", "spire_tactics.p8"))
    sim = CombatSim(cart, rng_seed=42)

    # Quick test: 3 squires vs 2 slimes
    party = [
        sim.make_player_unit(1, x=0, y=0),
        sim.make_player_unit(1, x=1, y=1),
        sim.make_player_unit(1, x=0, y=2),
    ]
    enemies = [
        sim.make_enemy(1, x=4, y=0),
        sim.make_enemy(1, x=5, y=1),
    ]
    result = sim.run(party, enemies)
    print(f"Result: {'WIN' if result.won else 'LOSS'} in {result.ticks} ticks")
    print(f"Surviving party HP%: {result.party_hp_pct:.1%}")
    for line in result.log[-10:]:
        print(f"  {line}")
