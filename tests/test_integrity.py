"""
test_integrity.py — Layer 1: Source-level structural assertions (v2).

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
# T1: Skill type handlers exist in combat code
# ============================================================

class TestSkillHandlers:
    def test_attack_handler_exists(self, cart):
        """doact must handle type 'a' skills."""
        body = cart.get_function_body("doact")
        assert body is not None, "doact function not found"
        assert re.search(r'[="]a"', body), \
            "doact has no handler for attack skills (type 'a')"

    def test_heal_handler_exists(self, cart):
        """doact must handle type 'h' skills."""
        body = cart.get_function_body("doact")
        assert body is not None
        assert re.search(r'[="]h"', body), \
            "doact has no handler for heal skills (type 'h')"

    def test_buff_handler_exists(self, cart):
        """doact must handle type 'b' skills."""
        body = cart.get_function_body("doact")
        assert body is not None
        assert re.search(r'[="]b"', body), \
            "doact has no handler for buff skills (type 'b')"


# ============================================================
# T2: Referential integrity — v2 data structure validation
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

    def test_every_job_has_three_skills(self, cart):
        """Every job should have exactly 3 skills."""
        from collections import Counter
        counts = Counter(s["job_id"] for s in cart.skills)
        for j in cart.jobs:
            jid = j["_index"]
            assert counts[jid] == 3, \
                f"Job '{j['name']}' (id={jid}) has {counts.get(jid, 0)} " \
                f"skills, expected 3"

    def test_accessory_data_valid(self, cart):
        """Every accessory should have a name and valid fields."""
        for a in cart.accessories:
            assert len(a["name"]) >= 3, \
                f"Accessory name '{a['name']}' is too short"

    def test_potion_data_valid(self, cart):
        """Every potion should have a name, effect, and cost."""
        for p in cart.potions:
            assert len(p["name"]) >= 3, \
                f"Potion name '{p['name']}' is too short"
            assert p["cost"] > 0, \
                f"Potion '{p['name']}' has invalid cost {p['cost']}"

    def test_boss_data_valid(self, cart):
        """Bosses should have valid stats."""
        for b in cart.bosses:
            assert b["hp"] >= 30, \
                f"Boss '{b['name']}' HP {b['hp']} is too low"
            assert b["atk"] >= 5, \
                f"Boss '{b['name']}' ATK {b['atk']} is too low"


# ============================================================
# T3: Sprite data integrity
# ============================================================

class TestSpriteIntegrity:
    def test_base_job_sprites_have_pixels(self, cart):
        """Sprites 1-6 (base job classes) must have pixel data."""
        for i in range(1, 7):
            assert cart.sprite_has_pixels(i), \
                f"Base job sprite {i} ({cart.jobs[i-1]['name']}) is blank"

    def test_base_enemy_sprites_have_pixels(self, cart):
        """Base enemy sprites (first 5) must have pixel data."""
        for e in cart.enemies[:5]:
            spr_id = e["spr"]
            assert cart.sprite_has_pixels(spr_id), \
                f"Enemy '{e['name']}' uses sprite {spr_id} which is blank"

    def test_ui_sprites_have_pixels(self, cart):
        """Key UI sprites must exist."""
        ui_sprites = {11: "heart", 18: "campfire"}
        for spr_id, name in ui_sprites.items():
            assert cart.sprite_has_pixels(spr_id), \
                f"UI sprite {spr_id} ({name}) is blank"


# ============================================================
# T4: HP attrition model
# ============================================================

class TestAttritionModel:
    def test_no_hp_reset_in_setup(self, cart):
        """init_setup must NOT set u.hp = u.mhp."""
        body = cart.get_function_body("init_setup")
        assert body is not None, "init_setup not found"
        has_reset = bool(re.search(
            r'\.hp\s*=\s*\w+\.mhp', body
        ))
        assert not has_reset, \
            "init_setup resets HP to maxHP, destroying attrition model"

    def test_dead_units_stay_dead_until_revive(self, cart):
        """init_setup should not unconditionally set alive=true."""
        body = cart.get_function_body("init_setup")
        assert body is not None
        lines = body.split("\n")
        for line in lines:
            stripped = line.strip()
            if "alive=true" in stripped or "alive = true" in stripped:
                assert "if" in stripped or "and" in stripped, \
                    f"Unconditional alive=true in init_setup: '{stripped}'"


# ============================================================
# T5: Placement range
# ============================================================

class TestPositioning:
    def test_placement_x_range(self, cart):
        """Setup cursor should reach at least 3 columns (0-2)."""
        body = cart.get_function_body("upset")
        assert body is not None, "upset (setup update) not found"
        m = re.search(r'min\((\d+)\s*,\s*cur\.x', body)
        if not m:
            m = re.search(r'cur\.x.*min\((\d+)', body)
        if m:
            max_x = int(m.group(1))
            assert max_x >= 2, \
                f"Placement x range capped at {max_x}, need at least 2"
        else:
            pytest.skip("Could not parse x range clamp from upset()")

    def test_placement_y_range(self, cart):
        """Setup cursor should reach at least 4 rows."""
        body = cart.get_function_body("upset")
        assert body is not None
        m = re.search(r'cur\.y[^=]*min\((\d+)', body)
        if m:
            max_y = int(m.group(1))
            assert max_y >= 3, \
                f"Placement y range capped at {max_y}, need at least 3"


# ============================================================
# T6: Enemy data variety
# ============================================================

class TestEnemyVariety:
    def test_enemy_data_has_behavior_field(self, cart):
        """Enemy data schema should include a behavior flag."""
        for e in cart.enemies:
            assert len(e) >= 7, \
                f"Enemy '{e['name']}' has {len(e)} fields, expected 7+"

    def test_enemies_have_varied_behaviors(self, cart):
        """At least 3 distinct behavior values must exist."""
        behaviors = set()
        for e in cart.enemies:
            b = e.get("behavior", None)
            if b is not None:
                behaviors.add(b)
        assert len(behaviors) >= 3, \
            f"Only {len(behaviors)} distinct enemy behaviors. Need >= 3."


# ============================================================
# T7: Accessory system
# ============================================================

class TestAccessories:
    def test_accessory_names_are_meaningful(self, cart):
        """Accessory names should be human-readable."""
        for a in cart.accessories:
            assert len(a["name"]) >= 3, \
                f"Accessory name '{a['name']}' is too short"

    def test_enough_accessory_variety(self, cart):
        """At least 10 accessories should exist per design."""
        assert len(cart.accessories) >= 10, \
            f"Only {len(cart.accessories)} accessories, expected >= 10"


# ============================================================
# T8: Campfire balance
# ============================================================

class TestCampfireBalance:
    def test_upgrade_is_bounded(self, cart):
        """Campfire should not give +1 to ALL stats for ALL units."""
        body = cart.get_function_body("upcamp")
        assert body is not None, "upcamp function not found"
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
            f"Campfire modifies {upgrade_stats} stats per unit (should be <=1)"


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
# T10: Placement bounds
# ============================================================

class TestPlacementBounds:
    def test_cursor_x_max_is_player_half(self, cart):
        """Setup cursor should be restricted to left half (x<=2)."""
        body = cart.get_function_body("upset")
        assert body is not None, "upset function not found"
        m = re.search(r'min\((\d+)\s*,\s*cur\.x', body)
        if not m:
            m = re.search(r'cur\.x[^=]*min\((\d+)', body)
        assert m, "Could not find cursor x clamp in upset()"
        max_x = int(m.group(1))
        assert max_x <= 2, \
            f"Cursor x max is {max_x}, should be <=2"


# ============================================================
# T11: Map constraints
# ============================================================

class TestMapConstraints:
    def test_row0_is_regular_battle(self, cart):
        """Row 0 must always be a regular battle (tp=0)."""
        body = cart.get_function_body("genmap")
        assert body is not None
        assert re.search(r'row==0\s+then\s+nd\.tp=0', body), \
            "genmap doesn't force row 0 to type 0"

    def test_row1_no_elites(self, cart):
        """Row 1 should not receive elite (tp=2) assignments."""
        body = cart.get_function_body("genmap")
        assert body is not None
        # Elites placed via br[3] and br[4] only
        assert re.search(r'br\[3\]', body) and 'tp=2' in body, \
            "genmap doesn't place elites on row 3"
        assert re.search(r'all\(br\[4\]\)', body), \
            "genmap doesn't iterate row 4 for elite placement"
        # Ensure no br[1] elite assignment
        assert not re.search(r'br\[1\].*tp=2', body), \
            "genmap places elites on row 1"

    def test_boss_only_on_last_row(self, cart):
        """Boss (tp=4) should only appear on row 5."""
        body = cart.get_function_body("genmap")
        assert body is not None
        assert re.search(r'row==5\s+then\s+nd\.tp=4', body), \
            "genmap doesn't restrict boss to row 5"

    def test_six_rows(self, cart):
        """Map should have 6 rows (0-5)."""
        body = cart.get_function_body("genmap")
        assert body is not None
        assert re.search(r'for\s+row=0\s*,\s*5\b', body), \
            "genmap doesn't iterate rows 0-5"

    def test_pinch_point_row2(self, cart):
        """Row 2 should be a pinch point (2 nodes max)."""
        body = cart.get_function_body("genmap")
        assert body is not None
        assert re.search(r'row==2\s+then\s+nc=2', body), \
            "genmap doesn't force row 2 to 2 nodes"

    def test_shop_type_exists(self, cart):
        """Map generator should include shop nodes (tp=5)."""
        body = cart.get_function_body("genmap")
        assert body is not None
        assert re.search(r'\.tp=5', body), \
            "genmap doesn't assign shop type (tp=5)"

    def test_structural_guarantees(self, cart):
        """Map must guarantee campfires, elites, and shop."""
        body = cart.get_function_body("genmap")
        assert body is not None
        # At least 2 campfire placements (tp=3)
        camp_placements = re.findall(r'\.tp=3', body)
        assert len(camp_placements) >= 2, \
            f"Only {len(camp_placements)} campfire placements, need >=2"
        # At least 2 elite placements (tp=2)
        elite_placements = re.findall(r'\.tp=2', body)
        assert len(elite_placements) >= 2, \
            f"Only {len(elite_placements)} elite placements, need >=2"
        # At least 1 shop placement (tp=5)
        shop_placements = re.findall(r'\.tp=5', body)
        assert len(shop_placements) >= 1, \
            f"No shop placements found"


# ============================================================
# T12: Campfire heals all
# ============================================================

class TestCampfireHealsAll:
    def test_heal_option_heals_all(self, cart):
        """Campfire heal should restore all party members."""
        body = cart.get_function_body("upcamp")
        assert body is not None
        has_single_heal = re.search(r'py\[sel\]\.hp\s*=\s*py\[sel\]\.mhp', body)
        assert not has_single_heal, \
            "Campfire heals only one unit"


# ============================================================
# T13: Tile collision
# ============================================================

class TestTileCollision:
    def test_placement_checks_collision(self, cart):
        """Unit placement should prevent two units on the same tile."""
        body = cart.get_function_body("upset")
        assert body is not None
        has_collision = (
            re.search(r'\.x\s*==\s*cur\.x.*\.y\s*==\s*cur\.y', body) or
            re.search(r'occ\b|occupied|taken|collision|overlap', body, re.IGNORECASE)
        )
        assert has_collision, \
            "upset() doesn't check for tile collision"


# ============================================================
# T14: Enemy spawn count
# ============================================================

class TestEnemySpawnCount:
    def test_max_enemies_reasonable(self, cart):
        """Regular enemy count per encounter should be bounded."""
        body = cart.get_function_body("init_combat")
        assert body is not None
        # Look for ne= assignment with min() clamp
        m = re.search(r'\bne\s*=\s*min\([^,]+,\s*(\d+)\)', body)
        if m:
            max_enemies = int(m.group(1))
            assert max_enemies <= 4, \
                f"Max enemy count is {max_enemies}, should be <=4"


# ============================================================
# T15: v2 class structure — 18 classes, proper tier/parent
# ============================================================

class TestClassStructure:
    def test_18_classes(self, cart):
        """v2 should have exactly 18 classes (6 base + 12 advanced)."""
        assert len(cart.jobs) == 18, \
            f"Expected 18 jobs, got {len(cart.jobs)}"

    def test_6_base_classes(self, cart):
        """Exactly 6 classes should be tier 1 (base)."""
        base = [j for j in cart.jobs if j["tier"] == 1]
        assert len(base) == 6, \
            f"Expected 6 base classes, got {len(base)}"

    def test_12_advanced_classes(self, cart):
        """Exactly 12 classes should be tier 2 (advanced)."""
        adv = [j for j in cart.jobs if j["tier"] == 2]
        assert len(adv) == 12, \
            f"Expected 12 advanced classes, got {len(adv)}"

    def test_each_base_has_two_branches(self, cart):
        """Each base class should have exactly 2 advanced branches."""
        from collections import Counter
        parents = Counter(
            j["parent"] for j in cart.jobs if j["tier"] == 2
        )
        for base_id in range(1, 7):
            assert parents[base_id] == 2, \
                f"Base class {base_id} ({cart.jobs[base_id-1]['name']}) " \
                f"has {parents.get(base_id, 0)} branches, expected 2"

    def test_advanced_parents_are_base(self, cart):
        """Every advanced class's parent must be a tier-1 class."""
        base_ids = set(j["_index"] for j in cart.jobs if j["tier"] == 1)
        for j in cart.jobs:
            if j["tier"] == 2:
                assert j["parent"] in base_ids, \
                    f"Advanced class '{j['name']}' parent {j['parent']} " \
                    f"is not a base class"


