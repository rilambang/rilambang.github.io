#!/usr/bin/env python3
"""Two Lottie figures per blog post.

Each scene is a state change in three stages: set up, the change, the result.
A figure that only moves a rectangle is not here. The poster is the scene's
final frame, so the no-JS fallback cannot drift from the animation.
"""
from lottie import Scene, ACCENT, INK, MUTED, LINE, SURFACE, TINT, WARM

BAD = "#ff8a8a"
OK = "#86e0a6"
DUR = 5.5


def _title(s, text, t=0.0):
    return s.fade_in(s.text(20, 26, text, 11.5, MUTED), t, 0.3)


def _appear(s, nodes, t0=0.2, step=0.28, d=0.3):
    for i, n in enumerate(nodes):
        s.fade_in(n, t0 + i * step, d)
    return nodes


def _arrow(s, x1, y1, x2, y2, t, d=0.35, color=LINE):
    return s.draw_on(s.arrow(x1, y1, x2, y2, color), t, d)


def _cap(s, x, y, text, t, size=11.5, color=MUTED, anchor="start"):
    n = s.text(x, y, text, size, color, anchor)
    s.fade_in(n, t, 0.35)
    return n


# ── 1. kiosk and assessment apps ─────────────────────────────────────────────
def kiosk_1():
    s = Scene("kiosk-1", 280, DUR, "Two questions decide what an exam app can lock")
    _title(s, "Two questions decide what the app can lock")
    a = s.chip(20, 54, 190, 54, "Is it supervised?", accent=True)
    b = s.chip(240, 54, 190, 54, "Does the OS have a mode?")
    _appear(s, [a, b], 0.2, 0.35)
    out = [s.chip(20, 176, 190, 54, "Assessment mode"),
           s.chip(240, 176, 190, 54, "Single app mode"),
           s.chip(460, 176, 160, 54, "A human proctor", accent=True)]
    _appear(s, out, 1.5, 0.3)
    _arrow(s, 115, 108, 115, 176, 1.0)
    _arrow(s, 335, 108, 335, 176, 1.2)
    s.fade_in(s.line(115, 140, 540, 140), 1.3, 0.3)
    for x in (335, 540):
        _arrow(s, x, 140, x, 176, 1.45)
    out[2].pulse(3.4, 0.6, 6)
    _cap(s, 20, 262, "The framework covers the app. It does not cover the room.", 4.0)
    return s


def kiosk_2():
    s = Scene("kiosk-2", 280, DUR, "A device boundary around the exam app, with everything outside it owned by someone else")
    _title(s, "The lock covers the app, not the room")
    frame = s.rect(20, 56, 300, 150, TINT, ACCENT, 12)
    s.fade_in(frame, 0.2, 0.3)
    app = s.chip(50, 96, 170, 52, "Exam app", accent=True)
    s.fade_in(app, 0.5, 0.3)
    _cap(s, 50, 190, "what the entitlement can lock", 0.9, 10.5, ACCENT)
    outside = [s.chip(360, 56, 260, 40, "Home button"),
               s.chip(360, 106, 260, 40, "Notifications"),
               s.chip(360, 156, 260, 40, "Second screen"),
               s.chip(360, 206, 260, 40, "A person in the room")]
    _appear(s, outside, 1.6, 0.3)
    app.pulse(3.0, 0.7, 5)
    _cap(s, 20, 262, "Everything outside the boundary is someone else's decision.", 3.9)
    return s


# ── 2. local packages ────────────────────────────────────────────────────────
def packages_1():
    s = Scene("packages-1", 320, DUR, "Four layers with dependencies pointing down to leaves that depend on nothing")
    _title(s, "Dependencies point one way")
    rows = [("App shell", "composition, navigation, configuration"),
            ("Feature modules", "the screens and their state"),
            ("Shared services", "networking, persistence, logging"),
            ("Leaves", "tokens and models, depending on nothing")]
    nodes = []
    for i, (t, sub) in enumerate(rows):
        n = s.row(20 + i * 6, 54 + i * 58, 600 - i * 12, 44, t, sub)
        s.fade_in(n, 0.2 + i * 0.35, 0.3)
        nodes.append(n)
        if i < 3:
            _arrow(s, 320, 98 + i * 58, 320, 108 + i * 58, 0.45 + i * 0.35, 0.25)
    nodes[3].pulse(3.2, 0.7, 4)
    _cap(s, 20, 302, "A cycle used to be invisible. Here it is a compile error.", 3.9)
    return s


