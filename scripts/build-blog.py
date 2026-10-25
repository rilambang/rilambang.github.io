#!/usr/bin/env python3
"""Emit the blog as plain static HTML into public/blog/.

Deliberately not a markdown pipeline and not a Vite multi-page entry: Vite copies
publicDir verbatim, so these land in docs/blog/ as real HTML with the prose in the
served file. A pasted link resolves cold, works with JS off, and is greppable in the
deployed bundle. No dependency, no router, no history-mode trap.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "public" / "blog"
SITE = "https://rilambang.github.io"
CARD = f"{SITE}/og.png"

# Palette comes from the app stylesheet, not from a copy of it. Diana's point: two hardcoded
# copies of the accent drift silently the first time the site is re-themed.
def read_tokens():
    css = (ROOT / "src" / "styles.css").read_text()
    block = css.split(":root {", 1)[1].split("}", 1)[0]
    out = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        k, v = line.strip().rstrip(";").split(":", 1)
        out[k.strip().lstrip('-')] = v.strip()
    return out


TOK = read_tokens()


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _lum(rgb):
    r, g, b = (_lin(x) for x in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _ratio(a, b):
    la, lb = _lum(a), _lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def _hex(v):
    return tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))


def _rgba(tok):
    """`rgba(9, 9, 16, 0.78)` -> ((9, 9, 16), 0.78). A plain hex token is opaque."""
    v = TOK[tok]
    if v.startswith("#"):
        return _hex(v), 1.0
    parts = v[v.find("(") + 1:v.rfind(")")].replace("/", " ").replace(",", " ").split()
    base = tuple(int(round(float(x))) for x in parts[:3])
    a = float(parts[3].rstrip("%"))
    return base, (a / 100 if parts[3].endswith("%") else a)


def _over(panel, behind):
    base, alpha = _rgba(panel)
    return tuple(alpha * c + (1 - alpha) * d for c, d in zip(base, _hex(behind)))


def check_bar():
    """A frosted panel decides the contrast of everything sitting on it, so its colour
    is not one value: it is the glass composited over whatever is behind it. Here that
    is the darkest gradient stop, the two coloured lights, and — for the sticky top bar —
    white screenshots scrolling underneath. Check every one of those, not the average.
    Change the glass, a gradient stop or a text token and the build fails instead of
    quietly thinning out."""
    checks = []
    for bg in ("bg-top", "bg-warm", "bg-cool"):
        panel = _over("glass", TOK[bg])
        checks += [(tok, panel, f"glass over {bg}") for tok in ("ink", "ink-soft", "muted", "accent")]
    for behind in ("#ffffff", TOK["bg"]):
        panel = _over("bar", behind)
        checks += [(tok, panel, f"bar over {behind}") for tok in ("ink", "ink-soft", "muted")]

    failures = []
    for tok, panel, label in checks:
        r = _ratio(_hex(TOK[tok]), panel)
        print(f"  {tok:9s} {TOK[tok]:9s} on {label:22s} {r:5.2f}:1")
        if r < 4.5:
            failures.append(f"{tok} ({TOK[tok]}) on {label} is {r:.2f}:1, under 4.5:1")

    if failures:
        raise SystemExit(
            "\n✗ " + "\n✗ ".join(failures) +
            "\n  Lighten the token, darken the panel, or thicken the glass.")


check_bar()

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root{{--bg:{bg};--bg-top:{bg-top};--bg-warm:{bg-warm};--bg-cool:{bg-cool};
  --ink:{ink};--ink-soft:{ink-soft};--muted:{muted};--line:{line};--edge:{edge};
  --accent:{accent};--tint:{tint};--warm:{warm};--surface:{surface};--figure:{figure};
  --glass:{glass};--bar:{bar};--rim:{rim};--radius:{radius};
  --sans:{sans};--display:{display};--mono:{mono}}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;min-height:100vh;background:var(--bg);color:var(--ink);
  font:17px/1.7 {sans};-webkit-font-smoothing:antialiased;overflow-x:hidden}}
/* the field, on a fixed pseudo-element: `background-attachment: fixed` is ignored
   by iOS Safari, which would scroll the gradient and flicker the sticky bar. */
body::before{{content:"";position:fixed;inset:0;z-index:-1;background:
  radial-gradient(1120px 780px at 6% -14%,rgba(98,64,236,.58) 0%,rgba(98,64,236,0) 58%),
  radial-gradient(1000px 720px at 100% -8%,rgba(12,122,172,.52) 0%,rgba(12,122,172,0) 55%),
  radial-gradient(1100px 820px at 46% 116%,rgba(76,46,158,.42) 0%,rgba(76,46,158,0) 62%),
  radial-gradient(760px 620px at 88% 62%,rgba(16,118,158,.24) 0%,rgba(16,118,158,0) 64%),
  radial-gradient(720px 600px at 6% 88%,rgba(92,60,204,.22) 0%,rgba(92,60,204,0) 66%),
  linear-gradient(180deg,var(--bg-top) 0%,var(--bg) 52%,#05050a 100%)}}
.wrap{{max-width:760px;margin:0 auto;padding:0 24px 80px}}
.top{{position:sticky;top:0;z-index:5;margin:0 calc(50% - 50vw) 52px;
  padding:16px max(24px,calc(50vw - 356px));
  display:flex;justify-content:space-between;align-items:baseline;
  background:var(--bar);-webkit-backdrop-filter:blur(22px) saturate(160%);
  backdrop-filter:blur(22px) saturate(160%);
  border-bottom:1px solid var(--line);font-size:13px;letter-spacing:.01em;
  color:var(--ink-soft)}}
.top a{{color:var(--ink-soft);text-decoration:none}}
.top a:hover{{color:var(--ink)}}
.top .who{{font-weight:600;color:var(--ink)}}
h1,h2,h3{{font-family:{display};font-weight:600;color:var(--ink)}}
h1{{font-size:44px;line-height:1.07;letter-spacing:-.032em;margin:0 0 16px;text-wrap:balance}}
h2{{font-size:23px;line-height:1.2;letter-spacing:-.022em;margin:44px 0 12px}}
h3{{font-size:17px;margin:28px 0 8px}}
p,li{{color:var(--ink-soft)}}
strong{{color:var(--ink);font-weight:600}}
.lede{{font-size:19.5px;line-height:1.6;color:var(--ink-soft);margin:0 0 38px}}
ul,ol{{padding-left:22px}}
li{{margin:7px 0}}
a{{color:var(--accent);text-decoration:none;border-bottom:1px solid transparent}}
a:hover{{border-color:var(--accent)}}
a:focus-visible{{outline:2px solid var(--accent);outline-offset:3px;border-radius:3px}}
code{{font:14px/1.5 var(--mono);background:var(--warm);padding:2px 6px;
  border:1px solid var(--line);border-radius:6px;color:var(--ink)}}
pre{{background:rgba(0,0,0,.3);border:1px solid var(--line);border-radius:14px;
  padding:16px 18px;overflow-x:auto;font-size:13.5px}}
pre code{{background:none;border:0;padding:0;color:var(--ink-soft)}}
blockquote{{margin:30px 0;padding:4px 0 4px 20px;border-left:2px solid var(--accent);
  font-size:18px;color:var(--ink-soft)}}
blockquote p{{margin:0}}
.chip{{display:inline-block;font-family:var(--mono);font-size:10.5px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--accent);background:rgba(138,180,255,.1);
  border:1px solid var(--accent);border-radius:999px;padding:4px 11px;margin:0 0 18px}}
.meta{{font-family:var(--mono);font-size:11px;letter-spacing:.05em;text-transform:uppercase;
  color:var(--muted);margin:0 0 40px}}
.fig{{margin:34px 0 40px;border:1px solid var(--rim);border-radius:18px;
  background:var(--figure);padding:18px;overflow-x:auto;
  box-shadow:0 26px 56px -32px rgba(0,0,0,.9),inset 0 1px 0 rgba(255,255,255,.07)}}
.fig svg{{max-width:100%;height:auto}}
.fig figcaption{{font-size:13px;line-height:1.55;color:var(--muted);margin-top:14px;
  padding-top:12px;border-top:1px solid var(--line)}}
.sources{{margin-top:56px;border-top:1px solid var(--line);padding-top:20px;font-size:14px}}
.sources h2{{font-family:var(--mono);font-size:11px;letter-spacing:.14em;
  text-transform:uppercase;color:var(--muted);margin:0 0 12px;font-weight:500}}
.sources li{{margin:7px 0;color:var(--muted)}}
.foot{{margin-top:48px;border-top:1px solid var(--line);padding-top:20px;
  font-size:13px;line-height:1.6;color:var(--muted)}}
.pager{{display:flex;justify-content:space-between;gap:16px;margin-top:32px;
  padding-top:18px;border-top:1px solid var(--line);font-size:14px}}
.pager a{{text-decoration:none;border-bottom:0}}
.pager a:hover{{color:var(--ink)}}
.pager span{{color:var(--muted)}}
/* index */
.lede--index{{margin-bottom:44px}}
.cards{{list-style:none;padding:6px 24px;margin:0;border-radius:18px;
  background:linear-gradient(160deg,rgba(255,255,255,.09) 0%,rgba(255,255,255,.032) 46%,rgba(255,255,255,.06) 100%);
  -webkit-backdrop-filter:blur(30px) saturate(180%);backdrop-filter:blur(30px) saturate(180%);
  border:1px solid var(--rim);box-shadow:0 30px 70px -34px rgba(0,0,0,.95),
  inset 0 1px 0 rgba(255,255,255,.24)}}
.cards li{{border-bottom:1px solid var(--line);padding:24px 0;display:grid;
  grid-template-columns:56px 1fr;gap:20px}}
.cards li:last-child{{border-bottom:0}}
.cards h2{{margin:0 0 7px;font-size:23px}}
.cards a{{text-decoration:none;border-bottom:0}}
.cards a:hover h2{{color:var(--accent)}}
.cards p{{margin:0;color:var(--muted);font-size:15.5px}}
.num{{font:500 12px/1 var(--mono);color:var(--accent);letter-spacing:.06em;
  border:1px solid var(--line);border-radius:999px;padding:9px 0;text-align:center;
  background:rgba(255,255,255,.04);height:fit-content}}
/* ── motion ────────────────────────────────────────────────────────────────
   Transform only, never opacity, on anything a reader needs. Diagrams draw their
   connectors, which are decoration: if an animation never runs, a box is a few
   pixels low and a line is already there, and nothing is ever invisible.        */
@keyframes rise{{from{{transform:translateY(16px)}}to{{transform:none}}}}
@keyframes draw{{to{{stroke-dashoffset:0}}}}
.post-head > *{{animation:rise .6s cubic-bezier(.22,.7,.3,1) both}}
.post-head > :nth-child(2){{animation-delay:.05s}}
.post-head > :nth-child(3){{animation-delay:.1s}}
.fig .d{{stroke-dasharray:var(--len,320);stroke-dashoffset:var(--len,320);
  animation:draw .9s ease-out .2s both}}
.fig .n{{animation:rise .7s cubic-bezier(.22,.7,.3,1) both}}
.fig .n:nth-child(2){{animation-delay:.06s}}
.fig .n:nth-child(3){{animation-delay:.12s}}
.fig .n:nth-child(4){{animation-delay:.18s}}
.fig .n:nth-child(5){{animation-delay:.24s}}
.fig .n:nth-child(6){{animation-delay:.3s}}
/* scroll-reveal, guarded: unsupported engine applies nothing and shows everything */
@supports (animation-timeline:view()){{
  article > h2,article > p,article > ul,article > ol,article > blockquote,
  article > pre,article > figure{{
    animation:rise linear both;animation-timeline:view();
    animation-range:entry 4% cover 26%}}
}}
@media (prefers-reduced-motion:reduce){{
  html{{scroll-behavior:auto}}
  .post-head > *,.fig .d,.fig .n,article > h2,article > p,article > ul,article > ol,
  article > blockquote,article > pre,article > figure{{animation:none}}
  .fig .d{{stroke-dasharray:none;stroke-dashoffset:0}}
}}
@media (max-width:600px){{
  .wrap{{padding:0 18px 60px}}h1{{font-size:32px}}h2{{font-size:21px}}
  .cards{{padding:4px 18px}}.cards li{{grid-template-columns:1fr;gap:8px}}.num{{display:none}}
  .fig{{padding:12px}}
  /* Diagrams keep their 640px drawing and scroll. Shrinking them to the column
     would render 11.5px labels at six pixels and call that responsive. */
  .fig svg{{max-width:none}}
}}
""".format(**TOK)


