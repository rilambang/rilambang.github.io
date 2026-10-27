#!/usr/bin/env python3
"""A small Lottie scene builder for the blog figures.

Shapes only. Every word is HTML laid over the canvas, because a font baked into
a Lottie file is the fastest way to make it look cheap: it falls back, it blurs,
and it cannot be selected. The scene emits the shape JSON, the poster SVG for
no-JS, and the label layer with its own frame keys.

Deterministic by construction: no clocks, no randomness, sorted keys.
"""
import json

FPS = 30
W = 640

INK = "#f4f6fb"
MUTED = "#aab2c4"
LINE = "#2c3040"
SURFACE = "#161822"
TINT = "#1b2440"
ACCENT = "#8ab4ff"
OK = "#86e0a6"
DIM = "#7b8496"

# Motion tokens. One set for every figure; nothing here is per-scene taste.
# ease-out-expo is the signature curve: fast out, long settle, never linear.
EASE_OUT = (0.16, 1, 0.3, 1)
EASE_IN = (0.7, 0, 0.84, 0)
EASE_IN_OUT = (0.65, 0, 0.35, 1)
# stiffness 380 / damping 30 / mass 1: about 2% overshoot, a soft settle.
SPRING = (0.34, 1.02, 0.64, 1)
LINEAR = (0, 0, 1, 1)

T_FLIP = 0.08      # state flips
T_HOVER = 0.16     # hover / focus
T_DEFAULT = 0.24   # default transition
T_MOVE = 0.40      # expanding or moving between positions
T_BEAT = 0.64      # a narrative beat, used sparingly
T_ARROW = 0.55     # an arrow drawing itself: 400-700ms, soft at the head

# A cursor that acts. Slow enough to read, never linear: soft acceleration and
# a longer deceleration into the target, a beat to settle, then a press.
T_TRAVEL = 1.05
T_DWELL = 0.22
T_DOWN = 0.12
T_UP = 0.20
T_RIPPLE = 0.45
EASE_TRAVEL = (0.45, 0, 0.15, 1)
# 120ms is 3.6 frames at 30fps: land on 4, or the dip is a three-frame blink.
T_DOWN_F = max(round(T_DOWN * FPS), 1)
T_UP_F = max(round(T_UP * FPS), 1)


def _rgb(hex_color):
    h = hex_color.lstrip("#")
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def _rgba(hex_color, alpha=1.0):
    return _rgb(hex_color) + [alpha]


def _kfs_eased(keys, dim=1):
    """Like _kfs, but each key carries its own ease: (frame, value, ease)."""
    out = []
    for n, k in enumerate(keys):
        t, v = k[0], k[1]
        ease = k[2] if len(k) > 2 else EASE_OUT
        item = {"t": t, "s": v}
        if n < len(keys) - 1:
            item["e"] = keys[n + 1][1]
            item["o"] = {"x": [ease[0]] * dim, "y": [ease[1]] * dim}
            item["i"] = {"x": [ease[2]] * dim, "y": [ease[3]] * dim}
        out.append(item)
    return {"a": 1, "k": out}


def _kfs(keys, ease=EASE_OUT, dim=1):
    """keys: [(frame, value)] where value is a list of `dim` numbers."""
    out = []
    for n, (t, v) in enumerate(keys):
        k = {"t": t, "s": v}
        if n < len(keys) - 1:
            k["e"] = keys[n + 1][1]
            k["o"] = {"x": [ease[0]] * dim, "y": [ease[1]] * dim}
            k["i"] = {"x": [ease[2]] * dim, "y": [ease[3]] * dim}
        out.append(k)
    return {"a": 1, "k": out}


def _const(v):
    return {"a": 0, "k": v}


def _frames(t):
    return int(round(t * FPS))


def _key(keys, t, v):
    """Append a keyframe, or replace the value if one already sits on that frame.

    Two keys on the same frame make lottie-web interpolate across a zero-length
    segment, which shows up as a one-frame jump.
    """
    if keys and keys[-1][0] == t:
        keys[-1] = (t, v)
    else:
        keys.append((t, v))
        keys.sort(key=lambda k: k[0])


