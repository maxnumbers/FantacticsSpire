"""
combat_sim.py — Shadow simulator for Spire Tactics combat.

Reimplements the ATB combat loop, AI targeting, damage formulas, and
skill execution in Python. Uses data extracted from the .p8 source
via p8_parser.py (no hardcoded copies).

This simulator serves as the DESIGN SPECIFICATION. The Lua implementation
should match its behavior. Drift is detected by anchor tests.
"""

import os
import random
from dataclasses import dataclass, field
from typing import Optional
from tests.p8_parser import P8Cart, load_cart


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
    behavior: int = 0  # 0=melee, 1=ranged, 2=aoe, 3=assassin
    buff_def: int = 0  # temporary def bonus from block
    buff_turns: int = 0

    def copy(self):
        u = Unit(
            name=self.name, job_id=self.job_id, hp=self.hp,
            max_hp=self.max_hp, atk=self.atk, def_=self.def_,
            spd=self.spd, x=self.x, y=self.y, atb=self.atb,
            alive=self.alive, team=self.team,
            cooldowns=dict(self.cooldowns), sprite=self.sprite,
            behavior=self.behavior, buff_def=self.buff_def,
            buff_turns=self.buff_turns
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
        """Sum relic bonuses for a stat. Only applies to player team."""
        if team != 1:
            return 0
        total = 0
        for r in self.relics:
            if r["stat_key"] == stat_key[0]:
                total += r["bonus"]
        return total

    def make_player_unit(self, job_id, level=1, x=0, y=0):
        """Create a player unit from job data."""
        j = self.jobs[job_id - 1]  # 1-indexed
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
        e = self.cart.enemies[enemy_id - 1]  # 1-indexed
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

    def calc_damage(self, attacker, defender, power=0):
        """Damage formula matching Lua: max(1, power + atk + relic - def + rnd(3)-1)
        
        Variance: ±1. Simple but effective — creates probabilistic outcomes
        so positioning, speed, and composition produce win rate differentials
        rather than binary 100%/0% results.
        """
        atk_bonus = self.relic_bonus("atk", attacker.team)
        base = power + attacker.atk + atk_bonus - defender.def_
        varied = base + random.randint(-1, 1)
        return max(1, varied)

    def do_action(self, unit, all_units):
        """Execute one unit's turn. Mirrors doact() in Lua."""
        friends = [u for u in all_units if u.alive and u.team == unit.team]
        foes = [u for u in all_units if u.alive and u.team != unit.team]
        if not foes:
            return

        skills = self.get_skills_for(unit)

        # Decrement buff
        if unit.buff_turns > 0:
            unit.buff_turns -= 1
            if unit.buff_turns <= 0:
                unit.def_ -= unit.buff_def
                unit.buff_def = 0

        # 1) Try heal if anyone is low
        for i, sk in enumerate(skills):
            sk_key = sk["name"]
            if sk["type"] == "h" and unit.cooldowns.get(sk_key, 0) == 0:
                target = None
                for f in friends:
                    if f.hp < f.max_hp * 0.5:
                        if target is None or f.hp < target.hp:
                            target = f
                if target:
                    power = sk["power"] + self.relic_bonus("atk", unit.team)
                    target.hp = min(target.max_hp, target.hp + power)
                    unit.cooldowns[sk_key] = sk["cd"]
                    self.log.append(f"{unit.name} heals {target.name} for {power}")
                    return

        # 2) Find target (behavior-aware, matches Lua doact)
        # FRONT-ROW BLOCKING: behavior 0 enemies must target frontmost
        # player units (highest x). They cannot bypass to backline.
        # behavior 1 (assassin) and 2 (backline) ignore blocking.
        target_pool = foes
        bf = unit.behavior
        if bf == 0 and unit.team == 2 and len(foes) > 1:
            max_x = max(f.x for f in foes)
            front = [f for f in foes if f.x == max_x]
            if front:
                target_pool = front

        nearest = None
        nearest_dist = 999

        for f in target_pool:
            d = self.manhattan(unit, f)
            if bf == 1:
                # Target lowest HP (assassin/focus fire)
                if (nearest is None or f.hp < nearest.hp
                        or (f.hp == nearest.hp and d < nearest_dist)):
                    nearest = f
                    nearest_dist = d
            elif bf == 2:
                # Target furthest back (lowest x = backrow)
                if (nearest is None or f.x < nearest.x
                        or (f.x == nearest.x and d < nearest_dist)):
                    nearest = f
                    nearest_dist = d
            else:
                # Default: nearest
                if d < nearest_dist:
                    nearest = f
                    nearest_dist = d

        if nearest:
            nearest_dist = self.manhattan(unit, nearest)

        # 3) Try buff/block skills (only when enemies are close)
        for i, sk in enumerate(skills):
            sk_key = sk["name"]
            if sk["type"] == "b" and unit.cooldowns.get(sk_key, 0) == 0:
                if nearest_dist <= 2:
                    # Remove old buff before applying new one
                    if unit.buff_def > 0:
                        unit.def_ -= unit.buff_def
                    unit.buff_def = sk["power"]
                    unit.buff_turns = 2
                    unit.def_ += unit.buff_def
                    unit.cooldowns[sk_key] = sk["cd"]
                    self.log.append(f"{unit.name} uses {sk['name']} (+{sk['power']} def)")
                    return

        # 4) Try attack skills in range
        for i, sk in enumerate(skills):
            sk_key = sk["name"]
            if sk["type"] == "a" and unit.cooldowns.get(sk_key, 0) == 0:
                if nearest_dist <= sk["range"]:
                    dmg = self.calc_damage(unit, nearest, sk["power"])
                    nearest.hp -= dmg
                    if nearest.hp <= 0:
                        nearest.alive = False
                    unit.cooldowns[sk_key] = sk["cd"]
                    self.log.append(
                        f"{unit.name} uses {sk['name']} on {nearest.name} "
                        f"for {dmg} dmg (hp: {nearest.hp})"
                    )
                    return

        # 5) Move or basic attack
        if nearest_dist > 1:
            # Move one step toward target
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
            # Basic attack
            dmg = self.calc_damage(unit, nearest)
            nearest.hp -= dmg
            if nearest.hp <= 0:
                nearest.alive = False
            self.log.append(
                f"{unit.name} attacks {nearest.name} for {dmg} dmg "
                f"(hp: {nearest.hp})"
            )

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
                u.atb += u.spd + spd_bonus
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