# ── figures ───────────────────────────────────────────────────────────────────
# Diagrams are SVG, drawn from text. That keeps them inside every existing guard:
# the prose deny-list reads them, they carry no EXIF, no screenshot of a product or
# a source tree is involved, and the filename never becomes a published URL that
# names something. They are also the only illustrations that stay exactly as general
# as the paragraph next to them.

F_INK = TOK["ink"]
F_MUTED = TOK["muted"]
F_LINE = TOK["line"]
F_ACC = TOK["accent"]
F_TINT = TOK["tint"]
F_WARM = TOK["warm"]
FONT = "font-family='Helvetica Neue,Helvetica,Arial,sans-serif'"


def _box(x, y, w, h, title, sub="", accent=False, n=0):
    fill = F_TINT if accent else TOK["surface"]
    stroke = F_ACC if accent else F_LINE
    t = (f"<text x='{x + 14}' y='{y + (26 if sub else h / 2 + 5)}' font-size='13' "
         f"font-weight='600' fill='{F_INK}'>{html.escape(title)}</text>")
    s = ""
    if sub:
        s = (f"<text x='{x + 14}' y='{y + 46}' font-size='11.5' fill='{F_MUTED}'>"
             f"{html.escape(sub)}</text>")
    return (f"<g class='n'><rect x='{x}' y='{y}' width='{w}' height='{h}' rx='10' "
            f"fill='{fill}' stroke='{stroke}'/>"
            f"<rect x='{x}' y='{y}' width='3' height='{h}' rx='1.5' fill='{F_ACC}'/>"
            f"{t}{s}</g>")


def _line(x1, y1, x2, y2, draw=True):
    cls = " class='d'" if draw else ""
    return (f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='{F_LINE}' "
            f"stroke-width='1.5'{cls}/>")


def _arrow(x1, y1, x2, y2):
    """Vertical or horizontal only, so the head is trivial to place."""
    head = 4.5
    if x1 == x2:
        d = -1 if y2 < y1 else 1
        tip = (f"<polygon points='{x2},{y2} {x2 - head},{y2 - d * head * 1.6} "
               f"{x2 + head},{y2 - d * head * 1.6}' fill='{F_LINE}'/>")
    else:
        d = -1 if x2 < x1 else 1
        tip = (f"<polygon points='{x2},{y2} {x2 - d * head * 1.6},{y2 - head} "
               f"{x2 - d * head * 1.6},{y2 + head}' fill='{F_LINE}'/>")
    return _line(x1, y1, x2, y2) + tip


def _cap(x, y, text, size=11.5, color=None, anchor="start", weight="400"):
    return (f"<text x='{x}' y='{y}' font-size='{size}' fill='{color or F_MUTED}' "
            f"text-anchor='{anchor}' font-weight='{weight}'>{html.escape(text)}</text>")


def _svg(label, h, body, w=640):
    return (f"<svg viewBox='0 0 {w} {h}' width='{w}' height='{h}' role='img' "
            f"aria-label='{html.escape(label)}' {FONT} "
            f"xmlns='http://www.w3.org/2000/svg'>{body}</svg>")


def fig_two_questions():
    b = _box(20, 16, 280, 62, "Is the device supervised?",
             "MDM or Apple Configurator")
    b += _box(340, 16, 280, 62, "Does the OS already have a mode?",
              "before you design a countermeasure")
    for x in (160, 480):
        b += _arrow(x, 78, x, 132)
    b += _line(110, 132, 520, 132)
    for x in (110, 310, 520):
        b += _arrow(x, 132, x, 168)
    b += _box(20, 170, 180, 72, "Assessment mode", "after Apple grants it", accent=True)
    b += _box(220, 170, 180, 72, "Single app mode", "and it supersedes")
    b += _box(420, 170, 200, 72, "A human proctor", "where every system ends up")
    b += _cap(20, 272, "The framework covers the app. It does not cover the room.")
    return _svg("Two questions decide what a proctored exam app can enforce, "
                "and three outcomes they lead to", 286, b)


def fig_layers():
    rows = [
        (90, 44, "App shell", "composition, navigation, configuration"),
        (170, 44, "Feature modules", "the screens and their state"),
        (250, 44, "Shared services", "networking, persistence, logging"),
        (330, 44, "Leaves", "tokens and models — nothing depends on them"),
    ]
    b = ""
    for i, (y, h, t, s) in enumerate(rows):
        x = 20 + i * 6
        b += _box(x, y, 530 + i * 22, h, t, s)
    for i in range(3):
        x = 20 + i * 6 + (530 + i * 22) / 2
        b += _arrow(x, rows[i][0] + 44, x, rows[i + 1][0] - 4)
    b += _cap(20, 400, "depends on ↓   A cycle used to be invisible; here it is a compile error.")
    return _svg("A modular app as four layers from a thin app shell down to leaf packages, "
                "with dependencies pointing downward", 414, b)


def fig_incremental():
    def grid(x, y, accent_col, label, sub):
        g = ""
        for i in range(4):
            for j in range(3):
                cx, cy = x + i * 34, y + j * 30
                on = (i * 3 + j) == accent_col
                g += (f"<rect x='{cx}' y='{cy}' width='28' height='24' rx='5' "
                      f"fill='{F_ACC if on else F_WARM}' stroke='{F_LINE}'/>")
        return _cap(x, y - 12, label, 12.5, F_INK, weight="600") + g + _cap(x, y + 118, sub)
    b = _box(20, 16, 600, 40, "One target: a change recompiles its neighbours")
    b += grid(40, 96, 5, "one file changed", "eleven boxes rebuild anyway")
    b += grid(360, 96, 5, "the same change, split", "one group rebuilds")
    b += _cap(20, 250, "Same edit, same machine. The unit of work is the only thing that moved.")
    return _svg("The same one-file change rebuilding almost a whole single target, "
                "against rebuilding one module of several", 268, b)


def fig_migration():
    steps = ["Leaf screens", "Shared services", "App shell", "Navigation last"]
    b = ""
    for i, s in enumerate(steps):
        x = 20 + i * 155
        b += _box(x, 30, 140, 58, s, "", accent=(i == 0))
        if i < 3:
            b += _arrow(x + 140, 59, x + 155, 59)
    b += _box(20, 130, 600, 58, "One owner of the stack, for the whole migration",
              "the other side renders content and reports events — it does not push")
    b += _cap(20, 216, "Availability is a plan, not an afterthought: every adoption "
                       "above your floor needs a fallback.")
    return _svg("A UIKit to SwiftUI migration as four ordered steps, with a single owner "
                "of navigation underneath the whole sequence", 230, b)


def fig_three_copies():
    b = _box(20, 16, 190, 62, "Design source", "where the value is decided")
    b += _box(225, 16, 190, 62, "Token file", "the name that carries intent")
    b += _box(430, 16, 190, 62, "A literal", "added at 6pm, on a deadline")
    b += _arrow(115, 78, 115, 122)
    b += _arrow(320, 78, 320, 122)
    b += _line(115, 122, 320, 122)
    b += _arrow(217, 122, 217, 150)
    b += _box(20, 152, 395, 62, "One value, two owners",
              "a rename is a two-file change and review can see it", accent=True)
    b += _arrow(525, 78, 525, 150)
    b += _box(430, 152, 190, 62, "Drift", "it just ages badly")
    b += _cap(20, 246, "The third box is the one that decides whether the system survives screen three.")
    return _svg("A design value with two traceable owners and a third copy that drifts "
                "away from both", 260, b)


