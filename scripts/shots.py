#!/usr/bin/env python3
"""Contact sheet: one figure, six frames, labels included. For looking at by eye."""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import lottie_specs  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
body{margin:0;background:#09090f;display:grid}
.cell{position:relative}
.cap{position:absolute;left:6px;top:2px;color:#ff8a8a;font:10px monospace;z-index:3}
.fig-lottie{position:relative;container-type:inline-size;line-height:1}
.fig-lottie svg{display:block;width:100%;height:auto}
.fig-lottie.is-live > svg.poster{display:none}
.fig-labels{position:absolute;inset:0;z-index:1;pointer-events:none;
  font-family:Inter,Helvetica Neue,Helvetica,Arial,sans-serif}
.fig-label{position:absolute;white-space:nowrap;font-weight:400;opacity:var(--a0,1)}
"""

PAINT = """
function alphaAt(list, f){
  var i = 0;
  while (i + 1 < list.length && list[i + 1][0] <= f) i += 1;
  if (i + 1 >= list.length) return list[i][1];
  var t0 = list[i][0], t1 = list[i + 1][0];
  var u = t1 > t0 ? (f - t0) / (t1 - t0) : 1;
  return list[i][1] + (list[i + 1][1] - list[i][1]) * u;
}
function painter(el, W, H){
  var labels = [].slice.call(el.querySelectorAll('.fig-label')).map(function(n){
    var a = n.getAttribute('data-alpha'), p = n.getAttribute('data-path');
    return {el: n, a: a ? a.split(' ').map(function(s){
      var q = s.split(':'); return [+q[0], +q[1]]; }) : null,
      p: p ? p.split(' ').map(Number) : null};
  });
  return function(f){
    labels.forEach(function(l){
      if (l.a) l.el.style.opacity = (alphaAt(l.a, f) / 100).toFixed(3);
      if (l.p) {
        var i = Math.min(Math.round(f), l.p.length / 2 - 1) * 2;
        // cqw is 1% of the container width, both axes: y divides by W too
        l.el.style.translate = (l.p[i] / W * 100).toFixed(3) + 'cqw ' +
                               (l.p[i + 1] / W * 100).toFixed(3) + 'cqw';
      }
    });
  };
}
"""


def main():
    name = sys.argv[1]
    frames = [int(f) for f in sys.argv[2].split(",")]
    scene = None
    for figs in lottie_specs.build_all().values():
        for sc, _alt, _cap in figs:
            if sc.name == name:
                scene = sc
    if scene is None:
        raise SystemExit(f"no scene named {name}")

    cells = []
    for f in frames:
        cells.append(
            f"<div class='cell'><div class='cap'>{name} f{f}</div>"
            f"<div class='fig-lottie' data-w='{scene.w}' data-h='{scene.h}' "
            f"data-json='{scene.dumps()}'>{scene.poster()}{scene.labels_html()}</div></div>")

    page = (f"<!doctype html><meta charset='utf-8'><style>{CSS}"
            f"body{{grid-template-columns:{scene.w}px {scene.w}px}}</style>"
            f"<script src='{ROOT}/node_modules/lottie-web/build/player/lottie.min.js'></script>"
            f"<body>{''.join(cells)}<script>{PAINT}"
            f"var FR={frames};"
            f"document.querySelectorAll('.fig-lottie').forEach(function(el, i){{"
            f"  var W=+el.dataset.w, H=+el.dataset.h, paint=painter(el, W, H);"
            f"  paint(0);"
            f"  var a=lottie.loadAnimation({{container:el, renderer:'svg', loop:false,"
            f"    autoplay:false, animationData:JSON.parse(el.dataset.json)}});"
            f"  a.addEventListener('DOMLoaded', function(){{"
            f"    el.classList.add('is-live'); a.goToAndStop(FR[i], true); paint(FR[i]); }});"
            f"}});</script>")

    tmp = ROOT / ".shots" / f"{name}.html"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(page)
    out = ROOT / ".shots" / f"{name}.png"
    rows = (len(frames) + 1) // 2
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--virtual-time-budget=4000", f"--window-size={scene.w * 2},{rows * scene.h}",
                    f"--screenshot={out}", tmp.as_uri()], capture_output=True, timeout=120)
    print(out)


if __name__ == "__main__":
    main()
