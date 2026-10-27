#!/usr/bin/env python3
"""A small Lottie scene builder for the blog figures.

The point is not to reimplement After Effects. It is to keep every figure as a
short, readable Python scene: primitives in, keyframes out. The same scene
renders the Lottie JSON and the inline SVG poster, so the no-JS fallback cannot
drift from the animation's final frame.

Deterministic by construction: no clocks, no randomness, sorted keys.
"""
import json
import math

FPS = 30
W = 640

INK = "#f4f6fb"
MUTED = "#aab2c4"
LINE = "#2c3040"
SURFACE = "#161822"
TINT = "#1b2440"
ACCENT = "#8ab4ff"
WARM = "#2a2438"


def _rgb(hex_color):
    h = hex_color.lstrip("#")
    return [round(int(h[i:i + 2], 16) / 255, 4) for i in (0, 2, 4)]


def _rgba(hex_color, alpha=1.0):
    return _rgb(hex_color) + [alpha]


def _ease(i=(0.42, 0), o=(0.58, 1)):
    return {"x": [i[0]], "y": [i[1]]}, {"x": [o[0]], "y": [o[1]]}


def _kfs(keys, ease=(0.42, 0, 0.58, 1), dim=1):
    """keys: [(frame, value)] where value is a list of `dim` numbers."""
    out = []
    for n, (t, v) in enumerate(keys):
        k = {"t": t, "s": v}
        if n < len(keys) - 1:
            k["e"] = keys[n + 1][1]
            k["i"] = {"x": [ease[0]] * dim, "y": [ease[1]] * dim}
            k["o"] = {"x": [ease[2]] * dim, "y": [ease[3]] * dim}
        out.append(k)
    return {"a": 1, "k": out}


def _const(v):
    return {"a": 0, "k": v}


def _frames(t):
    return int(round(t * FPS))


class Node:
    """One logical object; may be several Lottie layers (card = rect + text)."""

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
        for layer in layers:
            layer.pop("_trim", None)
            scene.layers.append(layer)

    def _apply_pos(self):
        for layer, base in zip(self.layers, self.base):
            keys = [(t, [base[0] + p[0] - self.origin[0],
                         base[1] + p[1] - self.origin[1], 0])
                    for t, p in self.pos_keys]
            layer["ks"]["p"] = _kfs(keys, dim=3)
        self.final["pos"] = list(self.pos_keys[-1][1])

    def _apply_opacity(self):
        for layer in self.layers:
            layer["ks"]["o"] = _kfs(self.opacity_keys, dim=1)
        self.final["opacity"] = self.opacity_keys[-1][1][0]

    def _apply_scale(self):
        for layer in self.layers:
            layer["ks"]["s"] = _kfs(self.scale_keys, dim=3)
        self.final["scale"] = self.scale_keys[-1][1][0]

    def move_to(self, t, x, y, d=0.45):
        t0 = _frames(t)
        t1 = _frames(t + d)
        self.pos_keys.append((t0, list(self.pos)))
        self.pos = [x, y]
        self.pos_keys.append((t1, list(self.pos)))
        self._apply_pos()
        return self

    def nudge(self, t, dx, dy, d=0.35, back=True, hold=1.0):
        self.move_to(t, self.pos[0] + dx, self.pos[1] + dy, d)
        if back:
            self.move_to(t + d + hold, self.pos[0] - dx, self.pos[1] - dy, d)
        return self

    def fade(self, t, to=100, d=0.4):
        t0 = _frames(t)
        t1 = _frames(t + d)
        start = self.opacity_keys[-1][1][0]
        self.opacity_keys.append((t0, [start]))
        self.opacity_keys.append((t1, [to]))
        self._apply_opacity()
        return self

    def show(self, t, d=0.4):
        return self.fade(t, 100, d)

    def hide(self, t, d=0.4):
        return self.fade(t, 0, d)

    def scale_to(self, t, s, d=0.35):
        t0 = _frames(t)
        t1 = _frames(t + d)
        start = self.scale_keys[-1][1][0]
        self.scale_keys.append((t0, [start, start, 100]))
        self.scale_keys.append((t1, [s, s, 100]))
        self._apply_scale()
        return self

    def pulse(self, t, d=0.5, amount=7):
        self.scale_to(t, 100 + amount, d / 2)
        self.scale_to(t + d / 2, 100, d / 2)
        return self

    def draw_on(self, t, d=0.7):
        for _layer_, prop in self.trim:
            prop["e"] = _kfs([(_frames(t), [0]), (_frames(t + d), [100])])
        self.opacity_keys.append((_frames(t), [100]))
        self._apply_opacity()
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


