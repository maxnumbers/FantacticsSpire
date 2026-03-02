"""
test_anchors.py — Layer 3: Drift detection anchors.

These tests verify that the Python shadow sim and the Lua game code
agree on specific deterministic calculations. If an anchor breaks,
either the sim or the Lua has changed without updating the other.

Small in number, high-coupling by design.

v2 damage formula: max(1, floor(pw*atk/10) + bonus - def ± 1)
v2 heal formula:   floor(pw * atk / 10)
"""

import os
import random
import pytest
from tests.p8_parser import P8Cart
from tests.combat_sim import CombatSim, Unit

CART_PATH = os.path.join(os.path.dirname(__file__), "..", "spire_tactics.p8")


@pytest.fixture
def cart():
    return P8Cart(CART_PATH)


class TestDamageFormulaAnchor:
    """Verify Python sim's damage formula matches Lua's calcdmg().

    v2 formula: max(1, floor(pw*atk/10) + accb - def ± 1)
    Basic attack uses pw=10 (1x multiplier).
    """

    def test_basic_damage_range(self, cart):
        """Squire (atk=4) vs slime (def=2), basic attack (pw=10).
        Base: floor(10*4/10) - 2 = 2, range=[1,3]
        """
        sim = CombatSim(cart)
        attacker = Unit("sqr", job_id=1, hp=12, max_hp=12, atk=4, def_=3, spd=3)
        defender = Unit("slime", job_id=0, hp=10, max_hp=10, atk=4, def_=2, spd=2, team=2)
        damages = set()
        for seed in range(100):
            random.seed(seed)
            damages.add(sim.calc_damage(attacker, defender, power=10))
        assert min(damages) >= 1, f"Damage below floor: {min(damages)}"
        assert max(damages) <= 3, f"Damage above expected range: {max(damages)}"
        assert 2 in damages, "Expected center value 2 not produced"

    def test_skill_damage_range(self, cart):
        """Apprentice (atk=5) fire (pw=12) vs goblin (def=2).
        Base: floor(12*5/10) - 2 = 4, range=[3,5]
        """
        sim = CombatSim(cart)
        attacker = Unit("apr", job_id=4, hp=7, max_hp=7, atk=5, def_=1, spd=4)
        defender = Unit("goblin", job_id=0, hp=12, max_hp=12, atk=5, def_=2, spd=3, team=2)
        damages = set()
        for seed in range(100):
            random.seed(seed)
            damages.add(sim.calc_damage(attacker, defender, power=12))
        assert min(damages) >= 3, f"Min damage {min(damages)} below expected 3"
        assert max(damages) <= 5, f"Max damage {max(damages)} above expected 5"
        assert 4 in damages, "Expected center value 4 not produced"

    def test_minimum_damage_floor(self, cart):
        """Damage should always be at least 1 regardless of variance."""
        sim = CombatSim(cart)
        attacker = Unit("slime", job_id=0, hp=10, max_hp=10, atk=4, def_=2, spd=2, team=2)
        defender = Unit("knt", job_id=7, hp=16, max_hp=16, atk=4, def_=5, spd=2, team=1)
        for seed in range(100):
            random.seed(seed)
            dmg = sim.calc_damage(attacker, defender, power=10)
            assert dmg >= 1, f"Damage {dmg} below floor of 1"

    def test_damage_with_accessories(self, cart):
        """Squire (atk=4) with 2 ATK accessories (+2 each) vs slime (def=2).
        Base: floor(10*4/10) + 4 - 2 = 6, range=[5,7]
        """
        sim = CombatSim(cart, relics=[
            {"stat": "a", "bonus": 2, "name": "pwr glv"},
            {"stat": "a", "bonus": 2, "name": "pwr glv"},
        ])
        attacker = Unit("sqr", job_id=1, hp=12, max_hp=12, atk=4, def_=3, spd=3, team=1)
        defender = Unit("slime", job_id=0, hp=10, max_hp=10, atk=4, def_=2, spd=2, team=2)
        damages = set()
        for seed in range(100):
            random.seed(seed)
            damages.add(sim.calc_damage(attacker, defender, power=10))
        assert 6 in damages, "Expected center value 6 not produced"
        assert min(damages) >= 5

    def test_high_def_floors_at_one(self, cart):
        """Slime (atk=4) vs knight (def=5). base=4-5=-1. Always floors at 1."""
        sim = CombatSim(cart)
        attacker = Unit("slime", job_id=0, hp=10, max_hp=10, atk=4, def_=2, spd=2, team=2)
        defender = Unit("knt", job_id=7, hp=16, max_hp=16, atk=4, def_=5, spd=2, team=1)
        for seed in range(50):
            random.seed(seed)
            dmg = sim.calc_damage(attacker, defender, power=10)
            assert dmg >= 1


