# PICO-8 API Reference

Complete reference for generating valid PICO-8 .p8 cartridges. Consult when building any cart.

## Table of Contents
1. [Color Palette](#color-palette)
2. [Graphics API](#graphics-api)
3. [Input API](#input-api)
4. [Sound API](#sound-api)
5. [Map API](#map-api)
6. [Math & Utility API](#math--utility-api)
7. [Table API](#table-api)
8. [String API](#string-api)
9. [Memory Layout](#memory-layout)
10. [.p8 File Format Specification](#p8-file-format-specification)
11. [Sprite Sheet Hex Encoding](#sprite-sheet-hex-encoding)
12. [Sprite Flags Encoding](#sprite-flags-encoding)
13. [Map Data Encoding](#map-data-encoding)
14. [SFX Data Encoding](#sfx-data-encoding)
15. [Music Data Encoding](#music-data-encoding)
16. [Token Counting Rules](#token-counting-rules)

---

## Color Palette

PICO-8 has a fixed 16-color palette. Each color is one hex digit (0-f):

```
 0 = #000000  black
 1 = #1D2B53  dark_blue
 2 = #7E2553  dark_purple
 3 = #008751  dark_green
 4 = #AB5236  brown
 5 = #5F574F  dark_gray
 6 = #C2C3C7  light_gray
 7 = #FFF1E8  white
 8 = #FF004D  red
 9 = #FFA300  orange
10 = #FFEC27  yellow       (hex: a)
11 = #00E436  green        (hex: b)
12 = #29ADFF  blue         (hex: c)
13 = #83769C  lavender     (hex: d)
14 = #FF77A8  pink         (hex: e)
15 = #FFCCAA  peach        (hex: f)
```

Use `pal(c0, c1)` to remap color c0 to c1 for palette swaps. `pal()` with no args resets.
Use `palt(c, transparent)` to set transparency for a color. By default, color 0 (black) is transparent when drawing sprites.

---

## Graphics API

### Screen
- `cls([col])` — Clear screen to color (default 0/black)
- `camera([x, y])` — Set camera offset. All draw calls shift by (-x, -y). `camera()` resets to (0,0).
- `clip([x, y, w, h])` — Set clipping rectangle. `clip()` resets.
- `color(col)` — Set default color for drawing functions.
- `cursor(x, y, [col])` — Set cursor position for `print`.
- `flip()` — Force screen update (rarely needed; `_draw()` does this automatically).

### Drawing Primitives
- `pset(x, y, [col])` — Set pixel
- `pget(x, y)` — Get pixel color
- `line(x0, y0, x1, y1, [col])` — Draw line
- `rect(x0, y0, x1, y1, [col])` — Draw rectangle outline
- `rectfill(x0, y0, x1, y1, [col])` — Draw filled rectangle
- `circ(x, y, r, [col])` — Draw circle outline
- `circfill(x, y, r, [col])` — Draw filled circle
- `oval(x0, y0, x1, y1, [col])` — Draw oval outline
- `ovalfill(x0, y0, x1, y1, [col])` — Draw filled oval
- `fillp([pattern])` — Set fill pattern for subsequent fills

### Sprites
- `spr(n, x, y, [w, h], [flip_x], [flip_y])` — Draw sprite n at (x,y). w,h in tiles (default 1,1). Set flip_x/flip_y to true to mirror.
- `sspr(sx, sy, sw, sh, dx, dy, [dw, dh], [flip_x], [flip_y])` — Draw a region of the sprite sheet (sx,sy,sw,sh) to screen (dx,dy,dw,dh). Supports stretching.

### Text
- `print(str, [x, y], [col])` — Print text. Each char is 4×6 pixels (with spacing). Returns the x position after the last character.
  - Special: `print("\n")` for newlines. `print` with just a string continues from cursor.

### Palette
- `pal([c0, c1, [p]])` — Remap color c0 to c1. p=0 for draw palette (default), p=1 for screen palette. `pal()` resets all.
- `palt([c, t])` — Set color c transparency. t=true means transparent. `palt()` resets (only 0 is transparent).

---

## Input API

PICO-8 supports 2 players, 6 buttons each.

### Button IDs
```
0 = ⬅️ left
1 = ➡️ right
2 = ⬆️ up
3 = ⬇️ down
4 = 🅾️ (Z / C / N on keyboard)
5 = ❎ (X / V / M on keyboard)
```

### Functions
- `btn([i, [p]])` — Is button i held? p=player (0 or 1, default 0). Returns true/false. With no args, returns bitfield.
- `btnp([i, [p]])` — Was button i just pressed this frame? Also auto-repeats after a delay (useful for menus).

---

## Sound API

### Sound Effects
- `sfx(n, [channel], [offset], [length])` — Play sound effect n (0-63). channel=-1 to auto-select, -2 to stop on that channel. offset/length in notes (0-31).
- `sfx(-1, channel)` — Stop sound on channel.
- `sfx(-2)` — Stop all sound.

### Music
- `music(n, [fade_ms], [channel_mask])` — Play music pattern n (0-63). n=-1 to stop. fade_ms for fade-in. channel_mask is a bitfield (0b0001 = ch0 only, 0b1111 = all).
- `music(-1)` — Stop music.

---

## Map API

The map is 128×64 tiles. Each tile is one byte (sprite index 0-255). The upper 32 rows (0-31) are stored in `__map__`. The lower 32 rows (32-63) share memory with the lower sprite sheet (sprites 128-255).

- `map([cel_x, cel_y, sx, sy, cel_w, cel_h, [layers]])` — Draw map region starting at tile (cel_x, cel_y), drawn to screen at (sx, sy), size cel_w × cel_h tiles. `layers` is a bitfield that filters tiles by sprite flags.
- `mget(x, y)` — Get map tile (sprite index) at tile position.
- `mset(x, y, v)` — Set map tile at tile position to sprite index v.

### Map Collision Pattern
```lua
-- check if tile at pixel position is solid (flag 0 set)
function solid(x, y)
  return fget(mget(x\8, y\8), 0)  -- \ is integer divide in pico-8
end

-- check player collision with map
function check_map_collision(px, py, pw, ph)
  -- check all four corners
  return solid(px, py) or solid(px+pw-1, py)
    or solid(px, py+ph-1) or solid(px+pw-1, py+ph-1)
end
```

---

## Math & Utility API

### Math
- `abs(x)` — Absolute value
- `flr(x)` — Floor
- `ceil(x)` — Ceiling
- `min(a, b)` — Minimum
- `max(a, b)` — Maximum
- `mid(a, b, c)` — Middle value (great for clamping: `mid(lo, val, hi)`)
- `rnd(x)` — Random float from 0 to x (exclusive). `rnd()` = 0 to 1.
- `srand(seed)` — Set random seed
- `sqrt(x)` — Square root
- `sin(x)` — Sine (PICO-8 uses 0-1 range, not 0-2π! 0.25 = 90°)
- `cos(x)` — Cosine (same 0-1 range)
- `atan2(dx, dy)` — Angle in 0-1 range
- `sgn(x)` — Sign (-1, 0, or 1)
- `band(a,b)`, `bor(a,b)`, `bxor(a,b)`, `bnot(a)` — Bitwise ops
- `shl(a,b)`, `shr(a,b)`, `lshr(a,b)`, `rotl(a,b)`, `rotr(a,b)` — Bit shifts

### Integer Division
- `a\b` — Integer division (equivalent to `flr(a/b)`)
- `a%b` — Modulo

### Coroutines
- `cocreate(fn)` — Create coroutine
- `coresume(co)` — Resume coroutine
- `costatus(co)` — Check status ("running", "suspended", "dead")
- `yield()` — Pause coroutine (resumes next frame if called from update)

### System
- `time()` or `t()` — Seconds since cart started
- `stat(n)` — System stats. `stat(1)` = CPU usage (1.0 = 100%). `stat(7)` = current FPS.
- `printh(str)` — Print to console (debug)
- `stop([msg])` — Stop execution
- `menuitem(index, label, callback)` — Add pause menu item (index 1-5)

---

## Table API

PICO-8 tables are Lua tables with extra convenience functions.

- `add(tbl, val, [index])` — Append val (or insert at index). Returns val.
- `del(tbl, val)` — Remove first occurrence of val. Safe during iteration with `for...in all()`.
- `deli(tbl, i)` — Remove by index.
- `count(tbl, [val])` — Count elements (or occurrences of val).
- `foreach(tbl, fn)` — Call fn(v) for each element.
- `all(tbl)` — Iterator: `for v in all(tbl) do ... end`
- `pairs(tbl)` — Iterator with keys: `for k,v in pairs(tbl) do ... end`
- `pack(...)` — Pack args into table
- `unpack(tbl)` — Unpack table to args
- `split(str, [sep], [convert])` — Split string into table. `split("1,2,3",",",true)` → {1,2,3}

---

## String API

- `#str` — Length
- `sub(str, start, [end])` — Substring (1-indexed)
- `tostr(val, [format])` — Convert to string. format=true for hex.
- `tonum(str)` — Convert to number
- `chr(n)` — Number to character
- `ord(str, [i])` — Character to number

---

## Memory Layout

PICO-8 has 32KB of addressable memory:

```
0x0000-0x0FFF  Sprite sheet (lower, sprites 0-127)
0x1000-0x1FFF  Sprite sheet (upper, sprites 128-255) / Map (lower half)
0x2000-0x2FFF  Map (upper half, rows 0-31)
0x3000-0x30FF  Sprite flags
0x3100-0x31FF  Music
0x3200-0x42FF  Sound effects
0x4300-0x55FF  General purpose / custom data
0x5E00-0x5EFF  Persistent cart data (64 numbers via dset/dget)
0x5F00-0x5F7F  Draw state (palette, camera, clip, etc.)
0x6000-0x7FFF  Screen (8KB, 128×128 pixels, 2 pixels per byte)
```

- `peek(addr)` / `poke(addr, val)` — Read/write single byte
- `peek2(addr)` / `poke2(addr, val)` — Read/write 16-bit
- `peek4(addr)` / `poke4(addr, val)` — Read/write 32-bit (fixed point)
- `memcpy(dest, src, len)` — Copy bytes
- `memset(addr, val, len)` — Fill bytes
- `dget(index)` / `dset(index, val)` — Persistent data (survives cart reload, index 0-63)
- `cartdata("id")` — Enable persistent data with a unique cart ID

---

## .p8 File Format Specification

A `.p8` file is plain text with this exact structure:

```
pico-8 cartridge // http://www.pico-8.com/version 42
version 42
__lua__
[lua source code]
__gfx__
[128 lines, each exactly 128 hex characters]
__gff__
[2 lines, each exactly 256 hex characters]
__map__
[32 lines, each exactly 256 hex characters]
__sfx__
[64 lines, each exactly 168 hex characters]
__music__
[64 lines, each exactly 11 characters]
```

**CRITICAL:** Every section must have exactly the right number of lines with exactly the right number of characters per line. Use `0` to pad unused data.

---

## Sprite Sheet Hex Encoding

The `__gfx__` section is 128 lines × 128 hex characters = 128×128 pixels.

Each hex character is one pixel. The 16×16 grid of 8×8 sprites is laid out as:

```
Sprite 0  | Sprite 1  | Sprite 2  | ... | Sprite 15
(cols 0-7)|(cols 8-15) |(cols 16-23)|    |(cols 120-127)
----------+-----------+-----------+-----+-----------
Sprite 16 | Sprite 17 | ...             | Sprite 31
...
Sprite 240| Sprite 241| ...             | Sprite 255
```

**To place a sprite at index N:**
- Top-left pixel position on sheet: `x = (N % 16) * 8`, `y = flr(N / 16) * 8`
- This means the sprite's pixels occupy rows y to y+7, columns x to x+7 of the `__gfx__` data

**Example: Drawing sprite 0 (a simple arrow pointing right)**

Each row of the sprite is 8 hex characters at columns 0-7 of the gfx line:
```
Row 0: 00010000    (a dot near top)
Row 1: 00011000    
Row 2: 00011100    
Row 3: 77711110    (body + arrow)
Row 4: 77711110    
Row 5: 00011100    
Row 6: 00011000    
Row 7: 00010000    
```

These go into columns 0-7 of __gfx__ lines 0-7. The rest of columns 8-127 on those lines belong to sprites 1-15 on that row.

**Building a full __gfx__ line:**
Line 0 = [sprite0_row0][sprite1_row0][sprite2_row0]...[sprite15_row0]
Each bracket is 8 hex chars, totaling 128.

For empty/unused sprites, fill with `00000000`.

---

## Sprite Flags Encoding

The `__gff__` section has 2 lines of 256 hex characters each = 256 bytes total, one byte per sprite (0-255).

Each byte stores 8 boolean flags (bits 0-7) for that sprite. Hex encoding: two hex chars per byte.

```
Line 0: sprites 0-127   (256 hex chars = 128 bytes)  
Line 1: sprites 128-255 (256 hex chars = 128 bytes)
```

Sprite N's flags byte is at position N*2 (two hex chars).

**Common flag usage:**
- Flag 0 (bit 0, value 0x01): Solid/collision
- Flag 1 (bit 1, value 0x02): Hazard/damage
- Flag 2 (bit 2, value 0x04): Collectible
- Flags 3-7: User-defined

**Example:** Sprite 3 is solid (flag 0) → byte value = 0x01 → hex "01"
Place "01" at chars 6-7 of __gff__ line 0 (sprite 3 × 2 = position 6).

**Checking flags in code:**
```lua
fget(sprite_num, flag_num)  -- returns true/false
fset(sprite_num, flag_num, val)  -- set a flag
fget(sprite_num)  -- returns bitfield of all flags
```

---

## Map Data Encoding

The `__map__` section has 32 lines of 256 hex characters each. This represents the upper half of the map (rows 0-31, 128 tiles wide).

Each tile is one byte = 2 hex characters = a sprite index (0-255).

```
Line 0: map row 0, tiles 0-127 (each tile = 2 hex chars, 256 chars total)
Line 1: map row 1
...
Line 31: map row 31
```

**Example:** To place sprite 5 at tile position (3, 0):
Position in line 0 = 3 × 2 = chars 6-7, value "05".

To place sprite 16 (hex 0x10) at tile (0, 1):
Position in line 1 = chars 0-1, value "10".

An empty map is all "00" (which displays sprite 0 — be aware if sprite 0 has pixel data, it will render everywhere. Use a blank sprite 0 or set map tiles to a known empty sprite).

---

## SFX Data Encoding

Each of the 64 SFX lines in `__sfx__` is 168 hex characters encoding:

```
[editor_mode: 2 chars][speed: 2 chars][loop_start: 2 chars][loop_end: 2 chars][32 notes × 5 chars each = 160 chars]
```

Total: 2 + 2 + 2 + 2 + 160 = 168 characters.

**Header (8 chars):**
- `editor_mode` (2 hex): Usually "01" for pitch mode
- `speed` (2 hex): Playback speed (01 = fastest, 20 = slowish). Lower = faster. Common: 08-20.
- `loop_start` (2 hex): Loop start note (00-1f)
- `loop_end` (2 hex): Loop end note (00-1f, 00 = no loop)

**Each note (5 hex chars):**
```
[pitch: 2 chars][waveform: 1 char][volume: 1 char][effect: 1 char]
```

- `pitch`: 00-3f (0-63, C-0 to D#-5). Common: 18 = C-2, 1c = E-2, 1f = G-2, 24 = C-3.
- `waveform`: 0=triangle, 1=tilted saw, 2=saw, 3=square, 4=pulse, 5=organ, 6=noise, 7=phaser
- `volume`: 0-7 (0=silent, 7=loudest). Use 5 as a good default.
- `effect`: 0=none, 1=slide, 2=vibrato, 3=drop, 4=fade_in, 5=fade_out, 6=arpeggio fast, 7=arpeggio slow

**Example — A simple "jump" sound effect (SFX 0):**
Quick ascending pitch with triangle wave:
```
010800001835018350183501a3501c3501e350203502235024350000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
```
- Header: `01` mode, `08` speed, `00` loop start, `00` no loop
- Notes: ascending pitches 18→24 with triangle(3) vol 5 no effect, then silence (00000)

**A blank/unused SFX line:**
```
001000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
```

---

## Music Data Encoding

Each of the 64 music lines is exactly 11 characters:

```
[flags: 2 hex chars] [ch0: 2 hex][ch1: 2 hex][ch2: 2 hex][ch3: 2 hex]
```

There is a space between the flags and the channel data.

**Flags byte:**
- Bit 0 (0x01): Loop start
- Bit 1 (0x02): Loop end  
- Bit 2 (0x04): Stop at end

**Channel values:** Each is a SFX index (00-63/0x00-0x3f). Add 0x40 to indicate the channel is disabled. So `41` means "channel disabled" (0x40 + 1, but the SFX index doesn't matter when disabled).

**Example — A simple 2-pattern loop using SFX 4-7:**
```
01 04054141    (pattern 0: loop start, ch0=sfx4, ch1=sfx5, ch2+3 disabled)
02 06074141    (pattern 1: loop end, ch0=sfx6, ch1=sfx7, ch2+3 disabled)
```

**Unused music line:**
```
00 41414141
```
(All channels disabled, no flags)

---

## Token Counting Rules

PICO-8 has an 8192 token limit. Understanding what counts helps stay within budget.

**Each counts as 1 token:**
- Each identifier (variable name, function name): `player` = 1
- Each number literal: `42` = 1, `3.14` = 1
- Each operator: `+`, `-`, `*`, `/`, `<`, `>`, `==`, `!=`, `..`, `\` = 1 each
- Each keyword: `if`, `then`, `else`, `elseif`, `end`, `for`, `while`, `do`, `function`, `return`, `local`, `and`, `or`, `not`, `in`, `repeat`, `until`, `goto` = 1 each
- Each punctuation: `(`, `)`, `{`, `}`, `[`, `]`, `,`, `.`, `:`, `=`, `;` = 1 each (mostly)
- String literals: 1 token each (regardless of length!)
- `...` (varargs): 1 token

**Free (0 tokens):**
- Comments (`--` and `--[[ ]]`)
- Whitespace and newlines
- The names of built-in functions when called (e.g., `spr` in `spr(1,0,0)` is free)
  - But only the name itself; the parens and args still cost tokens

**Tips to save tokens:**
- Short variable names: `p` instead of `player` (each use costs 1 token)
- String packing: store data as strings and parse them (strings are 1 token regardless of length)
- `a+=1` costs fewer tokens than `a=a+1` (compound assignment)
- Single-line if: `if (cond) stmt` — saves the `then`/`end` tokens
- `x\8` instead of `flr(x/8)` — saves 2 tokens
- Use `split()` to turn string data into tables efficiently
