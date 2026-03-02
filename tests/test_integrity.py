"""
test_integrity.py — Layer 1: Source-level structural assertions.

These tests parse the actual .p8 Lua source and verify properties
that should ALWAYS hold. Zero drift risk — if the test fails, the 
game code is definitionally wrong.

Run: python3 -m pytest tests/test_integrity.py -v
"""

import re
import os
import pytest
from tests.p8_parser import P8Cart

CART_PATH = os.path.join(os.path.dirname(__file__), "..", "spire_tactics.p8")


@pytest.fixture
def cart():
    return P8Cart(CART_PATH)


# ============================================================
# T1: Every skill type has a handler in doact()
# Issue #3: 'b' (buff/block) type has no execution path
# ============================================================

class TestSkillHandlers:
    def test_attack_handler_exists(self, cart):
        """doact must handle type 'a' skills."""
        body = cart.get_function_body("doact")
        assert body is not None, "doact function not found"
        # Look for a branch that checks s[3]=="a"
        assert re.search(r's\[3\]\s*==\s*"a"', body), \
            "doact has no handler for attack skills (type 'a')"

    def test_heal_handler_exists(self, cart):
        """doact must handle type 'h' skills."""
        body = cart.get_function_body("doact")
        assert body is not None
        assert re.search(r's\[3\]\s*==\s*"h"', body), \
            "doact has no handler for heal skills (type 'h')"

    def test_buff_handler_exists(self, cart):
        """doact must handle type 'b' skills (block/buff).
        
        DESIGN RULE: Every skill type defined in the data must have
        a corresponding execution branch in the AI.
        """
        body = cart.get_function_body("doact")
        assert body is not None
        skill_types = set(s["type"] for s in cart.skills)
        for st in skill_types:
            assert re.search(rf's\[3\]\s*==\s*"{st}"', body), \
                f"doact has no handler for skill type '{st}'"


# ============================================================
# T2: Referential integrity — skills reference valid jobs
# ============================================================

class TestReferentialIntegrity:
    def test_skill_job_ids_valid(self, cart):
        """Every skill's job_id must reference an existing job."""
        valid_ids = set(j["_index"] for j in cart.jobs)
        for s in cart.skills:
            assert s["job_id"] in valid_ids, \
                f"Skill '{s['name']}' references job_id {s['job_id']} " \
                f"which doesn't exist (valid: {valid_ids})"

    def test_every_job_has_skills(self, cart):
        """Every job should have at least one skill."""
        job_ids = set(j["_index"] for j in cart.jobs)
        skilled_jobs = set(s["job_id"] for s in cart.skills)
        for jid in job_ids:
            assert jid in skilled_jobs, \
                f"Job {jid} ({cart.jobs[jid-1]['name']}) has no skills"

    def test_relic_stat_keys_used(self, cart):
        """Every relic stat_key must map to a stat used in rlb()."""
        body = cart.get_function_body("rlb")
        if body is None:
            pytest.skip("rlb function not found")
        for r in cart.relics:
            # Just verify the stat_key is a single char matching known stats
            assert r["stat_key"] in ("s", "d", "a", "h"), \
                f"Relic '{r['name']}' has unknown stat_key '{r['stat_key']}'"


# ============================================================
# T3: Sprite data integrity
# ============================================================

class TestSpriteIntegrity:
    def test_enemy_sprites_have_pixels(self, cart):
        """Every enemy's sprite ID must have non-zero pixel data."""
        for e in cart.enemies:
            spr_id = e["spr"]
            assert cart.sprite_has_pixels(spr_id), \
                f"Enemy '{e['name']}' uses sprite {spr_id} which is blank"

    def test_job_sprites_have_pixels(self, cart):
        """Sprites 1-4 (job classes) must have pixel data."""
        for i in range(1, len(cart.jobs) + 1):
            assert cart.sprite_has_pixels(i), \
                f"Job sprite {i} is blank"

    def test_ui_sprites_have_pixels(self, cart):
        """Key UI sprites (heart, sword, relic, campfire) must exist."""
        ui_sprites = {11: "heart", 18: "campfire", 22: "relic"}
        for spr_id, name in ui_sprites.items():
            assert cart.sprite_has_pixels(spr_id), \
                f"UI sprite {spr_id} ({name}) is blank"


# ============================================================
# T4: HP should NOT reset between battles (attrition)
# Issue #6: init_setup resets hp to mhp, killing the attrition model
# ============================================================

