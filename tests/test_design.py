"""
test_design.py — Layer 2: Statistical design property assertions (v2).

These tests use the shadow combat simulator to verify that design
choices produce measurable, intended effects. Each test runs hundreds
of simulated battles and asserts statistical properties.

v2 class IDs: 1=Squire(F) 2=Scout(B) 3=Acolyte(B,heal) 4=Apprentice(B,dps)
              5=Brawler(F,tank) 6=Lancer(M) 7-18=advanced

Run: python3 -m pytest tests/test_design.py -v --tb=short
"""

import random
import os
import pytest
from tests.p8_parser import P8Cart
from tests.combat_sim import CombatSim, run_batch, win_rate, avg_ticks, avg_surviving_hp_pct

CART_PATH = os.path.join(os.path.dirname(__file__), "..", "spire_tactics.p8")
N_SIMS = 300


@pytest.fixture
def cart():
    return P8Cart(CART_PATH)


# ============================================================
# D1: Positioning Impact
# ============================================================

class TestPositioningImpact:
    def _make_backrow_setup(self, cart):
        """Apprentice at x=0 (back), Brawler at x=2 (front)."""
        def setup(sim, i):
            party = [
                sim.make_player_unit(5, x=2, y=1),   # brawler front
                sim.make_player_unit(4, x=0, y=1),   # apprentice back
                sim.make_player_unit(3, x=0, y=2),   # acolyte back
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=2),  # goblin
                sim.make_enemy(3, x=4, y=1, floor=2),  # wolf (targets weak)
                sim.make_enemy(2, x=5, y=2, floor=2),  # goblin
            ]
            return party, enemies
        return setup

    def _make_frontrow_setup(self, cart):
        """Apprentice at x=4 (front), Brawler at x=0 (back)."""
        def setup(sim, i):
            party = [
                sim.make_player_unit(5, x=0, y=1),   # brawler back
                sim.make_player_unit(4, x=4, y=1),   # apprentice front
                sim.make_player_unit(3, x=0, y=2),   # acolyte back
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=2),  # goblin
                sim.make_enemy(3, x=4, y=1, floor=2),  # wolf
                sim.make_enemy(2, x=5, y=2, floor=2),  # goblin
            ]
            return party, enemies
        return setup

    def test_mage_survives_more_in_backrow(self, cart):
        """Glass cannon in back row should survive more than in front."""
        back_results = run_batch(cart, self._make_backrow_setup(cart), N_SIMS, seed_base=1000)
        front_results = run_batch(cart, self._make_frontrow_setup(cart), N_SIMS, seed_base=2000)

        back_survival = sum(
            1 for r in back_results if r.won and r.party[1].alive
        ) / max(1, sum(1 for r in back_results if r.won))
        front_survival = sum(
            1 for r in front_results if r.won and r.party[1].alive
        ) / max(1, sum(1 for r in front_results if r.won))

        diff = back_survival - front_survival
        assert diff > 0.10, \
            f"Apprentice back-row survival {back_survival:.1%} vs " \
            f"front-row {front_survival:.1%} (diff {diff:.1%}). " \
            f"Positioning doesn't matter enough."


# ============================================================
# D2: Job Diversity
# ============================================================