def packages_2():
    s = Scene("packages-2", 260, DUR, "Two feature modules pointing at each other, and the compiler rejecting the cycle")
    _title(s, "A cycle cannot compile")
    a = s.chip(110, 62, 160, 54, "Feature A", accent=True)
    b = s.chip(370, 62, 160, 54, "Feature B", accent=True)
    _appear(s, [a, b], 0.2, 0.3)
    ab = _arrow(s, 270, 78, 370, 78, 0.8, 0.35)
    ba = _arrow(s, 370, 100, 270, 100, 1.2, 0.35, BAD)
    wall = s.rect(300, 52, 6, 74, BAD, None, 3)
    s.fade_in(wall, 2.2, 0.3)
    _cap(s, 320, 150, "rejected", 2.5, 12, BAD, "middle")
    s.fade_out(ba, 2.2, 0.3)
    ab.pulse(3.4, 0.6, 4)
    _cap(s, 20, 190, "One edge removed, and the graph builds again.", 3.6)
    _cap(s, 20, 214, "The compiler is the reviewer that never gets tired.", 4.2)
    return s


# ── 3. build time ────────────────────────────────────────────────────────────
def build_1():
    s = Scene("build-1", 300, DUR, "One file change rebuilding a whole target versus one module of several")
    _title(s, "Same edit, different unit of work")
    for gx, label in ((40, "one target"), (360, "split into modules")):
        _cap(s, gx, 56, label, 0.2, 12, INK)
    cells = []
    for i in range(4):
        for j in range(3):
            cells.append((40 + i * 34, 74 + j * 30, i * 3 + j))
    left = [s.rect(x, y, 28, 24, WARM, LINE, 5) for x, y, _ in cells]
    right = [s.rect(x + 320, y, 28, 24, WARM, LINE, 5) for x, y, _ in cells]
    _appear(s, left + right, 0.3, 0.01, 0.2)
    over = []
    for k, (x, y, _) in enumerate(cells):
        n = s.rect(x, y, 28, 24, ACCENT, None, 5, 0)
        s.fade_in(n, 1.2 + k * 0.06, 0.12)
        over.append(n)
    for k in (3, 4, 6, 7):
        x, y, _ = cells[k]
        n = s.rect(x + 320, y, 28, 24, ACCENT, None, 5, 0)
        s.fade_in(n, 2.1, 0.2)
    _cap(s, 40, 208, "eleven boxes rebuild anyway", 3.0)
    _cap(s, 360, 208, "one group rebuilds", 3.2)
    _cap(s, 20, 258, "The machine is identical in both pictures.", 3.9)
    return s


def build_2():
    s = Scene("build-2", 260, DUR, "A change propagating from one file through its module to the app")
    _title(s, "The edit travels, then it stops")
    a = s.chip(20, 62, 140, 50, "One file")
    b = s.chip(210, 62, 140, 50, "Its module")
    c = s.chip(400, 62, 140, 50, "Dependents")
    d = s.chip(400, 150, 140, 50, "The app")
    _appear(s, [a, b, c], 0.2, 0.3)
    _arrow(s, 160, 87, 210, 87, 0.9)
    _arrow(s, 350, 87, 400, 87, 1.2)
    _arrow(s, 470, 112, 470, 150, 1.6)
    _cap(s, 20, 136, "recompiles", 1.4, 10.5)
    b.pulse(2.2, 0.6, 6)
    c.pulse(2.6, 0.6, 6)
    s.fade_in(s.rect(210, 130, 140, 3, ACCENT, None, 1.5), 2.4, 0.2)
    _cap(s, 20, 210, "A narrow public surface is what makes it stop here.", 3.6)
    return s


# ── 4. UIKit to SwiftUI ──────────────────────────────────────────────────────
def migration_1():
    s = Scene("migration-1", 260, DUR, "A UIKit to SwiftUI migration in four ordered steps, navigation last")
    _title(s, "Progress in one direction")
    steps = ["Leaf screens", "Shared services", "App shell", "Navigation last"]
    nodes = []
    for i, t in enumerate(steps):
        n = s.chip(20 + i * 155, 62, 140, 54, t, accent=(i == 3))
        nodes.append(n)
        s.fade_in(n, 0.2 + i * 0.45, 0.3)
        if i < 3:
            _arrow(s, 160 + i * 155, 89, 175 + i * 155, 89, 0.45 + i * 0.45, 0.3)
    nodes[3].pulse(3.4, 0.7, 5)
    _cap(s, 20, 158, "The seam that owns the stack moves once, at the end.", 3.2)
    _cap(s, 20, 186, "Every adoption above your floor keeps a fallback.", 4.0)
    return s


def migration_2():
    s = Scene("migration-2", 280, DUR, "UIKit and SwiftUI screens reporting events to one navigation owner")
    _title(s, "One owner of the stack")
    left = s.chip(20, 58, 200, 52, "UIKit screens")
    right = s.chip(420, 58, 200, 52, "SwiftUI screens")
    _appear(s, [left, right], 0.2, 0.35)
    router = s.card(200, 150, 240, 60, "Router", "one owner, always", accent=True)
    s.fade_in(router, 1.3, 0.35)
    _arrow(s, 120, 110, 240, 150, 1.6)
    _arrow(s, 520, 110, 400, 150, 1.9)
    _cap(s, 20, 122, "reports events", 1.5, 10.5)
    _cap(s, 470, 122, "reports events", 1.8, 10.5)
    router.pulse(3.2, 0.7, 5)
    _cap(s, 20, 248, "Neither side pushes. Both sides describe what happened.", 3.8)
    return s


