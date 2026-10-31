#!/usr/bin/env python3
"""The blog's Lottie figures: two per post, one template, one bar.

Every figure is the same shape of story: a few real objects with their real
names, two or three arrows that draw themselves from one thing to another, a
state change at each arrowhead, and a held end state. The arrow is the beat:
what it leaves, where it lands, and what is different once it gets there.
Shapes move; the words are HTML laid over the canvas, because a font baked
into a Lottie file is the fastest way to make it look cheap.

Timing comes from the tokens in lottie.py -- arrow, flip, default -- never
from a per-figure guess. Nothing here is linear.
"""
import math

from lottie import (Scene, ACCENT, INK, MUTED, LINE, SURFACE, TINT, OK, DIM,
                    T_FLIP, T_HOVER, T_DEFAULT, T_MOVE, T_BEAT, T_ARROW,
                    EASE_IN, EASE_IN_OUT)

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


def _flow(s, x1, y1, x2, y2, t, d=T_ARROW, gap=0, color=DIM, width=1.5,
          label=None, size=12):
    """An arrow that draws itself; the head lands when the line gets there.

    The line is trim-drawn from tail to tip, the head is filled geometry
    oriented along the path, and it only appears on arrival. Whatever the head
    points at changes state at the returned time, never before. A gap breaks
    the line behind a short label.
    """
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    # the stroke stops under the head, so the tip is one piece of ink
    tipx, tipy = round(x2 - ux * 5, 2), round(y2 - uy * 5, 2)
    if gap:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        segs = [(x1, y1, mx - ux * gap / 2, my - uy * gap / 2),
                (mx + ux * gap / 2, my + uy * gap / 2, tipx, tipy)]
    else:
        segs = [(x1, y1, tipx, tipy)]
    segs = [tuple(round(v, 2) for v in seg) for seg in segs]
    total = sum(math.hypot(bx - ax, by - ay) for ax, ay, bx, by in segs)
    at = t
    for ax, ay, bx, by in segs:
        dd = max(d * math.hypot(bx - ax, by - ay) / total, 1 / 30)
        s.line(ax, ay, bx, by, color, width).draw_on(at, dd)
        at += dd
    head = s.poly(x2, y2, [(0, 0),
                           (round(-ux * 9 - uy * 4.6, 2),
                            round(-uy * 9 + ux * 4.6, 2)),
                           (round(-ux * 9 + uy * 4.6, 2),
                            round(-uy * 9 - ux * 4.6, 2))],
                  fill=color)
    head.opacity_keys = [(0, [0])]
    head._apply_opacity()
    head.show(t + d - 0.04, T_FLIP)
    if label:
        lab = s.text((x1 + x2) / 2, (y1 + y2) / 2 + 4, label, size, MUTED,
                     "middle", opacity=0)
        lab.fade(t + d * 0.4, 100, T_HOVER)
    return t + d


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


def _verdict(s, x, y, w, t, h=44, start=170, end=64, label=None, mark=None,
             fill="#2a1a22"):
    """An arrow inside a row: the name points at its own verdict.

    The rows are the claim; the arrow is the distance between what a gate says
    and what it actually ran. The head lands on the status, so the status is
    what changes. The mark is made first: it is the row's fill, and an arrow
    under it is an arrow nobody sees.
    """
    gap = len(label) * 7 if label else 0
    if mark:
        _mark(s, x, y, w, h, t + T_ARROW, color=mark, fill=fill)
    return _flow(s, x + start, y + h / 2, x + w - end, y + h / 2, t, gap=gap,
                 label=label)


def _row_scene(name, h, note, y, labels, links=(), dur=3.9, lit=None, gap=75):
    """Boxes in a line, arrows between them: the flow is the claim."""
    s = Scene(name, h, dur, note)
    w = (600 - (len(labels) - 1) * gap) / len(labels)
    xs = [PAD + i * (w + gap) for i in range(len(labels))]
    boxes, glows = [], []
    for i, lab in enumerate(labels):
        b, g = _step(s, xs[i], y, lab, lit=(i == lit), w=w)
        boxes.append(b)
        glows.append(g)
    t = 0.20
    for a, b in links:
        t = _flow(s, xs[a] + w + 5, y + BOX_H / 2, xs[b] - 5, y + BOX_H / 2, t)
        glows[b].fade(t, 100, T_DEFAULT)
        t += 0.62
    return s, boxes, glows, xs, w


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
    """A session starts and the four things iOS will hold go locked.

    The session is one source on the left; four arrows leave it and each one
    lands on a hold, which flips from open to locked at the head.
    """
    s = Scene("kiosk-and-assessment-apps-1", 320, 4.0,
              "Starting an assessment session: the app switcher, Home, "
              "notifications and other apps all going locked")
    s.text(PAD, 20, "Assessment session", 12, MUTED)
    rows = ["App switcher", "Home button", "Notifications", "Other apps"]
    x, w = 320, 280
    ys = [44 + i * 48 for i in range(4)]
    for lab, y in zip(rows, ys):
        _row(s, x, y, w, lab, "", MUTED, h=40, size=14)

    s.rect(40, 118, 216, 56, TINT, ACCENT, 8)
    btn = s.text(56, 152, "Start session", 15, ACCENT)
    live = s.text(56, 152, "Session running", 15, OK, opacity=0)

    t = 0.20
    for y in ys:
        t = _flow(s, 260, 146, x - 6, y + 20, t)
        _st(s, x + w - 16, y + 25, "open", "locked", t)
        _mark(s, x, y, w, 40, t, color=OK, fill="#12241c")
        t += 0.16
    btn.fade(t - 0.16, 0, T_FLIP, EASE_IN)
    live.fade(t - 0.16, 100, T_FLIP)
    return s