def fig_review_order():
    rows = [
        ("1", "Does it do what the description says?", False),
        ("2", "Can it crash?", False),
        ("3", "What is the failure path?", False),
        ("4", "What was deleted?", False),
        ("5", "Style — and usually not at all", True),
    ]
    b = ""
    for i, (n, t, last) in enumerate(rows):
        y = 16 + i * 46
        b += _box(20, y, 600, 38, "")
        b += _cap(40, y + 25, n, 12.5, F_ACC, weight="600")
        b += _cap(64, y + 25, t, 13, F_MUTED if last else F_INK)
    b += _cap(20, 268, "Read in this order. Starting at 5 wastes the attention that 2 needed.")
    return _svg("The order an iOS pull request is read in, from intent through crash risk "
                "to style last", 282, b)


def fig_stack():
    rows = [
        ("UI", "SwiftUI first, UIKit where the platform still requires it"),
        ("Navigation", "one owner, always"),
        ("Feature modules", "local packages, narrow public surfaces"),
        ("Data", "the platform's own persistence, constraints before validation"),
        ("Platform", "the OS before a dependency"),
    ]
    b = ""
    for i, (t, s) in enumerate(rows):
        y = 16 + i * 50
        b += _box(20, y, 600, 42, "")
        b += _cap(38, y + 27, t, 13, F_ACC, weight="600")
        b += _cap(210, y + 27, s, 12.5, F_MUTED)
    b += _cap(20, 288, "Every choice priced by the next engineer's ability to debug it at 3am.")
    return _svg("The iOS stack as five layers, each with the rule that decides it", 300, b)


def fig_agent_loop():
    rows = [
        (16, "Written once", "conventions, boundaries, roles, stop conditions", True),
        (106, "Written per task", "the brief: exact paths, the invariant, what proves it", False),
        (196, "The only proof", "a hash, a byte count, a test that was red", True),
        (286, "Still a person", "specificity, secrets, anything irreversible", True),
    ]
    b = ""
    for i, (y, t, s, acc) in enumerate(rows):
        b += _box(20, y, 470, 64, t, s, accent=acc)
        if i < 3:
            b += _arrow(255, y + 64, 255, y + 86)
    b += _line(512, 16, 512, 350, draw=False)
    b += _line(500, 180, 524, 180, draw=False)
    b += _cap(528, 92, "you write")
    b += _cap(528, 262, "you check")
    b += _cap(20, 380, "A blank context window each time. The document is the only memory.")
    return _svg("Four checkpoints in an agent workflow: what is written once, what is written "
                "per task, the evidence accepted, and what stays a person's decision", 394, b)


def fig_pinning():
    b = _box(20, 16, 180, 64, "App commit", "what the repository records")
    b += _box(230, 16, 180, 64, "Dependency row", "ref: main", accent=True)
    b += _box(440, 16, 180, 64, "Code compiled", "whatever main was")
    b += _arrow(200, 48, 230, 48)
    b += _arrow(410, 48, 440, 48)
    b += _cap(20, 108, "Two of the three are pinned. The build is only as "
                       "reproducible as the loosest one.")
    b += _arrow(320, 80, 320, 132)
    b += _box(20, 134, 600, 64, "Log the resolved revision of every dependency",
              "and put the revision in the row instead of a branch name", accent=True)
    b += _cap(20, 222, "The log line costs nothing. The pin is what makes the "
                       "log line mean something.")
    return _svg("A build's inputs: the app commit, a dependency row that names a moving "
                "branch, and the code that was actually compiled — resolved by printing "
                "revisions and pinning them", 236, b)


def fig_four_gates():
    """A table rather than a flow: the point is that nothing moves between the three
    columns. Each row is a gate, the input it actually read, and the claim its green
    text was taken to make. The rules are drawn, not animated: .fig .d animates a 320px
    dash, and a 600px rule would render as a dash with a gap in it once it finishes."""
    head = 38
    b = _line(20, head + 6, 620, head + 6, draw=False)
    b += _cap(20, head, "GATE", 10.5, F_MUTED)
    b += _cap(150, head, "IT READ", 10.5, F_MUTED)
    b += _cap(392, head, "IT CERTIFIED", 10.5, F_MUTED)
    rows = [
        ("Lint gate", "a directory of checkouts", "the set that ships"),
        ("Pre-push", "filenames, not the source", "every suite in the target"),
        ("Deploy job", "a build number nobody bumped", "a new artifact"),
        ("Snapshots", "the previous test's session", "the screen as drawn"),
    ]
    for i, (gate, read, claim) in enumerate(rows):
        y = head + 6 + i * 58
        b += _line(20, y, 620, y, draw=False)
        b += _cap(20, y + 26, gate, 13, F_INK, weight="600")
        b += _cap(150, y + 26, read, 11.5, F_MUTED)
        b += _cap(392, y + 26, claim, 11.5, F_ACC)
    bottom = head + 6 + len(rows) * 58
    b += _line(20, bottom, 620, bottom, draw=False)
    b += _cap(20, bottom + 30,
              "Right column: what I assumed. Middle column: what the check actually touched.")
    return _svg("Four CI gates, the input each one actually read, and the claim its green "
                "result was believed to make", bottom + 46, b)


FIGURES = {
    "kiosk-and-assessment-apps": (
        fig_two_questions(),
        "What the platform will enforce, and what is left to a person. Apple's "
        "documentation says Single App Mode and Guided Access supersede assessment mode."),
    "splitting-an-app-into-local-packages": (
        fig_layers(),
        "The shape that pays: leaves that depend on nothing, a thin shell that owns "
        "composition, and a cycle that cannot compile."),
    "build-time-is-a-dependency-graph-problem": (
        fig_incremental(),
        "One edit, two build graphs. The machine is identical in both."),
    "uikit-to-swiftui-without-a-rewrite": (
        fig_migration(),
        "Progress in one direction, with the navigation seam held still."),
    "a-design-system-is-a-review-policy": (
        fig_three_copies(),
        "Two owners is a system. Three is a countdown."),
    "how-i-review-ios-pull-requests": (
        fig_review_order(),
        "Cheapest questions first, taste last."),
    "the-ios-stack-i-actually-reach-for": (
        fig_stack(),
        "Not preferences — the rule each layer is chosen by."),
    "ai-native-development-process": (
        fig_agent_loop(),
        "Four checkpoints. Two are writing, and the two that matter most are the ones I "
        "will not take on trust."),
    "what-a-green-build-does-not-prove": (
        fig_pinning(),
        "Three inputs, one of them moving. The fix is one column and one log line."),
    "four-gates-that-certified-nothing": (
        fig_four_gates(),
        "Four gates, one mistake each: the check touched one thing and was trusted "
        "about another. Nothing in the middle column is the shipping artifact."),
}