def _eased(ease, u):
    """Solve a CSS cubic-bezier for its y at progress u. Used to bake label paths."""
    x1, y1, x2, y2 = ease
    lo, hi = 0.0, 1.0
    for _ in range(24):
        s = (lo + hi) / 2
        x = 3 * (1 - s) ** 2 * s * x1 + 3 * (1 - s) * s * s * x2 + s ** 3
        if x < u:
            lo = s
        else:
            hi = s
    s = (lo + hi) / 2
    return 3 * (1 - s) ** 2 * s * y1 + 3 * (1 - s) * s * s * y2 + s ** 3


class Label:
    """A word on the canvas. HTML, not a Lottie text layer.

    It still carries frame keys: opacity for the ones that appear or leave, and a
    sampled position path for the one that travels with a shape.
    """

    def __init__(self, x, y, text, size, color, anchor, weight, opacity):
        self.x, self.y = x, y
        self.text, self.size, self.color = text, size, color
        self.anchor, self.weight = anchor, weight
        self.a_keys = [(0, opacity)]
        self.segs = []

    @property
    def final_alpha(self):
        return self.a_keys[-1][1]

    @property
    def first_alpha(self):
        return self.a_keys[0][1]

    def fade(self, t, to, d=T_HOVER, ease=EASE_OUT):
        t0 = _frames(t)
        t1 = max(_frames(t + d), t0 + 1)
        _key(self.a_keys, t0, self.a_keys[-1][1])
        _key(self.a_keys, t1, to)
        return self

    def move_to(self, t, x, y, d=T_MOVE, ease=EASE_OUT):
        t0 = _frames(t)
        t1 = max(_frames(t + d), t0 + 1)
        start = self.segs[-1][3] if self.segs else (self.x, self.y)
        self.segs.append((t0, t1, start, (x, y), ease))
        return self

    def path(self, frames):
        """The position at every frame, eased, so the HTML can follow exactly."""
        out = []
        for f in range(frames + 1):
            p = (self.x, self.y)
            for t0, t1, a, b, ease in self.segs:
                if f <= t0:
                    p = a if f < t0 else a
                    break
                if f < t1:
                    e = _eased(ease, (f - t0) / (t1 - t0))
                    p = (a[0] + (b[0] - a[0]) * e, a[1] + (b[1] - a[1]) * e)
                    break
                p = b
            out.append(p)
        return out

    def alpha(self, frames):
        out = []
        for f in range(frames + 1):
            v = self.a_keys[0][1]
            for n, (t, a) in enumerate(self.a_keys):
                if f < t:
                    break
                nxt = self.a_keys[n + 1] if n + 1 < len(self.a_keys) else None
                if nxt is None:
                    v = a
                    break
                e = _eased(EASE_IN_OUT, (f - t) / max(1, nxt[0] - t))
                v = a + (nxt[1] - a) * e
            out.append(v)
        return out


