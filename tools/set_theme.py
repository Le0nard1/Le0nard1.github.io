"""
Colour schemes of the website.

A scheme can be given as a few colours, and the full theme is derived from them: background,
surface, text, muted text, borders, primary and accent, for light and dark mode, with text
contrast checked against WCAG AA (4.5:1) and corrected where it falls short.

    python tools/set_theme.py list
    python tools/set_theme.py add ocean "#0b6e99,#e07a1f"            # derive and store
    python tools/set_theme.py add ocean "#0b6e99,#e07a1f" --use      # ... and publish it
    python tools/set_theme.py add mine "primary=#7a1f5c,accent=#f2b134,bg=#fbf8f3"
    python tools/set_theme.py use ocean                              # publish a stored theme
    python tools/set_theme.py check

A plain list of colours is sorted by role: a very light colour becomes the background, a very
dark one the text, and the most saturated ones primary and accent. Missing roles are derived.
``use`` writes assets/theme.css; to preview without publishing, open index.html?theme=<name>.
"""
from __future__ import annotations

import colorsys
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "themes" / "themes.json"
CSS = ROOT / "assets" / "theme.css"
ROLES = ("bg", "surface", "text", "muted", "border", "primary", "accent", "on-primary", "on-accent")


def rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"not a hex colour: #{h}")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hexa(c):
    return "#" + "".join(f"{round(max(0, min(1, v)) * 255):02x}" for v in c)


def mix(a, b, t):
    """``t`` of the way from colour ``a`` to colour ``b``."""
    return hexa([x + (y - x) * t for x, y in zip(rgb(a), rgb(b))])


def luminance(h):
    lin = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb(h)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def saturation(h):
    return colorsys.rgb_to_hls(*rgb(h))[2]


def rotate(h, degrees):
    hh, l, s = colorsys.rgb_to_hls(*rgb(h))
    return hexa(colorsys.hls_to_rgb((hh + degrees / 360) % 1, l, s))


def readable(fg, bg, target=4.5):
    """Move ``fg`` towards black or white, whichever lies away from ``bg``, until it reaches
    the target contrast. Returns the colour and whether it had to change."""
    goal = "#000000" if luminance(bg) > 0.18 else "#ffffff"
    for i in range(41):
        c = mix(fg, goal, i / 40)
        if contrast(c, bg) >= target:
            return c, i > 0
    return goal, True


def on(colour, text):
    return "#ffffff" if contrast("#ffffff", colour) >= contrast(text, colour) else text


def roles_from(spec):
    """Parse ``#a,#b`` or ``primary=#a,bg=#b`` into a dict of the given roles."""
    parts = [p.strip() for p in spec.split(",") if p.strip()]
    if all("=" in p for p in parts):
        given = {k.strip(): hexa(rgb(v)) for k, v in (p.split("=", 1) for p in parts)}
        unknown = set(given) - set(ROLES)
        if unknown:
            raise ValueError(f"unknown roles {sorted(unknown)}; use {', '.join(ROLES)}")
        return given
    colours = [hexa(rgb(p)) for p in parts]
    given = {}
    light = [c for c in colours if luminance(c) > 0.8]
    dark = [c for c in colours if luminance(c) < 0.03]
    if light:
        given["bg"] = max(light, key=luminance)
    if dark:
        given["text"] = min(dark, key=luminance)
    brand = sorted((c for c in colours if c not in given.values()), key=saturation, reverse=True)
    for role, c in zip(("primary", "accent"), brand):
        given[role] = c
    return given


def derive(given):
    """Full light and dark themes from some roles, plus notes on every correction."""
    notes = []
    primary = given.get("primary", "#2f6f8f")
    accent = given.get("accent", rotate(primary, 150))
    bg = given.get("bg", mix("#ffffff", primary, 0.02))
    text = given.get("text", mix(primary, "#000000", 0.85))
    if contrast(text, bg) < 7:
        text, _ = readable(text, bg, 7)
        notes.append("text darkened for contrast")
    light = dict(bg=bg, surface=given.get("surface", mix(bg, primary, 0.045)), text=text,
                 muted=given.get("muted", mix(text, bg, 0.38)),
                 border=given.get("border", mix(text, bg, 0.86)), primary=primary, accent=accent)
    for role in ("primary", "muted"):
        light[role], changed = readable(light[role], light["bg"])
        if changed:
            notes.append(f"light {role} adjusted to reach 4.5:1 on the background")
    light["on-primary"] = on(light["primary"], text)
    light["on-accent"] = on(light["accent"], text)

    dbg = mix(text, "#000000", 0.45)
    dark = dict(bg=dbg, surface=mix(dbg, primary, 0.12), text=mix(bg, "#ffffff", 0.3),
                muted=mix(mix(bg, "#ffffff", 0.3), dbg, 0.35), border=mix(dbg, "#ffffff", 0.14),
                primary=mix(primary, "#ffffff", 0.25), accent=mix(accent, "#ffffff", 0.15))
    for role in ("text", "primary", "muted"):
        dark[role], changed = readable(dark[role], dark["bg"])
        if changed:
            notes.append(f"dark {role} adjusted to reach 4.5:1 on the background")
    dark["on-primary"] = on(dark["primary"], dbg)
    dark["on-accent"] = on(dark["accent"], dbg)
    return dict(light=light, dark=dark), notes


def css(theme, name):
    block = lambda t, pad: "\n".join(f"{pad}--{k}: {v};" for k, v in t.items())
    return (f"/* Theme \"{name}\", written by tools/set_theme.py. Edit themes/themes.json or run\n"
            f"   the tool instead of editing this file. */\n"
            f":root {{\n{block(theme['light'], '  ')}\n  color-scheme: light dark;\n}}\n\n"
            f"@media (prefers-color-scheme: dark) {{\n  :root {{\n{block(theme['dark'], '    ')}\n  }}\n}}\n")


def load():
    return json.loads(STORE.read_text(encoding="utf8")) if STORE.exists() else {"active": None, "themes": {}}


def save(store):
    STORE.parent.mkdir(exist_ok=True)
    STORE.write_text(json.dumps(store, indent=2) + "\n", encoding="utf8")


def report(name, theme):
    lt, dk = theme["light"], theme["dark"]
    print(f"{name}: text {contrast(lt['text'], lt['bg']):.1f}:1, links {contrast(lt['primary'], lt['bg']):.1f}:1, "
          f"dark text {contrast(dk['text'], dk['bg']):.1f}:1, dark links {contrast(dk['primary'], dk['bg']):.1f}:1")


def main(argv):
    store = load()
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd = argv[0]
    if cmd == "list":
        for name in store["themes"]:
            print(("* " if name == store["active"] else "  ") + name + "   " + store["themes"][name]["input"])
    elif cmd == "add":
        name, spec = argv[1], argv[2]
        theme, notes = derive(roles_from(spec))
        store["themes"][name] = dict(input=spec, **theme)
        for n in notes:
            print("note:", n)
        report(name, theme)
        if "--use" in argv:
            store["active"] = name
            CSS.write_text(css(theme, name), encoding="utf8")
            print("published", name)
        save(store)
    elif cmd == "use":
        name = argv[1]
        store["active"] = name
        CSS.write_text(css(store["themes"][name], name), encoding="utf8")
        save(store)
        print("published", name)
    elif cmd == "check":
        for name, theme in store["themes"].items():
            report(name, theme)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
