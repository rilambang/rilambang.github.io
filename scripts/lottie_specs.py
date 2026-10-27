#!/usr/bin/env python3
"""The blog's Lottie figures: two per post, one template, one bar.

Every figure is the same shape of story: a few real objects with their real
names, one cursor that travels to a control and presses it, one state change
that the press causes, and a held end state. Shapes move; the words are HTML
laid over the canvas, because a font baked into a Lottie file is the fastest
way to make it look cheap.

Timing comes from the tokens in lottie.py -- travel, dwell, press, ripple --
never from a per-figure guess. Nothing here is linear.
"""
from lottie import (Scene, ACCENT, INK, MUTED, LINE, SURFACE, TINT, OK, DIM,
                    T_FLIP, T_HOVER, T_DEFAULT, T_MOVE, T_BEAT, EASE_IN,
                    EASE_IN_OUT)

PAD = 20
BOX_H = 108


# ── kit ──────────────────────────────────────────────────────────────────────
def _grid(n):
    """The x grid every row uses: n boxes across the 600px text column."""
    w = (600 - (n - 1) * 10) / n
    return w, [PAD + i * (w + 10) for i in range(n)]


def _step(s, x, y, lines, lit=False, w=112, h=BOX_H, size=16):
    """One named box, and a lit overlay that says the flow reached it."""
    box = s.rect(x, y, w, h, SURFACE, LINE, 10)
    glow = s.rect(x, y, w, h, TINT, ACCENT, 10, opacity=100 if lit else 0)
    cx = x + w / 2
    if isinstance(lines, str):
        lines = [lines]
    if len(lines) == 1:
        s.text(cx, y + h / 2 + 6, lines[0], size, INK, "middle")
    else:
        s.text(cx, y + h / 2 - 8, lines[0], size, INK, "middle")
        s.text(cx, y + h / 2 + 14, lines[1], size, INK, "middle")
    return box, glow


def _row(s, x, y, w, label, status="", color=MUTED, h=40, size=15, tint=SURFACE,
         stroke=LINE):
    """A named row in a panel: label left, status right. Rows are the controls."""
    box = s.rect(x, y, w, h, tint, stroke, 8)
    s.text(x + 16, y + h / 2 + 5, label, size, INK)
    lab = None
    if status:
        lab = s.text(x + w - 16, y + h / 2 + 5, status, 13, color, "end")
    return box, lab


def _swap(s, x, y, old, new, t, size=13, color=OK):
    """A status that changes: the old word leaves, the new one arrives."""
    a = s.text(x, y, old, size, MUTED, "end")
    b = s.text(x, y, new, size, color, "end", opacity=0)
    a.fade(t, 0, T_FLIP, EASE_IN)
    b.fade(t, 100, T_FLIP)
    return a, b


