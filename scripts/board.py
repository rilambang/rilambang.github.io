#!/usr/bin/env python3
"""Contact sheet across several figures: name:frame[,frame] ...

Same painter as shots.py, several scenes per image, so a batch can be looked at
in one go. Review tool only; it writes to .shots/.
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import lottie_specs  # noqa: E402
from shots import CSS, PAINT  # noqa: E402

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

SPECS = {}
for figs in lottie_specs.build_all().values():
    for sc, _alt, _cap in figs:
        SPECS[sc.name] = sc


def main():
    cells, frames = [], []
    out_name = "board"
    for arg in sys.argv[1:]:
        if arg.startswith("out="):
            out_name = arg[4:]
            continue
        name, _, fs = arg.partition(":")
        scene = SPECS.get(name)
        if scene is None:
            raise SystemExit(f"no scene named {name}")
        for f in (int(x) for x in fs.split(",")):
            frames.append(f)
            cells.append(
                f"<div class='cell'><div class='cap'>{name} f{f}</div>"
                f"<div class='fig-lottie' data-w='{scene.w}' data-h='{scene.h}' "
                f"data-json='{scene.dumps()}'>{scene.poster()}{scene.labels_html()}</div></div>")

    page = (f"<!doctype html><meta charset='utf-8'><style>{CSS}"
            f"body{{grid-template-columns:640px 640px;align-items:start}}</style>"
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

    tmp = ROOT / ".shots" / "board.html"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_text(page)
    out = ROOT / ".shots" / f"{out_name}.png"
    rows = (len(cells) + 1) // 2
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--virtual-time-budget=5000", f"--window-size=1280,{rows * 350}",
                    f"--screenshot={out}", tmp.as_uri()], capture_output=True,
                   timeout=180)
    print(out)


if __name__ == "__main__":
    main()
