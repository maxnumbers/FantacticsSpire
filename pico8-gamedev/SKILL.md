---
name: pico8-gamedev
description: >
  Create complete, playable PICO-8 fantasy console games (.p8 files) from natural language descriptions. Use this skill whenever the user asks to make a PICO-8 game, create a retro game, build a fantasy console game, generate a .p8 file, or mentions PICO-8 in any game development context. Also trigger when users say things like "make me a small game", "retro pixel game", "tiny game", "8-bit game", or want a self-contained game in a single file. This skill handles the full pipeline from game design, sprite data generation, map layout, sound effects, music, and Lua code, all within PICO-8's strict constraints.
---

# PICO-8 Game Development Skill

Generate complete, playable PICO-8 games as `.p8` cart files from natural language prompts. PICO-8's tight constraints (128×128 screen, 16 colors, 8192 tokens of Lua) make it an ideal target for AI game generation — the solution space is small enough to produce polished results.

## Before You Start

Read `references/pico8-api.md` for the full API reference, `.p8` file format spec, sprite encoding, and color palette. You will need it for every cart you generate.

## The .p8 File Format

A `.p8` file is a plain-text cartridge. It has labeled sections that you write directly:

```
pico-8 cartridge // http://www.pico-8.com/version 42
version 42
__lua__
-- all game code here

__gfx__
-- 128 lines of 128 hex chars (sprite sheet, 8192 bytes)

__gff__
-- 2 lines of 256 hex chars (sprite flags)

__map__
-- 32 lines of 256 hex chars (map data, upper 32 rows)

__sfx__
-- 64 lines of sound effect data

__music__
-- 64 lines of music pattern data

```

Each hex character in `__gfx__` is one pixel (0-f = the 16 PICO-8 colors). Sprites are 8×8 pixels, laid out left-to-right, top-to-bottom on a 128×128 sheet (16 sprites per row, 16 rows = 256 sprites). The lower half of the sprite sheet (sprites 128-255) shares memory with the lower half of the map.

## Game Generation Workflow

### Step 1: Understand the Request

Identify the genre, core mechanic, and scope. Ask clarifying questions only if the request is genuinely ambiguous. For straightforward requests ("make a platformer", "make snake"), just build it.

Think about:
- What genre? (platformer, shooter, puzzle, RPG, arcade, etc.)
- What's the core loop? (jump/collect, shoot/dodge, match/clear, explore/fight)
- What entities are needed? (player, enemies, pickups, projectiles, tiles)
- What UI is needed? (score, lives, health bar, title screen, game over)

### Step 2: Design the Sprite Sheet

This is critical. You must generate valid `__gfx__` hex data. Each row is 128 hex characters representing 128 pixels across the full sprite sheet width.

Plan your sprite layout:
- Sprites 0-15: Row 0 (player, player animation frames)
- Sprites 16-31: Row 1 (enemies, enemy variants)
- Sprites 32-47: Row 2 (pickups, items, projectiles)
- Sprites 48-63: Row 3 (terrain/tiles — walls, ground, platforms)
- Sprites 64+: Additional as needed

Design sprites by hand in hex. Each sprite is 8 pixels wide, so 2 sprites = 16 hex chars. Think about what shapes will read well at 8×8.

**Sprite design principles at 8×8:**
- Use 2-3 colors max per sprite for clarity
- Outline with a dark color (1 or 0) for readability
- Leave at least 1px padding from edges when possible
- Symmetry reads well at low resolution
- Animate with 2-frame alternation for simplicity

**Color palette reference (hex digit → color):**
```
0: black       4: brown       8: red         c: light_gray
1: dark_blue   5: dark_gray   9: orange      d: light_peach
2: dark_purple 6: light_gray  a: yellow      e: pink
3: dark_green  7: white       b: green       f: peach
```

### Step 3: Write the Lua Code

Structure every game with this skeleton:

```lua
-- [game title]
-- by claude

-- game states
function _init()
  -- initialize game state variables
  -- set up player, enemies, level data
  gamestate="title"
end

function _update60()
  if gamestate=="title" then
    update_title()
  elseif gamestate=="game" then
    update_game()
  elseif gamestate=="gameover" then
    update_gameover()
  end
end

function _draw()
  cls()
  if gamestate=="title" then
    draw_title()
  elseif gamestate=="game" then
    draw_game()
  elseif gamestate=="gameover" then
    draw_gameover()
  end
end
```

**Code patterns to follow:**

- **Input:** Use `btn(0)`–`btn(5)` for ⬅️➡️⬆️⬇️🅾️❎. Use `btnp()` for single-press actions (menu select, jump initiation).
- **Collision (AABB):** `function collide(a,b) return a.x<b.x+b.w and a.x+a.w>b.x and a.y<b.y+b.h and a.y+a.h>b.y end`
- **Map collision:** Check sprite flags with `fget(mget(tile_x, tile_y), flag_num)` to test if a tile is solid.
- **Object pools:** Use tables as arrays: `enemies={}` → `add(enemies, {x=64,y=64,spd=1})` → iterate with `for e in all(enemies) do`.
- **Removing objects:** Use `del(enemies, e)` inside iteration, PICO-8 handles this safely.
- **Animation:** `spr(base_frame + flr(t/anim_speed) % num_frames, x, y)`
- **Screen shake:** Offset camera with `camera(rnd(n)-n/2, rnd(n)-n/2)` then reset with `camera()`.
- **Particles:** Simple table of `{x,y,dx,dy,life,col}` updated each frame.
- **Coroutines:** Use for cutscenes, wave spawning, timed events.