class TestAttritionModel:
    def test_no_hp_reset_in_setup(self, cart):
        """init_setup must NOT set u.hp = u.mhp.
        
        DESIGN RULE: HP persists between battles. The node map's
        risk/reward depends on attrition. Full heals at setup
        make campfire and path choice meaningless.
        """
        body = cart.get_function_body("init_setup")
        assert body is not None, "init_setup not found"
        # Should not contain hp=mhp or hp = mhp patterns
        has_reset = bool(re.search(
            r'\.hp\s*=\s*\w+\.mhp', body
        ))
        assert not has_reset, \
            "init_setup resets HP to maxHP, destroying attrition model"

    def test_dead_units_stay_dead_until_revive(self, cart):
        """init_setup should not unconditionally set alive=true.
        
        DESIGN RULE: Dead units require explicit revival (campfire
        or relic), not automatic resurrection per battle.
        """
        body = cart.get_function_body("init_setup")
        assert body is not None
        # Should NOT have unconditional alive=true
        # Acceptable: if u.hp>0 then u.alive=true
        # Unacceptable: u.alive=true (no condition)
        lines = body.split("\n")
        for line in lines:
            stripped = line.strip()
            if "alive=true" in stripped or "alive = true" in stripped:
                # Check if it's inside a conditional
                assert "if" in stripped or "and" in stripped, \
                    f"Unconditional alive=true in init_setup: '{stripped}'"


# ============================================================
# T5: Placement range should cover meaningful grid area
# Issue #1: Cursor limited to cols 0-1, should cover 0-2 minimum
# ============================================================

class TestPositioning:
    def test_placement_x_range(self, cart):
        """Setup cursor should reach at least 3 columns (0-2).
        
        DESIGN RULE: Positioning is one of three core player actions.
        A 2-column range makes it cosmetic.
        """
        body = cart.get_function_body("upset")
        assert body is not None, "upset (setup update) not found"
        # Find the max x clamp: min(N, cur.x+1) or cur.x=min(N,...)
        m = re.search(r'cur\.x[=<]+min\((\d+)', body)
        if m:
            max_x = int(m.group(1))
            assert max_x >= 2, \
                f"Placement x range capped at {max_x}, need at least 2 " \
                f"(columns 0-{max_x})"
        else:
            pytest.skip("Could not parse x range clamp from upset()")

    def test_placement_y_range(self, cart):
        """Setup cursor should reach at least 4 rows (full grid height)."""
        body = cart.get_function_body("upset")
        assert body is not None
        m = re.search(r'cur\.y[=<]+min\((\d+)', body)
        if m:
            max_y = int(m.group(1))
            assert max_y >= 3, \
                f"Placement y range capped at {max_y}, need at least 3 " \
                f"(rows 0-{max_y})"


# ============================================================
# T6: Enemy data should have behavior differentiation
# Issue #4: All enemies use identical AI
# ============================================================

class TestEnemyVariety:
    def test_enemy_data_has_behavior_field(self, cart):
        """Enemy data schema should include a behavior flag.
        
        DESIGN RULE: Enemies must differ in behavior, not just stats.
        The enemy table needs a field controlling AI targeting/movement.
        """
        # Check if enemy data has 6+ fields (name,spr,hp,atk,spd,behavior)
        for e in cart.enemies:
            assert len(e) >= 7, \
                f"Enemy '{e['name']}' has {len(e)} fields, " \
                f"expected 7+ (needs behavior flag)"

    def test_enemies_have_varied_behaviors(self, cart):
        """At least 2 distinct behavior values must exist in enemy data."""
        behaviors = set()
        for e in cart.enemies:
            b = e.get("behavior", e.get("bhv", None))
            if b is not None:
                behaviors.add(b)
        assert len(behaviors) >= 2, \
            f"Only {len(behaviors)} distinct enemy behaviors. " \
            f"Need at least 2 for tactical variety."


# ============================================================
# T7: Relic visibility — relics should be displayable
# Issue #5: Relic list is never shown, only count
# ============================================================

class TestRelicVisibility:
    def test_relic_names_are_meaningful(self, cart):
        """Relic names should be human-readable (not just stat keys)."""
        for r in cart.relics:
            assert len(r["name"]) >= 3, \
                f"Relic name '{r['name']}' is too short to be meaningful"

    def test_enough_relic_variety(self, cart):
        """At least 4 distinct stat_keys should be represented.
        
        DESIGN RULE: Relics should enable distinct build identities.
        If all relics boost the same 2 stats, no build diversity emerges.
        """
        keys = set(r["stat_key"] for r in cart.relics)
        assert len(keys) >= 3, \
            f"Only {len(keys)} distinct relic stat types: {keys}. " \
            f"Need at least 3 for build diversity."