def kiosk_2():
    """The entitlement is the first thing to ask for, and it takes a request."""
    s, boxes, glows, xs, w = _row_scene(
        "kiosk-and-assessment-apps-2", 240,
        "The assessment entitlement: request, review, session", 66,
        ["Entitlement", "Apple review", "Session"],
        links=[(0, 1), (1, 2)], lit=0)
    return s


# ── 2. splitting an app into local packages ─────────────────────────────────
def packages_1():
    """A file moves in a day; the boundary it crosses is the work.

    Two arrows are the architecture -- App into Feature, Feature into Core --
    and one is the file itself, leaving the app target and landing under the
    package it now belongs to.
    """
    s = Scene("splitting-an-app-into-local-packages-1", 300, 3.8,
              "Moving one file out of the app target and into a local package")
    w, gap = 160, 60
    xs = [PAD + i * (w + gap) for i in range(3)]
    for i, lab in enumerate(["App", "Feature", "Core"]):
        _step(s, xs[i], 48, [lab], w=w)
    feature_lit = s.rect(xs[1], 48, w, BOX_H, TINT, ACCENT, 10, opacity=0)

    card = s.rect(xs[0] + 16, 176, w - 32, 44, TINT, ACCENT, 8)
    label = s.text(xs[0] + w / 2, 204, "FeedView.swift", 13, ACCENT, "middle")

    t1 = _flow(s, xs[0] + w + 5, 102, xs[1] - 5, 102, 0.20)
    feature_lit.fade(t1, 100, T_DEFAULT)
    t2 = _flow(s, xs[0] + w - 16, 198, xs[1] + w / 2, 168, t1 + 0.55,
               gap=48, label="moves")
    card.move_to(t2 + 0.02, xs[1] + w / 2, 198, 0.55, EASE_IN_OUT)
    label.move_to(t2 + 0.02, xs[1] + w / 2, 204, 0.55, EASE_IN_OUT)
    t3 = _flow(s, xs[1] + w + 5, 102, xs[2] - 5, 102, t2 + 0.55)
    s.rect(xs[2], 48, w, BOX_H, TINT, ACCENT, 10, opacity=0).fade(
        t3, 100, T_DEFAULT)
    s.text(PAD, 272, "One file. One import boundary.", 12, MUTED)
    return s


def packages_2():
    """What breaks first is the boundary, not the build.

    Four arrows run from each thing that breaks to the day it breaks on, and
    each row goes red when its own head arrives.
    """
    s = Scene("splitting-an-app-into-local-packages-2", 320, 4.2,
              "The order a local-package split breaks in: import cycle, public "
              "API, test target, previews")
    s.text(PAD, 20, "What breaks, in order", 12, MUTED)
    items = ["Import cycle", "Public API", "Test target", "Previews"]
    ys = [44 + i * 52 for i in range(4)]
    for lab, y in zip(items, ys):
        _row(s, 40, y, 560, lab, "", h=44)
    t = 0.20
    for i, y in enumerate(ys):
        t = _verdict(s, 40, y, 560, t, h=44, start=180, mark="#ff9d9d")
        _st(s, 584, y + 27, "", "day %d" % (1 + i * 3), t, color="#ff9d9d")
        t += 0.14
    return s


# ── 3. build time is a dependency-graph problem ─────────────────────────────
def buildgraph_1():
    """Twelve edges become four when the script phase goes.

    One arrow leaves the phase and lands in the tangle it owns; the other
    carries what is left into the count. The bowed edges go when the first
    head arrives, not before.
    """
    s = Scene("build-time-is-a-dependency-graph-problem-1", 320, 3.9,
              "Deleting one script phase removes most of the edges in the "
              "build graph")
    s.text(PAD, 20, "Build graph", 12, MUTED)
    s.rect(40, 110, 130, 100, SURFACE, LINE, 12)
    s.text(105, 166, "App", 16, INK, "middle")

    s.rect(180, 36, 130, 44, SURFACE, LINE, 8)
    run = s.text(196, 62, "Run Script", 12.5, INK)
    gone = s.text(196, 62, "removed", 12.5, OK, opacity=0)

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

    count = s.rect(40, 246, 116, 40, SURFACE, LINE, 8)
    twelve = s.text(56, 271, "12 edges", 12.5, MUTED)
    four = s.text(56, 271, "4 edges", 12.5, OK, opacity=0)

    t1 = _flow(s, 180, 82, 140, 106, 0.20)
    for e in extra:
        e.fade(t1 + 0.04, 0, T_DEFAULT, EASE_IN)
    run.fade(t1, 0, T_FLIP, EASE_IN)
    gone.fade(t1, 100, T_FLIP)
    twelve.fade(t1, 0, T_FLIP, EASE_IN)
    four.fade(t1, 100, T_FLIP)

    _flow(s, 300, 230, 162, 266, t1 + 0.55, gap=54, label="left")
    return s


def buildgraph_2():
    """Hardware buys a constant; the graph is the exponent.

    Three builds stacked. The first arrow carries the faster machine down to
    its time; the second carries the same build into the phase deletion, and
    that is where the number falls.
    """
    s = Scene("build-time-is-a-dependency-graph-problem-2", 300, 3.8,
              "A clean build on faster hardware against the same build after "
              "deleting a script phase")
    s.text(PAD, 20, "Clean build", 12, MUTED)
    _row(s, 40, 40, 560, "MacBook Pro", "4:10", h=44)
    _row(s, 40, 124, 560, "Mac Studio", "", h=44)
    _row(s, 40, 208, 560, "MacBook Pro, one phase deleted", "", h=44,
         tint=TINT, stroke=ACCENT)

    t1 = _flow(s, 320, 86, 320, 120, 0.20)
    _st(s, 584, 151, "", "3:55", t1)
    t2 = _flow(s, 320, 170, 320, 204, t1 + 0.55, gap=0)
    _st(s, 584, 235, "", "2:05", t2, color=OK)
    _mark(s, 40, 208, 560, 44, t2, color=OK, fill="#12241c")
    s.text(PAD, 276, "Faster hardware is a constant. The graph is the exponent.",
           12, MUTED)
    return s