def _bow(s, x1, y1, x2, y2, bow, color=LINE, width=1.1, n=8):
    """A curved edge: the detours a script phase adds to the graph."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + bow
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(((1 - t) ** 2 * x1 + 2 * (1 - t) * t * mx + t * t * x2 - x1,
                    (1 - t) ** 2 * y1 + 2 * (1 - t) * t * my + t * t * y2 - y1))
    return s.poly(x1, y1, pts, stroke=color, width=width)


def _shield(s, cx, cy, s_=1.0, half=False):
    """Outline to filled, never nothing to something.

    half fills only the top half: the lock was still arming when the paper
    opened. The outline stays whole either way.
    """
    pts = [(0, -9), (7, -5), (7, 1), (0, 9), (-7, 1), (-7, -5)]
    pts = [(p[0] * s_, p[1] * s_) for p in pts]
    outline = s.poly(cx, cy, pts + [pts[0]], stroke=DIM, width=1.8)
    if half:
        # the cut at y=0 meets the two vertical sides at x = +-7
        shape = [(-7 * s_, 0), (-7 * s_, -5 * s_), (0, -9 * s_),
                 (7 * s_, -5 * s_), (7 * s_, 0)]
    else:
        shape = pts
    fill = s.poly(cx, cy, shape, fill=OK, width=0)
    fill.opacity_keys = [(0, [0])]
    fill._apply_opacity()
    return outline, fill


def _row_scene(name, h, note, y, labels, dur=5.5):
    """The common case: one row of named boxes, lit as the flow reaches them."""
    s = Scene(name, h, dur, note)
    boxes, glows, xs, w = [], [], [], 0
    w, xs = _grid(len(labels))
    for i, lab in enumerate(labels):
        b, g = _step(s, xs[i], y, lab, w=w)
        boxes.append(b)
        glows.append(g)
    return s, boxes, glows, xs, w


def _finish(s, cursor, t, x=566, y=None):
    """The hand leaves, and the end state is left alone."""
    y = y if y is not None else s.h - 34
    cursor.move_to(t, x, y, T_DEFAULT)
    cursor.fade(t + 0.10, 0, T_HOVER, EASE_IN)
    return s


# ── state helpers ───────────────────────────────────────────────────────────
def _mark(s, x, y, w, h, t, color=OK, fill=TINT, r=8):
    """A lasting state change on a shape, so the end state differs from frame 0."""
    node = s.rect(x, y, w, h, fill, color, r, opacity=0)
    node.fade(t, 100, T_DEFAULT)
    return node


def _st(s, x, y, old, new, t, size=13, color=OK, anchor="end"):
    """One status slot: the old word leaves, the new one arrives."""
    a = s.text(x, y, old, size, MUTED, anchor)
    b = s.text(x, y, new, size, color, anchor, opacity=0)
    a.fade(t, 0, T_FLIP, EASE_IN)
    b.fade(t, 100, T_FLIP)
    return a, b


# ── 1. kiosk and assessment apps ────────────────────────────────────────────
def kiosk_1():
    """A session starts and the four things iOS will hold go locked."""
    s = Scene("kiosk-and-assessment-apps-1", 320, 5.5,
              "Starting an assessment session: the app switcher, Home, "
              "notifications and other apps all going locked")
    s.text(PAD, 20, "Assessment session", 12, MUTED)
    rows = ["App switcher", "Home button", "Notifications", "Other apps"]
    x, w = 40, 560
    ys = [44 + i * 48 for i in range(4)]
    for lab, y in zip(rows, ys):
        _row(s, x, y, w, lab, "open", MUTED, h=40)
    s.rect(x, 240, w, 44, TINT, ACCENT, 8)
    btn = s.text(x + 16, 268, "Start session", 15, ACCENT)

    cursor = s.cursor(590, 300)
    t = s.travel(cursor, 0.15, x + w - 60, 262)
    p = s.press(cursor, s.ring(x + w - 60, 262, 10), t)
    for i, y in enumerate(ys):
        _st(s, x + w - 16, y + 25, "open", "locked", p + i * 0.06)
        _mark(s, x, y, w, 40, p + i * 0.06, color=OK, fill="#12241c")
    btn.fade(p, 0, T_FLIP, EASE_IN)
    s.text(x + 16, 268, "Session running", 15, OK, opacity=0).fade(p, 100, T_FLIP)
    return _finish(s, cursor, p + 0.9, y=300)


def kiosk_2():
    """The entitlement is the first thing to ask for, and it takes a request."""
    s, boxes, glows, xs, w = _row_scene(
        "kiosk-and-assessment-apps-2", 240,
        "The assessment entitlement: request, review, session", 66,
        ["Entitlement", "Apple review", "Session"])
    cursor = s.cursor(590, 210)
    t = s.travel(cursor, 0.15, xs[0] + w / 2, 120)
    p = s.press(cursor, s.ring(xs[0] + w / 2, 120, 10), t)
    glows[0].fade(p, 100, T_DEFAULT)
    glows[1].fade(p + 0.30, 100, T_DEFAULT)
    glows[2].fade(p + 0.66, 100, T_DEFAULT)
    return _finish(s, cursor, p + 0.9, y=220)


# ── 2. splitting an app into local packages ─────────────────────────────────
def packages_1():
    """A file moves in a day; the boundary it crosses is the work."""
    s = Scene("splitting-an-app-into-local-packages-1", 300, 5.5,
              "Moving one file out of the app target and into a local package")
    w, xs = _grid(3)
    _step(s, xs[0], 48, ["App"], w=w)
    _step(s, xs[1], 48, ["Feature"], w=w)
    _step(s, xs[2], 48, ["Core"], w=w)
    s.line(xs[0] + w, 102, xs[1], 102, LINE, 1.5)
    s.line(xs[1] + w, 102, xs[2], 102, LINE, 1.5)

    file_card = s.rect(xs[0] + 16, 176, w - 32, 44, TINT, ACCENT, 8)
    file_label = s.text(xs[0] + w / 2, 204, "FeedView.swift", 13, ACCENT, "middle")

    cursor = s.cursor(590, 280)
    t = s.travel(cursor, 0.15, xs[0] + w / 2, 198)
    p = s.press(cursor, s.ring(xs[0] + w / 2, 198, 10), t)
    file_card.move_to(p + 0.05, xs[1] + w / 2, 198, 0.8, EASE_IN_OUT)
    file_label.move_to(p + 0.05, xs[1] + w / 2, 204, 0.8, EASE_IN_OUT)
    s.text(PAD, 272, "One file. One import boundary.", 12, MUTED)
    return _finish(s, cursor, p + 1.1, y=280)


def packages_2():
    """What breaks first is the boundary, not the build."""
    s = Scene("splitting-an-app-into-local-packages-2", 320, 5.5,
              "The order a local-package split breaks in: import cycle, public "
              "API, test target, previews")
    s.text(PAD, 20, "What breaks, in order", 12, MUTED)
    items = ["Import cycle", "Public API", "Test target", "Previews"]
    ys = [44 + i * 52 for i in range(4)]
    for lab, y in zip(items, ys):
        _row(s, 40, y, 560, lab, "", h=44)
    cursor = s.cursor(590, 300)
    t = s.travel(cursor, 0.15, 300, ys[0] + 22)
    p = s.press(cursor, s.ring(300, ys[0] + 22, 10), t)
    for i, y in enumerate(ys):
        _st(s, 584, y + 27, "", "day %d" % (1 + i * 3), p + i * 0.28,
            color="#ff9d9d")
        _mark(s, 40, y, 560, 44, p + i * 0.28, color="#ff9d9d", fill="#2a1a22")
    return _finish(s, cursor, p + 1.5, y=300)


# ── 3. build time is a dependency-graph problem ─────────────────────────────
def buildgraph_1():
    """Twelve edges become four when the script phase goes."""
    s = Scene("build-time-is-a-dependency-graph-problem-1", 320, 5.5,
              "Deleting one script phase removes most of the edges in the "
              "build graph")
    s.text(PAD, 20, "Build graph", 12, MUTED)
    s.rect(40, 110, 130, 100, SURFACE, LINE, 12)
    s.text(105, 166, "App", 16, INK, "middle")

    # the phase is a row you can press, not empty canvas
    s.rect(490, 36, 130, 44, SURFACE, LINE, 8)
    run = s.text(504, 62, "Run Script", 12.5, INK)
    gone = s.text(504, 62, "removed", 12.5, OK, opacity=0)

    # three edges per module from three App ports; the eight the phase adds
    # are bowed, so the graph reads as a tangle until they leave
    mods = ["Feature A", "Feature B", "Core", "UI kit"]
    ys = [48, 116, 184, 252]
    ports = [130, 160, 190]
    extra = []
    for lab, y in zip(mods, ys):
        s.rect(330, y, 150, 48, SURFACE, LINE, 8)
        s.text(346, y + 30, lab, 14, INK)
        for k, py in enumerate(ports):
            ty = y + 12 + k * 12
            if k == 1:
                s.line(170, py, 330, ty, LINE, 1.4)
            else:
                extra.append(_bow(s, 170, py, 330, ty,
                                  -16 if k == 0 else 16))

    cursor = s.cursor(600, 300)
    t = s.travel(cursor, 0.15, 598, 58)
    p = s.press(cursor, s.ring(598, 58, 10), t)
    for e in extra:
        e.fade(p + 0.1, 0, T_DEFAULT, EASE_IN)
    run.fade(p, 0, T_FLIP, EASE_IN)
    gone.fade(p, 100, T_FLIP)
    _st(s, 150, 262, "12 edges", "4 edges", p)
    return _finish(s, cursor, p + 1.0, y=300)


def buildgraph_2():
    """Hardware buys a constant; the graph is the exponent."""
    s = Scene("build-time-is-a-dependency-graph-problem-2", 300, 5.5,
              "A clean build on faster hardware against the same build after "
              "deleting a script phase")
    s.text(PAD, 20, "Clean build", 12, MUTED)
    _row(s, 40, 48, 560, "MacBook Pro", "4:10", h=44)
    _row(s, 40, 100, 560, "Mac Studio", "3:55", h=44)
    _row(s, 40, 176, 560, "MacBook Pro, one phase deleted", "", h=44,
         tint=TINT, stroke=ACCENT)
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 520, 198)
    p = s.press(cursor, s.ring(520, 198, 10), t)
    _st(s, 584, 203, "3:20", "2:05", p)
    _mark(s, 40, 176, 560, 44, p, color=OK, fill="#12241c")
    s.text(PAD, 268, "Faster hardware is a constant. The graph is the exponent.",
           12, MUTED)
    return _finish(s, cursor, p + 1.2, y=280)


# ── 4. UIKit to SwiftUI without a rewrite ───────────────────────────────────
def uikit_1():
    """Navigation changes owner; the content does not move."""
    s = Scene("uikit-to-swiftui-without-a-rewrite-1", 340, 5.5,
              "One screen converted: the navigation chrome changes owner and "
              "the same four rows stay put")
    s.rect(40, 32, 240, 276, SURFACE, LINE, 18)
    bar = s.rect(40, 32, 240, 56, TINT, LINE, 18)
    s.text(160, 68, "Exam", 15, INK, "middle")
    for i, lab in enumerate(["Welcome", "Location", "Ready", "Paper"]):
        s.text(72, 124 + i * 40, lab, 14, INK)
        s.line(60, 142 + i * 40, 260, 142 + i * 40, LINE, 1)

    s.rect(320, 60, 280, 96, SURFACE, LINE, 12)
    s.text(338, 92, "Navigation owner", 12, MUTED)
    _ = bar

    cursor = s.cursor(600, 300)
    t = s.travel(cursor, 0.15, 566, 92)
    p = s.press(cursor, s.ring(566, 92, 10), t)
    _mark(s, 40, 32, 240, 56, p, color=ACCENT, fill=TINT, r=18)
    # the chrome has settled by p + T_DEFAULT; only then does the word agree
    _st(s, 338, 126, "UIKit", "SwiftUI", p + 0.40, size=18, anchor="start")
    # the empty quadrant is the lower right: the caption fills it
    s.text(600, 296, "Same screen.", 13, MUTED, "end")
    s.text(600, 320, "Same rows.", 13, MUTED, "end")
    return _finish(s, cursor, p + 0.9, y=320)


def uikit_2():
    """The file moves once, and lands once."""
    s = Scene("uikit-to-swiftui-without-a-rewrite-2", 320, 5.5,
              "One file moving from the UIKit views folder into a SwiftUI "
              "folder, drawn once at rest")
    s.text(PAD, 20, "Views/", 12, MUTED)
    s.text(360, 20, "SwiftUI/", 12, MUTED)
    s.rect(40, 40, 260, 232, SURFACE, LINE, 14)
    s.rect(340, 40, 260, 232, SURFACE, LINE, 14)

    card = s.rect(72, 76, 196, 64, TINT, ACCENT, 10)
    label = s.text(170, 116, "ExamScreen.swift", 15, ACCENT, "middle")

    cursor = s.cursor(600, 290)
    t = s.travel(cursor, 0.15, 170, 108)
    p = s.press(cursor, s.ring(170, 108, 10), t)
    # the flying card is the only instance; the destination slot stays empty
    # until it lands, then one card replaces the other on the same frame
    card.move_to(p + 0.05, 470, 108, 1.0, EASE_IN_OUT)
    label.move_to(p + 0.05, 470, 116, 1.0, EASE_IN_OUT)
    landed = s.rect(372, 76, 196, 64, TINT, ACCENT, 10, opacity=0)
    landed_lab = s.text(470, 116, "ExamScreen.swift", 15, ACCENT, "middle",
                        opacity=0)
    landed.fade(p + 1.05, 100, 0.02)
    landed_lab.fade(p + 1.05, 100, 0.02)
    card.fade(p + 1.05, 0, 0.02)
    label.fade(p + 1.05, 0, 0.02)
    s.text(PAD, 304, "One file, one boundary, one instance.", 12, MUTED)
    return _finish(s, cursor, p + 1.4, y=300)


# ── 5. a design system is a review policy ───────────────────────────────────
def designsystem_1():
    """The review, not the import, is what holds the system."""
    s = Scene("a-design-system-is-a-review-policy-1", 320, 5.5,
              "A pull request with a local colour override, and review "
              "refusing it")
    s.text(PAD, 20, "Pull request 412", 12, MUTED)
    _row(s, 40, 44, 560, "Use the accent token", "ok", OK, h=44)
    _row(s, 40, 96, 560, "Local override #8ab4ff", "found", ACCENT, h=44)
    _row(s, 40, 172, 560, "Review", "", h=44, tint=TINT, stroke=ACCENT)
    cursor = s.cursor(600, 300)
    t = s.travel(cursor, 0.15, 540, 194)
    p = s.press(cursor, s.ring(540, 194, 10), t)
    _st(s, 584, 199, "approve", "blocked", p, color="#ff9d9d")
    _mark(s, 40, 172, 560, 44, p, color="#ff9d9d", fill="#2a1a22")
    s.text(PAD, 268, "The token package changed nothing. Review did.", 12, MUTED)
    return _finish(s, cursor, p + 1.2, y=300)


def designsystem_2():
    """Two ways to write the same colour; one of them is the system."""
    s = Scene("a-design-system-is-a-review-policy-2", 300, 5.5,
              "Choosing the token instead of the literal, and the local "
              "override disappearing from the diff")
    s.text(PAD, 20, "Colour", 12, MUTED)
    _row(s, 40, 44, 560, "Color.accent", "token", OK, h=44, tint=TINT,
         stroke=ACCENT)
    _row(s, 40, 96, 560, "#8ab4ff", "literal", MUTED, h=44)
    s.rect(40, 168, 560, 76, SURFACE, LINE, 12)
    s.text(60, 200, "Diff", 12, MUTED)
    minus = s.text(60, 224, "- #8ab4ff", 14, "#ff9d9d")
    plus = s.text(220, 224, "+ Color.accent", 14, OK, opacity=0)
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 520, 66)
    p = s.press(cursor, s.ring(520, 66, 10), t)
    _mark(s, 40, 96, 560, 44, p, color="#ff9d9d", fill="#2a1a22")
    minus.fade(p + 0.2, 0, T_FLIP, EASE_IN)
    plus.fade(p + 0.2, 100, T_FLIP)
    return _finish(s, cursor, p + 1.2, y=280)


# ── 6. how I review iOS pull requests ───────────────────────────────────────
def review_1():
    """Risk comes first, style last, and the order is the review."""
    s = Scene("how-i-review-ios-pull-requests-1", 300, 5.5,
              "A pull request review reordered so risk is read before style")
    s.text(PAD, 20, "Review order", 12, MUTED)
    rows = ["Style", "Behaviour", "Risk"]
    ys = [44, 96, 148]
    boxes = []
    for lab, y in zip(rows, ys):
        boxes.append((s.rect(40, y, 560, 44, SURFACE, LINE, 8),
                      s.text(56, y + 27, lab, 15, INK)))
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 520, 66)
    p = s.press(cursor, s.ring(520, 66, 10), t)
    # risk to the top, style and behaviour one row down: absolute positions
    for (box, lab), y in zip([boxes[2], boxes[0], boxes[1]], [44, 96, 148]):
        box.move_to(p + 0.1, 320, y + 22, 0.7, EASE_IN_OUT)
        lab.move_to(p + 0.1, 56, y + 27, 0.7, EASE_IN_OUT)
    return _finish(s, cursor, p + 1.2, y=280)


def review_2():
    """The comment that names the failure mode is the review."""
    s = Scene("how-i-review-ios-pull-requests-2", 300, 5.5,
              "A review comment attached to the line that carries the risk")
    s.rect(40, 40, 560, 200, SURFACE, LINE, 12)
    s.text(60, 74, "ExamSession.swift", 13, MUTED)
    for i, lab in enumerate(["+ func start() {", "+   session.start()", "+   lock()"]):
        s.text(60, 112 + i * 32, lab, 14, INK)
    comment = s.rect(320, 104, 260, 76, TINT, ACCENT, 8, opacity=0)
    q1 = s.text(336, 132, "What if start() throws?", 13, ACCENT, opacity=0)
    q2 = s.text(336, 154, "The lock never runs.", 12, MUTED, opacity=0)
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 300, 140)
    p = s.press(cursor, s.ring(300, 140, 10), t)
    comment.fade(p + 0.1, 100, T_DEFAULT)
    q1.fade(p + 0.1, 100, T_DEFAULT)
    q2.fade(p + 0.18, 100, T_DEFAULT)
    return _finish(s, cursor, p + 1.1, y=280)


# ── 7. the iOS stack I actually reach for ───────────────────────────────────
def stack_1():
    """A stack chosen for who debugs it at 3am."""
    s = Scene("the-ios-stack-i-actually-reach-for-1", 320, 5.5,
              "A stack list where the choice is priced by whether the next "
              "engineer can debug it")
    s.text(PAD, 20, "The stack", 12, MUTED)
    for i, lab in enumerate(["SwiftUI", "SwiftData", "URLSession", "Swift Testing"]):
        _row(s, 40, 44 + i * 52, 560, lab, "keep", OK, h=44)
    _row(s, 40, 256, 560, "A dependency nobody can debug", "", h=44,
         tint=TINT, stroke=ACCENT)
    cursor = s.cursor(600, 300)
    t = s.travel(cursor, 0.15, 540, 278)
    p = s.press(cursor, s.ring(540, 278, 10), t)
    _st(s, 584, 283, "drop", "removed", p)
    _mark(s, 40, 256, 560, 44, p, color="#ff9d9d", fill="#2a1a22")
    return _finish(s, cursor, p + 1.1, y=300)


def stack_2():
    """Every dependency is a 3am page."""
    s = Scene("the-ios-stack-i-actually-reach-for-2", 300, 5.5,
              "Adding one dependency and the number of things that can wake "
              "you at 3am going up")
    s.text(PAD, 20, "Dependencies", 12, MUTED)
    _row(s, 40, 48, 560, "SwiftUI, SwiftData, URLSession", "3", h=44)
    _row(s, 40, 100, 560, "Add a networking wrapper", "4", ACCENT, h=44,
         tint=TINT, stroke=ACCENT)
    s.text(40, 176, "3am pages", 12, MUTED)
    pages = s.text(40, 216, "3", 34, INK)
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 520, 122)
    p = s.press(cursor, s.ring(520, 122, 10), t)
    _mark(s, 40, 100, 560, 44, p, color="#ff9d9d", fill="#2a1a22")
    pages.fade(p, 0, T_FLIP, EASE_IN)
    s.text(40, 216, "4", 34, "#ff9d9d", opacity=0).fade(p, 100, T_FLIP)
    return _finish(s, cursor, p + 1.2, y=280)


# ── 8. AI-native development is a process ───────────────────────────────────
def ai_1():
    """The agent works from the brief, not from the whole repo."""
    s, boxes, glows, xs, w = _row_scene(
        "ai-native-development-process-1", 240,
        "Conventions, brief and evidence: what the agent is allowed to work "
        "from", 66, ["Conventions", "Brief", "Evidence"])
    cursor = s.cursor(590, 210)
    t = s.travel(cursor, 0.15, xs[1] + w / 2, 120)
    p = s.press(cursor, s.ring(xs[1] + w / 2, 120, 10), t)
    glows[1].fade(p, 100, T_DEFAULT)
    glows[2].fade(p + 0.40, 100, T_DEFAULT)
    return _finish(s, cursor, p + 1.0, y=220)


def ai_2():
    """The agent proposes; the human merges."""
    s = Scene("ai-native-development-process-2", 300, 5.5,
              "An agent proposing a change and a human merging it")
    s.text(PAD, 20, "Proposed change", 12, MUTED)
    _row(s, 40, 44, 560, "Edit 3 files", "agent", MUTED, h=44)
    _row(s, 40, 96, 560, "Run the tests", "green", OK, h=44)
    _row(s, 40, 172, 560, "Merge", "", h=44, tint=TINT, stroke=ACCENT)
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 540, 194)
    p = s.press(cursor, s.ring(540, 194, 10), t)
    _st(s, 584, 199, "waiting", "human", p)
    _mark(s, 40, 172, 560, 44, p, color=ACCENT, fill=TINT)
    return _finish(s, cursor, p + 1.2, y=280)


# ── 9. what a green build does not prove ────────────────────────────────────
def green_1():
    """Five green ticks, three of which ran nothing."""
    s = Scene("what-a-green-build-does-not-prove-1", 320, 5.5,
              "Five green checks, three of which ran no tests")
    s.text(PAD, 20, "Checks", 12, MUTED)
    items = ["Lint", "Unit tests", "Snapshot tests", "UI tests", "Deploy"]
    ys = [44 + i * 46 for i in range(5)]
    for i, (lab, y) in enumerate(zip(items, ys)):
        _row(s, 40, y, 560, lab, "passed" if i in (0, 4) else "", OK, h=40)
    cursor = s.cursor(600, 300)
    t = s.travel(cursor, 0.15, 540, 62)
    p = s.press(cursor, s.ring(540, 62, 10), t)
    for i, y in enumerate(ys[1:4]):
        _st(s, 584, y + 25, "passed", "0 tests", p + i * 0.16, color="#ff9d9d")
        _mark(s, 40, y, 560, 40, p + i * 0.16, color="#ff9d9d", fill="#2a1a22")
    return _finish(s, cursor, p + 1.3, y=300)


def green_2():
    """A lock file that pinned a branch."""
    s = Scene("what-a-green-build-does-not-prove-2", 300, 5.5,
              "A resolved lock file pinned to a branch instead of a version")
    s.text(PAD, 20, "Package.resolved", 12, MUTED)
    _row(s, 40, 48, 560, "swift-argument-parser", "1.3.0", h=44)
    _row(s, 40, 100, 560, "networking", "", h=44)
    s.text(40, 176, "Pinned to", 12, MUTED)
    pin = s.text(40, 216, "main", 30, INK)
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 520, 122)
    p = s.press(cursor, s.ring(520, 122, 10), t)
    _st(s, 584, 127, "branch: main", "1.3.0", p)
    _mark(s, 40, 100, 560, 44, p, color=OK, fill="#12241c")
    pin.fade(p, 0, T_FLIP, EASE_IN)
    s.text(40, 216, "1.3.0", 30, OK, opacity=0).fade(p, 100, T_FLIP)
    return _finish(s, cursor, p + 1.2, y=280)


# ── 10. four gates that certified nothing ───────────────────────────────────
def gates_1():
    """Four gates, all green, and what each one actually ran."""
    s = Scene("four-gates-that-certified-nothing-1", 320, 5.5,
              "Four green gates revealing what each one actually ran")
    s.text(PAD, 20, "Release gates", 12, MUTED)
    items = ["Lint", "Pre-push tests", "Build number", "Snapshots"]
    ys = [44 + i * 52 for i in range(4)]
    for lab, y in zip(items, ys):
        _row(s, 40, y, 560, lab, "", h=44)
    cursor = s.cursor(600, 300)
    t = s.travel(cursor, 0.15, 300, ys[0] + 22)
    p = s.press(cursor, s.ring(300, ys[0] + 22, 10), t)
    ran = ["1 dir", "2 of 3", "1 of 3", "0 tests"]
    for i, y in enumerate(ys):
        _st(s, 584, y + 27, "green", ran[i], p + i * 0.24, color="#ff9d9d")
        _mark(s, 40, y, 560, 44, p + i * 0.24, color="#ff9d9d", fill="#2a1a22")
    return _finish(s, cursor, p + 1.6, y=300)


def gates_2():
    """Three uploads, one build number."""
    s = Scene("four-gates-that-certified-nothing-2", 300, 5.5,
              "Three uploads sharing one build number")
    s.text(PAD, 20, "Uploads", 12, MUTED)
    for y, lab in ((48, "TestFlight internal"), (100, "TestFlight external"),
                   (152, "App Store")):
        _row(s, 40, y, 560, lab, "build 42", MUTED, h=44)
    head = s.text(40, 236, "Three uploads. One build.", 15, INK)
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 520, 170)
    p = s.press(cursor, s.ring(520, 170, 10), t)
    for y in (48, 100, 152):
        _mark(s, 40, y, 560, 44, p, color="#ff9d9d", fill="#2a1a22")
    head.fade(p, 0, T_FLIP, EASE_IN)
    s.text(40, 236, "Nobody can tell them apart.", 15, "#ff9d9d", opacity=0).fade(
        p, 100, T_FLIP)
    return _finish(s, cursor, p + 1.3, y=280)


# ── 11. MVVM to VIPER, part one ─────────────────────────────────────────────
def mvvm1_1():
    """The view model quietly takes the screen's ownership."""
    s = Scene("mvvm-to-viper-part-one-1", 320, 5.5,
              "A view model absorbing navigation from the view")
    s.rect(40, 44, 260, 240, SURFACE, LINE, 14)
    s.text(60, 78, "ExamView", 14, MUTED)
    for i, lab in enumerate(["score", "timer", "questions"]):
        s.text(60, 126 + i * 40, lab, 14, INK)
    s.rect(340, 44, 260, 240, SURFACE, LINE, 14)
    s.text(360, 78, "ExamViewModel", 14, MUTED)
    for i, lab in enumerate(["score", "timer", "questions"]):
        s.text(360, 126 + i * 40, lab, 14, INK)
    s.text(360, 254, "navigate(to:)", 14, "#ff9d9d", opacity=0)
    cursor = s.cursor(600, 300)
    t = s.travel(cursor, 0.15, 470, 190)
    p = s.press(cursor, s.ring(470, 190, 10), t)
    _mark(s, 340, 232, 260, 44, p, color="#ff9d9d", fill="#2a1a22")
    s.text(360, 254, "navigate(to:)", 14, "#ff9d9d", opacity=0).fade(
        p, 100, T_DEFAULT)
    return _finish(s, cursor, p + 1.2, y=300)