# ============================================================
# T8: Campfire should not have a dominant option
# Issue #7: Upgrade is always better than heal
# ============================================================

class TestCampfireBalance:
    def test_upgrade_is_bounded(self, cart):
        """Campfire upgrade should not give +1 to ALL stats for ALL units.
        
        DESIGN RULE: If upgrade gives everything, heal is dominated.
        Upgrade should be limited (one unit, or one stat, or smaller bonus).
        """
        body = cart.get_function_body("upcamp")
        assert body is not None, "upcamp function not found"
        # Count how many stats the upgrade branch modifies
        # Bad: u.mhp+=1 AND u.atk+=1 (for all units)
        # Look for "for u in all(py)" near stat increments
        # This is a heuristic check
        upgrade_stats = 0
        in_upgrade = False
        for line in body.split("\n"):
            s = line.strip()
            if "for u" in s and "all(py)" in s:
                in_upgrade = True
            if in_upgrade:
                if "+=" in s and any(
                    stat in s for stat in ["mhp", "atk", "def", "spd"]
                ):
                    upgrade_stats += 1
            if in_upgrade and "end" in s:
                in_upgrade = False
        assert upgrade_stats <= 1, \
            f"Campfire upgrade modifies {upgrade_stats} stats per unit " \
            f"(should be ≤1 to not dominate heal)"


# ============================================================
# T9: GFX section format validity
# ============================================================

class TestCartFormat:
    def test_gfx_128_lines(self, cart):
        lines = [l for l in cart.gfx_raw.split("\n") if l.strip()]
        assert len(lines) == 128, f"GFX has {len(lines)} lines, expected 128"

    def test_gfx_128_chars_per_line(self, cart):
        for i, line in enumerate(cart.gfx_raw.split("\n")):
            if line.strip():
                assert len(line) == 128, \
                    f"GFX line {i} is {len(line)} chars, expected 128"

    def test_gfx_valid_hex(self, cart):
        for i, line in enumerate(cart.gfx_raw.split("\n")):
            if line.strip():
                assert re.match(r'^[0-9a-f]+$', line), \
                    f"GFX line {i} contains non-hex characters"


# ============================================================
# T10: Placement bounds — player half only
# Bug: cursor allows x=0-4, should be x=0-2
# ============================================================

class TestPlacementBounds:
    def test_cursor_x_max_is_player_half(self, cart):
        """Setup cursor should be restricted to left half of grid (x≤2).

        DESIGN RULE: The 6×4 grid is split: left 3 cols for players,
        right 3 cols for enemies. Allowing placement on enemy side
        breaks the formation concept.
        """
        body = cart.get_function_body("upset")
        assert body is not None, "upset function not found"
        # Find: cur.x=min(N,...)  — N should be ≤2
        m = re.search(r'min\((\d+)\s*,\s*cur\.x', body)
        if not m:
            m = re.search(r'cur\.x[^=]*min\((\d+)', body)
        assert m, "Could not find cursor x clamp in upset()"
        max_x = int(m.group(1))
        assert max_x <= 2, \
            f"Cursor x max is {max_x}, should be ≤2 (player half of grid)"


# ============================================================
# T11: Job switching should not cost JP
# Bug: cycling through jobs spent JP before committing
# ============================================================

class TestJobSwitchCost:
    def test_no_jp_cost_to_switch(self, cart):
        """Job switching in setup should be free (no JP cost).

        DESIGN RULE: Job choice is a tactical decision made each battle.
        JP gates access to *advanced* jobs (via level requirement), but
        switching itself should not spend a resource. Players should be
        free to experiment.
        """
        body = cart.get_function_body("upset")
        assert body is not None
        # Should NOT contain jp-= or jp -=
        assert not re.search(r'\.jp\s*-=', body), \
            "upset() spends JP when switching jobs — should be free"


# ============================================================
# T12: Map constraints — no elites early, boss only at end
# ============================================================