# ============================================================
# T16: v2 skill types cover all 11 handler types
# ============================================================

class TestSkillTypesCoverage:
    def test_54_skills(self, cart):
        """v2 should have exactly 54 skills (3 per class × 18)."""
        assert len(cart.skills) == 54, \
            f"Expected 54 skills, got {len(cart.skills)}"

    def test_all_11_effect_types_used(self, cart):
        """All 11 effect type codes should be present in skill data."""
        types = set(s["type"] for s in cart.skills)
        expected = {"a", "A", "h", "H", "b", "B", "d", "D", "p", "l", "c"}
        missing = expected - types
        assert not missing, \
            f"Missing skill effect types: {missing}"

    def test_skill_power_is_positive(self, cart):
        """All attack/heal skills should have power > 0."""
        for s in cart.skills:
            if s["type"] in ("a", "A", "h", "H", "p", "l"):
                assert s["power"] > 0, \
                    f"Skill '{s['name']}' has power={s['power']}, expected > 0"

    def test_skill_cd_is_non_negative(self, cart):
        """All skills should have cd >= 0."""
        for s in cart.skills:
            assert s["cd"] >= 0, \
                f"Skill '{s['name']}' has cd={s['cd']}, expected >= 0"


# ============================================================
# T17: v2 unit system functions exist
# ============================================================