# ── 4. UIKit to SwiftUI without a rewrite ───────────────────────────────────
def uikit_1():
    """Navigation changes owner; the content does not move.

    Two phones, before and after. One arrow lands on the nav bar and the word
    flips when the head gets there; one lands on the rows, and the bracket
    under both says they did not move.
    """
    s = Scene("uikit-to-swiftui-without-a-rewrite-1", 340, 3.8,
              "One screen converted: the navigation chrome changes owner and "
              "the same four rows stay put")
    s.text(PAD + 4, 26, "Before", 12, MUTED)
    s.text(404, 26, "After", 12, MUTED)

    for x in (24, 400):
        s.rect(x, 36, 216, 248, SURFACE, LINE, 18)
        s.rect(x, 36, 216, 52, TINT, LINE, 18)
        s.text(x + 16, 68, "Exam", 15, INK)
        for i, lab in enumerate(["Welcome", "Location", "Ready", "Paper"]):
            s.text(x + 16, 124 + i * 44, lab, 14, INK)
            if i < 3:
                s.line(x + 12, 140 + i * 44, x + 204, 140 + i * 44, LINE, 1)
    s.text(224, 68, "UIKit", 11, MUTED, "end")

    owner = s.rect(400, 36, 216, 52, None, ACCENT, 18, opacity=0)

    t1 = _flow(s, 244, 62, 396, 62, 0.25, gap=74, label="new owner")
    _st(s, 600, 68, "UIKit", "SwiftUI", t1, size=11, color=ACCENT)
    owner.fade(t1, 100, T_DEFAULT)

    t2 = _flow(s, 244, 212, 396, 212, 0.95)
    bracket = s.poly(24, 300, [(0, 8), (0, 0), (592, 0), (592, 8)],
                     stroke=OK, width=1.5)
    bracket.opacity_keys = [(0, [0])]
    bracket._apply_opacity()
    bracket.fade(t2, 100, T_DEFAULT)
    s.text(320, 326, "same rows", 12, OK, "middle",
           opacity=0).fade(t2, 100, T_DEFAULT)
    return s


def uikit_2():
    """The file moves once, and lands once.

    One arrow crosses the boundary at the top -- the folder it now lives in --
    and one carries the file itself across the gap and into the empty slot.
    """
    s = Scene("uikit-to-swiftui-without-a-rewrite-2", 320, 3.8,
              "One file moving from the UIKit views folder into a SwiftUI "
              "folder, drawn once at rest")
    s.text(56, 66, "Views/", 12, MUTED)
    s.text(416, 66, "SwiftUI/", 12, MUTED)
    s.rect(40, 36, 200, 250, SURFACE, LINE, 14)
    s.rect(400, 36, 200, 250, SURFACE, LINE, 14)
    home = s.rect(400, 36, 200, 250, None, ACCENT, 14, opacity=0)

    card = s.rect(56, 96, 168, 64, TINT, ACCENT, 10)
    label = s.text(140, 136, "ExamScreen.swift", 14, ACCENT, "middle")

    t1 = _flow(s, 240, 64, 396, 64, 0.20, gap=78, label="the boundary")
    home.fade(t1, 100, T_DEFAULT)
    t2 = _flow(s, 224, 128, 396, 128, t1 + 0.55, gap=70, label="moves once")
    card.move_to(t2 + 0.02, 500, 128, 0.6, EASE_IN_OUT)
    label.move_to(t2 + 0.02, 500, 136, 0.6, EASE_IN_OUT)
    s.text(PAD, 306, "One file, one boundary, one instance.", 12, MUTED)
    return s


# ── 5. a design system is a review policy ───────────────────────────────────
def designsystem_1():
    """The review, not the import, is what holds the system.

    The override goes down to the review; the review comes back and refuses it.
    Two arrows, one round trip, and the verdict is the thing that changes.
    """
    s = Scene("a-design-system-is-a-review-policy-1", 320, 3.9,
              "A pull request with a local colour override, and review "
              "refusing it")
    s.text(PAD, 20, "Pull request 412", 12, MUTED)
    _row(s, 40, 44, 560, "Use the accent token", "ok", OK, h=44)
    _row(s, 40, 96, 560, "Local override #8ab4ff", "found", ACCENT, h=44)
    _row(s, 40, 184, 560, "Review", "", MUTED, h=44, tint=TINT,
         stroke=ACCENT)

    t1 = _flow(s, 320, 144, 320, 180, 0.20)
    _st(s, 584, 211, "approve", "blocked", t1, color="#ff9d9d")
    _mark(s, 40, 184, 560, 44, t1, color="#ff9d9d", fill="#2a1a22")

    t2 = _flow(s, 380, 180, 380, 144, t1 + 0.55)
    _mark(s, 40, 96, 560, 44, t2, color="#ff9d9d", fill="#2a1a22")
    s.text(PAD, 268, "The token package changed nothing. Review did.", 12, MUTED)
    return s