class Node:
    """One logical shape. May be several Lottie layers (a row is rect + bar)."""

    def __init__(self, scene, layers, origin, svg_items, opacity=100):
        self.scene = scene
        self.layers = layers
        self.origin = list(origin)
        self.base = [list(l["ks"]["p"]["k"]) for l in layers]
        self.pos = list(origin)
        self.pos_keys = [(_frames(0), list(origin))]
        self.opacity_keys = [(_frames(0), [opacity])]
        self.scale_keys = [(_frames(0), [100, 100, 100])]
        self.trim = [(l, l["_trim"]) for l in layers if l.get("_trim")]
        self.svg_items = svg_items
        self.final = {"pos": list(origin), "opacity": opacity, "scale": 100}
        # The layer is born at 100. Anything created hidden has to say so, or it
        # shows on frame 0 and the poster disagrees with the animation.
        self._apply_opacity()
        for layer in layers:
            layer.pop("_trim", None)
            scene.layers.append(layer)

    def _apply_pos(self):
        for layer, base in zip(self.layers, self.base):
            keys = []
            for k in self.pos_keys:
                t, p = k[0], k[1]
                ease = k[2] if len(k) > 2 else EASE_OUT
                keys.append((t, [base[0] + p[0] - self.origin[0],
                                 base[1] + p[1] - self.origin[1], 0], ease))
            layer["ks"]["p"] = _kfs_eased(keys, dim=3)
        self.final["pos"] = list(self.pos_keys[-1][1])

    def _apply_opacity(self):
        for layer in self.layers:
            # one key is a constant: lottie-web's svg renderer throws on an
            # animated opacity with no end value.
            layer["ks"]["o"] = (_const(self.opacity_keys[0][1][0])
                                if len(self.opacity_keys) == 1
                                else _kfs(self.opacity_keys, dim=1))
        self.final["opacity"] = self.opacity_keys[-1][1][0]

    def _apply_scale(self):
        for layer in self.layers:
            layer["ks"]["s"] = _kfs(self.scale_keys, dim=3)
        self.final["scale"] = self.scale_keys[-1][1][0]

    def move_to(self, t, x, y, d=T_MOVE, ease=EASE_OUT):
        t0 = _frames(t)
        t1 = max(_frames(t + d), t0 + 1)
        _key(self.pos_keys, t0, list(self.pos))
        self.pos = [x, y]
        _key(self.pos_keys, t1, list(self.pos))
        # tag the segment so the curve is the one the caller asked for
        self.pos_keys = [k if k[0] != t1 else (k[0], k[1], ease)
                         for k in self.pos_keys]
        self._apply_pos()
        return self

    def fade(self, t, to=100, d=T_HOVER, ease=EASE_OUT):
        t0 = _frames(t)
        t1 = max(_frames(t + d), t0 + 1)
        start = self.opacity_keys[-1][1][0]
        _key(self.opacity_keys, t0, [start])
        _key(self.opacity_keys, t1, [to])
        self._apply_opacity()
        return self

    def show(self, t, d=T_HOVER):
        return self.fade(t, 100, d)

    def hide(self, t, d=T_FLIP):
        return self.fade(t, 0, d, EASE_IN)

    def set_scale(self, s):
        self.scale_keys = [(_frames(0), [s, s, 100])]
        self._apply_scale()
        return self

    def scale_to(self, t, s, d=T_DEFAULT, ease=EASE_OUT, frames=None):
        t0 = _frames(t)
        t1 = t0 + frames if frames else max(_frames(t + d), t0 + 1)
        start = self.scale_keys[-1][1][0]
        _key(self.scale_keys, t0, [start, start, 100])
        _key(self.scale_keys, t1, [s, s, 100])
        self._apply_scale()
        return self

    def settle(self, t, d=T_DEFAULT):
        """A soft landing: 2% up, spring back. No cartoon bounce."""
        self.scale_to(t, 102, T_FLIP)
        self.scale_to(t + T_FLIP, 100, d, SPRING)
        return self

    def pop(self, t, d=T_DEFAULT):
        """Appear from nothing and settle, no cartoon bounce.

        Both keys are written here rather than through scale_to: two calls on the
        same frame collapse into one, which silently turns the pop into a slow
        grow from frame 0.
        """
        t0 = _frames(t)
        t1 = max(_frames(t + d), t0 + 1)
        _key(self.scale_keys, t0, [0, 0, 100])
        _key(self.scale_keys, t1, [100, 100, 100])
        for layer in self.layers:
            layer["ks"]["s"] = _kfs(self.scale_keys, SPRING, dim=3)
        self.final["scale"] = 100
        return self

    def draw_on(self, t, d=T_DEFAULT):
        for _layer_, prop in self.trim:
            prop["e"] = _kfs([(_frames(t), [0]), (_frames(t + d), [100])])
        return self


def _layer(scene, name, shapes, x, y, ty=4):
    scene.ind += 1
    return {
        "ddd": 0, "ind": scene.ind, "ty": ty, "nm": name, "sr": 1,
        "ks": {
            "o": _const(100), "r": _const(0),
            "p": _const([x, y, 0]), "a": _const([0, 0, 0]), "s": _const([100, 100, 100]),
        },
        "ao": 0, "shapes": shapes, "ip": 0, "op": scene.frames, "st": 0, "bm": 0,
    }


def _tr():
    """Every shape group must end with a transform item.

    Lottie's expressions plugin walks the group looking for it; without one the
    SVG renderer throws inside initExpressions and the layer never gets appended.
    """
    return {"ty": "tr", "p": _const([0, 0]), "a": _const([0, 0]),
            "s": _const([100, 100]), "r": _const(0), "o": _const(100),
            "sk": _const(0), "sa": _const(0)}


def _rect_shapes(w, h, fill, stroke=None, radius=0, sw=1.2):
    items = [{"ty": "rc", "d": 1, "s": _const([w, h]), "p": _const([0, 0]),
              "r": _const(radius)}]
    if fill:
        items.append({"ty": "fl", "c": _const(_rgba(fill)), "o": _const(100), "r": 1, "bm": 0})
    if stroke:
        items.append({"ty": "st", "c": _const(_rgba(stroke)), "o": _const(100),
                      "w": _const(sw), "lc": 1, "lj": 1, "ml": 4, "bm": 0})
    items.append(_tr())
    return [{"ty": "gr", "it": items}]