POSTS = [

    {
        "slug": "kiosk-and-assessment-apps",
        "tag": "Platform rules",
        "title": "Kiosk and assessment apps: what Apple will and won't let you lock",
        "summary": "The hardest problem in a proctored exam app is not the exam. It is that the OS owns the device, and your anti-cheat has to be something Apple agreed to.",
        "body": """
<p class="lede">The hardest problem in a proctored exam app is not the exam. It is that the
operating system owns the device, and every restriction you want has to be one Apple already
agreed to enforce.</p>

<p>Every team building assessment software has the same first instinct: build the lock.
Disable the home button, block the app switcher, kill notifications, watch for screenshots,
detect a second screen. It is a long list of interesting engineering, and almost all of it
is either impossible or unnecessary.</p>

<h2>Two questions decide everything</h2>

<p>Before writing a line of anti-cheat, answer these:</p>

<ol>
  <li><strong>Is the device supervised?</strong> A supervised device is enrolled and managed
  by an organisation — the school or the testing centre owns it and can configure it
  centrally. A student's own iPad is not supervised and never will be.</li>
  <li><strong>Does the OS already have a mode for this?</strong> If it does, your job is to
  turn it on correctly, not to reimplement it worse.</li>
</ol>

<p>Those two questions divide the problem cleanly, and they are the reason a kiosk app is a
smaller engineering project than it looks.</p>

<h2>What Apple actually provides</h2>

<p>For assessment software specifically, Apple ships the <strong>Automatic Assessment
Configuration</strong> framework. Its own summary is the clearest possible statement of
scope: <em>"Enter single-app mode and prevent students from accessing specific system
features while taking an exam."</em></p>

<p>Three properties of it are worth knowing before you plan anything:</p>

<ul>
  <li><strong>It needs no device management.</strong> Apple's own support documentation says
  securing an iPad or Mac for testing with a supported app "requires no additional setup or
  management, such as a device management service." An app that adopts this framework locks
  the device into itself automatically. That is the difference between shipping an exam mode
  to every student and shipping it only to schools with an MDM.</li>
  <li><strong>It is the app's decision, not the tester's.</strong> The app enables it, and
  while it is active the user cannot switch to another app. There is no setup flow the exam
  taker can skip, because there is nothing for them to do.</li>
  <li><strong>Manual modes win, and that is a trap.</strong> If Single App Mode or Guided
  Access is already enabled on the device, "that feature supersedes assessment mode
  restrictions." A school that pre-locked the iPads by hand is not getting your app's
  configuration — they are getting their own, and it may be stricter or looser than you
  assume.</li>
</ul>

<p><strong>And it is gated by an entitlement you have to ask Apple for.</strong> The framework
requires <code>com.apple.developer.automatic-assessment-configuration</code> — "a Boolean value
that indicates whether an app may create an assessment session" — and Apple's documentation is
explicit that you "must first get permission to use it" by submitting a request form. Without
it the assessment session does not begin and the app is just an app. That is lead time on a
product schedule, and it is the one item here that no amount of engineering removes. Ask for it
in week one.</p>

<p>Assessment mode arrived in iOS and iPadOS 13.4, and in macOS 10.15.4 — the same framework
answering the same product question on two platforms, rather than two separate anti-cheat
implementations.</p>

<h2>The part that is a product decision, not a technical one</h2>

<p>Once you know what the OS will do, the remaining work is a policy conversation dressed as
engineering:</p>

<p><strong>What do you do with a violation?</strong> A framework that prevents an action gives
you a clean story. A framework that merely observes one does not. If you cannot prevent it,
your options are to warn, to log, or to ignore — and each of those is a different product.
Discovery after the exam is not prevention, and telling a candidate they failed because of
telemetry they cannot see is not a defensible process.</p>

<p><strong>What do you do when the lock fails?</strong> Exam mode is a state the app enters,
which means it can also fail to enter — low battery, a crash, a force-quit, a device the OS
decided to restart. The honest design assumes the lock will break at least once, and decides
in advance what the exam does when it notices. An exam that silently continues in an unlocked
state is worse than one that visibly halts.</p>

<p><strong>Who is the fallback for?</strong> Assessment mode covers the app. It does not cover
a second phone on the desk, a written answer sheet, or a person helping. Every proctoring
system has a human layer eventually; deciding where your layer ends is cheaper than
discovering it during an incident.</p>

<h2>What I'd tell anyone starting this</h2>

<p>Read Apple's platform capabilities before designing the countermeasure, because the
countermeasures you invent yourself are the ones that get rejected, break on OS updates, or
quietly stop working when a device is configured differently than you assumed. The interesting
engineering in a proctored exam app is not the lock — it is the exam runtime: offline
resilience, autosave that survives a crash, a submission that is idempotent, and a state
machine that never loses a candidate's work. The lock is a configuration. Treat it like one,
and spend the effort where the candidate actually feels it.</p>
""",
        "sources": [
            ("Set up iPad and Mac to give tests and assessments — Apple Support", "https://support.apple.com/101976"),
            ("Automatic Assessment Configuration — Apple Developer Documentation", "https://developer.apple.com/documentation/automaticassessmentconfiguration"),
            ("com.apple.developer.automatic-assessment-configuration — entitlement and request form", "https://developer.apple.com/documentation/bundleresources/entitlements/com.apple.developer.automatic-assessment-configuration"),
            ("iOS Configuration and APIs for Kiosk and Assessment Apps — WWDC17 session 716", "https://developer.apple.com/videos/play/wwdc2017/716/"),
        ],
    },
    {
        "slug": "splitting-an-app-into-local-packages",
        "tag": "Modularisation",
        "title": "Splitting an app into local Swift packages: what breaks first",
        "summary": "The files move in a day. The boundaries take a quarter. Here is the order things actually break in, and the one rule that keeps the first week from turning into a public-API explosion.",
        "body": """
<p class="lede">Moving files into packages takes a day. Getting the boundaries right takes a
quarter. The gap between those two numbers is where most modularisation projects quietly
stall.</p>

<p>I have done this on more than one app now, and the failures are consistent enough to
predict. This is the order things actually break in.</p>

<h2>1. Resources, and the fact that they fail at runtime</h2>

<p>The first casualty is anything that reads from the bundle. A JSON fixture, a font, a
string file, an asset catalog image. Inside a package, the code needs
<code>Bundle.module</code>. Code that still reaches for <code>Bundle.main</code> compiles
perfectly and returns nil at runtime.</p>

<p>This is the worst class of breakage in the whole migration: it is invisible to the compiler,
invisible in code review, and usually caught by a user rather than a test. Sweep for
<code>Bundle.main</code> and <code>UIImage(named:)</code> <em>before</em> moving anything, and
decide per call site whether it belongs to the package or to the app.</p>

<h2>2. <code>internal</code> becomes <code>public</code>, and everything gets worse</h2>

<p>The moment code lives in another module, <code>internal</code> stops being enough. The
tempting response is to add <code>public</code> until it compiles. That is how a codebase ends
up with a package that exposes forty types and enforces nothing — the boundary exists
physically and not at all conceptually.</p>

<blockquote>The test I use: if a package needs more than a handful of public symbols, it is
not a module. It is a folder that happens to have a manifest.</blockquote>

<p>So the real work is not moving code, it is <em>designing the API you wish existed</em> and
then making the code fit behind it. Write the interface first. If it is awkward to write, the
boundary is in the wrong place, and you have found that out before the expensive part.</p>

<h2>3. Build settings stop being inherited</h2>

<p>A package does not inherit your app target's build settings. The Swift language version, the
warnings you had silenced, optimisation flags, the deployment target — all of it is declared in
the manifest and is now a decision someone has to make deliberately. Do it in one pass, or you
will spend a fortnight on warnings that appear in one module and not the adjacent one.</p>

<h2>4. Names collide immediately</h2>

<p>Every modular codebase has a <code>User</code>, a <code>Config</code>, an
<code>Extensions</code>, a <code>Logger</code>. Once they are in separate modules they are all
legal and all ambiguous at every call site. Type names have to say what they are now — which
sounds like a nit and is actually a boundary leaking into every file that touches two modules.</p>

<h2>5. Tests cannot see across the wall either</h2>

<p><code>@testable import</code> works for a package's own tests. It does not let a test in one
module reach into another's internals. That is the point, but it means tests that were quietly
testing implementation details have to be rewritten against the public surface — or the surface
has to grow to make the behaviour testable. The second option is usually correct, and it is a
useful signal that something is missing from the API.</p>

<h2>6. The awkward middle, and why people quit here</h2>

<p>For a while, everything is public, nothing is faster, and there are more files than before.
That is not the design failing; it is the design being incomplete. The end state — narrow
public surfaces, small rebuilds, obvious ownership — is what pays. Judge it at the end, not in
week two.</p>

<h2>7. Cycles surface, which is the whole point</h2>

<p>The first genuinely valuable thing modularisation does is make circular dependencies
<em>compile errors</em>. In a single target, A using B and B using A is invisible. Across
module boundaries it cannot exist.</p>

<p>That error is not an obstacle in your way. It is the design bug you had been hiding,
finally unable to hide. The wrong fix is to merge the two modules so it compiles again.</p>

<h2>The sequencing I'd use again</h2>

<ol>
  <li><strong>Leaves first.</strong> The things that depend on nothing: design tokens, models,
  a networking core, a logger. Low risk, immediate proof that the tooling works.</li>
  <li><strong>Then the middle.</strong> Shared UI, shared services. This is where the API
  design conversation actually happens.</li>
  <li><strong>Feature modules last.</strong> They are the ones that need the seams below them
  to be settled, and the ones most likely to move again if they are not.</li>
  <li><strong>The app target ends up a shell.</strong> Composition, navigation, configuration.
  If the app target still contains business logic, the split is not finished.</li>
</ol>

<p>The thing I would do differently: agree the vocabulary <em>and</em> the public surface
before anyone starts moving code, in writing, and treat a change to either as a design
decision rather than a refactor. Moving files is mechanical. Everything that made the project
worth doing is not.</p>
""",
        "sources": [
            ("Creating Swift Packages — WWDC19 session 410", "https://developer.apple.com/videos/play/wwdc2019/410/"),
            ("Binary Frameworks in Swift — WWDC19 session 416", "https://developer.apple.com/videos/play/wwdc2019/416/"),
            ("Swift API Design Guidelines", "https://www.swift.org/documentation/api-design-guidelines/"),
        ],
    },
    {
        "slug": "build-time-is-a-dependency-graph-problem",
        "tag": "Build systems",
        "title": "Build time is a dependency-graph problem, not a machine problem",
        "summary": "Faster hardware buys you a constant factor. The graph is the exponent. Why the first fix is almost always deleting a script phase, and what to measure before you touch anything.",
        "body": """
<p class="lede">When builds get slow, the first proposal is always a better machine. A faster
Mac buys a constant factor. The dependency graph is the exponent.</p>

<p>Apple's own guidance on incremental build performance is worth reading before optimising
anything, and it is refreshingly blunt: the things that break incrementality are the things
that make the build redo work it did not need to redo. That is a graph problem.</p>

<h2>Measure the build, not the vibe</h2>

<p>Before changing a setting, get the timing summary from a build and look at where the time
actually goes. Two facts usually fall out immediately:</p>

<ul>
  <li>One or two tasks dominate, and they are not the compiler.</li>
  <li>The build is compiling far more than the change touched.</li>
</ul>

<p>Both point at structure rather than at hardware.</p>

<h2>The most common culprit is a Run Script phase</h2>

<p>A script phase with no declared inputs and outputs runs on <em>every</em> build. It does not
matter that the script is quick. The cost is not the script's runtime, it is that it invalidates
downstream work and forces the build to redo it. A five-line script can be responsible for
minutes.</p>

<p>Three responses, in order of preference:</p>

<ol>
  <li><strong>Delete it.</strong> A surprising share of script phases exist to do something the
  build system already does, or to copy a file that should be a build setting.</li>
  <li><strong>Declare inputs and outputs.</strong> If the script genuinely generates something,
  tell the build system what it reads and what it writes, so it can be skipped when neither
  changed.</li>
  <li><strong>Move it somewhere it is not on the critical path</strong> — earlier in the
  pipeline, or out of the build entirely.</li>
</ol>

<h2>Then look at what a change actually invalidates</h2>

<p>In a single-target app, the answer is usually "everything downstream", which is to say
"most of the app". A change to a shared file in a large target can recompile a majority of the
codebase — not because the compiler is slow, but because the unit of work is the target.</p>

<p>Splitting the target is the fix, and the reason it works is not micro-optimisation. It is
that an unchanged module is genuinely unchanged, and the build system can skip it. The
incremental case — which is the case you live in, hundreds of times a day — gets faster by an
order of magnitude rather than by a percentage.</p>

<h2>Whole-module optimisation, and the debug/release asymmetry</h2>

<p>Whole-module compilation is faster for a clean build and much worse for an incremental one,
because the module is the unit that must be redone. The interesting consequence is that your
debug builds and your release builds want opposite things, and a configuration that is right
for one is wrong for the other. Decide per configuration rather than applying one global
preference.</p>

<h2>Type-checking hot spots are real and they are local</h2>

<p>A single expression that the type checker cannot resolve quickly — a large literal, a deep
nesting of operators, a long chain of overloaded calls — can take longer to compile than the
file around it. The compiler will tell you if you ask it, and the fix is to make the expression
simpler or to name the type explicitly. It is a small, contained edit with an outsize effect.</p>

<h2>Asset catalogs</h2>

<p>Assets are compiled, and a large catalog that changes often is a step you pay for repeatedly.
Keeping generated or throwaway assets out of the catalog is not a style preference; it is
build time.</p>

<h2>What I'd tell a team staring at a slow build</h2>

<ol>
  <li>Get the timing summary. Guess nothing.</li>
  <li>Delete or declare script phases. Cheapest win available, almost always.</li>
  <li>Split the target so unchanged code can be skipped.</li>
  <li>Fix the one or two type-checking hot spots the compiler names.</li>
  <li>Only then consider hardware or caching, and expect a constant factor rather than a step
  change.</li>
</ol>

<p>The uncomfortable part is that the first four are all structural. The build is slow because
the code is shaped in a way that makes it slow, and no amount of machine fixes a shape.</p>
""",
        "sources": [
            ("Improving the speed of incremental builds — Apple Developer Documentation", "https://developer.apple.com/documentation/xcode/improving-the-speed-of-incremental-builds"),
            ("Creating Swift Packages — WWDC19 session 410", "https://developer.apple.com/videos/play/wwdc2019/410/"),
        ],
    },
    {
        "slug": "uikit-to-swiftui-without-a-rewrite",
        "tag": "Migration",
        "title": "UIKit to SwiftUI without a rewrite",
        "summary": "The migration succeeds or fails on one decision: who owns navigation. Everything else is a sequence of small, reversible steps.",
        "body": """
<p class="lede">The migration succeeds or fails on one decision: who owns navigation. Get that
right and the rest is a sequence of small, reversible steps. Get it wrong and you end up with
two systems that each half-know where you are.</p>

<p>I have taken more than one shipped app across this boundary. Nobody regrets the destination.
People regret the order.</p>

<h2>Do not start with the app shell</h2>

<p>The instinct is to rewrite the root and let the screens follow. That inverts the risk: the
shell is the part every screen depends on, and it is the part you cannot ship incrementally.</p>

<p>Start with leaf screens — a detail view, a settings page, a form. Screens that do not own
navigation are the safe unit of migration, because failure costs you one screen rather than
the app.</p>

<h2>Pick one direction of interop at a time</h2>

<p>The two directions are not symmetric and should not be started together:</p>

<ul>
  <li><strong>UIKit shell, SwiftUI leaves</strong> — a UIKit view controller hosts a SwiftUI
  view. This is the low-risk direction, and it is where a migration should begin.</li>
  <li><strong>SwiftUI shell, UIKit leaves</strong> — a SwiftUI view wraps a UIKit component.
  Necessary for the handful of things SwiftUI still does not do well, and the direction that
  tends to accumulate if you are careless.</li>
</ul>

<p>Whichever you are in, know which one it is. A codebase that is doing both, everywhere, with
no rule, has no migration at all.</p>

<h2>Navigation is the seam, so give it exactly one owner</h2>

<p>This is the decision that determines whether the migration is a project or a permanent tax.
Two systems that both believe they own the stack produce bugs that are extremely hard to
diagnose: a screen that appears twice, a back button that does nothing, state that resets on
pop.</p>

<p>Keep navigation in one place for the whole migration — whether that is the UIKit navigation
controller or a SwiftUI stack driven by a coordinator. The other side renders content and
reports events. It does not push.</p>

<h2>State ownership: pass data in, events out</h2>

<p>Do not let the two worlds observe each other's state. A view controller watching a SwiftUI
observable object, or a SwiftUI view holding a reference to a view controller and polling it,
is a future bug in both directions.</p>

<p>The contract that survives: the parent passes a value in and receives callbacks out. That is
enough for almost every screen, and it keeps either side replaceable.</p>

<h2>What actually bites</h2>

<ul>
  <li><strong>Keyboard avoidance.</strong> Two systems, two opinions, one screen. This is the
  most common source of visual regressions during the swap and it is worth a dedicated pass.</li>
  <li><strong>List identity.</strong> A list that reuses cells and a list that keys on identity
  behave differently on update. Missing or unstable identity produces animations and state loss
  that look like a rendering bug and are not.</li>
  <li><strong>Lifecycle timing.</strong> "Appeared" does not mean the same instant in both
  systems. Code that kicks off work on appear and cancels on disappear will behave differently,
  and the difference shows up under a slow network, not on your desk.</li>
  <li><strong>Measurement.</strong> Geometry readers used for layout maths are a smell in a
  declarative system. Most of the time the layout you were computing by hand is a two-line
  native layout, and the manual version is the expensive one.</li>
</ul>

<h2>Availability is part of the plan, not an afterthought</h2>

<p>Everything you adopt has to exist on your deployment target, and anything newer needs a
working fallback — not an <code>#available</code> that silently renders nothing. Write down the
minimum supported version and treat every adoption above it as a decision with a cost.</p>

<h2>How you know it is finished</h2>

<p>The app target compiles without importing the old UI framework outside the places the
platform genuinely requires it. Until then, you have a mixed app, which is a perfectly good
state to ship from — but it is a state, not an outcome. Name the finish line, or the migration
becomes the architecture.</p>
""",
        "sources": [
            ("Introducing SwiftUI: Building Your First App — WWDC19 session 204", "https://developer.apple.com/videos/play/wwdc2019/204/"),
            ("SwiftUI Essentials — WWDC19 session 216", "https://developer.apple.com/videos/play/wwdc2019/216/"),
            ("Human Interface Guidelines — Apple Developer", "https://developer.apple.com/design/human-interface-guidelines"),
        ],
    },
    {
        "slug": "a-design-system-is-a-review-policy",
        "tag": "Craft",
        "title": "A design system is a review policy, not a library",
        "summary": "Importing a token package changes nothing. The system holds when the correct choice is easier than the wrong one — and when review refuses the local override.",
        "body": """
<p class="lede">A design system is not a package you import. It is a set of decisions that
review enforces, and the package is only the place those decisions live.</p>

<p>I have watched more than one design system die at screen three. The failure is always the
same and never looks like a design problem at the time: someone had a deadline, the component
almost fit, and they wrote the value inline. That file is now the precedent.</p>

<h2>Three copies of every value</h2>

<p>In a healthy system there are exactly two places a colour can come from: the design source,
and the token that mirrors it. In a real codebase there is a third — the literal somebody
pasted into a view — and that is the one that ages badly. It does not break. It just drifts,
one hex at a time, until nobody can change the brand colour without a treasure hunt.</p>

<h2>What makes it stick</h2>

<ol>
  <li><strong>Token names describe intent, not value.</strong> <code>surface</code>,
  <code>danger</code>, <code>border-subtle</code> survive a redesign. <code>grey300</code>
  does not, and it invites the next person to pick a neighbouring number by eye.</li>
  <li><strong>The default has to be the correct one.</strong> If using the system is harder
  than not using it, the system loses, every time, to someone under pressure. Convenience beats
  policy.</li>
  <li><strong>The component owns its own spacing.</strong> A system where every screen
  re-specifies the padding of the same button is a component in name only.</li>
  <li><strong>Review rejects the override.</strong> This is the actual enforcement. Not a lint
  rule, not a guideline — a person saying no, in a review, with a reason. The first few of
  those set the norm for the next hundred.</li>
</ol>

<h2>What I check in review</h2>

<ul>
  <li>No raw colour values outside the tokens file. None, including "just for the shadow".</li>
  <li>No font sizes written as numbers in a view.</li>
  <li>Spacing from the scale — not <code>13</code> because it looked right that afternoon.</li>
  <li>A component not re-specifying spacing the component already defines.</li>
  <li>New tokens: does an existing one already mean this? Duplicated intent is how a token file
  becomes a colour palette.</li>
</ul>

<h2>The honest cost, said out loud</h2>

<p>A design system slows down the first screen and speeds up the tenth. That is the entire trade,
and it is a bad deal if you only ever build one screen. Teams abandon systems because nobody
said the first half of that sentence, so the first screen feels like overhead and the tenth
never arrives.</p>

<p>Say it in the same breath as the plan. "This will be slower for a fortnight and faster after
that" is a sentence a team can agree to. "We are adopting a design system" is not.</p>

<h2>The design side is a person, not a handoff</h2>

<p>The systems I have seen work have a designer who reads the diff, or a developer who has the
design file open. The ones that fail have a Figma link and a prayer. The gap between the mock
and the implementation is where defaults get invented — and invented defaults are the beginning
of the third copy.</p>

<p>None of this is about tooling. It is about which choice is the path of least resistance on a
Thursday afternoon, and who is standing between the deadline and the hardcoded hex.</p>
""",
        "sources": [
            ("Human Interface Guidelines — Apple Developer", "https://developer.apple.com/design/human-interface-guidelines"),
            ("Swift API Design Guidelines", "https://www.swift.org/documentation/api-design-guidelines/"),
        ],
    },
    {
        "slug": "how-i-review-ios-pull-requests",
        "tag": "Behaviour",
        "title": "How I review iOS pull requests",
        "summary": "Risk before style, deletion before addition, and three questions I ask on every diff. What I refuse to merge, and why the comment that explains the failure mode is worth ten that state the rule.",
        "body": """
<p class="lede">A review that starts with naming has already wasted its most useful attention.
Here is the order I read a diff in, and the things I refuse to merge.</p>

<h2>The order</h2>

<ol>
  <li><strong>Does it do what the description says?</strong> Not what the code says — what the
  description claims. If they diverge, that is the first comment, before anything else.</li>
  <li><strong>Can it crash?</strong> Force unwraps, array indexing, casts, anything that
  assumes a shape it has not checked.</li>
  <li><strong>What is the failure path?</strong> Every network call fails. Every write can be
  interrupted. A diff that only handles success is half a diff.</li>
  <li><strong>What was deleted?</strong> Removed guards and removed tests first.</li>
  <li><strong>Style.</strong> Last, and usually not at all.</li>
</ol>

<h2>Three questions, every time</h2>

<ul>
  <li><strong>What happens on a slow network?</strong> Not down — slow. That is the state
  where double submissions, spinners that never resolve, and buttons that fire twice live.</li>
  <li><strong>What happens if the user backgrounds the app mid-operation?</strong> Very few
  diffs survive this question unconcerned, and the ones that do are the ones I trust.</li>
  <li><strong>What happens the second time?</strong> Is this operation idempotent? Retrying a
  payment, a submission, a sync — the second call is where data loss is born.</li>
</ul>

<h2>What I refuse to merge</h2>

<ul>
  <li>A skipped or disabled test. If it cannot pass, delete it and say so; a disabled test is a
  lie that gets inherited.</li>
  <li>A test that asserts nothing, or that asserts the mock.</li>
  <li><code>try?</code> on a write. Swallowing a failed save is how a user loses an hour of work
  and nobody finds out.</li>
  <li>A new dependency for something the platform already does.</li>
  <li>A control with no accessibility label. This is not a later ticket; it is an unfinished
  control.</li>
</ul>

<h2>Concurrency, because that is where the crashes actually are</h2>

<p>Most of the real defects I find in review are structural rather than logical:</p>

<ul>
  <li>A task started from a view that outlives the view, and writes to state after it is gone.</li>
  <li>State mutated off the main actor that a view reads on it.</li>
  <li>Two writes racing to the same store with no single owner.</li>
</ul>

<p>These do not need a deep read of the logic. They need one question: <em>who owns this state,
and on which actor is it touched?</em> If the diff cannot answer in one sentence, that is the
comment.</p>

<h2>Two habits that pay</h2>

<p><strong>I review the smallest possible unit, early.</strong> A large diff gets a shallow read
and a rubber stamp, and both parties know it. Several small diffs get real attention. If a
change is too big to review carefully, the review is not the problem to fix — the change is.</p>

<p><strong>I explain the failure, not the rule.</strong> "This will double-submit if the user
taps twice before the response" teaches something. "Don't allow double taps" produces a fix for
this instance and the same bug next month. The comment that names the failure mode is worth ten
that quote the standard — and it is the difference between a review and a gate.</p>

<h2>What review is for</h2>

<p>Not catching typos, and not demonstrating that the reviewer read the code. It is the last
point at which the person who wrote something still remembers why, and someone else can ask
"what happens when this goes wrong?" while the answer is cheap. Everything else about it is
negotiable. That is not.</p>
""",
        "sources": [
            ("Swift API Design Guidelines", "https://www.swift.org/documentation/api-design-guidelines/"),
            ("Human Interface Guidelines — Apple Developer", "https://developer.apple.com/design/human-interface-guidelines"),
        ],
    },
    {
        "slug": "the-ios-stack-i-actually-reach-for",
        "tag": "Tooling",
        "title": "The iOS stack I actually reach for",
        "summary": "Not the stack I would pick on a greenfield project — the one I reach for on someone else's codebase at 3am. Every choice is priced by the next engineer's ability to debug it.",
        "body": """
<p class="lede">This is not the stack I would choose on a blank project. It is the one I reach
for on a codebase I did not write, where the deciding question is who has to debug this at
3am.</p>

<h2>Language and concurrency</h2>

<p>Swift, on the newest language mode the team can hold, with strict concurrency on rather than
aspirational. Adopting it late costs more than adopting it early, because the cost is
proportional to how much code you already have. Everything is main-actor by default and
explicitly off it only where work is genuinely expensive — the opposite default produces code
that is concurrent by accident.</p>

<h2>UI</h2>

<p>SwiftUI for new screens, UIKit where the platform still requires it or where a table or
collection needs control the declarative layer does not yet give. That is an honest position
rather than a religious one: a rewrite that ships is better than a purity that does not.</p>

<p>Navigation has one owner. Always. Two systems that both think they own the stack produce the
worst bugs to diagnose.</p>

<h2>Structure</h2>

<p>Local Swift packages per seam, the app target as a thin shell. The reason is not elegance —
it is that an unchanged module does not get rebuilt, and a circular dependency becomes a
compile error rather than a convention nobody follows.</p>

<h2>Networking</h2>

<p>Whatever the codebase already has, unless it is actively harmful. A second networking layer
is a worse outcome than an imperfect first one. On a greenfield app I would reach for the
platform's own concurrency tools over a reactive framework; on an existing app I leave the
existing one alone until there is a reason to move it.</p>

<h2>Persistence</h2>

<p>The platform's own persistence before a hand-rolled SQL layer, and a real constraint in the
schema before validation in the app. Constraints are enforced under concurrency and app bugs
are not. Where the data matters, the second copy of the truth is the one that goes stale.</p>

<h2>Strings</h2>

<p>A single string catalogue, referenced by key. Never a literal in a view — not because of
localisation, though that too, but because a literal in a view is unsearchable and permanent.
This is the cheapest discipline on the list and the one most often skipped.</p>

<h2>Testing</h2>

<p>Tests for logic, first and always: parsers, state machines, anything with a branch. They run
in seconds and they catch the regressions that matter. UI tests sparingly, on the flows that
carry money or data, because they are slow and inherently flaky and a flaky suite gets ignored
— which is worse than not having one.</p>

<p>A test that cannot fail is not a test. If I cannot describe the change that would turn it
red, it is decoration.</p>

<h2>Third-party dependencies</h2>

<p>Only for a problem the platform does not solve. The bar is not popularity, it is: can I read
this library when it misbehaves, and is anyone still maintaining it in two years? A small
dependency I understand beats a large one I do not, and "we might need it later" has never once
been true.</p>

<h2>Build health</h2>

<p>Build warnings treated as a budget rather than as weather. A codebase with three hundred
warnings cannot notice the fourth hundred, and one of those was going to tell you that a main
thread write had just become an act of faith.</p>

<h2>The meta-decision</h2>

<p>I have changed stacks more than once, and each time the framework-specific knowledge expired
faster than I expected. What survived is the habit underneath it: prefer the boring choice,
prefer the platform's own tool, prefer the option a new hire can debug on their first weekend
on call, and leave the codebase so that the next person's hard problem is the interesting one
— not the one you set up for them by being clever.</p>
""",
        "sources": [
            ("Swift API Design Guidelines", "https://www.swift.org/documentation/api-design-guidelines/"),
            ("Improving the speed of incremental builds — Apple Developer Documentation", "https://developer.apple.com/documentation/xcode/improving-the-speed-of-incremental-builds"),
            ("Human Interface Guidelines — Apple Developer", "https://developer.apple.com/design/human-interface-guidelines"),
        ],
    },
    {
        "slug": "ai-native-development-process",
        "tag": "Process",
        "title": "AI-native development is a process, not a feature",
        "summary": "What I write down so an agent is useful inside a real codebase: the conventions file, the brief, the one piece of evidence I accept — and the parts I refuse to hand over.",
        "body": """
<p class="lede">"AI-native" describes how an app gets built, not something that ships inside it.
The interesting engineering is not the model. It is the document you write so a stateless tool
can work inside a codebase that took years to shape.</p>

<p>I have spent the last weeks setting this up on my own projects — an agent harness in the
editor, skills, plugins — and the installation is the easy half. These are the rules that
survived contact.</p>

<h2>An agent starts every task with nothing, so the document is the memory</h2>

<p>The first surprise is how much of a good brief turns out to be a restatement of rules that
were never written down. Which language mode. Which deployment floor. Which layer may call
which. What "done" means. When to stop and ask rather than try harder.</p>

<p>Those conventions used to live in a senior engineer's head and in the review comments of a
dozen pull requests. A tool with an empty context window can read neither. Written down once,
they become the thing every task is briefed from — which is why that file matters more than
the prompt, and why "I run an agent in my editor" describes almost none of the work.</p>

<h2>What the IDE now gives you, and what it does not</h2>

<p>This stopped being a bolt-on. The Xcode 26 release notes describe "coding intelligence
features that help you write code, generate tests and documentation, fix errors, refactor
existing implementations, and navigate codebases" — with a model of your choosing, including
one that runs locally on Apple silicon.</p>

<p>Xcode 27 pushes further in exactly the direction this post is about: "Planning with agents
is now first class in Xcode. Plans appear as editable Markdown artifacts next to the
conversation" — review, annotate, discuss, and approve, before the agent proceeds. And the
Xcode MCP server's tools now reach real platform state: manipulating the active run state,
reading the debugger console, listing and switching schemes and run destinations, and
inspecting or modifying build settings, compiler flags, entitlements and Info.plist keys.</p>

<p>That list deserves reading twice, because two of its items are the whole discipline in
miniature. A plan you must approve before work starts is a review gate placed at the cheapest
possible moment. Entitlements and Info.plist behind a tool call means the blast radius of a
careless instruction now includes your signing configuration.</p>

<p>What the platform still does not ship is the part specific to your codebase. The harness is
general; the conventions are not. That asymmetry is where a person's leverage sits.</p>

<h2>Four things I write down before the first task</h2>

<ul>
  <li><strong>Conventions</strong> — what the compiler and the linter enforce and, more
  usefully, what they cannot: which layer may depend on which, where a string comes from, what
  an error is allowed to say.</li>
  <li><strong>Boundaries</strong> — the files an agent may touch, and the ones it must stop at
  and ask about. Credentials, permissions, payments, privacy surfaces and anything that leaves
  the machine are on the second list, always.</li>
  <li><strong>Definition of done</strong> — the exact command that proves the change. Not
  "looks right": a build, or a test that was red and is now green.</li>
  <li><strong>Stop conditions</strong> — after a few failed attempts, re-plan rather than try
  harder; never delete or skip a test to reach green; never widen the scope of a change
  without saying so.</li>
</ul>

<p>The shape, as a pattern rather than anyone's real file:</p>

<pre><code>Conventions        language mode · deployment floor · layer rules · where strings live
Boundaries         may touch: &lt;paths&gt; · must ask: credentials, permissions, payments
Definition of done the one command that proves it
Stop conditions    three failed attempts → re-plan · never skip a test · never widen scope
Roles              who plans, who writes, who verifies, who is allowed to fix</code></pre>

<h2>Two rules about what never goes into a prompt</h2>

<p><strong>Secrets and paths.</strong> A key prefix or a home-directory path is not prose, so a
word-by-word blocklist can never anticipate it — the check has to be shaped, not spelled. This
site's own content check now fails the build on a key-shaped string or a
<code>/Users/&lt;name&gt;/</code> path in the published output. Not because a blog post would
contain one, but because that class is guessable, and a script can hold a guessable class.</p>

<p><strong>Transcripts.</strong> A real transcript is a document about your job; a pattern is a
document about your craft. So I show the structure of a brief — the invariant, the constraint,
the evidence — and never the text. The text carries whatever the session happened to contain,
and nobody can write the blocklist for a conversation in advance. This is the rule I broke most
often before I wrote it down.</p>

<h2>What stays a person's job</h2>

<p><strong>Specificity.</strong> App Review is blunt about it: guideline 2.3.1(a) requires new
features to be "described with specificity in the Notes for Review section of App Store Connect
(generic descriptions will be rejected)". A generic description is exactly what a templated
draft produces well — plausible, complete-looking, and about nothing. The model can draft; the
specificity has to be mine.</p>

<p><strong>The irreversible.</strong> Deployments, credentials, purchases, anything a revert
cannot undo.</p>

<p><strong>The shape of the whole.</strong> Whether the feature should exist, where the seam
belongs, which of two working designs will still be right in a year. An empty context window
does not make any of that easier to delegate.</p>

<p>The pattern that keeps repeating: agents are good at the parts of engineering that are
typing, and bad at the parts that are deciding. Most of the value of setting this up is the
writing down — being forced to say, in plain language, which is which.</p>
""",
        "sources": [
            ("Xcode 26 Release Notes — coding intelligence, model choice, local models", "https://developer.apple.com/documentation/xcode-release-notes/xcode-26-release-notes"),
            ("Xcode 27 Release Notes — plans as artifacts, Gemini, Xcode MCP server", "https://developer.apple.com/documentation/xcode-release-notes/xcode-27-release-notes"),
            ("App Review Guidelines — 2.3.1(a)", "https://developer.apple.com/app-store/review/guidelines/"),
        ],
    },
    {
        "slug": "what-a-green-build-does-not-prove",
        "tag": "Build systems",
        "title": "What a green build does not prove",
        "summary": "Four things I described as verified this week that were not — a pipeline that compiled a working copy, a lock file that pinned a branch, a push I said would deploy once, and a release that changed nothing. Same mistake each time: a colour accepted as evidence about inputs.",
        "body": """
<p class="lede">A green pipeline says a build succeeded. It says nothing about what went into
it. This week four claims I had called verified turned out not to be, and all four were the
same mistake: a colour accepted as evidence about inputs.</p>

<h2>The build that compiled a working copy</h2>

<p>The pipeline went green and I reported what I believed it proved: CI read the committed
dependency list, fetched each dependency at the revision the list named, and compiled against
it. It proved the build succeeded. The input was wrong.</p>

<p>The runner was a shell executor whose build directory sits inside a developer's home
directory — one level below the folder holding the dependency checkouts. So the code the build
compiled was not fetched from the list at all. It was the local copies already on that disk, in
whatever state the last person left them. No commit was required for an uncommitted edit to
reach a build. The dirty-tree guard in the sync script existed and was correct; nothing on the
publishing path called it.</p>

<p>The lesson is not "configure your runner properly", though that too. It is that a pipeline's
inputs are a claim, and the only way to hold that claim is to print them. A build that does not
name its inputs in its own log is a build nobody can reproduce — including the person who
pressed the button.</p>

<h2>The lock file that pins a branch</h2>

<p>The dependency list had one row per package and every row named a branch. Zero rows named a
revision. That file looks like a lock and behaves like a wish: on one afternoon the branch on a
single dependency moved twice, so the same app commit resolved to two different sets of code on
two runs, and neither build's log said which one it got.</p>

<p>This is a cheap bug to have and a cheap bug to fix, which is why it is worth writing down. The
script already supported a revision in that column — it falls back to a plain checkout when the
name is not a remote branch. So the fix is one column, and the cost is honest: bumping a pinned
dependency becomes an explicit commit, and you cannot fast-forward a pinned checkout any more.
That is the trade you are buying. It is the whole point of the file.</p>

<h2>The push that deploys twice</h2>

<p>I said pushing the branch would deploy once. It deployed twice: once from the push, and again
from the merge into the default branch. What I had actually verified was that the merge-request
pipeline does not deploy — the rules exclude every source that is not a push, in as many
words — and I had quietly stopped counting there. Two, and the second one arrives after the
review, when nobody is watching for it.</p>

<pre><code>- if: '$CI_PIPELINE_SOURCE != "push"'
  when: never</code></pre>

<p>The rule is a good design: a branch that has not been merged should not ship. But "the MR
cannot deploy" and "this work deploys once" are different sentences, and only the second one
tells a tester how many builds are coming.</p>

<h2>The release that changed nothing</h2>

<p>Two builds went out carrying the same version and the same build number, both identical in
content to a build testers already had. The version strings had been lost in a merge — three
files quietly disagreeing about what the app was called — and restoring them was the right fix.
It also meant an entire release whose only real change was a string.</p>

<p>Nothing in the store tells a tester that. The two releases are distinguishable only by an
internal release id, which is exactly the kind of identifier nobody outside the console ever
sees. The only artifact that can say "you have already tested this, there is nothing here" is
the release note. So the note is hand-written, per release, and it is the one piece of writing
in the process I will not generate: a changelog derived from commits would have said "fix
version strings", which is accurate and useless.</p>

<h2>The analytics change that was almost free</h2>

<p>Identity handling moved from a per-event parameter to a first-class user property, and three
custom parameters were dropped along the way. I called that free. A colleague checked the
documentation instead of agreeing: one of the three is collected automatically with every
event, and the other two are not.</p>

<p>So the precise statement is narrower than "nothing was lost". The information survives, because
the platform's own Platform and Operating system dimensions collect it. What dies is the custom
dimension names — any report built on those literal parameter names goes blank on the next
release. That is a five-minute console check, not a code change, and it is the sort of removal
that stays unused right up until a chart proves otherwise.</p>

<h2>What I do differently now</h2>

<ul>
  <li><strong>Print the revisions.</strong> Every job dumps the resolved revision of every
  dependency next to the app commit. If the inputs are not in the log, the claim about the
  binary is not evidence.</li>
  <li><strong>Pin revisions, not branches.</strong> In anything whose output ships. A branch in
  a lock file records intent; a revision records a build.</li>
  <li><strong>Count deploys from the rules file.</strong> Not from memory, and not from "the MR
  can't ship". Read what each pipeline shape does and add them up.</li>
  <li><strong>Put the purpose in the release note.</strong> Two identical builds and a tester
  who cannot tell them apart is a documentation defect, not a testing plan.</li>
  <li><strong>Check "unused" against the documentation.</strong> Before deleting a field, find
  out whether something was already collecting it. "We never used that" and "the SDK always
  did" look identical in a diff.</li>
</ul>

<p>The habit underneath all five is the cheapest one available: verify with a command, not with
a colour. A green check is a statement about the past tense of a machine I cannot see. One
<code>rev-parse</code> is a statement about now.</p>
""",
        "sources": [
            ("GitLab CI/CD — control when jobs run: rules and when: never", "https://docs.gitlab.com/ci/jobs/job_control/"),
            ("Writing custom build scripts — Xcode Cloud", "https://developer.apple.com/documentation/xcode/writing-custom-build-scripts"),
            ("Automatically collected events — Analytics Help", "https://support.google.com/analytics/answer/9234069"),
        ],
    },
    {
        "slug": "four-gates-that-certified-nothing",
        "tag": "Build systems",
        "title": "Four gates that passed without testing anything",
        "summary": "A lint gate that linted a directory, a pre-push script that ran two thirds of the tests and printed success, a build number shared by three uploads, and snapshots that recorded a session instead of a screen. Every one of them was green, and every green was true about the wrong thing.",
        "body": """
<p class="lede">Every gate I added this month passed. That was the problem. Four of them
were answering a different question than the one I thought I had asked, and in each case
the green text was accurate — about something other than what I believed it certified.</p>

<p>None of the four was a subtle bug. Each was a single line that described the machine
the job happened to run on rather than the thing that was supposed to ship. That is why
they all looked fine: they were correct on my laptop.</p>

<h2>The gate that described a disk</h2>

<p>A lint job went red with a wall of violations, almost none of them new. The dependency
manifest names the packages the app actually links. The gate never read it. It globbed a
parent directory and linted every checkout sitting there, including two old working copies
that nobody had linked in months. Those two produced most of the failure, and the packages
that really shipped were clean.</p>

<p>The same config carried a second defect in the same direction. The baseline that
absorbs legacy violations was keyed by absolute path — one entry per file, prefixed with
the path of the machine that generated it. On that machine it matched and the gate was
green. On any other checkout, in CI, on a fresh clone, the keys match nothing, and every
legacy violation becomes an error in a job that never gets as far as the compiler.</p>

<p>The fix was to drive the include from column one of the manifest instead of a glob,
and to delete the baseline rather than repair it. A file that is a hundred kilobytes of
one machine's state is not configuration. The rules it was suppressing belong in a
<code>disabled_rules</code> list, which is stable, reviewable, and identical everywhere.</p>

<h2>The gate that ran two thirds of the tests</h2>

<p>The complaint was that snapshot failures were discovered in CI, after a push, rather
than before it. So I built a pre-push script that ran only the snapshot suites. It selected
them by filename: twelve files with <em>Snapshot</em> in the name, twelve
<code>-only-testing</code> arguments.</p>

<p><code>xcodebuild</code> accepted all twelve, ran a third fewer tests than the suite
contains, and printed <code>TEST SUCCEEDED</code>. Three of the twelve selectors matched
nothing at all, because the suites do not live in files named after them — they live in
files named after features. A selector that matches nothing is not an error to the tool. It
is simply omitted, silently, from a run that still exits zero.</p>

<p>The lesson is narrower than "test everything" and more useful: derive the selector from
the source, then assert that what you derived equals what you passed. The count is the
cheap check, and it is the one that would have caught this. A gate that quietly tests less
than it claims is worse than no gate, because it consumes the attention you would have
spent checking.</p>

<h2>The build number that told nothing apart</h2>

<p>Three consecutive uploads carried the same marketing version and the same build number.
The deploy job had no <code>changes:</code> rule, so every branch push produced a build,
including pushes whose diff could not compile into the app. And nobody bumped the build
number, because nobody was looking at the artifact — the pipeline was green, and green was
the thing being watched.</p>

<p>Firebase accepts three uploads with one identity and gives each a release ID. App Store
Connect does not: it rejects a duplicate build number at upload. That rejection arrives
weeks later, on a release branch, when the person holding it has no memory of why the
number stopped moving. The bandage is one line in each configuration. The cause is a deploy
job that treats every push as shippable.</p>

<h2>The snapshot that recorded the session</h2>

<p>Three captures differed from their references. Both images were the same size, on the
same device, with the same scale, so this was not a device or a runtime mismatch. The
difference was a student's name.</p>

<p>The references had been recorded signed out. The new captures had a signed-in user —
leaked from an earlier test in the same process. The harness reset its cache between
captures and not its session, so the reference described the history of the test run rather
than the screen. Re-recording would have made it pass, and would have baked a leaked
session into the reference permanently, where no one would ever look again.</p>

<p>That is the most dangerous shape of a stale reference: not old pixels, but a test that
is measuring the wrong thing and will keep measuring it, consistently, forever.</p>

<h2>The shape they share</h2>

<p>All four gates reported on their input accurately and on their claim inaccurately. The
lint job told me about a directory. The pre-push script told me that twelve selectors had
been accepted. The deploy job told me that a command had exited zero. The snapshot run told
me that the screen matched a previous process.</p>

<p>Three questions, asked before trusting any gate:</p>

<ol>
  <li><strong>What does it read?</strong> A manifest, a source tree, or whatever happens
  to be on this disk? If the answer is the last one, the result is a property of one
  machine, and portability is not a nicety to fix later.</li>
  <li><strong>What does green mean?</strong> That a command exited zero, or that a
  property holds? Most of the work is turning the first into the second.</li>
  <li><strong>Does it fail on a machine that is not mine?</strong> Not "would it run" —
  xcodebuild would. Whether the answer it gives there is still true.</li>
</ol>

<p>In every case the repair was smaller than the analysis: one column, one count, one
bump, one reset. The expensive part was noticing that a green check says nothing until you
can name what it checked.</p>
""",
        "sources": [
            ("SwiftLint — configuration, baselines and included paths", "https://realm.github.io/SwiftLint/configuration.html"),
            ("GitLab CI/CD — control when jobs run: rules and when: never", "https://docs.gitlab.com/ci/jobs/job_control/"),
            ("Build settings reference — CURRENT_PROJECT_VERSION", "https://developer.apple.com/documentation/xcode/build-settings-reference"),
            ("swift-snapshot-testing — recording and asserting references", "https://github.com/pointfreeco/swift-snapshot-testing"),
        ],
    },
]