def designsystem_2():
    """Two ways to write the same colour; one of them is the system.

    The literal hands over to the token, and the token is what lands in the
    diff: two arrows down a column, each one changing the row it reaches.
    """
    s = Scene("a-design-system-is-a-review-policy-2", 300, 3.9,
              "Choosing the token instead of the literal, and the local "
              "override disappearing from the diff")
    s.text(PAD, 20, "Colour", 12, MUTED)
    _row(s, 40, 40, 560, "#8ab4ff", "literal", MUTED, h=44)
    _row(s, 40, 124, 560, "Color.accent", "", h=44)
    lit = s.rect(40, 124, 560, 44, TINT, ACCENT, 8, opacity=0)
    s.rect(40, 208, 560, 76, SURFACE, LINE, 12)
    s.text(60, 236, "Diff", 12, MUTED)
    minus = s.text(60, 260, "- #8ab4ff", 14, "#ff9d9d")
    plus = s.text(220, 260, "+ Color.accent", 14, OK, opacity=0)

    t1 = _flow(s, 320, 86, 320, 120, 0.20)
    lit.fade(t1, 100, T_DEFAULT)
    _st(s, 584, 151, "token", "token", t1, color=OK)

    t2 = _flow(s, 320, 170, 270, 242, t1 + 0.55)
    minus.fade(t2, 0, T_FLIP, EASE_IN)
    plus.fade(t2, 100, T_FLIP)
    return s


# ── 6. how I review iOS pull requests ───────────────────────────────────────
def review_1():
    """Risk comes first, style last, and the order is the review.

    Two arrows: one carries Risk up to the first slot, one carries Style down
    one. Both heads land on the row they reach.
    """
    s = Scene("how-i-review-ios-pull-requests-1", 300, 3.8,
              "A pull request review reordered so risk is read before style")
    s.text(PAD, 20, "Review order", 12, MUTED)
    rows = ["Style", "Behaviour", "Risk"]
    ys = [44, 96, 148]
    boxes = []
    for lab, y in zip(rows, ys):
        boxes.append((s.rect(40, y, 440, 44, SURFACE, LINE, 8),
                      s.text(56, y + 27, lab, 15, INK)))

    t1 = _flow(s, 490, 168, 490, 74, 0.20)
    _flow(s, 522, 70, 522, 170, 0.80)
    # risk to the top, style and behaviour one row down: absolute positions
    for (box, lab), y in zip([boxes[2], boxes[0], boxes[1]], [44, 96, 148]):
        box.move_to(t1 + 0.10, 240, y + 22, 0.7, EASE_IN_OUT)
        lab.move_to(t1 + 0.10, 56, y + 27, 0.7, EASE_IN_OUT)
    return s


def review_2():
    """The comment that names the failure mode is the review.

    Two arrows leave the two lines that matter and land on the comment, one
    for the question and one for what it costs.
    """
    s = Scene("how-i-review-ios-pull-requests-2", 300, 3.8,
              "A review comment attached to the line that carries the risk")
    s.rect(40, 40, 560, 200, SURFACE, LINE, 12)
    s.text(60, 74, "ExamSession.swift", 13, MUTED)
    for i, lab in enumerate(["+ func start() {", "+   session.start()",
                             "+   lock()"]):
        s.text(60, 112 + i * 32, lab, 14, INK)
    comment = s.rect(320, 104, 260, 76, TINT, ACCENT, 8, opacity=0)
    q1 = s.text(336, 132, "What if start() throws?", 13, ACCENT, opacity=0)
    q2 = s.text(336, 154, "The lock never runs.", 12, MUTED, opacity=0)

    t1 = _flow(s, 186, 112, 314, 130, 0.20)
    comment.fade(t1, 100, T_DEFAULT)
    q1.fade(t1 + 0.06, 100, T_DEFAULT)

    t2 = _flow(s, 156, 176, 314, 158, t1 + 0.55)
    q2.fade(t2, 100, T_DEFAULT)
    return s


# ── 7. the iOS stack I actually reach for ───────────────────────────────────
def stack_1():
    """A stack chosen for who debugs it at 3am.

    One arrow leaves the dependency nobody can debug and goes up through the
    stack it prices; the other lands on that row's verdict.
    """
    s = Scene("the-ios-stack-i-actually-reach-for-1", 320, 4.0,
              "A stack list where the choice is priced by whether the next "
              "engineer can debug it")
    s.text(PAD, 20, "The stack", 12, MUTED)
    ys = [44 + i * 52 for i in range(4)]
    for lab, y in zip(["SwiftUI", "SwiftData", "URLSession", "Swift Testing"],
                      ys):
        _row(s, 40, y, 440, lab, "keep", OK, h=44)
    _row(s, 40, 256, 440, "A dependency nobody can debug", "", MUTED, h=44,
         tint=TINT, stroke=ACCENT)

    t1 = _flow(s, 520, 74, 520, 250, 0.20, gap=77, label="debuggable?")
    t2 = _verdict(s, 40, 256, 440, t1 + 0.55, h=44, start=300, end=80,
                  mark="#ff9d9d")
    _swap(s, 464, 283, "drop", "removed", t2, color="#ff9d9d")
    return s


def stack_2():
    """Every dependency is a 3am page.

    Two arrows leave the two rows and land on the count: the three you have,
    then the fourth the wrapper adds.
    """
    s = Scene("the-ios-stack-i-actually-reach-for-2", 300, 3.9,
              "Adding one dependency and the number of things that can wake "
              "you at 3am going up")
    s.text(PAD, 20, "Dependencies", 12, MUTED)
    _row(s, 40, 48, 440, "SwiftUI, SwiftData, URLSession", "3", h=44)
    _row(s, 40, 100, 440, "Add a networking wrapper", "4", ACCENT, h=44,
         tint=TINT, stroke=ACCENT)

    s.text(496, 282, "3am pages", 12, MUTED)
    three = s.text(496, 240, "3", 40, INK)
    four = s.text(496, 240, "4", 40, "#ff9d9d", opacity=0)

    t1 = _flow(s, 470, 70, 500, 208, 0.20)
    t2 = _flow(s, 470, 122, 516, 208, t1 + 0.55)
    three.fade(t2, 0, T_FLIP, EASE_IN)
    four.fade(t2, 100, T_FLIP)
    _mark(s, 40, 100, 440, 44, t2, color="#ff9d9d", fill="#2a1a22")
    return s