def mvvm1_2():
    """One screen, one owner: the router owns where you go next."""
    s, boxes, glows, xs, w = _row_scene(
        "mvvm-to-viper-part-one-2", 240,
        "A screen, six use cases and one router: who owns navigation", 66,
        ["Screen", "6 use cases", "Router"])
    cursor = s.cursor(590, 210)
    t = s.travel(cursor, 0.15, xs[2] + w / 2, 120)
    p = s.press(cursor, s.ring(xs[2] + w / 2, 120, 10), t)
    glows[2].fade(p, 100, T_DEFAULT)
    return _finish(s, cursor, p + 1.0, y=220)


# ── 12. MVVM to VIPER, part two ─────────────────────────────────────────────
def mvvm2_1():
    """Three targets per feature becomes forty-three packages."""
    s = Scene("mvvm-to-viper-part-two-1", 300, 5.5,
              "Splitting a feature into three targets and the package count "
              "going from three to forty-three")
    s.text(PAD, 20, "Packages", 12, MUTED)
    _row(s, 40, 48, 560, "One app target", "1", h=44)
    _row(s, 40, 100, 560, "Three targets per feature", "", ACCENT, h=44,
         tint=TINT, stroke=ACCENT)
    count = s.text(40, 190, "3", 44, INK)
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 520, 122)
    p = s.press(cursor, s.ring(520, 122, 10), t)
    _st(s, 584, 127, "3", "43", p, color="#ff9d9d")
    _mark(s, 40, 100, 560, 44, p, color="#ff9d9d", fill="#2a1a22")
    count.fade(p, 0, T_FLIP, EASE_IN)
    s.text(40, 190, "43", 44, "#ff9d9d", opacity=0).fade(p, 100, T_FLIP)
    return _finish(s, cursor, p + 1.2, y=280)


