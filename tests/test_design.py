"""
test_design.py — Layer 2: Statistical design property assertions.

These tests use the shadow combat simulator to verify that design
choices produce measurable, intended effects. Each test runs hundreds
of simulated battles and asserts statistical properties.

Run: python3 -m pytest tests/test_design.py -v --tb=short
"""

import random
import os
import pytest
from tests.p8_parser import P8Cart
from tests.combat_sim import CombatSim, run_batch, win_rate, avg_ticks, avg_surviving_hp_pct

CART_PATH = os.path.join(os.path.dirname(__file__), "..", "spire_tactics.p8")
N_SIMS = 300  # Per test. Enough for ±5% confidence at p<0.05


@pytest.fixture
def cart():
    return P8Cart(CART_PATH)


# ============================================================
# D1: Positioning Impact
# "Placing mage in back row vs front row should measurably affect
#  mage survival rate."
# ============================================================

class TestPositioningImpact:
    def _make_backrow_setup(self, cart):
        """Mage at x=0 (back), knight at x=2 (front)."""
        def setup(sim, i):
            party = [
                sim.make_player_unit(2, x=2, y=1),   # knight front
                sim.make_player_unit(3, x=0, y=1),   # mage back
                sim.make_player_unit(4, x=0, y=2),   # priest back
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=2),  # goblin
                sim.make_enemy(3, x=4, y=1, floor=2),  # wolf (targets weak)
                sim.make_enemy(2, x=5, y=2, floor=2),  # goblin
            ]
            return party, enemies
        return setup

    def _make_frontrow_setup(self, cart):
        """Mage at x=4 (front), knight at x=0 (back — reversed)."""
        def setup(sim, i):
            party = [
                sim.make_player_unit(2, x=0, y=1),   # knight back
                sim.make_player_unit(3, x=4, y=1),   # mage front
                sim.make_player_unit(4, x=0, y=2),   # priest back
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=2),  # goblin
                sim.make_enemy(3, x=4, y=1, floor=2),  # wolf (targets weak)
                sim.make_enemy(2, x=5, y=2, floor=2),  # goblin
            ]
            return party, enemies
        return setup

    def test_mage_survives_more_in_backrow(self, cart):
        """Mage in back row should survive significantly more often
        than mage in front row.
        
        DESIGN RULE: Positioning must be meaningful. Squishy units
        (low HP/DEF) should benefit measurably from being placed
        behind tanky units.

        Threshold: >10% difference in mage survival rate.
        """
        back_results = run_batch(cart, self._make_backrow_setup(cart), N_SIMS, seed_base=1000)
        front_results = run_batch(cart, self._make_frontrow_setup(cart), N_SIMS, seed_base=2000)

        # Count mage survival (mage is index 1 in party)
        back_mage_survival = sum(
            1 for r in back_results if r.won and r.party[1].alive
        ) / max(1, sum(1 for r in back_results if r.won))
        front_mage_survival = sum(
            1 for r in front_results if r.won and r.party[1].alive
        ) / max(1, sum(1 for r in front_results if r.won))

        diff = back_mage_survival - front_mage_survival
        assert diff > 0.10, \
            f"Mage back-row survival {back_mage_survival:.1%} vs " \
            f"front-row {front_mage_survival:.1%} (diff {diff:.1%}). " \
            f"Positioning doesn't matter enough."