# ── 8. AI-native development is a process ───────────────────────────────────
def ai_1():
    """The agent works from the brief, not from the whole repo."""
    s, boxes, glows, xs, w = _row_scene(
        "ai-native-development-process-1", 240,
        "Conventions, brief and evidence: what the agent is allowed to work "
        "from", 66, ["Conventions", "Brief", "Evidence"],
        links=[(0, 1), (1, 2)])
    return s


def ai_2():
    """The agent proposes; the human merges.

    The change runs the tests, and the tests reach the merge; the last head is
    where a person takes over.
    """
    s = Scene("ai-native-development-process-2", 300, 3.9,
              "An agent proposing a change and a human merging it")
    s.text(PAD, 20, "Proposed change", 12, MUTED)
    _row(s, 40, 44, 440, "Edit 3 files", "agent", MUTED, h=44)
    _row(s, 40, 96, 440, "Run the tests", "", OK, h=44)
    _row(s, 40, 172, 440, "Merge", "", h=44, tint=TINT, stroke=ACCENT)

    t1 = _flow(s, 500, 66, 482, 118, 0.20)
    _st(s, 464, 123, "", "green", t1, color=OK)
    t2 = _flow(s, 500, 118, 482, 190, t1 + 0.55)
    _st(s, 464, 199, "waiting", "human", t2)
    _mark(s, 40, 172, 440, 44, t2, color=ACCENT, fill=TINT)
    return s


# ── 9. what a green build does not prove ────────────────────────────────────
def green_1():
    """Five green ticks, three of which ran nothing.

    Three arrows run from the three checks that ran nothing to their own
    verdicts, and the verdict is what changes at each head.
    """
    s = Scene("what-a-green-build-does-not-prove-1", 320, 3.9,
              "Five green checks, three of which ran no tests")
    s.text(PAD, 20, "Checks", 12, MUTED)
    items = ["Lint", "Unit tests", "Snapshot tests", "UI tests", "Deploy"]
    ys = [44 + i * 46 for i in range(5)]
    for i, (lab, y) in enumerate(zip(items, ys)):
        _row(s, 40, y, 560, lab, "passed" if i in (0, 4) else "", OK, h=40)

    t = 0.20
    for y in ys[1:4]:
        t = _verdict(s, 40, y, 560, t, h=40, start=170, mark="#ff9d9d")
        _st(s, 584, y + 25, "passed", "0 tests", t, color="#ff9d9d")
        t += 0.14
    return s


def green_2():
    """A lock file that pinned a branch.

    The row resolves to what it is pinned to -- a branch -- and the second
    arrow carries the repair back up: the same lock, pinned to a version.
    """
    s = Scene("what-a-green-build-does-not-prove-2", 300, 3.9,
              "A resolved lock file pinned to a branch instead of a version")
    s.text(PAD, 20, "Package.resolved", 12, MUTED)
    _row(s, 40, 48, 560, "swift-argument-parser", "1.3.0", h=44)
    _row(s, 40, 100, 560, "networking", "", h=44)
    s.text(40, 176, "Pinned to", 12, MUTED)
    pin = s.text(40, 216, "main", 30, INK)
    version = s.text(40, 216, "1.3.0", 30, OK, opacity=0)
    branch = s.text(584, 127, "branch: main", 13, "#ff9d9d", "end", opacity=0)
    fixed = s.text(584, 127, "1.3.0", 13, OK, "end", opacity=0)

    t1 = _flow(s, 584, 124, 120, 204, 0.20)
    branch.fade(t1, 100, T_FLIP)

    t2 = t1 + 0.55 + T_ARROW
    _mark(s, 40, 100, 560, 44, t2, color=OK, fill="#12241c")
    _flow(s, 140, 200, 584, 128, t1 + 0.55, gap=62, label="a version")
    branch.fade(t2, 0, T_FLIP, EASE_IN)
    fixed.fade(t2, 100, T_FLIP)
    pin.fade(t2, 0, T_FLIP, EASE_IN)
    version.fade(t2, 100, T_FLIP)
    return s


# ── 10. four gates that certified nothing ───────────────────────────────────
def gates_1():
    """Four gates, all green, and what each one actually ran.

    One arrow per gate, from the gate to the number it actually ran, landing on
    the verdict it cannot survive.
    """
    s = Scene("four-gates-that-certified-nothing-1", 320, 4.2,
              "Four green gates revealing what each one actually ran")
    s.text(PAD, 20, "Release gates", 12, MUTED)
    items = ["Lint", "Pre-push tests", "Build number", "Snapshots"]
    ys = [44 + i * 52 for i in range(4)]
    for lab, y in zip(items, ys):
        _row(s, 40, y, 560, lab, "", h=44)

    ran = ["1 dir", "2 of 3", "1 of 3", "0 tests"]
    t = 0.20
    for i, y in enumerate(ys):
        t = _verdict(s, 40, y, 560, t, h=44, start=170, mark="#ff9d9d")
        _st(s, 584, y + 27, "green", ran[i], t, color="#ff9d9d")
        t += 0.14
    return s


def gates_2():
    """Three uploads, one build number.

    Three arrows land on the same number, one per upload, and the number goes
    red as each head arrives; the last one rewrites the line under them.
    """
    s = Scene("four-gates-that-certified-nothing-2", 300, 3.9,
              "Three uploads sharing one build number")
    s.text(PAD, 20, "Uploads", 12, MUTED)
    for y, lab in ((48, "TestFlight internal"), (100, "TestFlight external"),
                   (152, "App Store")):
        _row(s, 40, y, 440, lab, "", MUTED, h=44)
    head = s.text(40, 236, "Three uploads. One build.", 15, INK)

    # the same number, once, beside all three: the brace is what says "one"
    brace = s.poly(516, 48, [(8, 0), (0, 0), (0, 148), (8, 148)],
                   stroke=MUTED, width=1.5)
    brace.opacity_keys = [(0, [0])]
    brace._apply_opacity()
    stamp = s.text(528, 126, "build 42", 13, "#ff9d9d", opacity=0)

    t1 = _flow(s, 470, 122, 508, 122, 0.20)
    brace.fade(t1, 100, T_DEFAULT)
    stamp.fade(t1, 100, T_DEFAULT)
    for y in (48, 100, 152):
        _mark(s, 40, y, 440, 44, t1, color="#ff9d9d", fill="#2a1a22")
    t2 = _flow(s, 516, 200, 150, 220, t1 + 0.55)
    head.fade(t2, 0, T_FLIP, EASE_IN)
    s.text(40, 236, "Nobody can tell them apart.", 15, "#ff9d9d",
           opacity=0).fade(t2, 100, T_FLIP)
    return s