# ── 5. design system ─────────────────────────────────────────────────────────
def design_1():
    s = Scene("design-1", 300, DUR, "A design value with two traceable owners and a third copy that drifts")
    _title(s, "Two owners is a system. Three is a countdown.")
    src = s.card(20, 52, 180, 58, "Design source", "the value is decided")
    tok = s.card(230, 52, 180, 58, "Token file", "the name carries intent")
    lit = s.card(440, 52, 180, 58, "A literal", "added at 6pm")
    _appear(s, [src, tok, lit], 0.2, 0.35)
    _arrow(s, 200, 81, 230, 81, 1.2)
    one = s.card(20, 170, 390, 60, "One value, two owners",
                 "a rename is a two-file change", accent=True)
    s.fade_in(one, 1.6, 0.35)
    _arrow(s, 110, 110, 110, 170, 1.5)
    _arrow(s, 320, 110, 320, 170, 1.7)
    drift = s.card(440, 170, 180, 60, "Drift", "it just ages badly")
    s.fade_in(drift, 2.2, 0.35)
    lit.move_to(2.6, 530, 200, 0.6)
    _cap(s, 20, 262, "The third copy decides whether the system survives screen three.", 3.8)
    return s


def design_2():
    s = Scene("design-2", 260, DUR, "A review replacing a hardcoded colour with the design token")
    _title(s, "Review replaces the local override")
    screen = s.card(20, 54, 300, 150, "Exam screen", "a hardcoded colour")
    s.fade_in(screen, 0.2, 0.35)
    literal = s.card(56, 130, 230, 44, "color: #3A6FF7", "")
    s.fade_in(literal, 0.6, 0.3)
    token = s.chip(360, 62, 240, 50, "token: accent", accent=True)
    s.fade_in(token, 1.2, 0.3)
    _cap(s, 360, 140, "one name, one owner", 1.5, 10.5)
    fixed = s.card(56, 130, 230, 44, "color: accent", "")
    s.swap(literal, fixed, 2.2, 0.4)
    fixed.pulse(3.0, 0.6, 4)
    _arrow(s, 360, 112, 300, 132, 2.6)
    _cap(s, 20, 230, "A literal at 6pm is a review problem, not a design-system problem.", 3.7)
    return s


# ── 6. review ────────────────────────────────────────────────────────────────
def review_1():
    s = Scene("review-1", 340, DUR, "The order a pull request is read in, intent first and style last")
    _title(s, "Cheapest questions first, taste last")
    rows = ["1.  Does it do what the description says?",
            "2.  Can it crash?",
            "3.  What is the failure path?",
            "4.  What was deleted?",
            "5.  Style, and usually not at all"]
    for i, t in enumerate(rows):
        y = 52 + i * 50
        box = s.row(20, y, 600, 42, t, "", accent=(i == 4))
        s.fade_in(box, 0.2 + i * 0.5, 0.3)
        box.pulse(2.9 + i * 0.12, 0.4, 2)
    _cap(s, 20, 324, "Starting at 5 wastes the attention that 2 needed.", 4.2)
    return s


def review_2():
    s = Scene("review-2", 260, DUR, "A two hundred line diff with sixty deletions read before any style comment")
    _title(s, "Deletions before style")
    total = s.rect(20, 56, 600, 46, SURFACE, LINE, 8)
    s.fade_in(total, 0.2, 0.3)
    add = s.rect(20, 56, 420, 46, TINT, None, 8)
    s.fade_in(add, 0.6, 0.35)
    gone = s.rect(440, 56, 180, 46, WARM, None, 8)
    s.fade_in(gone, 1.3, 0.35)
    _cap(s, 30, 84, "140 added", 0.9, 11.5, INK)
    _cap(s, 530, 84, "60 deleted", 1.6, 11.5, BAD, "middle")
    d = s.card(20, 132, 290, 56, "What was deleted?", "it is the fastest signal", accent=True)
    s.fade_in(d, 2.2, 0.35)
    st = s.card(330, 132, 290, 56, "Style", "and usually not at all")
    s.fade_in(st, 3.1, 0.35)
    _cap(s, 20, 228, "A deletion is a decision someone already made.", 3.9)
    return s