def _path_shapes(pts, fill, stroke, sw):
    shape = {"ty": "sh", "ks": _const({
        "i": [[0, 0]] * len(pts), "o": [[0, 0]] * len(pts),
        "v": [list(p) for p in pts], "c": bool(fill)})}
    items = [shape]
    if fill:
        items.append({"ty": "fl", "c": _const(_rgba(fill)), "o": _const(100), "r": 1, "bm": 0})
    if stroke:
        items.append({"ty": "st", "c": _const(_rgba(stroke)), "o": _const(100),
                      "w": _const(sw), "lc": 2, "lj": 2, "ml": 4, "bm": 0})
    items.append(_tr())
    return [{"ty": "gr", "it": items}]


class Scene:
    def __init__(self, name, h, dur, poster_note="", w=W):
        self.name = name
        self.w = w
        self.h = h
        self.dur = dur
        self.frames = _frames(dur)
        self.layers = []
        self.nodes = []
        self.labels = []
        self.ind = 0
        self.poster_note = poster_note

    def rect(self, x, y, w, h, fill=SURFACE, stroke=LINE, radius=10, opacity=100):
        layer = _layer(self, "rect", _rect_shapes(w, h, fill, stroke, radius),
                       x + w / 2, y + h / 2)
        items = [{"kind": "rect", "x": x + w / 2, "y": y + h / 2, "w": w, "h": h,
                  "r": radius, "fill": fill, "stroke": stroke, "sw": 1.2}]
        node = Node(self, [layer], (x + w / 2, y + h / 2), items, opacity)
        self.nodes.append(node)
        return node

    def text(self, x, y, text, size=13, color=INK, anchor="start", weight=400,
             opacity=100):
        label = Label(x, y, text, size, color, anchor, weight, opacity)
        self.labels.append(label)
        return label

    def line(self, x1, y1, x2, y2, color=LINE, width=1.5, trim=True):
        dx, dy = x2 - x1, y2 - y1
        shape = {"ty": "sh", "ks": _const({
            "i": [[0, 0], [0, 0]], "o": [[0, 0], [0, 0]],
            "v": [[0, 0], [dx, dy]], "c": False})}
        stroke = {"ty": "st", "c": _const(_rgba(color)), "o": _const(100),
                  "w": _const(width), "lc": 2, "lj": 1, "ml": 4, "bm": 0}
        group = {"ty": "gr", "it": [shape, stroke]}
        item = None
        if trim:
            item = {"ty": "tm", "s": _const(0), "e": _const(100), "o": _const(0), "m": 1}
            group["it"].append(item)
        group["it"].append(_tr())
        layer = _layer(self, "line", [group], x1, y1)
        if trim:
            layer["_trim"] = item
        items = [{"kind": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                  "color": color, "w": width}]
        node = Node(self, [layer], (x1, y1), items)
        self.nodes.append(node)
        return node

    def poly(self, cx, cy, pts, fill=None, stroke=None, width=1.4):
        layer = _layer(self, "poly", _path_shapes(pts, fill, stroke, width), cx, cy)
        items = [{"kind": "poly", "x": cx, "y": cy,
                  "points": [(cx + p[0], cy + p[1]) for p in pts],
                  "fill": fill, "stroke": stroke, "w": width,
                  "closed": bool(fill)}]
        node = Node(self, [layer], (cx, cy), items)
        self.nodes.append(node)
        return node

    def ring(self, cx, cy, r=8, color=ACCENT, width=2, opacity=100):
        shape = {"ty": "el", "s": _const([r * 2, r * 2]), "p": _const([0, 0])}
        stroke = {"ty": "st", "c": _const(_rgba(color)), "o": _const(100),
                  "w": _const(width), "lc": 2, "lj": 2, "ml": 4, "bm": 0}
        layer = _layer(self, "ring", [{"ty": "gr", "it": [shape, stroke, _tr()]}], cx, cy)
        node = Node(self, [layer], (cx, cy),
                    [{"kind": "ring", "x": cx, "y": cy, "r": r, "stroke": color,
                      "w": width}], opacity)
        self.nodes.append(node)
        return node

    def pointer(self, x, y, opacity=100):
        """A mouse pointer, tip at (x, y)."""
        pts = [(0, 0), (0, 17), (4.1, 13.2), (6.9, 19.4), (9.3, 18.3),
               (6.5, 12.2), (11.6, 12.2)]
        node = self.poly(x, y, pts, fill=INK, stroke="#0b0d13", width=1.4)
        node.opacity_keys = [(_frames(0), [opacity])]
        node._apply_opacity()
        return node

    def tick(self, cx, cy, s=10, color=OK, width=2.4):
        return self.poly(cx, cy, [(-s, 0), (-s / 3, s * 0.6), (s, -s * 0.7)],
                         stroke=color, width=width)

    def arrow(self, x1, y1, x2, y2, color=LINE, width=1.5):
        line = self.line(x1, y1, x2, y2, color, width)
        h = 6.5
        if x1 == x2:
            d = -1 if y2 < y1 else 1
            pts = [(x2, y2), (x2 - h, y2 - d * h * 1.6), (x2 + h, y2 - d * h * 1.6)]
        else:
            d = -1 if x2 < x1 else 1
            pts = [(x2, y2), (x2 - d * h * 1.6, y2 - h), (x2 - d * h * 1.6, y2 + h)]
        head = self.poly(x2, y2, [(p[0] - x2, p[1] - y2) for p in pts], fill=color)
        line.head = head
        line.svg_items.append({"kind": "poly", "x": x2, "y": y2, "points": pts,
                               "fill": color, "stroke": None, "w": 0, "closed": True})
        return line

    def row(self, x, y, w, h, label, sub="", accent=False, size=12.5):
        node = self.rect(x, y, w, h, TINT if accent else SURFACE,
                         ACCENT if accent else LINE, 8)
        self.text(x + 14, y + h / 2 + size * 0.36, label, size,
                  ACCENT if accent else INK)
        if sub:
            self.text(x + w - 14, y + h / 2 + 4.5, sub, 11.5, MUTED, "end")
        return node

    # ── helpers ────────────────────────────────────────────────────────────
    def travel(self, cursor, t, x, y):
        """Move the pointer to a target. Returns the frame it settles on."""
        cursor.move_to(t, x, y, T_TRAVEL, EASE_TRAVEL)
        return t + T_TRAVEL

    def press(self, cursor, ring, t):
        """Settle, dip, spring, ripple. Returns when the state should flip.

        The dip is counted in frames, not seconds: rounding a start and an end
        time separately gives a 3-frame dip on some scenes and 4 on others.
        """
        t_down = t + T_DWELL
        f0 = _frames(t_down)
        cursor.scale_to(t_down, 86, T_DOWN, EASE_IN, frames=T_DOWN_F)
        cursor.scale_to((f0 + T_DOWN_F) / FPS, 100, T_UP, SPRING,
                        frames=T_UP_F)
        self.ripple(ring, t_down, 2.2, T_RIPPLE)
        return (f0 + T_DOWN_F) / FPS

    def cursor(self, x, y, t=0.0, opacity=100):
        """A pointer that fades in where it stands, ready to travel."""
        node = self.pointer(x, y, opacity=0)
        node.fade(t, opacity, T_HOVER)
        return node

    def ripple(self, node, t, scale_to=2.4, d=T_HOVER):
        """A press ring: out of the touch point and gone before the state flips.

        scale_to is a multiple of the ring's drawn radius, so 2.2 means 220%.
        Kept dim and short on purpose: it confirms the press, it is not the show.
        """
        node.scale_keys = [(_frames(0), [25, 25, 100])]
        node.opacity_keys = [(_frames(0), [0])]
        node.scale_to(t, scale_to * 100, d)
        node.fade(t, 70, 0.02)
        node.fade(t + d * 0.35, 0, d * 0.65, EASE_IN)
        return node

    def draw_on(self, node, t, d=T_DEFAULT):
        node.opacity_keys = [(_frames(0), [0])]
        node.show(t, 0.01)
        node.draw_on(t, d)
        if hasattr(node, "head"):
            node.head.opacity_keys = [(_frames(0), [0])]
            node.head.show(t + d * 0.7, T_FLIP)
        return node

    # ── output ─────────────────────────────────────────────────────────────
    def json(self):
        return {
            "v": "5.13.0", "fr": FPS, "ip": 0, "op": self.frames,
            "w": self.w, "h": self.h, "nm": self.name, "ddd": 0,
            "assets": [], "layers": list(reversed(self.layers)), "markers": [],
        }

    def dumps(self):
        return json.dumps(self.json(), sort_keys=True, separators=(",", ":"))

    def poster(self):
        out = [f"<svg viewBox='0 0 {self.w} {self.h}' width='{self.w}' "
               f"height='{self.h}' class='poster' aria-hidden='true' "
               f"xmlns='http://www.w3.org/2000/svg'>"]
        for node in self.nodes:
            if node.final["opacity"] <= 0:
                continue
            sx = sy = node.final["scale"] / 100
            px, py = node.final["pos"]
            op = node.final["opacity"] / 100
            dx, dy = px - node.origin[0], py - node.origin[1]
            for it in node.svg_items:
                out.append(_svg_item(it, dx, dy, sx, sy, op))
        out.append("</svg>")
        return "".join(out)

    def labels_html(self):
        out = ["<div class='fig-labels' aria-hidden='true'>"]
        for i, lab in enumerate(self.labels):
            alpha = lab.alpha(self.frames)
            pos = lab.path(self.frames)
            # The markup carries the end state, so the no-JS poster is right.
            # Offsets are measured from that end point, so frame 0 lands where
            # the label actually starts.
            fx, fy = pos[-1]
            style = (f"left:{fx / self.w * 100:.3f}%;"
                     f"top:{fy / self.h * 100:.3f}%;"
                     f"font-size:{lab.size / self.w * 100:.4f}cqw;"
                     f"color:{lab.color};"
                     f"--a1:{alpha[-1] / 100:.2f}")
            if lab.anchor == "middle":
                style += ";transform:translate(-50%,calc(-100% + .24em))"
            elif lab.anchor == "end":
                style += ";transform:translate(-100%,calc(-100% + .24em))"
            else:
                style += ";transform:translate(0,calc(-100% + .24em))"
            attrs = f" class='fig-label' data-i='{i}' style='{style}'"
            if any(a != alpha[0] for a in alpha):
                keys = " ".join(f"{f}:{round(a)}" for f, a in enumerate(alpha))
                attrs += f" data-alpha='{keys}'"
            if lab.segs:
                path = " ".join(f"{p[0] - fx:.1f} {p[1] - fy:.1f}" for p in pos)
                attrs += f" data-path='{path}'"
            out.append(f"<span{attrs}>{_esc(lab.text)}</span>")
        out.append("</div>")
        return "".join(out)


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace("'", "&#x27;"))