# ── 11. MVVM to VIPER, part one ─────────────────────────────────────────────
def mvvm1_1():
    """The view model quietly takes the screen's ownership.

    Two arrows leave the view and land on the view model: the navigation
    first, then the screen itself, which is the panel outline changing.
    """
    s = Scene("mvvm-to-viper-part-one-1", 320, 3.9,
              "A view model absorbing navigation from the view")
    s.rect(40, 44, 220, 240, SURFACE, LINE, 14)
    s.text(60, 78, "ExamView", 14, MUTED)
    for i, lab in enumerate(["score", "timer", "questions"]):
        s.text(60, 126 + i * 40, lab, 14, INK)
    s.rect(380, 44, 220, 240, SURFACE, LINE, 14)
    s.text(400, 78, "ExamViewModel", 14, MUTED)
    for i, lab in enumerate(["score", "timer", "questions"]):
        s.text(400, 126 + i * 40, lab, 14, INK)
    navigate = s.text(400, 254, "navigate(to:)", 14, "#ff9d9d", opacity=0)
    owner = s.rect(380, 44, 220, 240, None, ACCENT, 14, opacity=0)

    t1 = _flow(s, 264, 240, 376, 240, 0.20, gap=70, label="navigation")
    navigate.fade(t1, 100, T_DEFAULT)
    _mark(s, 380, 232, 220, 44, t1, color="#ff9d9d", fill="#2a1a22")

    t2 = _flow(s, 264, 268, 376, 268, t1 + 0.55, gap=64, label="ownership")
    owner.fade(t2, 100, T_DEFAULT)
    return s


def mvvm1_2():
    """One screen, one owner: the router owns where you go next."""
    s, boxes, glows, xs, w = _row_scene(
        "mvvm-to-viper-part-one-2", 240,
        "A screen, six use cases and one router: who owns navigation", 66,
        ["Screen", "6 use cases", "Router"], links=[(0, 1), (1, 2)], lit=0)
    return s


# ── 12. MVVM to VIPER, part two ─────────────────────────────────────────────
def mvvm2_1():
    """Three targets per feature becomes forty-three packages.

    The app target splits into three per feature, and that number is what
    turns into forty-three packages at the bottom.
    """
    s = Scene("mvvm-to-viper-part-two-1", 300, 3.9,
              "Splitting a feature into three targets and the package count "
              "going from three to forty-three")
    s.text(PAD, 20, "Packages", 12, MUTED)
    _row(s, 40, 40, 560, "One app target", "1", h=44)
    _row(s, 40, 122, 560, "Three targets per feature", "", ACCENT, h=44,
         tint=TINT, stroke=ACCENT)
    s.rect(40, 208, 130, 64, SURFACE, LINE, 10)
    three = s.text(105, 250, "3", 40, INK, "middle")
    forty = s.text(105, 250, "43", 40, "#ff9d9d", "middle", opacity=0)

    t1 = _flow(s, 320, 84, 320, 118, 0.20)
    _st(s, 584, 149, "", "3", t1, color="#ff9d9d")
    _mark(s, 40, 122, 560, 44, t1, color="#ff9d9d", fill="#2a1a22")

    t2 = _flow(s, 105, 166, 105, 204, t1 + 0.55)
    three.fade(t2, 0, T_FLIP, EASE_IN)
    forty.fade(t2, 100, T_FLIP)
    return s


def mvvm2_2():
    """The bill for the split arrives at compile time.

    Packages carry into targets, targets carry into the build, and the time is
    what changes when the last head lands.
    """
    s = Scene("mvvm-to-viper-part-two-2", 300, 3.9,
              "The compile time bill for splitting every feature into three "
              "targets")
    s.text(PAD, 20, "The bill", 12, MUTED)
    _row(s, 40, 36, 560, "Packages", "43", h=44)
    _row(s, 40, 122, 560, "Targets", "", h=44)
    _row(s, 40, 208, 560, "Clean build", "", h=44, tint=TINT, stroke=ACCENT)

    t1 = _flow(s, 320, 80, 320, 118, 0.20)
    _st(s, 584, 149, "", "129", t1)

    t2 = _flow(s, 320, 166, 320, 204, t1 + 0.55)
    _st(s, 584, 235, "4:40", "9:10", t2, color="#ff9d9d")
    _mark(s, 40, 208, 560, 44, t2, color="#ff9d9d", fill="#2a1a22")
    return s


# ── 13. MVVM to VIPER, part three ───────────────────────────────────────────
def mvvm3_1():
    """Forty-three packages down to nineteen, by merging what was never apart.

    The same chain in reverse: the split count feeds the merge, and the merge
    is what brings the number down.
    """
    s = Scene("mvvm-to-viper-part-three-1", 300, 3.9,
              "Merging packages back down from forty-three to nineteen")
    s.text(PAD, 20, "Packages", 12, MUTED)
    _row(s, 40, 40, 560, "After the split", "43", h=44)
    _row(s, 40, 122, 560, "Merge the router into the screen", "", OK, h=44,
         tint=TINT, stroke=ACCENT)
    s.rect(40, 208, 130, 64, SURFACE, LINE, 10)
    count = s.text(105, 250, "43", 40, INK, "middle")
    less = s.text(105, 250, "19", 40, OK, "middle", opacity=0)

    t1 = _flow(s, 320, 84, 320, 118, 0.20)
    _st(s, 584, 149, "", "19", t1, color=OK)
    _mark(s, 40, 122, 560, 44, t1, color=OK, fill="#12241c")

    t2 = _flow(s, 105, 166, 105, 204, t1 + 0.55)
    count.fade(t2, 0, T_FLIP, EASE_IN)
    less.fade(t2, 100, T_FLIP)
    return s