# ── 7. stack ─────────────────────────────────────────────────────────────────
def stack_1():
    s = Scene("stack-1", 340, DUR, "Five layers of an iOS stack, each with the rule that decides it")
    _title(s, "Each layer chosen by a rule, not a preference")
    rows = [("UI", "SwiftUI first, UIKit where required"),
            ("Navigation", "one owner, always"),
            ("Feature modules", "local packages, narrow surfaces"),
            ("Data", "the platform's persistence, constraints first"),
            ("Platform", "the OS before a dependency")]
    for i, (t, sub) in enumerate(rows):
        n = s.row(20, 52 + i * 52, 600, 44, t, sub)
        s.fade_in(n, 0.2 + i * 0.35, 0.3)
        if i < 4:
            _arrow(s, 320, 96 + i * 52, 320, 104 + i * 52, 0.4 + i * 0.35, 0.2)
    _cap(s, 20, 326, "Priced by the next engineer's ability to debug it at 3am.", 3.8)
    return s


def stack_2():
    s = Scene("stack-2", 280, DUR, "A requirement descending the stack until the platform replaces a package")
    _title(s, "The requirement descends the layers")
    need = s.chip(20, 56, 220, 50, "Need: offline queue", accent=True)
    feat = s.chip(20, 126, 220, 50, "Feature module")
    data = s.chip(20, 196, 220, 50, "Data layer")
    pkg = s.chip(330, 126, 200, 50, "A package")
    plat = s.chip(330, 196, 200, 50, "Platform API", accent=True)
    _appear(s, [need, feat, data], 0.2, 0.35)
    s.fade_in(pkg, 1.4, 0.3)
    _arrow(s, 120, 106, 120, 126, 0.9, 0.3)
    _arrow(s, 120, 176, 120, 196, 1.1, 0.3)
    _arrow(s, 240, 151, 330, 151, 1.7, 0.3)
    _cap(s, 340, 112, "a package", 1.5, 10.5)
    s.swap(pkg, plat, 2.4, 0.45)
    _arrow(s, 240, 221, 330, 221, 2.7, 0.3)
    _cap(s, 340, 244, "the OS already has it", 3.0, 10.5)
    _cap(s, 20, 268, "Reach for the platform before the dependency.", 3.9)
    return s


# ── 8. AI process ────────────────────────────────────────────────────────────
def ai_1():
    s = Scene("ai-1", 320, DUR, "Four checkpoints in an agent workflow, two of them verified rather than trusted")
    _title(s, "Four checkpoints, two of them proof")
    rows = [("Written once", "conventions, boundaries, stop conditions"),
            ("Written per task", "exact paths, the invariant, what proves it"),
            ("The only proof", "a hash, a byte count, a test that was red"),
            ("Still a person", "specificity, secrets, anything irreversible")]
    for i, (t, sub) in enumerate(rows):
        n = s.card(20, 52 + i * 62, 500, 52, t, sub, accent=(i in (2, 3)))
        s.fade_in(n, 0.2 + i * 0.45, 0.3)
        if i < 3:
            _arrow(s, 270, 104 + i * 62, 270, 114 + i * 62, 0.5 + i * 0.45, 0.2)
    dot = s.dot(270, 78, 5)
    s.fade_in(dot, 0.4, 0.2)
    dot.move_to(1.2, 270, 202, 0.5)
    dot.move_to(2.0, 270, 78, 0.5)
    _cap(s, 20, 302, "A blank context window each time. The document is the only memory.", 3.9)
    return s


def ai_2():
    s = Scene("ai-2", 260, DUR, "A document surviving an empty context window and restoring the next one")
    _title(s, "The document outlives the context")
    ctx = s.card(20, 54, 280, 120, "Context window", "one task, then empty")
    s.fade_in(ctx, 0.2, 0.35)
    doc = s.card(340, 54, 280, 120, "The document", "conventions, boundaries, proof", accent=True)
    s.fade_in(doc, 0.5, 0.35)
    task = s.chip(56, 116, 200, 40, "task + files")
    s.fade_in(task, 0.9, 0.3)
    _arrow(s, 300, 114, 340, 114, 1.4)
    s.fade_out(task, 2.2, 0.35)
    _cap(s, 56, 156, "context cleared", 2.5, 10.5, BAD)
    ctx2 = s.card(20, 190, 280, 52, "Next context", "same document, new task")
    s.fade_in(ctx2, 2.9, 0.35)
    _arrow(s, 340, 174, 300, 190, 3.2)
    _cap(s, 20, 258, "What survives is what someone wrote down.", 4.2)
    return s