def _svg_item(it, dx, dy, sx, sy, op):
    a = f" opacity='{op:.2f}'" if op < 1 else ""
    k = it["kind"]
    if k == "rect":
        x = it["x"] + dx - it["w"] * sx / 2
        y = it["y"] + dy - it["h"] * sy / 2
        stroke = (f" stroke='{it['stroke']}' stroke-width='{it['sw']}'"
                  if it.get("stroke") else "")
        return (f"<rect x='{x:.1f}' y='{y:.1f}' width='{it['w'] * sx:.1f}' "
                f"height='{it['h'] * sy:.1f}' rx='{it['r']}' "
                f"fill='{it['fill'] or 'none'}'{stroke}{a}/>")
    if k == "line":
        return (f"<line x1='{it['x1'] + dx:.1f}' y1='{it['y1'] + dy:.1f}' "
                f"x2='{it['x2'] + dx:.1f}' y2='{it['y2'] + dy:.1f}' "
                f"stroke='{it['color']}' stroke-width='{it['w']}'{a}/>")
    if k == "dot":
        return (f"<circle cx='{it['x'] + dx:.1f}' cy='{it['y'] + dy:.1f}' "
                f"r='{it['r']}' fill='{it['fill']}'{a}/>")
    if k == "ring":
        return (f"<circle cx='{it['x'] + dx:.1f}' cy='{it['y'] + dy:.1f}' "
                f"r='{it['r'] * sx:.1f}' fill='none' stroke='{it['stroke']}' "
                f"stroke-width='{it['w']}'{a}/>")
    if k == "poly":
        pts = " ".join(f"{p[0] + dx:.1f},{p[1] + dy:.1f}" for p in it["points"])
        stroke = (f" stroke='{it['stroke']}' stroke-width='{it['w']}' stroke-linejoin='round'"
                  if it.get("stroke") else "")
        fill = it.get("fill") or "none"
        tag = "polygon" if it.get("closed") else "polyline"
        return f"<{tag} points='{pts}' fill='{fill}'{stroke}{a}/>"
    return ""