def mvvm3_2():
    """The rename fixed nothing Clean had not; the screen was the last owner."""
    s, boxes, glows, xs, w = _row_scene(
        "mvvm-to-viper-part-three-2", 240,
        "The screen as the last unowned thing, and the router taking it", 66,
        ["View", "Presenter", "Router"], links=[(0, 1), (1, 2)])
    return s


# ── 14. exam mode, one screen earlier ───────────────────────────────────────
def exam_mode_1():
    """The lock moves from inside the paper to the step before it.

    The before row is the premise, already true at rest: the paper opened and
    the lock was still arming. Two arrows leave that paper: one lands on
    Activate, where the lock lives now, and one lands on Paper, which now
    arrives after it. The head is the beat; the state changes when it gets
    there.
    """
    s = Scene("exam-mode-one-screen-earlier-1", 340, 3.9,
              "The exam-mode lock moving from inside the paper to the step "
              "before it: one screen earlier")

    Y1, Y2 = 48, 200
    s.text(PAD, 32, "Before", 12, MUTED)
    s.text(PAD, 184, "Now", 12, MUTED)

    _step(s, 20, Y1, ["Welcome"], lit=True)
    _step(s, 142, Y1, ["Location"], lit=True)
    _step(s, 264, Y1, ["Ready"], lit=True)
    _step(s, 386, Y1, ["Paper"], lit=True)
    s.rect(386, Y1, 112, BOX_H, None, OK, 10)
    _, paper_shield = _shield(s, 442, Y1 + 86, half=True)
    paper_shield.opacity_keys = [(0, [100])]
    paper_shield._apply_opacity()

    _step(s, 20, Y2, ["Welcome"], lit=True)
    _step(s, 142, Y2, ["Location"], lit=True)
    _, act_lit = _step(s, 264, Y2, ["Activate", "exam mode"])
    _, ready_lit = _step(s, 386, Y2, ["Ready"])
    _, paper2_lit = _step(s, 508, Y2, ["Paper"])
    lock2 = s.rect(264, Y2, 112, BOX_H, None, OK, 10, opacity=0)
    act_out, act_shield = _shield(s, 320, Y2 + 86)
    act_out.opacity_keys = [(0, [0])]
    act_out._apply_opacity()

    t1 = _flow(s, 442, Y1 + 110, 320, Y2 - 4, 0.20, gap=36, label="lock")
    act_lit.show(t1, T_FLIP)
    lock2.show(t1, T_FLIP)
    act_out.show(t1, T_DEFAULT)
    act_shield.show(t1, T_DEFAULT)
    ready_lit.show(t1 + 0.20, T_FLIP)

    t2 = _flow(s, 442, Y1 + 110, 564, Y2 - 4, 0.85, gap=38, label="after")
    paper2_lit.show(t2, T_FLIP)
    return s


def exam_mode_2():
    """The blocked screen: the lock is not the hard part, the words are.

    The sentence under the title forks to both ways out: one arrow lands on the
    retry, which becomes the live button, and one on the link to a person.
    """
    s = Scene("exam-mode-one-screen-earlier-2", 320, 3.9,
              "The screen a student sees when the lock cannot start: the "
              "words, and the way out")
    s.rect(40, 36, 560, 240, SURFACE, LINE, 14)
    s.text(60, 76, "Exam mode could not start", 18, INK)
    s.text(60, 112, "Your device is not ready for this assessment.", 14, MUTED)
    _, button = _row(s, 60, 176, 250, "Try again", "button", ACCENT, h=64,
                     size=14, tint=TINT, stroke=ACCENT)
    _, link = _row(s, 330, 176, 250, "Ask your teacher for help", "link",
                   MUTED, h=64, size=14)

    t1 = _flow(s, 400, 120, 200, 172, 0.20)
    button.fade(t1, 0, T_FLIP, EASE_IN)
    s.text(294, 213, "retry", 13, OK, "end", opacity=0).fade(t1, 100, T_FLIP)
    _mark(s, 60, 176, 250, 64, t1, color=OK, fill="#12241c")

    t2 = _flow(s, 400, 120, 450, 172, t1 + 0.70)
    link.fade(t2, 0, T_FLIP, EASE_IN)
    s.text(564, 213, "link", 13, OK, "end", opacity=0).fade(t2, 100, T_FLIP)
    s.text(60, 296, "No dead end, and no blame.", 12, MUTED)
    return s