# ── 9. green build ───────────────────────────────────────────────────────────
def green_1():
    s = Scene("green-1", 250, DUR, "Three build inputs, one of them a moving branch name")
    _title(s, "Two of three inputs are pinned")
    a = s.card(20, 56, 180, 60, "App commit", "what the repo records")
    b = s.card(230, 56, 180, 60, "Dependency row", "ref: main", accent=True)
    c = s.card(440, 56, 180, 60, "Code compiled", "whatever main was")
    _appear(s, [a, b, c], 0.2, 0.35)
    _arrow(s, 200, 86, 230, 86, 1.1)
    _arrow(s, 410, 86, 440, 86, 1.3)
    pinned = s.card(230, 56, 180, 60, "Dependency row", "sha 4f2c91", accent=True)
    s.swap(b, pinned, 2.2, 0.45)
    _cap(s, 20, 150, "The build is only as reproducible as the loosest input.", 2.9)
    fix = s.card(20, 176, 600, 52, "Log the resolved revision of every dependency",
                 "and put the revision in the row", accent=True)
    s.fade_in(fix, 3.3, 0.35)
    return s


def green_2():
    s = Scene("green-2", 250, DUR, "A gate that reads the test session while a different artifact ships")
    _title(s, "The gate reads one input and ships another")
    gate = s.card(20, 56, 260, 60, "Gate", "reads the test session")
    art = s.card(340, 56, 280, 60, "Artifact", "built from a different revision", accent=True)
    _appear(s, [gate, art], 0.2, 0.35)
    green = s.chip(80, 146, 140, 44, "green", accent=True)
    s.fade_in(green, 1.2, 0.3)
    _arrow(s, 150, 116, 150, 146, 1.0)
    _cap(s, 20, 220, "A green check is a claim about an input, not about the artifact.", 2.6)
    ship = s.chip(400, 146, 160, 44, "ships")
    s.fade_in(ship, 2.4, 0.3)
    _arrow(s, 480, 116, 480, 146, 2.2)
    _cap(s, 20, 240, "The gap between the two is the bug.", 3.6)
    return s


# ── 10. four gates ───────────────────────────────────────────────────────────
def gates_1():
    s = Scene("gates-1", 320, DUR, "Four CI gates, the input each read, and the claim each green result was believed to make")
    _title(s, "What it read, what it certified")
    for x, t in ((20, "GATE"), (150, "IT READ"), (392, "IT CERTIFIED")):
        s.fade_in(s.text(x, 52, t, 10.5, MUTED), 0.2, 0.3)
    rows = [("Lint gate", "a directory of checkouts", "the set that ships"),
            ("Pre-push", "filenames, not the source", "every suite in the target"),
            ("Deploy job", "a build number nobody bumped", "a new artifact"),
            ("Snapshots", "the previous test's session", "the screen as drawn")]
    for i, (g, r, c) in enumerate(rows):
        y = 64 + i * 58
        line = s.line(20, y, 620, y, LINE, 1, trim=False)
        s.fade_in(line, 0.25 + i * 0.45, 0.25)
        s.fade_in(s.text(20, y + 30, g, 12.5, INK), 0.3 + i * 0.45, 0.3)
        s.fade_in(s.text(150, y + 30, r, 11, MUTED), 0.45 + i * 0.45, 0.3)
        s.fade_in(s.text(392, y + 30, c, 11, ACCENT), 0.6 + i * 0.45, 0.3)
    _cap(s, 20, 310, "Right column: what I assumed. Middle: what it touched.", 4.0)
    return s


def gates_2():
    s = Scene("gates-2", 280, DUR, "Four gate results converging on one green badge that is not the shipping artifact")
    _title(s, "Four greens, none of them the artifact")
    corners = [s.chip(20, 56, 170, 46, "lint"),
               s.chip(20, 190, 170, 46, "tests"),
               s.chip(450, 56, 170, 46, "deploy"),
               s.chip(450, 190, 170, 46, "snapshots")]
    _appear(s, corners, 0.2, 0.3)
    badge = s.chip(245, 108, 150, 54, "green", accent=True)
    s.fade_in(badge, 1.8, 0.35)
    _arrow(s, 190, 79, 245, 108, 1.2)
    _arrow(s, 190, 213, 245, 162, 1.4)
    _arrow(s, 450, 79, 395, 108, 1.6)
    _arrow(s, 450, 213, 395, 162, 1.8)
    art = s.chip(245, 200, 150, 46, "artifact?")
    s.fade_in(art, 2.8, 0.35)
    _cap(s, 245, 264, "not in this picture", 3.2, 10.5, BAD, "middle")
    return s