def mvvm2_2():
    """The bill for the split arrives at compile time."""
    s = Scene("mvvm-to-viper-part-two-2", 300, 5.5,
              "The compile time bill for splitting every feature into three "
              "targets")
    s.text(PAD, 20, "The bill", 12, MUTED)
    _row(s, 40, 48, 560, "Packages", "43", h=44)
    _row(s, 40, 100, 560, "Targets", "129", h=44)
    _row(s, 40, 176, 560, "Clean build", "", h=44, tint=TINT, stroke=ACCENT)
    s.text(584, 223, "4:40", 13, MUTED, "end")
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 520, 198)
    p = s.press(cursor, s.ring(520, 198, 10), t)
    _st(s, 584, 223, "4:40", "9:10", p, color="#ff9d9d")
    _mark(s, 40, 176, 560, 44, p, color="#ff9d9d", fill="#2a1a22")
    return _finish(s, cursor, p + 1.2, y=280)


# ── 13. MVVM to VIPER, part three ───────────────────────────────────────────
def mvvm3_1():
    """Forty-three packages down to nineteen, by merging what was never apart."""
    s = Scene("mvvm-to-viper-part-three-1", 300, 5.5,
              "Merging packages back down from forty-three to nineteen")
    s.text(PAD, 20, "Packages", 12, MUTED)
    _row(s, 40, 48, 560, "After the split", "43", h=44)
    _row(s, 40, 100, 560, "Merge the router into the screen", "", OK, h=44,
         tint=TINT, stroke=ACCENT)
    count = s.text(40, 190, "43", 44, INK)
    cursor = s.cursor(600, 280)
    t = s.travel(cursor, 0.15, 520, 122)
    p = s.press(cursor, s.ring(520, 122, 10), t)
    _st(s, 584, 127, "43", "19", p, color=OK)
    _mark(s, 40, 100, 560, 44, p, color=OK, fill="#12241c")
    count.fade(p, 0, T_FLIP, EASE_IN)
    s.text(40, 190, "19", 44, OK, opacity=0).fade(p, 100, T_FLIP)
    return _finish(s, cursor, p + 1.2, y=280)