def _text_layer(scene, text, x, y, size, color, anchor, weight):
    scene.ind += 1
    justify = {"start": 0, "middle": 2, "end": 1}[anchor]
    doc = {
        "s": size, "f": "Inter", "t": text, "j": justify, "tr": 0,
        "lh": round(size * 1.35, 2), "ls": 0,
        "fc": _rgb(color), "sc": _rgb(color), "sw": 0, "of": False,
    }
    return {
        "ddd": 0, "ind": scene.ind, "ty": 5, "nm": f"text:{text[:18]}", "sr": 1,
        "ks": {"o": _const(100), "r": _const(0), "p": _const([x, y, 0]),
               "a": _const([0, 0, 0]), "s": _const([100, 100, 100])},
        "ao": 0,
        "t": {"d": {"k": [{"s": doc, "t": 0}]}, "p": {}, "m": {"g": 1, "a": _const([0, 0])},
              "a": []},
        "ip": 0, "op": scene.frames, "st": 0, "bm": 0,
    }


class Scene:
    def __init__(self, name, h, dur, poster_note=""):
        self.name = name
        self.w = W
        self.h = h
        self.dur = dur
        self.frames = _frames(dur)
        self.layers = []
        self.nodes = []
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
        layer = _text_layer(self, text, x, y, size, color, anchor, weight)
        items = [{"kind": "text", "x": x, "y": y, "text": text, "size": size,
                  "color": color, "anchor": anchor}]
        node = Node(self, [layer], (x, y), items, opacity)
        self.nodes.append(node)
        return node

    def line(self, x1, y1, x2, y2, color=LINE, width=1.5, trim=True):
        dx, dy = x2 - x1, y2 - y1
        shape = {"ty": "sh", "ks": _const({
            "i": [[0, 0], [0, 0]], "o": [[0, 0], [0, 0]],
            "v": [[0, 0], [dx, dy]], "c": False})}
        stroke = {"ty": "st", "c": _const(_rgba(color)), "o": _const(100),
                  "w": _const(width), "lc": 2, "lj": 1, "ml": 4, "bm": 0}
        group = {"ty": "gr", "it": [shape, stroke]}
        if trim:
            tprop = {"s": _const(0), "e": _const(100), "o": _const(0), "m": 1}
            group["it"].append({"ty": "tm", **tprop})
        group["it"].append(_tr())
        layer = _layer(self, "line", [group], x1, y1)
        if trim:
            layer["_trim"] = tprop["e"]
        items = [{"kind": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                  "color": color, "w": width}]
        node = Node(self, [layer], (x1, y1), items)
        self.nodes.append(node)
        return node

    def arrow(self, x1, y1, x2, y2, color=LINE, width=1.5):
        line = self.line(x1, y1, x2, y2, color, width)
        h = 5
        if x1 == x2:
            d = -1 if y2 < y1 else 1
            pts = [(x2, y2), (x2 - h, y2 - d * h * 1.6), (x2 + h, y2 - d * h * 1.6)]
        else:
            d = -1 if x2 < x1 else 1
            pts = [(x2, y2), (x2 - d * h * 1.6, y2 - h), (x2 - d * h * 1.6, y2 + h)]
        path = {"ty": "sh", "ks": _const({
            "i": [[0, 0]] * 3, "o": [[0, 0]] * 3,
            "v": [[p[0] - x2, p[1] - y2] for p in pts], "c": True})}
        fill = {"ty": "fl", "c": _const(_rgba(color)), "o": _const(100), "r": 1, "bm": 0}
        head = _layer(self, "arrowhead", [{"ty": "gr", "it": [path, fill, _tr()]}], x2, y2)
        head_node = Node(self, [head], (x2, y2), [])
        self.nodes.append(head_node)
        line.head = head_node
        line.svg_items.append({"kind": "poly", "x": x2, "y": y2, "points": pts,
                               "fill": color})
        return line

    def dot(self, cx, cy, r=5, color=ACCENT, opacity=100):
        shape = {"ty": "el", "s": _const([r * 2, r * 2]), "p": _const([0, 0])}
        fill = {"ty": "fl", "c": _const(_rgba(color)), "o": _const(100), "r": 1, "bm": 0}
        layer = _layer(self, "dot", [{"ty": "gr", "it": [shape, fill, _tr()]}], cx, cy)
        node = Node(self, [layer], (cx, cy),
                    [{"kind": "dot", "x": cx, "y": cy, "r": r, "fill": color}], opacity)
        self.nodes.append(node)
        return node

    def _absorb(self, target, node):
        """Fold a text node into the shape node so both move and fade as one."""
        target.layers += node.layers
        target.base += node.base
        for layer in node.layers:
            self.layers.remove(layer)
        target.svg_items += node.svg_items
        self.nodes.remove(node)
        return target

    def chip(self, x, y, w, h, label, accent=False, size=12.5):
        node = self.rect(x, y, w, h, TINT if accent else SURFACE,
                         ACCENT if accent else LINE, 9)
        return self._absorb(node, self.text(x + w / 2, y + h / 2 + 4.5, label, size,
                                           INK, "middle"))

    def card(self, x, y, w, h, title, sub="", accent=False, size=13):
        node = self.rect(x, y, w, h, TINT if accent else SURFACE,
                         ACCENT if accent else LINE, 10)
        self._absorb(node, self.text(x + 14, y + (26 if sub else h / 2 + 4.5), title,
                                     size, INK))
        if sub:
            self._absorb(node, self.text(x + 14, y + 46, sub, 11.5, MUTED))
        self._absorb(node, self.rect(x, y + 1, 3, h - 2, ACCENT, None, 1.5))
        return node

    def row(self, x, y, w, h, label, sub="", accent=False, size=12.5):
        node = self.rect(x, y, w, h, TINT if accent else SURFACE,
                         ACCENT if accent else LINE, 8)
        self._absorb(node, self.text(x + 14, y + h / 2 + 4.5, label, size,
                                     ACCENT if accent else INK))
        if sub:
            self._absorb(node, self.text(x + w - 14, y + h / 2 + 4.5, sub, 11.5,
                                         MUTED, "end"))
        return node

    # ── helpers ────────────────────────────────────────────────────────────
    def fade_in(self, node, t, d=0.4):
        node.opacity_keys = [(_frames(0), [0])]
        node.fade(t, 100, d)
        return node

    def fade_out(self, node, t, d=0.4):
        return node.fade(t, 0, d)

    def draw_on(self, node, t, d=0.7):
        node.opacity_keys = [(_frames(0), [0])]
        node.show(t, 0.01)
        node.draw_on(t, d)
        if hasattr(node, "head"):
            node.head.opacity_keys = [(_frames(0), [0])]
            node.head.show(t + d * 0.75, 0.2)
        return node

    def swap_state(self, a, b, t, d=0.5):
        """Crossfade one state into another in the same place."""
        return self.swap(a, b, t, d)

    def swap(self, a, b, t, d=0.5):
        a.fade(t, 0, d)
        b.opacity_keys = [(_frames(0), [0])]
        b.show(t, d)
        return b

    def json(self):
        return {
            "v": "5.13.0", "fr": FPS, "ip": 0, "op": self.frames,
            "w": self.w, "h": self.h, "nm": self.name, "ddd": 0,
            "assets": [], "layers": self.layers, "markers": [],
            "fonts": {"list": [{"fName": "Inter", "fFamily": "Inter",
                                "fStyle": "Regular", "ascent": 75}]},
        }

    def dumps(self):
        return json.dumps(self.json(), sort_keys=True, separators=(",", ":"))

    # ── poster ─────────────────────────────────────────────────────────────
    def poster(self):
        out = [f"<svg viewBox='0 0 {self.w} {self.h}' width='{self.w}' "
               f"height='{self.h}' role='img' aria-label='{_esc(self.poster_note)}' "
               f"font-family='Inter,Helvetica Neue,Helvetica,Arial,sans-serif' "
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
                f"height='{it['h'] * sy:.1f}' rx='{it['r']}' fill='{it['fill']}'"
                f"{stroke}{a}/>")
    if k == "text":
        anchor = it["anchor"]
        return (f"<text x='{it['x'] + dx:.1f}' y='{it['y'] + dy:.1f}' "
                f"font-size='{it['size']}' fill='{it['color']}' "
                f"text-anchor='{anchor}'{a}>{_esc(it['text'])}</text>")
    if k == "line":
        return (f"<line x1='{it['x1'] + dx:.1f}' y1='{it['y1'] + dy:.1f}' "
                f"x2='{it['x2'] + dx:.1f}' y2='{it['y2'] + dy:.1f}' "
                f"stroke='{it['color']}' stroke-width='{it['w']}'{a}/>")
    if k == "dot":
        return (f"<circle cx='{it['x'] + dx:.1f}' cy='{it['y'] + dy:.1f}' "
                f"r='{it['r']}' fill='{it['fill']}'{a}/>")
    if k == "poly":
        pts = " ".join(f"{p[0] + dx:.1f},{p[1] + dy:.1f}" for p in it["points"])
        return f"<polygon points='{pts}' fill='{it['fill']}'{a}/>"
    return ""
