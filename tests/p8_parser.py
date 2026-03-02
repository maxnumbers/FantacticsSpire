"""
p8_parser.py — Parse a PICO-8 .p8 cartridge into structured Python data.

Extracts:
- Raw section text (lua, gfx, gff, map, sfx, music)
- String-packed data tables (_j, _s, _r, _e) as Python dicts
- Sprite pixel data (for reference validation)
- Sprite flags
- Function bodies (for structural assertions)
"""

import os
import re
from pathlib import Path


class P8Cart:
    """Parsed PICO-8 cartridge."""

    def __init__(self, path):
        self.path = Path(path)
        self.raw = self.path.read_text()
        self.sections = self._split_sections()
        self.lua = self.sections.get("lua", "")
        self.gfx_raw = self.sections.get("gfx", "")
        self.gff_raw = self.sections.get("gff", "")
        self.map_raw = self.sections.get("map", "")
        self.sfx_raw = self.sections.get("sfx", "")
        self.music_raw = self.sections.get("music", "")

        # Parsed data — v2 format
        self.jobs = self._parse_packed_table("_j", [
            "name", "hp", "atk", "def_", "spd", "pos", "tier", "parent"
        ])
        self.skills = self._parse_packed_table("_s", [
            "name", "job_id", "type", "power", "range", "cd", "xtra", "dur"
        ])
        self.accessories = self._parse_packed_table("_a", [
            "name", "stat", "bonus", "special"
        ])
        self.potions = self._parse_packed_table("_p", [
            "name", "effect", "power", "cost"
        ])
        self.enemies = self._parse_packed_table("_e", [
            "name", "spr", "hp", "atk", "spd", "behavior", "def_"
        ])
        self.bosses = self._parse_packed_table("_b", [
            "name", "spr", "hp", "atk", "spd", "behavior", "def_", "mechanic"
        ])
        # Legacy alias
        self.relics = self.accessories
        self.sprites = self._parse_sprites()
        self.sprite_flags = self._parse_sprite_flags()

    def _split_sections(self):
        """Split .p8 into named sections."""
        sections = {}
        current = None
        lines = []
        for line in self.raw.split("\n"):
            m = re.match(r"^__(\w+)__$", line)
            if m:
                if current:
                    sections[current] = "\n".join(lines)
                current = m.group(1)
                lines = []
            elif current:
                lines.append(line)
        if current:
            sections[current] = "\n".join(lines)
        return sections

    def _parse_packed_table(self, var_name, fields):
        """Extract a pd(...) string-packed table from Lua source."""
        # Match: _j=pd("...|...|...")
        pattern = rf'{re.escape(var_name)}\s*=\s*pd\(\s*"([^"]+)"\s*\)'
        m = re.search(pattern, self.lua)
        if not m:
            return []
        raw = m.group(1)
        rows = []
        for row_str in raw.split("|"):
            vals = row_str.split(",")
            entry = {}
            for i, field in enumerate(fields):
                if i < len(vals):
                    v = vals[i].strip()
                    # Try numeric conversion
                    try:
                        v = int(v)
                    except ValueError:
                        try:
                            v = float(v)
                        except ValueError:
                            pass
                    entry[field] = v
                else:
                    entry[field] = None
            entry["_index"] = len(rows) + 1  # 1-indexed like Lua
            rows.append(entry)
        return rows

    def _parse_sprites(self):
        """Parse __gfx__ into a dict of sprite_index -> 8x8 pixel arrays."""
        lines = [l for l in self.gfx_raw.split("\n") if l.strip()]
        if len(lines) != 128:
            return {}
        sprites = {}
        for spr_row in range(16):
            for spr_col in range(16):
                spr_idx = spr_row * 16 + spr_col
                pixels = []
                for py in range(8):
                    line_idx = spr_row * 8 + py
                    if line_idx >= len(lines):
                        pixels.append([0] * 8)
                        continue
                    line = lines[line_idx]
                    start = spr_col * 8
                    row = []
                    for px in range(8):
                        c = line[start + px] if start + px < len(line) else '0'
                        row.append(int(c, 16))
                    pixels.append(row)
                sprites[spr_idx] = pixels
        return sprites

    def _parse_sprite_flags(self):
        """Parse __gff__ into dict of sprite_index -> flag byte."""
        lines = [l for l in self.gff_raw.split("\n") if l.strip()]
        flags = {}
        for line_idx, line in enumerate(lines):
            for i in range(0, len(line), 2):
                spr_idx = line_idx * 128 + i // 2
                byte_hex = line[i:i + 2]
                try:
                    flags[spr_idx] = int(byte_hex, 16)
                except ValueError:
                    flags[spr_idx] = 0
        return flags

    def sprite_has_pixels(self, spr_idx):
        """Check if a sprite has any non-zero pixel data."""
        if spr_idx not in self.sprites:
            return False
        for row in self.sprites[spr_idx]:
            for pixel in row:
                if pixel != 0:
                    return True
        return False

    def get_function_body(self, func_name):
        """Extract a function body from Lua source (simple heuristic).
        
        Returns the source text between 'function func_name(...)' and
        its matching 'end'. Handles nested end/if/for blocks.
        """
        # Find function start
        pattern = rf'function\s+{re.escape(func_name)}\s*\([^)]*\)'
        m = re.search(pattern, self.lua)
        if not m:
            return None
        start = m.start()
        # Track nesting depth to find matching end
        text = self.lua[start:]
        depth = 0
        # Walk line by line
        lines = text.split("\n")
        body_lines = []
        for line in lines:
            body_lines.append(line)
            stripped = line.strip()
            # Remove strings and comments for block counting
            cleaned = re.sub(r'"[^"]*"', '', stripped)
            cleaned = re.sub(r"'[^']*'", '', cleaned)
            cleaned = re.sub(r'--.*$', '', cleaned)
            # Count block openers
            # function, if...then, for...do, while...do, repeat
            openers = len(re.findall(
                r'\b(?:function|if\b.*\bthen|for\b.*\bdo|while\b.*\bdo|repeat)\b',
                cleaned
            ))
            # Count closers
            closers = len(re.findall(r'\bend\b', cleaned))
            # Single-line if: "if (cond) stmt" without then — not a block
            # We need to be careful here
            depth += openers - closers
            if depth <= 0 and len(body_lines) > 1:
                break
        return "\n".join(body_lines)

    def find_all_calls(self, func_name):
        """Find all calls to a function in the Lua source.
        Returns list of (line_number, line_text) tuples.
        """
        results = []
        for i, line in enumerate(self.lua.split("\n")):
            if re.search(rf'\b{re.escape(func_name)}\s*\(', line):
                results.append((i + 1, line.strip()))
        return results

    def lua_contains(self, pattern):
        """Check if Lua source contains a regex pattern."""
        return bool(re.search(pattern, self.lua))

    def get_packed_var_names(self):
        """Find all variables assigned via pd()."""
        return re.findall(r'(\w+)\s*=\s*pd\(', self.lua)


def load_cart(path="spire_tactics.p8"):
    """Convenience loader."""
    return P8Cart(path)


if __name__ == "__main__":
    cart = load_cart(os.path.join(os.path.dirname(__file__), "..", "spire_tactics.p8"))
    print(f"Lua: {len(cart.lua)} chars")
    print(f"Jobs: {len(cart.jobs)}")
    for j in cart.jobs:
        print(f"  {j}")
    print(f"Skills: {len(cart.skills)}")
    for s in cart.skills:
        print(f"  {s}")
    print(f"Relics: {len(cart.relics)}")
    print(f"Enemies: {len(cart.enemies)}")
    print(f"Sprites with pixels: {sum(1 for i in range(256) if cart.sprite_has_pixels(i))}")
    print(f"\nFunction 'doact':")
    body = cart.get_function_body("doact")
    if body:
        print(f"  {len(body.split(chr(10)))} lines")
    print(f"\ninit_setup body snippet:")
    body = cart.get_function_body("init_setup")
    if body:
        for line in body.split("\n")[:10]:
            print(f"  {line}")