class TestUnitSystem:
    def test_mku_exists(self, cart):
        """mku() function must exist for unit creation."""
        body = cart.get_function_body("mku")
        assert body is not None, "mku function not found"

    def test_advu_exists(self, cart):
        """advu() function must exist for class advancement."""
        body = cart.get_function_body("advu")
        assert body is not None, "advu (advance unit) function not found"

    def test_getsk_exists(self, cart):
        """getsk() function must exist for skill lookup."""
        body = cart.get_function_body("getsk")
        assert body is not None, "getsk (get skills) function not found"

    def test_ugetsk_exists(self, cart):
        """ugetsk() function must exist for unit skill lookup."""
        body = cart.get_function_body("ugetsk")
        assert body is not None, "ugetsk (unit get skills) function not found"

    def test_advopt_exists(self, cart):
        """advopt() function must exist for advancement options."""
        body = cart.get_function_body("advopt")
        assert body is not None, "advopt function not found"

    def test_mku_assigns_name(self, cart):
        """mku() should assign a name from the name pool."""
        body = cart.get_function_body("mku")
        assert body is not None
        assert re.search(r'_nm\b', body), \
            "mku doesn't reference _nm (name pool)"

    def test_mku_sets_tier(self, cart):
        """mku() should set tier field on new units."""
        body = cart.get_function_body("mku")
        assert body is not None
        assert "tier" in body, "mku doesn't set tier field"