class TestATBOrderAnchor:
    """Verify ATB turn ordering matches between sim and Lua logic."""

    def test_faster_unit_acts_first(self, cart):
        """In a 1v1, the faster unit should get the first action."""
        sim = CombatSim(cart, rng_seed=42)
        fast = sim.make_player_unit(2, x=0, y=0)    # scout, spd=6
        slow = sim.make_enemy(6, x=5, y=0, floor=1)  # golem, spd=1
        result = sim.run([fast], [slow])
        assert len(result.log) > 0
        assert result.log[0].startswith("sct"), \
            f"Expected scout (spd=6) to act first, got: {result.log[0]}"

    def test_equal_speed_order(self, cart):
        """Units with equal speed: earlier in the iteration order acts first.
        This matches Lua's for loop iteration order.
        """
        sim = CombatSim(cart, rng_seed=42)
        # Both spd=3: squire (job 1) and goblin (enemy 2)
        player = sim.make_player_unit(1, x=0, y=0)  # sqr spd=3
        enemy = sim.make_enemy(2, x=5, y=0, floor=1)  # goblin spd=3
        result = sim.run([player], [enemy])
        assert len(result.log) > 0
        assert result.log[0].startswith("sqr"), \
            f"Expected squire (first in iteration) to act first, got: {result.log[0]}"


class TestHealFormulaAnchor:
    """Verify heal calculations match.

    v2 heal: floor(pw * atk / 10), capped at max_hp.
    """

    def test_basic_heal(self, cart):
        """Acolyte (job 3, atk=2) mend (pw=15): heal = floor(15*2/10) = 3.
        Target at 4/14 HP should heal to 7/14.
        """
        sim = CombatSim(cart, rng_seed=42)
        acolyte = Unit("aco", job_id=3, hp=9, max_hp=9, atk=2, def_=2,
                        spd=4, team=1, x=0, y=0)
        wounded = Unit("knt", job_id=7, hp=4, max_hp=14, atk=4, def_=5,
                        spd=2, team=1, x=1, y=0)
        enemy = Unit("slime", job_id=0, hp=10, max_hp=10, atk=4, def_=2,
                      spd=2, team=2, x=5, y=0)

        # Acolyte should heal wounded knight (4 < 14*0.5=7)
        sim.do_action(acolyte, [acolyte, wounded, enemy])
        assert wounded.hp == 7, \
            f"Expected heal to 7 (4+3), got {wounded.hp}"

    def test_heal_capped_at_max(self, cart):
        """Heal should not exceed max_hp."""
        sim = CombatSim(cart, rng_seed=42)
        acolyte = Unit("aco", job_id=3, hp=9, max_hp=9, atk=2, def_=2,
                        spd=4, team=1, x=0, y=0)
        wounded = Unit("sqr", job_id=1, hp=1, max_hp=3, atk=4,
                        def_=3, spd=3, team=1, x=1, y=0)
        enemy = Unit("slime", job_id=0, hp=10, max_hp=10, atk=4, def_=2,
                      spd=2, team=2, x=5, y=0)

        # Heal=3 would bring 1→4, but max=3 so should cap at 3
        sim.do_action(acolyte, [acolyte, wounded, enemy])
        assert wounded.hp <= wounded.max_hp, \
            f"Heal exceeded max HP: {wounded.hp}/{wounded.max_hp}"
        assert wounded.hp == 3, \
            f"Expected heal capped at max_hp=3, got {wounded.hp}"