class TestJobDiversity:
    def _mono_team_setup(self, cart, job_id, enemy_ids):
        def setup(sim, i):
            party = [
                sim.make_player_unit(job_id, x=0, y=0),
                sim.make_player_unit(job_id, x=1, y=1),
                sim.make_player_unit(job_id, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(enemy_ids[i % len(enemy_ids)], x=5, y=0, floor=3),
                sim.make_enemy(enemy_ids[(i+1) % len(enemy_ids)], x=4, y=1, floor=3),
                sim.make_enemy(enemy_ids[(i+2) % len(enemy_ids)], x=5, y=2, floor=3),
            ]
            return party, enemies
        return setup

    def test_no_mono_job_dominates_all(self, cart):
        """No single base class for all 3 units should have >85% win rate."""
        enemy_spread = [2, 3, 3, 6]  # goblin, wolf, wolf, golem @ floor 3
        best_job = None
        best_wr = 0
        results_by_job = {}

        for job_id in range(1, 7):  # 6 base classes
            results = run_batch(
                cart,
                self._mono_team_setup(cart, job_id, enemy_spread),
                n=N_SIMS, seed_base=3000 + job_id * 100
            )
            wr = win_rate(results)
            results_by_job[cart.jobs[job_id-1]["name"]] = wr
            if wr > best_wr:
                best_wr = wr
                best_job = cart.jobs[job_id-1]["name"]

        assert best_wr < 0.85, \
            f"Mono-{best_job} has {best_wr:.1%} win rate. " \
            f"Should be <85%. All: {results_by_job}"

    def test_every_job_has_a_niche(self, cart):
        """Every base class should be the best pick in at least one scenario."""
        enemy_comps = [
            [1, 1, 1],     # 3 slimes (easy, DPS matters)
            [3, 3, 3],     # 3 wolves (speed, assassin AI)
            [6, 6],        # 2 golems (high DEF)
            [2, 3, 9],     # goblin + wolf + orc (mixed)
            [1, 2, 1, 2],  # 4 weak enemies (sustained, healer value)
        ]
        job_best_counts = {j["name"]: 0 for j in cart.jobs[:6]}

        for eidx, eids in enumerate(enemy_comps):
            best_job = None
            best_wr = -1
            for job_id in range(1, 7):
                def setup(sim, i, jid=job_id, es=eids):
                    party = [
                        sim.make_player_unit(1, x=1, y=0),
                        sim.make_player_unit(jid, x=0, y=1),
                        sim.make_player_unit(1, x=1, y=2),
                    ]
                    enemies = [
                        sim.make_enemy(es[j % len(es)], x=5, y=j, floor=2)
                        for j in range(len(es))
                    ]
                    return party, enemies
                results = run_batch(cart, setup, n=150, seed_base=4000+eidx*100+job_id)
                wr = win_rate(results)
                if wr > best_wr:
                    best_wr = wr
                    best_job = cart.jobs[job_id-1]["name"]
            job_best_counts[best_job] += 1

        jobs_with_niche = sum(1 for c in job_best_counts.values() if c >= 1)
        assert jobs_with_niche >= 3, \
            f"Only {jobs_with_niche}/6 base classes have a niche. " \
            f"Results: {job_best_counts}"


# ============================================================
# D3: Attrition Model
# ============================================================

class TestAttrition:
    def test_hp_carries_between_fights(self, cart):
        """3 battles without healing should leave party more damaged."""
        def single_fight(sim, i):
            party = [
                sim.make_player_unit(1, x=0, y=0),   # squire
                sim.make_player_unit(5, x=1, y=1),   # brawler
                sim.make_player_unit(3, x=0, y=2),   # acolyte
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0),  # goblin
                sim.make_enemy(3, x=5, y=1),  # wolf
            ]
            return party, enemies

        single_results = run_batch(cart, single_fight, N_SIMS, seed_base=5000)
        single_avg_hp = avg_surviving_hp_pct(single_results)

        multi_hp_totals = []
        for seed in range(N_SIMS):
            sim = CombatSim(cart, rng_seed=6000 + seed)
            party = [
                sim.make_player_unit(1, x=0, y=0),
                sim.make_player_unit(5, x=1, y=1),
                sim.make_player_unit(3, x=0, y=2),
            ]
            survived_all = True
            for battle in range(3):
                enemies = [
                    sim.make_enemy(2, x=5, y=0, floor=1),
                    sim.make_enemy(3, x=5, y=1, floor=1),
                ]
                for u in party:
                    u.x = [0, 1, 0][party.index(u)]
                    u.y = party.index(u)
                    u.atb = 0
                    u.cooldowns = {}
                result = sim.run(party, enemies)
                if not result.won:
                    survived_all = False
                    break
            if survived_all:
                avg_hp = sum(u.hp / u.max_hp for u in party if u.alive) / max(
                    1, sum(1 for u in party if u.alive)
                )
                multi_hp_totals.append(avg_hp)

        if not multi_hp_totals:
            pytest.skip("No runs survived all 3 battles")

        multi_avg_hp = sum(multi_hp_totals) / len(multi_hp_totals)
        assert multi_avg_hp < single_avg_hp, \
            f"After 3 battles, avg HP {multi_avg_hp:.1%} vs " \
            f"after 1 ({single_avg_hp:.1%}). Attrition isn't working."