# ============================================================
# T18: v2 data tables exist
# ============================================================

class TestDataTables:
    def test_accessory_table_exists(self, cart):
        """_a (accessories) table must be present."""
        assert len(cart.accessories) >= 12, \
            f"Expected >= 12 accessories, got {len(cart.accessories)}"

    def test_potion_table_exists(self, cart):
        """_p (potions) table must be present."""
        assert len(cart.potions) >= 8, \
            f"Expected >= 8 potions, got {len(cart.potions)}"

    def test_boss_table_exists(self, cart):
        """_b (bosses) table must be present."""
        assert len(cart.bosses) >= 3, \
            f"Expected >= 3 bosses, got {len(cart.bosses)}"

    def test_enemy_table_expanded(self, cart):
        """_e should have >= 15 enemies (10 regular + 5 elite)."""
        assert len(cart.enemies) >= 15, \
            f"Expected >= 15 enemies, got {len(cart.enemies)}"

    def test_name_pool_exists(self, cart):
        """_nm (name pool) should be present in Lua source."""
        assert cart.lua_contains(r'_nm\s*=\s*split\('), \
            "_nm name pool not found in Lua source"


# ============================================================
# T20: Draft Screen
# ============================================================

class TestDraftScreen:
    def test_init_draft_exists(self, cart):
        """init_draft() function must exist."""
        body = cart.get_function_body("init_draft")
        assert body is not None, "init_draft function not found"

    def test_draft_offers_five(self, cart):
        """Draft should offer 5 of 6 base classes."""
        body = cart.get_function_body("init_draft")
        assert body is not None
        # Pool starts with 6 and removes 1
        assert re.search(r'pool\s*=\s*\{1,2,3,4,5,6\}', body), \
            "Draft doesn't start with 6-class pool"
        assert re.search(r'deli\(pool', body), \
            "Draft doesn't remove a class from pool"

    def test_draft_picks_three(self, cart):
        """Draft should require exactly 3 picks."""
        body = cart.get_function_body("updraft")
        assert body is not None
        assert re.search(r'dpick\s*>=\s*3', body), \
            "Draft doesn't check for 3 picks"

    def test_draft_creates_units(self, cart):
        """Draft must call mku() to create units."""
        body = cart.get_function_body("updraft")
        assert body is not None
        assert re.search(r'mku\(', body), \
            "Draft doesn't create units via mku()"

    def test_draft_transitions_to_map(self, cart):
        """After 3 picks, draft should generate map."""
        body = cart.get_function_body("updraft")
        assert body is not None
        assert re.search(r'genmap\(\)', body), \
            "Draft doesn't call genmap() after picking"
        assert re.search(r'gs\s*=\s*"map"', body), \
            "Draft doesn't transition to map state"