# ── 11. MVVM part one ────────────────────────────────────────────────────────
def mvvm1_1():
    s = Scene("mvvm1-1", 300, DUR, "Five responsibilities fanning into a single view model file")
    _title(s, "Five responsibilities, one file")
    file = s.card(20, 52, 600, 54, "The exam screen's view model",
                  "no rule about what may not move in", accent=True)
    s.fade_in(file, 0.2, 0.35)
    boxes = [("Question state", 20, 140), ("The answer rule", 225, 140),
             ("The offline queue", 430, 140), ("Navigation", 20, 214),
             ("The network calls", 225, 214)]
    for i, (t, x, y) in enumerate(boxes):
        n = s.chip(x, y, 190, 50, t)
        s.fade_in(n, 0.6 + i * 0.3, 0.3)
        _arrow(s, x + 95, 106, x + 95, y, 0.5 + i * 0.3, 0.25)
    sixth = s.chip(430, 214, 190, 50, "a sixth story", accent=True)
    s.fade_in(sixth, 2.6, 0.35)
    sixth.pulse(3.4, 0.6, 5)
    _cap(s, 20, 292, "Every one arrived as the smallest change that got a story done.", 4.0)
    return s


def mvvm1_2():
    s = Scene("mvvm1-2", 280, DUR, "The same view model file growing each time a new story adds one more responsibility")
    _title(s, "The file only ever grows")
    file = s.card(20, 52, 300, 80, "Exam view model", "state + rules + network + queue")
    s.fade_in(file, 0.2, 0.35)
    for i, t in enumerate(["story 1", "story 2", "story 3", "story 4"]):
        n = s.chip(380, 52 + i * 44, 200, 36, t, size=11.5)
        s.fade_in(n, 0.7 + i * 0.35, 0.25)
    _cap(s, 20, 160, "no boundary", 2.2, 10.5, BAD)
    sixth = s.chip(380, 228, 200, 36, "story 6 arrives", accent=True, size=11.5)
    s.fade_in(sixth, 2.8, 0.35)
    _arrow(s, 480, 228, 320, 132, 3.2)
    _cap(s, 20, 216, "The sixth is always one story away.", 3.8)
    return s