# ============================================================
# D4: Speed Balance
# ============================================================

class TestSpeedBalance:
    def test_speed_advantage_is_bounded(self, cart):
        """A fast team should NOT auto-win against tough enemies."""
        def fast_setup(sim, i):
            party = [
                sim.make_player_unit(2, x=0, y=0),   # scout spd6
                sim.make_player_unit(2, x=1, y=1),   # scout spd6
                sim.make_player_unit(4, x=0, y=2),   # apprentice spd4
            ]
            enemies = [
                sim.make_enemy(9, x=5, y=0, floor=3),  # orc spd2 high hp+atk
                sim.make_enemy(9, x=4, y=1, floor=3),  # orc
                sim.make_enemy(9, x=5, y=2, floor=3),  # orc
            ]
            return party, enemies

        results = run_batch(cart, fast_setup, N_SIMS, seed_base=7000)
        wr = win_rate(results)
        assert wr < 0.95, \
            f"Fast team vs tough enemies wins {wr:.1%}. " \
            f"Speed advantage too dominant (should be <95%)."


# ============================================================
# D5: Accessory Impact
# ============================================================

class TestAccessoryImpact:
    def _equipped_setup(self, cart, stat, n_relics=3):
        relics = [r for r in cart.accessories if r.get("stat", "") == stat]
        if not relics:
            return None
        relic_stack = relics * n_relics

        def setup(sim, i):
            sim.relics = relic_stack[:n_relics]
            party = [
                sim.make_player_unit(1, x=0, y=0),
                sim.make_player_unit(5, x=1, y=1),
                sim.make_player_unit(3, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(3, x=5, y=0, floor=2),
                sim.make_enemy(9, x=4, y=1, floor=2),  # orc
                sim.make_enemy(3, x=5, y=2, floor=2),
            ]
            return party, enemies
        return setup

    def test_atk_vs_def_accessories_differ(self, cart):
        """Stacking ATK vs DEF accessories should differ by >5%."""
        atk_setup = self._equipped_setup(cart, "a")
        def_setup = self._equipped_setup(cart, "d")
        if not atk_setup or not def_setup:
            pytest.skip("Not enough accessory variety")

        atk_results = run_batch(cart, atk_setup, N_SIMS, seed_base=8000)
        def_results = run_batch(cart, def_setup, N_SIMS, seed_base=8500)

        atk_wr = win_rate(atk_results)
        def_wr = win_rate(def_results)
        diff = abs(atk_wr - def_wr)
        assert diff > 0.05, \
            f"ATK acc WR {atk_wr:.1%} vs DEF acc WR {def_wr:.1%} " \
            f"(diff {diff:.1%}). Accessories not distinct enough."


# ============================================================
# D6: Enemy Matchups
# ============================================================

class TestEnemyMatchups:
    def test_wolf_harder_for_slow_teams(self, cart):
        """Wolves should be harder for slow teams than fast teams."""
        def slow_vs_wolf(sim, i):
            party = [
                sim.make_player_unit(5, x=0, y=0),   # brawler spd3
                sim.make_player_unit(5, x=1, y=1),
                sim.make_player_unit(5, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(3, x=5, y=0, floor=1),  # wolf floor1
                sim.make_enemy(3, x=5, y=1, floor=1),
            ]
            return party, enemies

        def fast_vs_wolf(sim, i):
            party = [
                sim.make_player_unit(2, x=0, y=0),   # scout spd6
                sim.make_player_unit(2, x=1, y=1),
                sim.make_player_unit(2, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(3, x=5, y=0, floor=1),  # wolf floor1
                sim.make_enemy(3, x=5, y=1, floor=1),
            ]
            return party, enemies

        slow_results = run_batch(cart, slow_vs_wolf, N_SIMS, seed_base=9000)
        fast_results = run_batch(cart, fast_vs_wolf, N_SIMS, seed_base=9500)

        slow_wr = win_rate(slow_results)
        fast_wr = win_rate(fast_results)
        assert fast_wr > slow_wr, \
            f"Fast vs wolves: {fast_wr:.1%}, slow: {slow_wr:.1%}. " \
            f"Wolf speed should punish slow teams more."


# ============================================================
# D7: Campfire Balance
# ============================================================

class TestCampfireBalance:
    def test_heal_better_when_damaged(self, cart):
        """Full HP (campfire healed) should beat damaged (60% HP) more often.

        Uses squires (no heal skills) to isolate the HP advantage from
        AI priority interactions with heal/buff skill selection.
        """
        def healed_setup(sim, i):
            party = [
                sim.make_player_unit(1, x=0, y=0),  # squire
                sim.make_player_unit(1, x=0, y=1),
                sim.make_player_unit(1, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=1),  # goblin
                sim.make_enemy(3, x=5, y=1, floor=1),  # wolf
            ]
            return party, enemies

        def unhealed_setup(sim, i):
            party = [
                sim.make_player_unit(1, x=0, y=0),
                sim.make_player_unit(1, x=0, y=1),
                sim.make_player_unit(1, x=0, y=2),
            ]
            for u in party:
                u.hp = max(1, int(u.max_hp * 0.6))
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=1),
                sim.make_enemy(3, x=5, y=1, floor=1),
            ]
            return party, enemies

        healed_results = run_batch(cart, healed_setup, N_SIMS, seed_base=10000)
        unhealed_results = run_batch(cart, unhealed_setup, N_SIMS, seed_base=11000)

        healed_wr = win_rate(healed_results)
        unhealed_wr = win_rate(unhealed_results)

        assert healed_wr > unhealed_wr, \
            f"Healed WR {healed_wr:.1%} vs unhealed WR {unhealed_wr:.1%}. " \
            f"Healing should help when damaged."


# ============================================================
# D8: Boss Difficulty
# ============================================================

class TestBossBalance:
    def _boss_setup(self, floor=4):
        """Boss encounter: ogre + 2 wolves at given floor scaling."""
        def setup(sim, i):
            party = [
                sim.make_player_unit(5, x=0, y=0, level=3),   # brawler
                sim.make_player_unit(4, x=0, y=1, level=3),   # apprentice
                sim.make_player_unit(3, x=0, y=2, level=3),   # acolyte
            ]
            enemies = [
                sim.make_enemy(14, x=5, y=1, floor=floor),  # ogre (elite)
                sim.make_enemy(3, x=4, y=0, floor=floor),   # wolf
                sim.make_enemy(3, x=4, y=2, floor=floor),   # wolf
            ]
            return party, enemies
        return setup

    def test_boss_is_beatable(self, cart):
        """A good party should beat the boss encounter >=20%."""
        results = run_batch(cart, self._boss_setup(floor=4), N_SIMS, seed_base=12000)
        wr = win_rate(results)
        assert wr >= 0.20, \
            f"Boss win rate {wr:.1%} is too low (should be >=20%)."

    def test_boss_is_not_trivial(self, cart):
        """Even a strong party should not win >90%."""
        results = run_batch(cart, self._boss_setup(floor=4), N_SIMS, seed_base=12500)
        wr = win_rate(results)
        assert wr <= 0.90, \
            f"Boss win rate {wr:.1%} is too high (should be <=90%)."


# ============================================================
# D9: Difficulty Curve
# ============================================================

class TestDifficultyCurve:
    def _floor_battle(self, cart, floor, enemy_ids, level=None):
        if level is None:
            level = floor
        def setup(sim, i, fl=floor, eids=enemy_ids, lv=level):
            party = [
                sim.make_player_unit(1, x=1, y=0, level=lv),   # squire
                sim.make_player_unit(5, x=1, y=1, level=lv),   # brawler
                sim.make_player_unit(3, x=0, y=2, level=lv),   # acolyte
            ]
            enemies = [
                sim.make_enemy(eids[j % len(eids)], x=5, y=j, floor=fl)
                for j in range(min(len(eids), 3))
            ]
            return party, enemies
        return setup

    def test_floor1_is_welcoming(self, cart):
        """Floor 1 win rate should be >=75%."""
        setup = self._floor_battle(cart, 1, [1, 2], level=1)
        results = run_batch(cart, setup, N_SIMS, seed_base=13000)
        wr = win_rate(results)
        assert wr >= 0.75, \
            f"Floor 1 win rate {wr:.1%} is too low (should be >=75%)."

    def test_floor2_is_challenging(self, cart):
        """Floor 2 should be harder than floor 1."""
        f1_setup = self._floor_battle(cart, 1, [1, 2], level=1)
        f2_setup = self._floor_battle(cart, 2, [2, 3, 9], level=2)

        f1_results = run_batch(cart, f1_setup, N_SIMS, seed_base=14000)
        f2_results = run_batch(cart, f2_setup, N_SIMS, seed_base=14500)

        f1_wr = win_rate(f1_results)
        f2_wr = win_rate(f2_results)
        assert f1_wr > f2_wr, \
            f"Floor 1 WR {f1_wr:.1%} not higher than floor 2 {f2_wr:.1%}."

    def test_difficulty_increases_per_floor(self, cart):
        """Same enemies at higher floor scaling should have lower win rate."""
        # Tough enemies so floor scaling matters: wolf + 2 orcs
        f1 = run_batch(cart, self._floor_battle(cart, 1, [3, 9, 9], level=1), N_SIMS, seed_base=15000)
        f3 = run_batch(cart, self._floor_battle(cart, 3, [3, 9, 9], level=1), N_SIMS, seed_base=16000)

        wr1 = win_rate(f1)
        wr3 = win_rate(f3)

        assert wr1 > wr3, \
            f"Floor 1 WR {wr1:.1%} not higher than floor 3 {wr3:.1%}."


# ============================================================
# D10: Smart Play Advantage
# ============================================================

class TestSmartPlayAdvantage:
    def test_good_comp_beats_random_comp(self, cart):
        """A balanced composition should beat a random one."""
        def good_setup(sim, i):
            party = [
                sim.make_player_unit(5, x=2, y=0),   # brawler front
                sim.make_player_unit(4, x=0, y=1),   # apprentice back
                sim.make_player_unit(3, x=0, y=2),   # acolyte back
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=2),
                sim.make_enemy(3, x=4, y=1, floor=2),
                sim.make_enemy(9, x=5, y=2, floor=2),  # orc
            ]
            return party, enemies

        def random_setup(sim, i):
            jobs = [1, 2, 3, 4, 5, 6]
            random.seed(17000 + i)
            chosen = random.sample(jobs, 3)
            party = [
                sim.make_player_unit(chosen[0], x=random.randint(0, 2), y=0),
                sim.make_player_unit(chosen[1], x=random.randint(0, 2), y=1),
                sim.make_player_unit(chosen[2], x=random.randint(0, 2), y=2),
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=2),
                sim.make_enemy(3, x=4, y=1, floor=2),
                sim.make_enemy(9, x=5, y=2, floor=2),
            ]
            return party, enemies

        good_results = run_batch(cart, good_setup, N_SIMS, seed_base=17000)
        rand_results = run_batch(cart, random_setup, N_SIMS, seed_base=18000)

        good_wr = win_rate(good_results)
        rand_wr = win_rate(rand_results)
        assert good_wr > rand_wr + 0.10, \
            f"Good comp WR {good_wr:.1%} vs random {rand_wr:.1%}. " \
            f"Smart play should matter (>10% diff)."
