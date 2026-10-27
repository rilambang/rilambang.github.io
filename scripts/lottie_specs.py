#!/usr/bin/env python3
"""The Lottie figures that are built so far, and nothing else.

One post so far: exam-mode-one-screen-earlier. The two UIKit-to-SwiftUI scenes
are not on this branch -- that post is back on its inline SVG until this one is
signed off.

Every scene is cut the same way: setup, one change, a held result. Shapes move;
the words are HTML laid over the canvas. Timing comes from the shared tokens in
lottie.py, never from a per-figure guess.
"""
from lottie import (Scene, ACCENT, INK, MUTED, LINE, SURFACE, TINT, OK, DIM,
                    T_FLIP, T_HOVER, T_DEFAULT, T_MOVE, EASE_IN)


# ── exam mode ────────────────────────────────────────────────────────────────
# Two rows of the same flow, on the same x grid, so an inserted step shows up as
# the boxes after it moving right. 126px boxes at 16px type: the names are the
# content here, not decoration, so they have to be readable at 640 wide.

BOX_W, BOX_H = 112, 108
SHIELD = [(0, -9), (7, -5), (7, 1), (0, 9), (-7, 1), (-7, -5)]


def _step(s, x, y, lines, lit=False):
    """One step box: a name, and a lit overlay that says the flow reached it."""
    box = s.rect(x, y, BOX_W, BOX_H, SURFACE, LINE, 10)
    glow = s.rect(x, y, BOX_W, BOX_H, TINT, ACCENT, 10, opacity=100 if lit else 0)
    cx = x + BOX_W / 2
    if len(lines) == 1:
        s.text(cx, y + 58, lines[0], 16, INK, "middle")
    else:
        s.text(cx, y + 42, lines[0], 16, INK, "middle")
        s.text(cx, y + 64, lines[1], 16, INK, "middle")
    return box, glow


def _shield(s, cx, cy):
    """A shield that goes from outline to filled, not from nothing to something."""
    outline = s.poly(cx, cy, SHIELD + [SHIELD[0]], stroke=DIM, width=1.8)
    fill = s.poly(cx, cy, SHIELD, fill=OK, width=0)
    fill.opacity_keys = [(0, [0])]
    fill._apply_opacity()
    return outline, fill


def exam_mode_1():
    """The lock moves from inside the paper to the step before it.

    Before: the paper opens, then the shield fills. Now: the shield fills, and
    only then does the flow reach Ready. Same cursor, same gesture, one screen
    earlier -- the difference is where the green lands, so it is read, not
    captioned.
    """
    s = Scene("exam-mode-one-screen-earlier-1", 340, 3.5,
              "The exam-mode lock moving from inside the paper to the step "
              "before it: the same cursor, one screen earlier")

    Y1, Y2 = 48, 200
    s.text(20, 32, "Before", 12, MUTED)
    s.text(20, 184, "Now", 12, MUTED)

    # Before: four steps, the lock sits at the last one.
    _step(s, 20, Y1, ["Welcome"], lit=True)
    _step(s, 142, Y1, ["Location"], lit=True)
    _step(s, 264, Y1, ["Ready"], lit=True)
    _paper, paper_lit = _step(s, 386, Y1, ["Paper"])
    paper_glow = s.rect(386, Y1, BOX_W, BOX_H, ACCENT, None, 10, opacity=0)
    _, paper_shield = _shield(s, 442, Y1 + 86)

    # Now: one extra step, and the lock sits at that step.
    _step(s, 20, Y2, ["Welcome"], lit=True)
    _step(s, 142, Y2, ["Location"], lit=True)
    _act, act_lit = _step(s, 264, Y2, ["Activate", "exam mode"])
    _ready, ready_lit = _step(s, 386, Y2, ["Ready"])
    _paper2, paper2_lit = _step(s, 508, Y2, ["Paper"])
    act_glow = s.rect(264, Y2, BOX_W, BOX_H, ACCENT, None, 10, opacity=0)
    _, act_shield = _shield(s, 320, Y2 + 86)

    cursor = s.pointer(600, 300, opacity=0)

    # Same gesture in both rows, aimed at the same place inside the box: the
    # lock. That is what makes the two presses comparable.
    cursor.fade(0.06, 100, T_HOVER)
    cursor.move_to(0.16, 442, Y1 + 86, T_MOVE)

    # the paper opens first, and the lock arms after it: 240ms late
    paper_glow.fade(0.60, 22, T_FLIP)
    paper_glow.fade(0.68, 0, T_HOVER, EASE_IN)
    paper_lit.show(0.66, T_FLIP)

    # The hand leaves before the lock fills, so the fill is not hidden under it.
    cursor.move_to(0.84, 320, Y2 + 86, T_MOVE)
    paper_shield.show(0.90, T_DEFAULT)

    act_glow.fade(1.30, 22, T_FLIP)
    act_glow.fade(1.38, 0, T_HOVER, EASE_IN)
    act_lit.show(1.36, T_FLIP)
    act_shield.show(1.42, T_DEFAULT)

    # the lock is live before the flow moves on, which is the whole point
    ready_lit.show(1.70, T_FLIP)
    paper2_lit.show(1.84, T_FLIP)

    cursor.move_to(1.98, 390, 306, T_DEFAULT)
    cursor.fade(2.10, 0, T_HOVER, EASE_IN)
    return s


SPECS = {
    "exam-mode-one-screen-earlier": [
        (exam_mode_1,
         "Two flows side by side. Before, the exam-mode lock arms inside the "
         "paper, after it has already opened. Now, the same lock arms at the "
         "new Activate exam mode step, before the flow reaches Ready and Paper.",
         "The lock did not get stronger. It moved one screen earlier, to the "
         "last moment before the questions appear."),
    ],
}


def build_all():
    """Return {slug: [(Scene, alt, caption), ...]}."""
    return {slug: [(fn(), alt, cap) for fn, alt, cap in entries]
            for slug, entries in SPECS.items()}