# ============================================================
# T21: Setup Screen + Enemy Preview (W4.2 + W2.3)
# ============================================================

class TestSetupScreen:
    def test_gen_ens_exists(self, cart):
        """gen_ens() must exist as separate enemy generator."""
        body = cart.get_function_body("gen_ens")
        assert body is not None, "gen_ens function not found"

    def test_gen_ens_handles_boss(self, cart):
        """gen_ens() should handle boss encounters (tp==4)."""
        body = cart.get_function_body("gen_ens")
        assert body is not None
        assert re.search(r'cnod\.tp\s*==\s*4', body), \
            "gen_ens doesn't check for boss node type"
        assert re.search(r'_b\[', body), \
            "gen_ens doesn't reference boss table for boss fights"

    def test_gen_ens_handles_elite(self, cart):
        """gen_ens() should handle elite encounters (tp==2)."""
        body = cart.get_function_body("gen_ens")
        assert body is not None
        assert re.search(r'cnod\.tp\s*==\s*2', body), \
            "gen_ens doesn't check for elite node type"

    def test_init_setup_calls_gen_ens(self, cart):
        """init_setup() must call gen_ens() to populate enemies before placement."""
        body = cart.get_function_body("init_setup")
        assert body is not None
        assert re.search(r'gen_ens\(\)', body), \
            "init_setup doesn't call gen_ens()"

    def test_init_setup_sets_state(self, cart):
        """init_setup() must set gs='setup'."""
        body = cart.get_function_body("init_setup")
        assert body is not None
        assert re.search(r'gs\s*=\s*"setup"', body), \
            "init_setup doesn't set game state to 'setup'"

    def test_dsetup_shows_enemies_on_grid(self, cart):
        """dsetup() must render enemies on the battle grid."""
        body = cart.get_function_body("dsetup")
        assert body is not None
        assert re.search(r'for\s+e\s+in\s+all\(ens\)', body), \
            "dsetup doesn't iterate enemies for grid display"
        assert re.search(r'spr\(e\.spr', body), \
            "dsetup doesn't draw enemy sprites"

    def test_dsetup_shows_enemy_lineup(self, cart):
        """dsetup() must show enemy stats in bottom panel."""
        body = cart.get_function_body("dsetup")
        assert body is not None
        assert re.search(r'e\.mhp', body), \
            "dsetup doesn't show enemy HP"
        assert re.search(r'e\.atk', body), \
            "dsetup doesn't show enemy ATK"

    def test_dmap_shows_node_type_preview(self, cart):
        """dmap() should show selected node type name."""
        body = cart.get_function_body("dmap")
        assert body is not None
        assert re.search(r'battle.*elite.*campfire.*boss.*shop', body), \
            "dmap doesn't contain node type name list"