# ── 12. MVVM part two ────────────────────────────────────────────────────────
def mvvm2_1():
    s = Scene("mvvm2-1", 320, DUR, "A compiler wall around three layers, beside forty-three packages of bookkeeping")
    _title(s, "The wall works. The bill compounds.")
    for i, (t, sub) in enumerate((("Feature", "view, presenter, its state"),
                                  ("Data", "repository, mappers, network"),
                                  ("Domain", "entities, protocols"))):
        n = s.card(20, 52 + i * 66, 290, 56, t, sub)
        s.fade_in(n, 0.2 + i * 0.35, 0.3)
        if i < 2:
            _arrow(s, 165, 108 + i * 66, 165, 118 + i * 66, 0.4 + i * 0.35, 0.25)
    _cap(s, 20, 268, "a compile error", 1.5, 10.5, OK)
    cells = []
    for i in range(24):
        cells.append(s.rect(360 + (i % 6) * 40, 52 + (i // 6) * 40, 34, 32,
                            WARM if i % 7 else TINT, LINE, 6))
    _appear(s, cells, 1.8, 0.04, 0.15)
    _cap(s, 360, 226, "43 packages", 2.6, 13, ACCENT)
    _cap(s, 360, 248, "a repo, a manifest, a lock row,", 2.9, 11)
    _cap(s, 360, 266, "a CI path, a checkout", 3.1, 11)
    return s


def mvvm2_2():
    s = Scene("mvvm2-2", 280, DUR, "The package count growing with each feature, and the bookkeeping per module")
    _title(s, "The bill grows per module, not per feature")
    for i, (w, label) in enumerate(((200, "8 features, 12 core"),
                                    (360, "19 modules"),
                                    (500, "43 packages"))):
        n = s.rect(20, 70 + i * 46, w, 26, ACCENT if i == 2 else TINT, None, 4)
        s.fade_in(n, 0.4 + i * 0.6, 0.4)
        s.fade_in(s.text(20 + w + 12, 89 + i * 46, label, 11.5,
                         INK if i == 2 else MUTED), 0.5 + i * 0.6, 0.3)
    _cap(s, 20, 250, "Every feature pays the same per-module tax.", 3.4)
    return s


# ── 13. MVVM part three ──────────────────────────────────────────────────────
def viper_1():
    s = Scene("viper-1", 280, DUR, "Three architectures over one app and what the screen owned in each")
    _title(s, "What the screen owned, and what it cost")
    for x, t in ((20, "THE APP"), (150, "WHAT THE SCREEN OWNED"), (430, "THE BILL")):
        s.fade_in(s.text(x, 52, t, 10.5, MUTED), 0.2, 0.3)
    rows = [("MVVM", "state, rules, networking, navigation", "a file with no limits"),
            ("+ Clean", "entities and repositories behind a wall", "43 packages of bookkeeping"),
            ("VIPER", "state and intents; rules in interactors", "three files per screen, paid")]
    for i, (era, what, bill) in enumerate(rows):
        y = 64 + i * 64
        s.fade_in(s.line(20, y, 620, y, LINE, 1, trim=False), 0.25 + i * 0.5, 0.25)
        s.fade_in(s.text(20, y + 30, era, 12.5, INK), 0.3 + i * 0.5, 0.3)
        s.fade_in(s.text(150, y + 30, what, 11, MUTED), 0.45 + i * 0.5, 0.3)
        s.fade_in(s.text(430, y + 30, bill, 11, ACCENT), 0.6 + i * 0.5, 0.3)
    _cap(s, 20, 268, "The last row is why VIPER was worth paying for, here.", 3.8)
    return s


def viper_2():
    s = Scene("viper-2", 280, DUR, "What the screen owns falling while the bill rises, then a final payment")
    _title(s, "Ownership down, bill up, then paid")
    owned = s.card(20, 56, 290, 56, "What the screen owns", "state and intents")
    s.fade_in(owned, 0.2, 0.35)
    bill = s.card(330, 56, 290, 56, "The bill", "three files per screen", accent=True)
    s.fade_in(bill, 0.5, 0.35)
    down = s.rect(20, 140, 290, 10, ACCENT, None, 5)
    s.fade_in(down, 1.0, 0.3)
    down.scale_to(2.0, 35, 0.8)
    up = s.rect(330, 140, 290, 10, BAD, None, 5)
    up.scale_to(0.05, 35, 0.01)
    s.fade_in(up, 1.2, 0.3)
    up.scale_to(2.4, 100, 0.8)
    paid = s.chip(20, 186, 600, 46, "the bill, paid once per screen", accent=True)
    s.fade_in(paid, 3.2, 0.4)
    _cap(s, 20, 262, "Cheaper per change, dearer per screen. That was the trade.", 4.0)
    return s


# ── 14. exam mode ────────────────────────────────────────────────────────────
def exam_1():
    s = Scene("exam-1", 240, DUR, "Two preparation flows: the lock arming inside the paper, then one screen earlier")
    _title(s, "The lock moved one screen earlier")
    after = [s.chip(20 + i * 123, 52, 112, 50, t, accent=(i == 2))
             for i, t in enumerate(["Welcome", "Location", "Activate mode", "Ready", "Paper"])]
    before = [s.chip(20 + i * 123, 150, 112, 50, t, accent=(i == 4))
              for i, t in enumerate(["Welcome", "Location", "Ready", "Paper"])]
    _appear(s, after, 0.2, 0.22)
    _appear(s, before, 2.0, 0.22)
    _cap(s, 20, 44, "AFTER: armed in preparation", 0.1, 10.5, ACCENT)
    _cap(s, 20, 142, "BEFORE: armed inside the paper", 1.9, 10.5, MUTED)
    s.fade_in(s.rect(266, 150, 112, 50, None, LINE, 9), 2.3, 0.3)
    _cap(s, 322, 180, "no step", 2.6, 10.5, MUTED, "middle")
    after[2].pulse(3.6, 0.7, 5)
    _cap(s, 20, 226, "The lock did not get stronger. It moved.", 4.2)
    return s


def exam_2():
    s = Scene("exam-2", 260, DUR, "One blocked screen layout with two word sets, a server verdict and a missing device lock")
    _title(s, "One layout, two claims")
    frame = s.rect(20, 52, 600, 150, SURFACE, LINE, 14)
    s.fade_in(frame, 0.2, 0.35)
    server = s.card(56, 70, 500, 74, "Assessment blocked",
                    "The system detected activity that breaks the rules.")
    s.fade_in(server, 0.5, 0.3)
    lock = s.card(56, 70, 500, 74, "Activate exam mode",
                  "Exam mode is not running on this device.")
    s.swap(server, lock, 2.2, 0.45)
    btn = s.chip(56, 154, 210, 38, "Reload assessment")
    s.fade_in(btn, 2.8, 0.3)
    btn.pulse(3.6, 0.6, 5)
    _cap(s, 20, 226, "Sharing the words made both screens wrong.", 4.0)
    return s


SPECS = {
    "kiosk-and-assessment-apps": [
        (kiosk_1, "Two questions about supervision and OS support lead to three ways to lock an exam device.",
         "What the platform will enforce, and what is left to a person. Apple's documentation says Single App Mode and Guided Access supersede assessment mode."),
        (kiosk_2, "A boundary drawn around the exam app, with the home button, notifications and a proctor outside it.",
         "The entitlement covers the app. The room is still someone else's decision, which is why a proctor cannot be designed away."),
    ],
    "splitting-an-app-into-local-packages": [
        (packages_1, "Four layers from app shell down to leaves, with dependencies pointing downward.",
         "The shape that pays: leaves that depend on nothing, a thin shell that owns composition, and a cycle that cannot compile."),
        (packages_2, "Two feature modules pointing at each other until one edge is removed and the graph builds.",
         "A cycle is not a style problem. It is the one dependency rule the compiler can enforce for free."),
    ],
    "build-time-is-a-dependency-graph-problem": [
        (build_1, "The same one-file change rebuilding almost a whole target, against rebuilding one module of several.",
         "One edit, two build graphs. The machine is identical in both."),
        (build_2, "A change travelling from one file through its module and its dependents, then stopping at a narrow surface.",
         "The edit propagates until a boundary stops it. Build time is a property of where those boundaries are."),
    ],
    "uikit-to-swiftui-without-a-rewrite": [
        (migration_1, "A migration in four ordered steps, with navigation moved last.",
         "Progress in one direction, with the navigation seam held still until the end."),
        (migration_2, "UIKit and SwiftUI screens both reporting events to a single router that owns the stack.",
         "Neither side pushes. Both describe what happened, and one owner decides what that means."),
    ],
    "a-design-system-is-a-review-policy": [
        (design_1, "A design value with two traceable owners and a third literal copy drifting away from both.",
         "Two owners is a system. Three is a countdown."),
        (design_2, "A hardcoded colour in a screen replaced during review by the design token.",
         "The policy lives in review. A literal at 6pm is a review problem before it is a design-system problem."),
    ],
    "how-i-review-ios-pull-requests": [
        (review_1, "Five review questions lighting in order, from intent and crash risk down to style last.",
         "Cheapest questions first, taste last."),
        (review_2, "A diff split into added and deleted lines, with deletions read before any style comment.",
         "A deletion is a decision someone already made. It is the fastest signal in the diff."),
    ],
    "the-ios-stack-i-actually-reach-for": [
        (stack_1, "Five layers of an iOS stack, each labelled with the rule that decides it.",
         "Not preferences. The rule each layer is chosen by."),
        (stack_2, "A requirement descending from a feature to the data layer, where the platform API replaces a package.",
         "Reach for the platform before the dependency. The cheapest dependency is the one the OS already ships."),
    ],
    "ai-native-development-process": [
        (ai_1, "Four checkpoints in an agent workflow with a marker travelling the loop, two checkpoints marked as proof.",
         "Four checkpoints. Two are writing, and the two that matter most are the ones I will not take on trust."),
        (ai_2, "A context window cleared between tasks while the written document survives and restores the next one.",
         "A blank context window each time. The document is the only memory, which is why it is written down."),
    ],
    "what-a-green-build-does-not-prove": [
        (green_1, "Three build inputs, with a branch name replaced by a resolved revision.",
         "Three inputs, one of them moving. The fix is one column and one log line."),
        (green_2, "A gate reading a test session and a different artifact shipping from another revision.",
         "A green check is a claim about an input. The artifact is a separate question."),
    ],
    "four-gates-that-certified-nothing": [
        (gates_1, "Four CI gates with the input each read and the claim its green result was believed to make.",
         "Four gates, one mistake each: the check touched one thing and was trusted about another."),
        (gates_2, "Four gate results converging on one green badge that is not the shipping artifact.",
         "Nothing in the middle of that picture is the artifact. That is the whole failure."),
    ],
    "mvvm-to-viper-part-one": [
        (mvvm1_1, "Five responsibilities fanning into a single view model file, with a sixth arriving.",
         "Five responsibilities, one file, and no rule that says a sixth cannot move in."),
        (mvvm1_2, "The same view model file growing as each story adds one more responsibility.",
         "Every one of them arrived as the smallest change that would get a story done. That is how a file becomes a layer."),
    ],
    "mvvm-to-viper-part-two": [
        (mvvm2_1, "A three-layer feature behind a compiler wall, beside a grid of forty-three packages.",
         "The wall is on the left, and it works. The bill is on the right, and it compounds per module."),
        (mvvm2_2, "The package count growing with each feature while the per-module bookkeeping stays the same.",
         "The bill is not per feature. It is per module, which is why it outlives the feature that justified it."),
    ],
    "mvvm-to-viper-part-three": [
        (viper_1, "Three architectures over one app, with what the screen owned and what each cost.",
         "Three passes over one app. The last row is why VIPER was worth paying for, here."),
        (viper_2, "What the screen owns shrinking while the bill rises, then the bill paid once per screen.",
         "Cheaper per change, dearer per screen. That was the trade, made with open eyes."),
    ],
    "exam-mode-one-screen-earlier": [
        (exam_1, "Two preparation flows: the device lock arming inside the paper, then one step earlier.",
         "The lock did not get stronger. It moved one screen earlier, to the last moment before the questions appear."),
        (exam_2, "One blocked screen with two word sets: a server verdict and a missing device lock.",
         "One layout, two claims. Sharing the words made both screens wrong."),
    ],
}


def build_all():
    """Return {slug: [(Scene, alt, caption), ...]} and the deterministic bytes."""
    out = {}
    for slug, entries in SPECS.items():
        out[slug] = [(fn(), alt, cap) for fn, alt, cap in entries]
    return out