def page(title, description, url, body, extra_head=""):
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{CARD}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='0' fill='%232563eb'/><text x='16' y='23' font-family='Georgia,serif' font-size='20' fill='%23ffffff' text-anchor='middle'>R</text></svg>">
<link rel="stylesheet" href="./blog.css">
{extra_head}</head>
<body>
<div class="wrap">
  <div class="top">
    <a class="who" href="/">Muhammad Ilham Rilambang</a>
    <a href="./index.html">Blog</a>
  </div>
{body}
</div>
</body>
</html>
"""


LEDE_RE = re.compile(r'(<p class="lede">.*?</p>)', re.S)


def minutes(body_html):
    words = len(re.sub(r"<[^>]+>", " ", body_html).split())
    return max(1, round(words / 220))


def render_post(p, i):
    svg, cap = FIGURES[p["slug"]]
    figure = (f'\n  <figure class="fig">{svg}\n'
              f'    <figcaption>{html.escape(cap)}</figcaption>\n  </figure>\n')
    body_src = p["body"].strip()
    body = (LEDE_RE.sub(lambda m: m.group(1) + "\n" + figure, body_src, count=1)
            if LEDE_RE.search(body_src) else figure + body_src)

    src = "".join(
        f'      <li><a href="{u}" target="_blank" rel="noreferrer">{html.escape(t)}</a></li>\n'
        for t, u in p["sources"]
    )
    prev = POSTS[i - 1] if i else None
    nxt = POSTS[i + 1] if i < len(POSTS) - 1 else None
    left = (f'<a href="./{prev["slug"]}.html">← {html.escape(prev["title"])}</a>'
            if prev else "<span></span>")
    right = (f'<a href="./{nxt["slug"]}.html">{html.escape(nxt["title"])} →</a>'
             if nxt else "<span></span>")
    pager = ('  <nav class="pager">\n'
             f'    {left}\n'
             f'    {right}\n'
             '  </nav>\n')

    out = (
        '  <header class="post-head">\n'
        f'    <p class="chip">{html.escape(p["tag"])}</p>\n'
        f'    <h1>{html.escape(p["title"])}</h1>\n'
        f'    <p class="meta">{minutes(body_src)} min read · Muhammad Ilham Rilambang</p>\n'
        '  </header>\n'
        '  <article>\n'
        f'{body}\n'
        f'    <div class="sources">\n      <h2>Sources</h2>\n      <ul>\n{src}      </ul>\n    </div>\n'
        '  </article>\n'
        '  <p class="foot">Written from experience shipping iOS apps. No client names, no '
        'internal details, no unpublished numbers — everything citable here is public.</p>\n'
        f'{pager}'
    )
    return page(p["title"], p["summary"], f"{SITE}/blog/{p['slug']}.html", out)


def render_index():
    # Newest first. POSTS is authored oldest-first because each post's prev/next pager
    # reads in publication order; the index is a reading list, and a reader lands on it
    # wanting today, not the beginning.
    recent = list(reversed(POSTS))
    items = "".join(
        f'      <li>\n'
        f'        <span class="num">{len(recent) - i:02d}</span>\n'
        f'        <div>\n'
        f'          <a href="./{p["slug"]}.html"><h2>{html.escape(p["title"])}</h2></a>\n'
        f'          <p>{html.escape(p["summary"])}</p>\n'
        f'          <p class="meta" style="margin:8px 0 0">{html.escape(p["tag"])} · '
        f'{minutes(p["body"])} min read</p>\n'
        f'        </div>\n'
        f'      </li>\n'
        for i, p in enumerate(recent)
    )
    body = (
        '  <h1>Blog</h1>\n'
        '  <p class="lede lede--index">Notes on the craft of iOS — platform rules,\n'
        '  modularisation, build health, migration, review practice, and the development\n'
        f'  process I use with agents. {len(POSTS)} pieces, newest first, written in\n'
        '  October 2026.</p>\n'
        f'  <ul class="cards">\n{items}  </ul>\n'
        '  <p class="foot">Everything here is public and citable — no employer internals, no\n'
        '  colleague names, no unpublished metrics. If a claim needs a source it has one, and\n'
        '  every diagram here is drawn from text rather than a screenshot of anything.</p>\n'
    )
    return page(
        "Blog — Muhammad Ilham Rilambang",
        "Notes on the craft of iOS: platform rules, modularisation, build health, migration, "
        "review practice and the agent workflow I actually run.",
        f"{SITE}/blog/",
        body,
    )


OUT.mkdir(parents=True, exist_ok=True)
# Stale pages are worse than missing ones: rename a slug and the old post stays published,
# still linked from wherever it was linked, with nothing to show that it is gone.
for stale in OUT.glob("*.html"):
    stale.unlink()
(OUT / "blog.css").write_text(CSS.lstrip())
(OUT / "index.html").write_text(render_index())
for i, p in enumerate(POSTS):
    (OUT / f"{p['slug']}.html").write_text(render_post(p, i))
print(f"{len(POSTS)} posts + index + css -> {OUT}")