def mvvm3_2():
    """The rename fixed nothing Clean had not; the screen was the last owner."""
    s, boxes, glows, xs, w = _row_scene(
        "mvvm-to-viper-part-three-2", 240,
        "The screen as the last unowned thing, and the router taking it", 66,
        ["View", "Presenter", "Router"])
    cursor = s.cursor(590, 210)
    t = s.travel(cursor, 0.15, xs[2] + w / 2, 120)
    p = s.press(cursor, s.ring(xs[2] + w / 2, 120, 10), t)
    glows[2].fade(p, 100, T_DEFAULT)
    return _finish(s, cursor, p + 1.0, y=220)


# ── 14. exam mode, one screen earlier ───────────────────────────────────────
def exam_mode_1():
    """The lock moves from inside the paper to the step before it.

    Before: the paper opens, then the shield fills. Now: the shield fills, and
    only then does the flow reach Ready. Same cursor, same gesture, one screen
    earlier -- the difference is where the green lands, so it is read, not
    captioned.
    """
    s = Scene("exam-mode-one-screen-earlier-1", 340, 5.5,
              "The exam-mode lock moving from inside the paper to the step "
              "before it: the same cursor, one screen earlier")

    Y1, Y2 = 48, 200
    s.text(PAD, 32, "Before", 12, MUTED)
    s.text(PAD, 184, "Now", 12, MUTED)

    _step(s, 20, Y1, ["Welcome"], lit=True)
    _step(s, 142, Y1, ["Location"], lit=True)
    _step(s, 264, Y1, ["Ready"], lit=True)
    _paper, paper_lit = _step(s, 386, Y1, ["Paper"])
    paper_glow = s.rect(386, Y1, 112, BOX_H, ACCENT, None, 10, opacity=0)
    _, paper_shield = _shield(s, 442, Y1 + 86, half=True)
    lock1 = s.rect(386, Y1, 112, BOX_H, None, OK, 10, opacity=0)

    _step(s, 20, Y2, ["Welcome"], lit=True)
    _step(s, 142, Y2, ["Location"], lit=True)
    _act, act_lit = _step(s, 264, Y2, ["Activate", "exam mode"])
    _ready, ready_lit = _step(s, 386, Y2, ["Ready"])
    _paper2, paper2_lit = _step(s, 508, Y2, ["Paper"])
    act_glow = s.rect(264, Y2, 112, BOX_H, ACCENT, None, 10, opacity=0)
    _, act_shield = _shield(s, 320, Y2 + 86)
    lock2 = s.rect(264, Y2, 112, BOX_H, None, OK, 10, opacity=0)

    ring1 = s.ring(442, Y1 + 86, 10)
    ring2 = s.ring(320, Y2 + 86, 10)
    cursor = s.cursor(600, 300)

    t1 = s.travel(cursor, 0.15, 442, Y1 + 86)
    p1 = s.press(cursor, ring1, t1)

    paper_glow.fade(p1 - 0.12, 22, T_FLIP)
    paper_glow.fade(p1 - 0.04, 0, T_HOVER, EASE_IN)
    paper_lit.show(p1, T_FLIP)

    # the hand leaves before the lock fills, and the lock arms after the paper
    # was already open: the wrong moment
    t2 = s.travel(cursor, p1 + 0.56, 320, Y2 + 86)
    paper_shield.show(p1 + 0.24, T_DEFAULT)
    lock1.show(p1 + 0.24, T_DEFAULT)

    p2 = s.press(cursor, ring2, t2)
    act_glow.fade(p2 - 0.12, 22, T_FLIP)
    act_glow.fade(p2 - 0.04, 0, T_HOVER, EASE_IN)
    act_lit.show(p2, T_FLIP)
    act_shield.show(p2 + 0.04, T_DEFAULT)
    lock2.show(p2 + 0.04, T_DEFAULT)

    ready_lit.show(p2 + 0.46, T_FLIP)
    paper2_lit.show(p2 + 0.66, T_FLIP)

    cursor.move_to(p2 + 0.76, 390, 306, T_DEFAULT)
    cursor.fade(p2 + 0.86, 0, T_HOVER, EASE_IN)
    return s