# ============================================================
# D2: Job Diversity
# "No single job composition should dominate all encounters."
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
                sim.make_enemy(enemy_ids[i % len(enemy_ids)], x=5, y=0, floor=2),
                sim.make_enemy(enemy_ids[(i+1) % len(enemy_ids)], x=4, y=1, floor=2),
                sim.make_enemy(enemy_ids[(i+2) % len(enemy_ids)], x=5, y=2, floor=2),
            ]
            return party, enemies
        return setup

    def test_no_mono_job_dominates_all(self, cart):
        """No single job used for all 3 units should have >85% win rate
        across diverse enemy matchups.
        
        DESIGN RULE: The game should incentivize mixed compositions.
        If 3x Knight beats everything, there's no reason to use Mage.
        """
        enemy_spread = [2, 3, 3, 4]  # goblin, wolf, wolf, ogre (wolf-heavy)
        best_job = None
        best_wr = 0
        results_by_job = {}

        for job_id in range(1, 5):
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
            f"Should be <85% to incentivize diversity. " \
            f"All results: {results_by_job}"

    def test_every_job_has_a_niche(self, cart):
        """Every job should improve team performance in at least one scenario.

        DESIGN RULE: If a job never contributes to a better outcome than
        substituting another job, it's a trap option. We test by comparing
        teams where one slot varies: does having each job in that slot
        ever produce the best win rate?
        """
        # Test: 2 squires + 1 variable slot vs mixed enemies
        enemy_comps = [
            [1, 1, 1],  # 3 slimes (easy, raw DPS matters)
            [3, 3, 3],  # 3 wolves (speed + assassin AI, need tank)
            [4, 4],     # 2 ogres (high ATK, need defense)
            [2, 3, 4],  # mixed (balanced)
            [1, 2, 1, 2],  # 4 weak enemies (sustained fight, healer value)
        ]
        job_best_counts = {j["name"]: 0 for j in cart.jobs}

        for eidx, eids in enumerate(enemy_comps):
            best_job = None
            best_wr = -1
            for job_id in range(1, 5):
                def setup(sim, i, jid=job_id, es=eids):
                    party = [
                        sim.make_player_unit(1, x=1, y=0),   # squire front
                        sim.make_player_unit(jid, x=0, y=1),  # variable slot
                        sim.make_player_unit(1, x=1, y=2),   # squire front
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

        # Every job should be the best choice in at least one scenario
        for job_name, count in job_best_counts.items():
            assert count >= 1, \
                f"Job '{job_name}' is never the best choice in any team " \
                f"composition scenario. It has no niche. Results: {job_best_counts}"


# ============================================================
# D3: Attrition Model
# "Multi-battle sequences without healing should leave party damaged."
# ============================================================

class TestAttrition:
    def test_hp_carries_between_fights(self, cart):
        """Running 3 battles in sequence without healing should result
        in lower HP than a single battle.
        
        DESIGN RULE: The node map only matters if battles cost resources
        that don't regenerate. HP attrition is the core tension.
        """
        def single_fight(sim, i):
            party = [
                sim.make_player_unit(1, x=0, y=0),
                sim.make_player_unit(2, x=1, y=1),
                sim.make_player_unit(4, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0),  # goblin
                sim.make_enemy(3, x=5, y=1),  # wolf (targets low HP)
            ]
            return party, enemies

        single_results = run_batch(cart, single_fight, N_SIMS, seed_base=5000)
        single_avg_hp = avg_surviving_hp_pct(single_results)

        # Simulate 3 consecutive battles (carry HP forward)
        multi_hp_totals = []
        for seed in range(N_SIMS):
            sim = CombatSim(cart, rng_seed=6000 + seed)
            party = [
                sim.make_player_unit(1, x=0, y=0),
                sim.make_player_unit(2, x=1, y=1),
                sim.make_player_unit(4, x=0, y=2),
            ]
            survived_all = True
            for battle in range(3):
                enemies = [
                    sim.make_enemy(2, x=5, y=0, floor=1),  # goblin
                    sim.make_enemy(3, x=5, y=1, floor=1),  # wolf
                ]
                # Reset positions and ATB, but NOT hp
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
        assert multi_avg_hp < single_avg_hp - 0.05, \
            f"After 3 battles, avg HP {multi_avg_hp:.1%} is not meaningfully " \
            f"lower than after 1 battle ({single_avg_hp:.1%}). " \
            f"Attrition isn't working."


# ============================================================
# D4: Speed Balance
# "High-speed teams should act first, but not auto-win."
# ============================================================

class TestSpeedBalance:
    def test_speed_advantage_is_bounded(self, cart):
        """A team with 2x speed should NOT have >95% win rate.
        
        DESIGN RULE: Speed is an advantage, not a win condition.
        If speed makes you act twice before the enemy, the fight
        is decided before damage/defense even matter.
        """
        # Fast team (mage+priest, spd=4)
        def fast_setup(sim, i):
            party = [
                sim.make_player_unit(3, x=0, y=0),  # mage spd4
                sim.make_player_unit(3, x=1, y=1),  # mage spd4
                sim.make_player_unit(4, x=0, y=2),  # priest spd4
            ]
            enemies = [
                sim.make_enemy(4, x=5, y=0, floor=2),  # ogre spd2
                sim.make_enemy(4, x=4, y=1, floor=2),  # ogre spd2
                sim.make_enemy(4, x=5, y=2, floor=2),  # ogre spd2
            ]
            return party, enemies

        results = run_batch(cart, fast_setup, N_SIMS, seed_base=7000)
        wr = win_rate(results)
        assert wr < 0.95, \
            f"3x fast (spd=4) vs 2x slow (spd=2) wins {wr:.1%}. " \
            f"Speed advantage is too dominant (should be <95%)."


# ============================================================
# D5: Relic Impact
# "Different relic stacks should produce measurably different outcomes."
# ============================================================

class TestRelicImpact:
    def _reliced_setup(self, cart, relic_stat, n_relics=3):
        relics = [r for r in cart.relics if r["stat_key"] == relic_stat]
        if not relics:
            return None
        relic_stack = relics * n_relics  # repeat to get enough

        def setup(sim, i):
            sim.relics = relic_stack[:n_relics]
            party = [
                sim.make_player_unit(1, x=0, y=0),
                sim.make_player_unit(2, x=1, y=1),
                sim.make_player_unit(4, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(3, x=5, y=0, floor=2),  # wolf
                sim.make_enemy(4, x=4, y=1, floor=2),  # ogre
                sim.make_enemy(3, x=5, y=2, floor=2),  # wolf
            ]
            return party, enemies
        return setup

    def test_atk_vs_def_relics_differ(self, cart):
        """Stacking 3 ATK relics vs 3 DEF relics should produce
        measurably different win rates (>5% difference).
        
        DESIGN RULE: Relic choices should create distinct builds
        with different strengths, not be interchangeable stat bumps.
        """
        atk_setup = self._reliced_setup(cart, "a")
        def_setup = self._reliced_setup(cart, "d")
        if not atk_setup or not def_setup:
            pytest.skip("Not enough relic variety")

        atk_results = run_batch(cart, atk_setup, N_SIMS, seed_base=8000)
        def_results = run_batch(cart, def_setup, N_SIMS, seed_base=8500)

        atk_wr = win_rate(atk_results)
        def_wr = win_rate(def_results)
        diff = abs(atk_wr - def_wr)
        assert diff > 0.05, \
            f"ATK relics WR {atk_wr:.1%} vs DEF relics WR {def_wr:.1%} " \
            f"(diff {diff:.1%}). Relics don't create distinct enough builds."


# ============================================================
# D6: Enemy Variety
# "Different enemies should be harder for different team comps."
# ============================================================

class TestEnemyMatchups:
    def test_wolf_harder_for_slow_teams(self, cart):
        """Wolves (high spd) should produce lower win rates for
        slow teams (knights, spd=2) than for fast teams (mages, spd=4).
        
        DESIGN RULE: Enemy stat profiles should create distinct
        tactical challenges, not just "bigger numbers."
        """
        def slow_vs_wolf(sim, i):
            party = [
                sim.make_player_unit(2, x=0, y=0),  # knight spd2
                sim.make_player_unit(2, x=1, y=1),
                sim.make_player_unit(2, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(3, x=5, y=0, floor=2),  # wolf
                sim.make_enemy(3, x=4, y=1, floor=2),
                sim.make_enemy(3, x=5, y=2, floor=2),
            ]
            return party, enemies

        def fast_vs_wolf(sim, i):
            party = [
                sim.make_player_unit(3, x=0, y=0),  # mage spd4
                sim.make_player_unit(3, x=1, y=1),
                sim.make_player_unit(3, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(3, x=5, y=0, floor=2),
                sim.make_enemy(3, x=4, y=1, floor=2),
                sim.make_enemy(3, x=5, y=2, floor=2),
            ]
            return party, enemies

        slow_results = run_batch(cart, slow_vs_wolf, N_SIMS, seed_base=9000)
        fast_results = run_batch(cart, fast_vs_wolf, N_SIMS, seed_base=9500)

        slow_wr = win_rate(slow_results)
        fast_wr = win_rate(fast_results)
        assert fast_wr > slow_wr + 0.05, \
            f"Fast team vs wolves: {fast_wr:.1%}, slow team: {slow_wr:.1%}. " \
            f"Wolf speed advantage should punish slow teams more."


# ============================================================
# D7: Campfire Balance
# "Neither campfire option should strictly dominate the other."
# ============================================================

class TestCampfireBalance:
    def test_heal_better_when_damaged(self, cart):
        """When party is heavily damaged, heal should be more valuable
        than upgrade for the next battle's win rate.
        
        DESIGN RULE: If upgrade always dominates, heal is a trap choice.
        Scenario: mixed enemy comp (gob+slime+wolf) at floor 1, where
        wolves bypass front row and punish low-HP units.
        """
        def damaged_healed_setup(sim, i):
            party = [
                sim.make_player_unit(1, x=0, y=0),
                sim.make_player_unit(2, x=1, y=1),
                sim.make_player_unit(4, x=0, y=2),
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=1),  # goblin
                sim.make_enemy(1, x=5, y=1, floor=1),  # slime
                sim.make_enemy(3, x=5, y=2, floor=1),  # wolf (targets low HP)
            ]
            return party, enemies

        def damaged_upgraded_setup(sim, i):
            party = [
                sim.make_player_unit(1, x=0, y=0),
                sim.make_player_unit(2, x=1, y=1),
                sim.make_player_unit(4, x=0, y=2),
            ]
            # 40% HP but +1 atk from upgrade
            for u in party:
                u.hp = max(1, int(u.max_hp * 0.4))
                u.atk += 1
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=1),
                sim.make_enemy(1, x=5, y=1, floor=1),
                sim.make_enemy(3, x=5, y=2, floor=1),
            ]
            return party, enemies

        healed_results = run_batch(cart, damaged_healed_setup, N_SIMS, seed_base=10000)
        upgraded_results = run_batch(cart, damaged_upgraded_setup, N_SIMS, seed_base=11000)

        healed_wr = win_rate(healed_results)
        upgraded_wr = win_rate(upgraded_results)

        # Heal should beat upgrade when damaged
        assert healed_wr > upgraded_wr, \
            f"When damaged to 40% HP: healed WR {healed_wr:.1%} vs " \
            f"upgraded WR {upgraded_wr:.1%}. Heal should win here."


# ============================================================
# D8: Boss Difficulty
# "Floor 3 boss should be challenging but beatable."
# ============================================================

class TestBossBalance:
    def test_boss_is_beatable(self, cart):
        """A well-composed party should beat the floor 3 boss
        at least 30% of the time.
        
        Realistic boss encounter: dragon + 2 wolves (the game spawns
        3-4 enemies for boss fights, not just 1).
        """
        def boss_setup(sim, i):
            party = [
                sim.make_player_unit(2, x=0, y=0, level=3),  # knight
                sim.make_player_unit(3, x=0, y=1, level=3),  # mage
                sim.make_player_unit(4, x=0, y=2, level=3),  # priest
            ]
            enemies = [
                sim.make_enemy(5, x=5, y=1, floor=3),  # dragon
                sim.make_enemy(3, x=4, y=0, floor=3),  # wolf
                sim.make_enemy(3, x=4, y=2, floor=3),  # wolf
            ]
            return party, enemies

        results = run_batch(cart, boss_setup, N_SIMS, seed_base=12000)
        wr = win_rate(results)
        assert wr >= 0.30, \
            f"Boss win rate {wr:.1%} is too low (should be ≥30%). " \
            f"Boss is overtuned or party is underleveled."

    def test_boss_is_not_trivial(self, cart):
        """Even a strong party should not beat the floor 3 boss
        more than 90% of the time.
        """
        def boss_setup(sim, i):
            party = [
                sim.make_player_unit(2, x=0, y=0, level=3),
                sim.make_player_unit(3, x=0, y=1, level=3),
                sim.make_player_unit(4, x=0, y=2, level=3),
            ]
            enemies = [
                sim.make_enemy(5, x=5, y=1, floor=3),
                sim.make_enemy(3, x=4, y=0, floor=3),
                sim.make_enemy(3, x=4, y=2, floor=3),
            ]
            return party, enemies

        results = run_batch(cart, boss_setup, N_SIMS, seed_base=12500)
        wr = win_rate(results)
        assert wr <= 0.90, \
            f"Boss win rate {wr:.1%} is too high (should be ≤90%). " \
            f"Boss is not threatening enough."


# ============================================================
# D9: Difficulty Curve — win rate narrows across floors
# "Floor 1 should be easy, floor 3 should be hard."
# ============================================================

class TestDifficultyCurve:
    def _floor_battle(self, cart, floor, enemy_ids, level=None):
        """Setup for a floor-appropriate encounter."""
        if level is None:
            level = floor
        def setup(sim, i, fl=floor, eids=enemy_ids, lv=level):
            party = [
                sim.make_player_unit(1, x=1, y=0, level=lv),  # squire front
                sim.make_player_unit(2, x=1, y=1, level=lv),  # knight front
                sim.make_player_unit(4, x=0, y=2, level=lv),  # priest back
            ]
            enemies = [
                sim.make_enemy(eids[j % len(eids)], x=5, y=j, floor=fl)
                for j in range(len(eids))
            ]
            return party, enemies
        return setup

    def test_floor1_is_welcoming(self, cart):
        """Floor 1 regular battle should have ≥80% win rate.

        DESIGN RULE: The first floor teaches the player. Losing on
        the first fight feels unfair and drives players away.
        """
        setup = self._floor_battle(cart, floor=1, enemy_ids=[1, 2], level=1)
        results = run_batch(cart, setup, N_SIMS, seed_base=20000)
        wr = win_rate(results)
        assert wr >= 0.80, \
            f"Floor 1 win rate {wr:.1%} is too low (should be ≥80%). " \
            f"First floor should be welcoming."

    def test_floor2_is_challenging(self, cart):
        """Floor 2 encounters should have 40-85% win rate (with level-ups).

        DESIGN RULE: Floor 2 is the mid-game. Fights should feel
        winnable but costly. The player should feel attrition building.
        """
        setup = self._floor_battle(cart, floor=2, enemy_ids=[2, 3, 2], level=2)
        results = run_batch(cart, setup, N_SIMS, seed_base=21000)
        wr = win_rate(results)
        assert 0.40 <= wr <= 0.85, \
            f"Floor 2 win rate {wr:.1%} is outside 40-85% range. " \
            f"Mid-game should be challenging but not brutal."

    def test_difficulty_increases_per_floor(self, cart):
        """Win rate should decrease from floor 1 to floor 2 to floor 3.

        DESIGN RULE: The narrowing funnel is what makes a roguelike.
        If later floors aren't harder, there's no tension.
        """
        wrs = []
        for fl in [1, 2, 3]:
            eids = {1: [1, 2], 2: [2, 3, 2], 3: [3, 4, 3]}[fl]
            setup = self._floor_battle(cart, floor=fl, enemy_ids=eids, level=fl)
            results = run_batch(cart, setup, N_SIMS, seed_base=22000 + fl * 100)
            wrs.append(win_rate(results))

        assert wrs[0] > wrs[1], \
            f"Floor 1 WR ({wrs[0]:.1%}) should exceed floor 2 ({wrs[1]:.1%})"
        assert wrs[1] > wrs[2], \
            f"Floor 2 WR ({wrs[1]:.1%}) should exceed floor 3 ({wrs[2]:.1%})"


# ============================================================
# D10: Smart Play Advantage
# "Good tactical decisions should produce measurably better outcomes."
# ============================================================

class TestSmartPlayAdvantage:
    def test_good_comp_beats_random_comp(self, cart):
        """A smart team composition (tank front, healer back) should
        beat a random composition by ≥10% win rate.

        DESIGN RULE: If good decisions don't help, the game has no
        skill expression. Players should be rewarded for thinking.
        """
        # Smart: knight front, mage mid, priest back
        def smart_setup(sim, i):
            party = [
                sim.make_player_unit(2, x=2, y=1),   # knight front
                sim.make_player_unit(3, x=0, y=0),   # mage back
                sim.make_player_unit(4, x=0, y=2),   # priest back
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=2),
                sim.make_enemy(3, x=4, y=1, floor=2),
                sim.make_enemy(2, x=5, y=2, floor=2),
            ]
            return party, enemies

        # Random: all squires, bad positions
        def random_setup(sim, i):
            import random as rng
            rng.seed(30000 + i)
            jobs = [rng.randint(1, 4) for _ in range(3)]
            party = [
                sim.make_player_unit(jobs[0], x=rng.randint(0, 2), y=0),
                sim.make_player_unit(jobs[1], x=rng.randint(0, 2), y=1),
                sim.make_player_unit(jobs[2], x=rng.randint(0, 2), y=2),
            ]
            enemies = [
                sim.make_enemy(2, x=5, y=0, floor=2),
                sim.make_enemy(3, x=4, y=1, floor=2),
                sim.make_enemy(2, x=5, y=2, floor=2),
            ]
            return party, enemies

        smart_results = run_batch(cart, smart_setup, N_SIMS, seed_base=31000)
        random_results = run_batch(cart, random_setup, N_SIMS, seed_base=32000)

        smart_wr = win_rate(smart_results)
        random_wr = win_rate(random_results)

        assert smart_wr > random_wr + 0.10, \
            f"Smart comp WR {smart_wr:.1%} vs random comp {random_wr:.1%} " \
            f"(diff {smart_wr - random_wr:.1%}). Good decisions should " \
            f"matter more (≥10% advantage)."