# ── 15. a year of AI-native iOS ─────────────────────────────────────────────
def ai_audit_1():
    """One pointer, three tools, then the pointer starts copying the docs.

    Three arrows carry the tool filenames into AGENTS.md. The fourth leaves
    the file for the docs it points to, labelled with the size it grew to, and
    the status flips from pointer to second truth when the head lands.
    """
    s = Scene("what-a-year-of-ai-native-ios-still-cant-prove-1", 340, 4.0,
              "Three tool instruction files pointing at one AGENTS.md, and an "
              "18 KB copy leaking into the docs it points to")
    s.text(PAD, 28, "Tool files", 12, MUTED)
    for lab, y in (("CLAUDE.md", 44), ("GEMINI.md", 104),
                   ("copilot-instructions.md", 164)):
        _row(s, 20, y, 220, lab, "", h=44, size=13)
    s.rect(320, 44, 280, 104, SURFACE, LINE, 12)
    s.text(460, 82, "AGENTS.md", 18, INK, "middle")
    pointer = s.text(460, 118, "pointer", 12, MUTED, "middle")
    second = s.text(460, 118, "second truth", 12, "#ff9d9d", "middle",
                    opacity=0)

    t1 = _flow(s, 244, 66, 316, 76, 0.20)
    t2 = _flow(s, 244, 126, 316, 96, t1 + 0.12)
    t3 = _flow(s, 244, 186, 316, 116, t2 + 0.12)

    s.rect(320, 230, 280, 64, SURFACE, LINE, 12)
    s.text(460, 268, "the docs it points to", 13, MUTED, "middle")
    leak = s.rect(320, 230, 280, 64, None, "#ff9d9d", 12, opacity=0)
    t4 = _flow(s, 460, 152, 460, 226, t3 + 0.18, gap=44, label="18 KB")
    leak.fade(t4, 100, T_DEFAULT)
    pointer.fade(t4, 0, T_FLIP, EASE_IN)
    second.fade(t4, 100, T_FLIP)
    s.text(PAD, 326, "A pointer that restates becomes a second truth.", 12,
           MUTED)
    return s


def ai_audit_2():
    """Two rules become scripts; the third stays prose and drifts.

    Three rows, one arrow each. The head lands on the verdict: two flip green
    to enforced, the prose one flips red to drift.
    """
    s = Scene("what-a-year-of-ai-native-ios-still-cant-prove-2", 320, 3.9,
              "Three rules routed to their enforcement: two land in "
              "pre-commit, the prose one drifts")
    s.text(PAD, 24, "Where each rule lives", 12, MUTED)
    ys = [48, 112, 176]
    for lab, y in zip(["Secret scan", "SwiftLint", "Write the MR body"], ys):
        _row(s, 40, y, 560, lab, "", h=48, size=15)
    t = 0.20
    for i, y in enumerate(ys):
        color = OK if i < 2 else "#ff9d9d"
        fill = "#12241c" if i < 2 else "#2a1a22"
        t = _verdict(s, 40, y, 560, t, h=48, start=260, end=110, mark=color,
                     fill=fill)
        _st(s, 584, y + 30, "", "enforced" if i < 2 else "drift", t,
            color=color)
        t += 0.14
    s.text(PAD, 288,
           "Two rules run before the commit. One is still a sentence.", 12,
           MUTED)
    return s


def ai_audit_3():
    """Four roles in a line, with the last two limited where it matters.

    Three arrows carry the work down the chain. qa's edit and the fixer's push
    flip to denied when each head arrives.
    """
    s = Scene("what-a-year-of-ai-native-ios-still-cant-prove-3", 260, 3.9,
              "Architect, reviewer, qa and fixer in a chain, with qa denied "
              "edits and fixer denied push")
    s.text(PAD, 24, "Four roles, four limits", 12, MUTED)
    roles = [("architect", "plans"), ("reviewer", "reads"),
             ("qa", "edit: allowed"), ("fixer", "push: allowed")]
    w, gap, y = 112, 50, 56
    xs = [PAD + i * (w + gap) for i in range(4)]
    statuses = []
    for (name, status), x in zip(roles, xs):
        s.rect(x, y, w, 104, SURFACE, LINE, 10)
        s.text(x + w / 2, y + 40, name, 14, INK, "middle")
        statuses.append(s.text(x + w / 2, y + 70, status, 12, MUTED,
                               "middle"))
    qa_denied = s.text(xs[2] + w / 2, y + 70, "edit: denied", 12,
                       "#ff9d9d", "middle", opacity=0)
    fix_denied = s.text(xs[3] + w / 2, y + 70, "push: denied", 12,
                        "#ff9d9d", "middle", opacity=0)
    qa_out = s.rect(xs[2], y, w, 104, None, "#ff9d9d", 10, opacity=0)
    fix_out = s.rect(xs[3], y, w, 104, None, "#ff9d9d", 10, opacity=0)

    t1 = _flow(s, xs[0] + w + 5, y + 52, xs[1] - 5, y + 52, 0.20)
    t2 = _flow(s, xs[1] + w + 5, y + 52, xs[2] - 5, y + 52, t1 + 0.18)
    qa_out.fade(t2, 100, T_DEFAULT)
    statuses[2].fade(t2, 0, T_FLIP, EASE_IN)
    qa_denied.fade(t2, 100, T_FLIP)

    t3 = _flow(s, xs[2] + w + 5, y + 52, xs[3] - 5, y + 52, t2 + 0.18)
    fix_out.fade(t3, 100, T_DEFAULT)
    statuses[3].fade(t3, 0, T_FLIP, EASE_IN)
    fix_denied.fade(t3, 100, T_FLIP)
    s.text(PAD, 210,
           "A narrow role only holds if the capability limit does.", 12,
           MUTED)
    return s


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
    "what-a-year-of-ai-native-ios-still-cant-prove": [
        (ai_audit_1,
         "Three tool instruction files pointing at one AGENTS.md, and an "
         "18 KB copy leaking into the docs it points to",
         "One file every tool reads, until it starts restating the docs it "
         "points to."),
        (ai_audit_2,
         "Three rules routed to their enforcement: two land in pre-commit, "
         "the prose one drifts",
         "The rule that stayed prose is the one that drifted."),
        (ai_audit_3,
         "Architect, reviewer, qa and fixer in a chain, with qa denied edits "
         "and fixer denied push",
         "The roles are real because the limits are."),
    ],
}


def build_all():
    """Return {slug: [(Scene, alt, caption), ...]}, one or more figures per post."""
    return {slug: [(fn(), alt, cap) for fn, alt, cap in entries]
            for slug, entries in SPECS.items()}