def exam_mode_2():
    """The blocked screen: the lock is not the hard part, the words are."""
    s = Scene("exam-mode-one-screen-earlier-2", 320, 5.5,
              "The screen a student sees when the lock cannot start: the "
              "words, and the way out")
    s.rect(40, 36, 560, 240, SURFACE, LINE, 14)
    s.text(60, 76, "Exam mode could not start", 18, INK)
    s.text(60, 112, "Your device is not ready for this assessment.", 14, MUTED)
    _row(s, 60, 148, 520, "Try again", "", ACCENT, h=44, tint=TINT,
         stroke=ACCENT)
    _row(s, 60, 200, 520, "Ask your teacher for help", "link", MUTED, h=44)
    cursor = s.cursor(600, 300)
    t = s.travel(cursor, 0.15, 520, 170)
    p = s.press(cursor, s.ring(520, 170, 10), t)
    _st(s, 560, 174, "button", "retry", p, color=OK)
    _mark(s, 60, 148, 520, 44, p, color=OK, fill="#12241c")
    s.text(60, 296, "No dead end, and no blame.", 12, MUTED)
    return _finish(s, cursor, p + 1.2, y=300)


SPECS = {
    "kiosk-and-assessment-apps": [
        (kiosk_1,
         "Starting an assessment session: the app switcher, Home, "
         "notifications and other apps all going locked",
         "A session starts and the four things iOS will hold go locked."),
        (kiosk_2,
         "The assessment entitlement: request, review, session",
         "The entitlement is the first thing to ask for, and it is a request."),
    ],
    "splitting-an-app-into-local-packages": [
        (packages_1,
         "Moving one file out of the app target and into a local package",
         "The file moves in a day; the boundary it crosses is the work."),
        (packages_2,
         "The order a local-package split breaks in",
         "What breaks first is the boundary, not the build."),
    ],
    "build-time-is-a-dependency-graph-problem": [
        (buildgraph_1,
         "Deleting one script phase removes most of the edges in the build graph",
         "Twelve edges become four when the script phase goes."),
        (buildgraph_2,
         "A clean build on faster hardware against the same build after "
         "deleting a script phase",
         "Faster hardware is a constant. The graph is the exponent."),
    ],
    "uikit-to-swiftui-without-a-rewrite": [
        (uikit_1,
         "One screen converted: the navigation chrome changes owner and the "
         "same four rows stay put",
         "Navigation changes owner; the content does not move."),
        (uikit_2,
         "One file moving from the UIKit views folder into a SwiftUI folder",
         "The file moves once, and lands once."),
    ],
    "a-design-system-is-a-review-policy": [
        (designsystem_1,
         "A pull request with a local colour override, and review refusing it",
         "The review, not the import, is what holds the system."),
        (designsystem_2,
         "Choosing the token instead of the literal",
         "Two ways to write the same colour; one of them is the system."),
    ],
    "how-i-review-ios-pull-requests": [
        (review_1,
         "A pull request review reordered so risk is read before style",
         "Risk comes first, style last, and the order is the review."),
        (review_2,
         "A review comment attached to the line that carries the risk",
         "The comment that names the failure mode is the review."),
    ],
    "the-ios-stack-i-actually-reach-for": [
        (stack_1,
         "A stack list where the choice is priced by whether the next engineer "
         "can debug it",
         "A stack chosen for who debugs it at 3am."),
        (stack_2,
         "Adding one dependency and the number of things that can wake you at "
         "3am going up",
         "Every dependency is a 3am page."),
    ],
    "ai-native-development-process": [
        (ai_1,
         "Conventions, brief and evidence: what the agent is allowed to work from",
         "The agent works from the brief, not from the whole repo."),
        (ai_2,
         "An agent proposing a change and a human merging it",
         "The agent proposes; the human merges."),
    ],
    "what-a-green-build-does-not-prove": [
        (green_1,
         "Five green checks, three of which ran no tests",
         "Five green ticks, three of which ran nothing."),
        (green_2,
         "A resolved lock file pinned to a branch instead of a version",
         "A lock file that pinned a branch."),
    ],
    "four-gates-that-certified-nothing": [
        (gates_1,
         "Four green gates revealing what each one actually ran",
         "Four gates, all green, and what each one actually ran."),
        (gates_2,
         "Three uploads sharing one build number",
         "Three uploads, one build number."),
    ],
    "mvvm-to-viper-part-one": [
        (mvvm1_1,
         "A view model absorbing navigation from the view",
         "The view model quietly takes the screen's ownership."),
        (mvvm1_2,
         "A screen, six use cases and one router: who owns navigation",
         "One screen, one owner: the router owns where you go next."),
    ],
    "mvvm-to-viper-part-two": [
        (mvvm2_1,
         "Splitting a feature into three targets and the package count going "
         "from three to forty-three",
         "Three targets per feature becomes forty-three packages."),
        (mvvm2_2,
         "The compile time bill for splitting every feature into three targets",
         "The bill for the split arrives at compile time."),
    ],
    "mvvm-to-viper-part-three": [
        (mvvm3_1,
         "Merging packages back down from forty-three to nineteen",
         "Forty-three packages down to nineteen."),
        (mvvm3_2,
         "The screen as the last unowned thing, and the router taking it",
         "The rename fixed nothing Clean had not. The screen was the last owner."),
    ],
    "exam-mode-one-screen-earlier": [
        (exam_mode_1,
         "The exam-mode lock moving from inside the paper to the step before it",
         "The lock did not get stronger. It moved one screen earlier."),
        (exam_mode_2,
         "The screen a student sees when the lock cannot start",
         "The lock is not the hard part. The words are."),
    ],
}


def build_all():
    """Return {slug: [(Scene, alt, caption), ...]}, two figures per post."""
    return {slug: [(fn(), alt, cap) for fn, alt, cap in entries]
            for slug, entries in SPECS.items()}