**Token conservation tips:**
- Combine similar update logic for different entity types
- Use short variable names for frequently accessed values
- Prefer `if (cond) stmt` single-line form
- Use `foreach(tbl, fn)` or `for v in all(tbl)` over index loops when you don't need the index
- Reuse functions across game states where possible
- Inline small computations rather than creating helper functions for one-off use

### Step 4: Design Sound Effects (Optional but Recommended)

The `__sfx__` section contains 64 sound effects. Each line is 168 hex characters encoding 32 notes with speed, loop, and instrument data. For simple games, you can leave this section empty or minimal.

Quick approach: define a few key SFX by ID and reference them:
- SFX 0: jump
- SFX 1: collect/pickup
- SFX 2: hit/damage
- SFX 3: explosion/death
- SFX 4-7: music patterns

Play with `sfx(n)` in code.

If you generate SFX data, see the reference file for the exact encoding format.

### Step 5: Assemble the .p8 File

Combine all sections into a single `.p8` file. Every section must be present even if empty. Ensure:
- `__gfx__` has exactly 128 lines of exactly 128 hex characters each
- `__gff__` has exactly 2 lines of 256 hex characters each  
- `__map__` has exactly 32 lines of 256 hex characters each
- `__sfx__` has exactly 64 lines (each 168 hex chars, or use `000000000000...` for unused)
- `__music__` has exactly 64 lines (each 11 chars: 2 flag chars + space + 8 hex chars, or `00 41414141` for unused)
- No trailing whitespace or extra blank lines within data sections

### Step 6: Validate

After generating the cart, do a quick sanity check:
- Count lines in `__gfx__` (must be 128)
- Verify hex characters are only 0-9, a-f
- Ensure sprite indices referenced in code actually have drawn pixel data
- Check that map tile indices reference drawn sprites
- Verify all `spr()`, `mget()`, `fget()` calls use valid sprite numbers
- Test that collision bounds match sprite sizes
- Confirm game state transitions are reachable (can you get from title → game → gameover → title?)

## Game Genre Templates

### Platformer
Core: gravity, ground collision, jump arc, platforms, collectibles.
Key sprites: player (2-4 frames), ground tile, platform tile, collectible, hazard.
Key mechanics: `player.dy += gravity`, ground check via `mget`, `btnp(4)` to jump only when grounded.

### Top-Down Shooter
Core: 8-direction movement, projectile spawning, enemy AI, health.
Key sprites: player (4 directional), enemy (2+ types), bullet, explosion, pickup.
Key mechanics: bullet pool, spawn timer, simple chase AI (`if e.x<p.x then e.x+=e.spd`).

### Puzzle Game (e.g., Match-3, Sokoban)
Core: grid-based state, input validation, win/lose detection.
Key sprites: tile types (4-6 distinct), cursor/selector, wall.
Key mechanics: 2D array for grid, check matches/valid moves, animate clears.

### Arcade (e.g., Snake, Breakout, Pong)
Core: simple physics, score tracking, increasing difficulty.
Key sprites: minimal (ball, paddle, segments, blocks).
Key mechanics: velocity-based movement, bounce logic, timer-based difficulty ramp.

### RPG / Adventure
Core: tile-based world, NPC interaction, inventory, combat.
Key sprites: player (4 dir walk), NPCs, terrain tiles, UI elements.
Key mechanics: map scrolling with `map()` + `camera()`, flag-based doors/walls, simple turn-based combat.

## Quality Checklist

Before delivering the .p8 file, verify:
- [ ] Title screen with game name and "press ❎ to start" (or 🅾️)
- [ ] Core gameplay loop is functional and fun
- [ ] Game over state with score display and restart option
- [ ] At least basic sprite art (not just colored rectangles — give shapes character)
- [ ] Collision detection works correctly
- [ ] No obvious softlocks or unreachable states
- [ ] Score or progression feedback visible during gameplay
- [ ] Code is under 8192 tokens (keep well under — aim for <6000 for safety)
- [ ] Difficulty ramps or game has replayability

## Common Pitfalls

- **Forgetting `cls()` in `_draw()`** — causes ghosting/visual garbage
- **Using `_update()` with 60fps logic** — use `_update60()` for smooth movement, or `_update()` at 30fps with appropriate speeds
- **Off-by-one in map collision** — remember `mget` uses tile coordinates (pixel / 8)
- **Sprite sheet row math errors** — sprite N is at pixel position `(N%16)*8, flr(N/16)*8` on the sheet
- **Exceeding token limit** — check with awareness that strings, comments, and whitespace don't count but every identifier, operator, and number does
- **Map/sprite sheet memory overlap** — sprites 128-255 share memory with map rows 32-63. If you use the full map, don't put important sprites there, and vice versa
- **Forgetting to handle both btn and btnp** — `btn` for held actions (movement), `btnp` for press actions (jump, shoot, menu select)

## Output Format

Always output the complete `.p8` file saved to disk. Name it descriptively based on the game (e.g., `space_shooter.p8`, `cave_explorer.p8`). Briefly explain the controls and how to play after presenting the file.

The user can load the `.p8` file directly in PICO-8 with `load filename` or by placing it in their PICO-8 carts directory.