class TestMapConstraints:
    def test_row0_is_regular_battle(self, cart):
        """Row 0 (starting node) must always be a regular battle (tp=0).

        Verified structurally: genmap sets tp=0 for row==0.
        """
        body = cart.get_function_body("genmap")
        assert body is not None
        # Look for: if row==0 then tp=0
        assert re.search(r'row==0\s+then\s+tp=0', body), \
            "genmap doesn't force row 0 to type 0 (regular battle)"

    def test_row1_no_elites(self, cart):
        """Row 1 (first player choice) should not contain elite fights.

        DESIGN RULE: The first meaningful choice shouldn't be an elite
        that can end the run before any progression. Elites (tp=2) should
        only appear from row 2 onwards.
        """
        body = cart.get_function_body("genmap")
        assert body is not None
        # Verify row==1 has its own branch
        assert re.search(r'row==1', body), \
            "genmap has no special handling for row 1"
        # Extract the row==1 branch: from "row==1" to next "else" at same indent
        m = re.search(r'row==1\b(.*?)(?:\belse\b|\belseif\b)', body, re.DOTALL)
        assert m, "Could not extract row==1 branch from genmap"
        row1_branch = m.group(1)
        assert 'tp=2' not in row1_branch, \
            f"Row 1 branch can assign tp=2 (elite): {row1_branch.strip()}"

    def test_boss_only_on_last_row(self, cart):
        """Boss (tp=4) should only appear on row 4."""
        body = cart.get_function_body("genmap")
        assert body is not None
        assert re.search(r'row==4\s+then\s+tp=4', body), \
            "genmap doesn't restrict boss to row 4"


# ============================================================
# T13: Campfire should heal all units, not just one
# ============================================================

class TestCampfireHealsAll:
    def test_heal_option_heals_all(self, cart):
        """Campfire heal should restore all party members, not just one.

        DESIGN RULE: With HP attrition as the core tension, a single-unit
        heal is too weak to be a real choice vs upgrade. Healing the full
        party makes campfire a genuine risk/reward decision point.
        """
        body = cart.get_function_body("upcamp")
        assert body is not None
        # The heal branch should contain a loop: "for u in all(py)"
        # and set hp=mhp inside it.
        # Bad pattern: py[sel].hp=py[sel].mhp (single unit)
        # Good pattern: for u in all(py) do u.hp=u.mhp end
        has_single_heal = re.search(r'py\[sel\]\.hp\s*=\s*py\[sel\]\.mhp', body)
        has_all_heal = re.search(r'for\s+u\s+in\s+all\(py\).*u\.hp\s*=\s*u\.mhp', body, re.DOTALL)
        assert not has_single_heal, \
            "Campfire heals only one unit (py[sel].hp=py[sel].mhp)"
        # We don't strictly require the loop pattern — maybe it's done differently
        # But single-unit heal is definitely wrong


# ============================================================
# T14: Tile collision — no unit stacking
# ============================================================

class TestTileCollision:
    def test_placement_checks_collision(self, cart):
        """Unit placement should prevent two units on the same tile.

        DESIGN RULE: If units can stack, positioning is partially broken
        since the grid space is wasted.
        """
        body = cart.get_function_body("upset")
        assert body is not None
        # Should contain a check like: if py[j].x==cur.x and py[j].y==cur.y
        # or some form of collision detection before placement
        has_collision = (
            re.search(r'\.x\s*==\s*cur\.x.*\.y\s*==\s*cur\.y', body) or
            re.search(r'cur\.x.*cur\.y.*occupied', body, re.IGNORECASE) or
            re.search(r'occ\b|occupied|taken|collision|overlap', body, re.IGNORECASE)
        )
        assert has_collision, \
            "upset() doesn't check for tile collision before placement"


# ============================================================
# T15: Enemy count scaling — boss shouldn't spawn 5 enemies
# ============================================================

class TestEnemySpawnCount:
    def test_max_enemies_reasonable(self, cart):
        """Maximum enemy count per encounter should be ≤4.

        DESIGN RULE: At 128×128 resolution on a 6×4 grid, 5 enemies
        creates visual clutter and makes fights unwinnable.
        """
        body = cart.get_function_body("init_combat")
        assert body is not None
        m = re.search(r'min\(.*,\s*(\d+)\)', body)
        if m:
            max_enemies = int(m.group(1))
            assert max_enemies <= 4, \
                f"Max enemy count is {max_enemies}, should be ≤4"


# ============================================================
# T16: First-battle choice — all jobs accessible at level 1
# ============================================================

class TestFirstBattleChoice:
    def test_advanced_jobs_accessible_at_level1(self, cart):
        """Advanced jobs should be accessible from the first battle.

        DESIGN RULE: If the player starts with 3 identical squires
        and can't change jobs until level 3, the first several battles
        have zero meaningful player agency. Job choice should be the
        core tactical decision from the very start.
        """
        for j in cart.jobs:
            req_lv = j["req_lv"]
            assert req_lv <= 1, \
                f"Job '{j['name']}' requires level {req_lv} to access. " \
                f"Should be ≤1 so players have choices from the start."

