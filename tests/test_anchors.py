"""
test_anchors.py — Layer 3: Drift detection anchors.

These tests verify that the Python shadow sim and the Lua game code
agree on specific deterministic calculations. If an anchor breaks,
either the sim or the Lua has changed without updating the other.

Small in number, high-coupling by design.
"""

import os
import pytest
from tests.p8_parser import P8Cart
from tests.combat_sim import CombatSim, Unit

CART_PATH = os.path.join(os.path.dirname(__file__), "..", "spire_tactics.p8")


@pytest.fixture
def cart():
    return P8Cart(CART_PATH)


class TestDamageFormulaAnchor:
    """Verify Python sim's damage formula matches Lua's.
    
    With ±1 variance, base damage ± 1. Always min 1.
    """

    def test_basic_damage_range(self, cart):
        """Squire (atk=3) vs slime (def=1), no skill power.
        Base: 3+0-1 = 2, range=[1,3]
        """
        sim = CombatSim(cart)
        attacker = Unit("sqr", job_id=1, hp=10, max_hp=10, atk=3, def_=2, spd=3)
        defender = Unit("slime", job_id=0, hp=6, max_hp=6, atk=2, def_=1, spd=2, team=2)
        damages = set()
        for seed in range(100):
            import random
            random.seed(seed)
            damages.add(sim.calc_damage(attacker, defender, power=0))
        assert min(damages) >= 1, f"Damage below floor: {min(damages)}"
        assert max(damages) <= 3, f"Damage above expected range: {max(damages)}"
        assert 2 in damages, "Expected center value 2 not produced"

    def test_skill_damage_range(self, cart):
        """Knight (atk=5) cleave (power=4) vs goblin (def=2).
        Base: 4+5-2 = 7, range=[6,8]
        """
        sim = CombatSim(cart)
        attacker = Unit("knt", job_id=2, hp=14, max_hp=14, atk=5, def_=4, spd=2)
        defender = Unit("gobln", job_id=0, hp=14, max_hp=14, atk=6, def_=2, spd=3, team=2)
        damages = set()
        for seed in range(100):
            import random
            random.seed(seed)
            damages.add(sim.calc_damage(attacker, defender, power=4))
        assert min(damages) >= 6, f"Min damage {min(damages)} below expected 6"
        assert max(damages) <= 8, f"Max damage {max(damages)} above expected 8"
        assert 7 in damages, "Expected center value 7 not produced"

    def test_minimum_damage_floor(self, cart):
        """Damage should always be at least 1 regardless of variance."""
        sim = CombatSim(cart)
        attacker = Unit("slime", job_id=0, hp=6, max_hp=6, atk=1, def_=1, spd=2, team=2)
        defender = Unit("knt", job_id=2, hp=14, max_hp=14, atk=5, def_=8, spd=2, team=1)
        for seed in range(100):
            import random
            random.seed(seed)
            dmg = sim.calc_damage(attacker, defender, power=0)
            assert dmg >= 1, f"Damage {dmg} below floor of 1"

    def test_damage_with_relics(self, cart):
        """Squire (atk=3) with 2 ATK relics (+2 each) vs slime (def=2).
        Base: 0+3+4-2 = 5, range=[4,6]
        """
        sim = CombatSim(cart, relics=[
            {"stat_key": "a", "bonus": 2, "name": "atk+"},
            {"stat_key": "a", "bonus": 2, "name": "atk+"},
        ])
        attacker = Unit("sqr", job_id=1, hp=10, max_hp=10, atk=3, def_=2, spd=3, team=1)
        defender = Unit("slime", job_id=0, hp=12, max_hp=12, atk=5, def_=2, spd=2, team=2)
        damages = set()
        for seed in range(100):
            import random
            random.seed(seed)
            damages.add(sim.calc_damage(attacker, defender, power=0))
        assert 5 in damages, "Expected center value 5 not produced"
        assert min(damages) >= 4

    def test_high_def_floors_at_one(self, cart):
        """Slime (atk=2) vs knight (def=4). base=2-4=-2+var. Always floors at 1."""
        sim = CombatSim(cart)
        attacker = Unit("slime", job_id=0, hp=12, max_hp=12, atk=2, def_=2, spd=2, team=2)
        defender = Unit("knt", job_id=2, hp=14, max_hp=14, atk=5, def_=4, spd=2, team=1)
        for seed in range(50):
            import random
            random.seed(seed)
            dmg = sim.calc_damage(attacker, defender, power=0)
            assert dmg >= 1


class TestATBOrderAnchor:
    """Verify ATB turn ordering matches between sim and Lua logic."""

    def test_faster_unit_acts_first(self, cart):
        """In a 1v1, the faster unit should get the first action."""
        sim = CombatSim(cart, rng_seed=42)
        fast = sim.make_player_unit(3, x=0, y=0)    # mage, spd=4
        slow = sim.make_enemy(4, x=5, y=0, floor=1)  # ogre, spd=2
        result = sim.run([fast], [slow])
        # First log entry should be the fast unit
        assert len(result.log) > 0
        assert result.log[0].startswith("mag"), \
            f"Expected mage (spd=4) to act first, got: {result.log[0]}"

    def test_equal_speed_order(self, cart):
        """Units with equal speed: earlier in the iteration order acts first.
        This matches Lua's for loop iteration order.
        """
        sim = CombatSim(cart, rng_seed=42)
        # Both squires (spd=3), player acts before enemy in Lua
        player = sim.make_player_unit(1, x=0, y=0)  # sqr spd3
        enemy = sim.make_enemy(2, x=5, y=0, floor=1)  # goblin spd3
        result = sim.run([player], [enemy])
        assert len(result.log) > 0
        assert result.log[0].startswith("sqr"), \
            f"Expected squire (first in iteration) to act first, got: {result.log[0]}"


class TestHealFormulaAnchor:
    """Verify heal calculations match."""

    def test_basic_heal(self, cart):
        """Priest heal skill: power=4, no relics.
        Target at 4/14 HP should heal to 8/14.
        """
        sim = CombatSim(cart, rng_seed=42)
        priest = Unit("prt", job_id=4, hp=9, max_hp=9, atk=2, def_=3,
                       spd=4, team=1, x=0, y=0)
        wounded = Unit("knt", job_id=2, hp=4, max_hp=14, atk=5, def_=4,
                        spd=2, team=1, x=1, y=0)
        enemy = Unit("slime", job_id=0, hp=12, max_hp=12, atk=5, def_=2,
                      spd=2, team=2, x=5, y=0)

        # Priest should heal wounded knight (4 < 14*0.5=7)
        sim.do_action(priest, [priest, wounded, enemy])
        assert wounded.hp == 8, \
            f"Expected heal to 8 (4+4), got {wounded.hp}"

    def test_heal_capped_at_max(self, cart):
        """Heal should not exceed max_hp."""
        sim = CombatSim(cart, rng_seed=42)
        priest = Unit("prt", job_id=4, hp=9, max_hp=9, atk=2, def_=3,
                       spd=4, team=1, x=0, y=0)
        slightly_wounded = Unit("sqr", job_id=1, hp=4, max_hp=10, atk=3,
                                 def_=2, spd=3, team=1, x=1, y=0)
        enemy = Unit("slime", job_id=0, hp=12, max_hp=12, atk=5, def_=2,
                      spd=2, team=2, x=5, y=0)

        sim.do_action(priest, [priest, slightly_wounded, enemy])
        assert slightly_wounded.hp <= slightly_wounded.max_hp, \
            f"Heal exceeded max HP: {slightly_wounded.hp}/{slightly_wounded.max_hp}"