# ============================================================
# T22: Reward Screen (W4.3)
# ============================================================

class TestRewardScreen:
    def test_upreward_exists(self, cart):
        """upreward() must exist."""
        body = cart.get_function_body("upreward")
        assert body is not None, "upreward function not found"

    def test_dreward_exists(self, cart):
        """dreward() must exist."""
        body = cart.get_function_body("dreward")
        assert body is not None, "dreward function not found"

    def test_cwin_sets_reward_state(self, cart):
        """cwin() must set gs='reward' and rws for elite."""
        body = cart.get_function_body("cwin")
        assert body is not None
        assert re.search(r'gs\s*=\s*"reward"', body), \
            "cwin doesn't set game state to reward"
        assert re.search(r'rws\s*=\s*"elite_pick"', body), \
            "cwin doesn't set elite pick state"

    def test_elite_reward_has_advance_and_accessory(self, cart):
        """Elite reward flow must support advancing and accessories."""
        body = cart.get_function_body("upreward")
        assert body is not None
        assert re.search(r'rws\s*==\s*"pick_unit"', body), \
            "upreward missing pick_unit state"
        assert re.search(r'rws\s*==\s*"pick_branch"', body), \
            "upreward missing pick_branch state"
        assert re.search(r'rws\s*==\s*"pick_skill"', body), \
            "upreward missing pick_skill state"
        assert re.search(r'rws\s*==\s*"pick_acc"', body), \
            "upreward missing pick_acc state"

    def test_reward_calls_advu(self, cart):
        """Reward advancement must call advu()."""
        body = cart.get_function_body("upreward")
        assert body is not None
        assert re.search(r'advu\(', body), \
            "upreward doesn't call advu() for advancement"

    def test_potion_drop_on_normal_battle(self, cart):
        """Normal battles should have potion drop chance."""
        body = cart.get_function_body("cwin")
        assert body is not None
        assert re.search(r'pots', body), \
            "cwin doesn't reference potion inventory"
        assert re.search(r'rwdr', body), \
            "cwin doesn't set potion drop reward"
