#!/usr/bin/env python3
"""A crash check, not a taste check.

Lottie fails silently: a bad file still produces an <svg> element, it just draws
nothing. This proves each file loads, has a real duration, and draws something
that changes. It says nothing about whether the motion is any good -- that needs
a person watching it.
"""
import html
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
LOTTIE = ROOT / "public" / "blog" / "lottie"
PLAYER = ROOT / "node_modules" / "lottie-web" / "build" / "player" / "lottie.min.js"
CHROME = pathlib.Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

MAX_BYTES = 200 * 1024
MAX_FRAMES = 3000

PAGE = """<!doctype html><meta charset="utf-8"><pre id="out">pending</pre>
<script>%s</script>
<script>
const DATA = %s;
const errs = [];
window.onerror = (m) => errs.push('window:' + m);
console.error = (...a) => errs.push(a.map(String).join(' '));
const results = [];
const done = () => {
  document.getElementById('out').textContent = JSON.stringify({results, errs});
};
const check = (i) => {
  if (i >= DATA.length) return setTimeout(done, 50);
  const d = DATA[i];
  const c = document.createElement('div');
  document.body.appendChild(c);
  let anim;
  try {
    anim = lottie.loadAnimation({container: c, renderer: 'svg', loop: false,
      autoplay: false, animationData: d.data});
  } catch (e) {
    results.push({name: d.name, error: 'throw:' + e, dur: 0, diff: false});
    return check(i + 1);
  }
  const local = [];
  anim.addEventListener('error', (e) => local.push(JSON.stringify(e.detail || e)));
  setTimeout(() => {
    try {
      anim.goToAndStop(0, true);
      const a = c.innerHTML;
      anim.goToAndStop(Math.floor(d.data.op / 2), true);
      const b = c.innerHTML;
      results.push({name: d.name, error: local.join('|'), dur: anim.getDuration(),
        diff: a !== b, frames: anim.totalFrames, drawn: c.querySelectorAll('path,text').length});
    } catch (e) {
      results.push({name: d.name, error: 'frame:' + e, dur: 0, diff: false});
    }
    c.remove();
    check(i + 1);
  }, 60);
};
check(0);
</script>"""


def _dup_keys(node, path, bad, name):
    """Two keyframes on the same frame make lottie-web interpolate across a
    zero-length segment: a one-frame jump, or a property that silently never
    animates. Cheap to catch here, invisible to the eye until it ships."""
    if isinstance(node, dict):
        if node.get("a") == 1 and isinstance(node.get("k"), list):
            ts = [k["t"] for k in node["k"] if isinstance(k, dict)]
            if any(b <= a for a, b in zip(ts, ts[1:])):
                bad.append(f"{name}: two keys on one frame at {path} {ts}")
        for k, v in node.items():
            _dup_keys(v, f"{path}.{k}", bad, name)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _dup_keys(v, f"{path}[{i}]", bad, name)


def main():
    files = sorted(LOTTIE.glob("*.json"))
    if not files:
        print("no lottie files -- run scripts/build-blog.py first")
        return 1
    if not CHROME.exists():
        print(f"headless Chrome not found at {CHROME}")
        return 1

    bad = []
    total = 0
    data = []
    for f in files:
        raw = f.read_bytes()
        doc = json.loads(raw)
        frames = int(doc.get("op", 0))
        total += len(raw)
        if len(raw) > MAX_BYTES:
            bad.append(f"{f.name}: {len(raw)}B over {MAX_BYTES}B")
        if frames > MAX_FRAMES:
            bad.append(f"{f.name}: {frames} frames over {MAX_FRAMES}")
        _dup_keys(doc, "", bad, f.name)
        data.append({"name": f.name, "data": doc})

    page = PAGE % (PLAYER.read_text(), json.dumps(data, separators=(",", ":")))
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as fh:
        fh.write(page)
        tmp = fh.name

    out = subprocess.run(
        [str(CHROME), "--headless=new", "--disable-gpu", "--virtual-time-budget=60000",
         "--dump-dom", pathlib.Path(tmp).as_uri()],
        capture_output=True, text=True, timeout=300).stdout
    pathlib.Path(tmp).unlink(missing_ok=True)

    start = out.find('<pre id="out">')
    if start == -1:
        print("validator page produced no output")
        return 1
    body = out[start + len('<pre id="out">'):].split("</pre>", 1)[0]
    payload = json.loads(html.unescape(body))
    results = {r["name"]: r for r in payload["results"]}

    for item in data:
        name = item["name"]
        r = results.get(name)
        raw = LOTTIE / name
        if r is None:
            bad.append(f"{name}: not reached by the player")
            continue
        ok = (r["dur"] > 0 and r["diff"] and not r["error"]
              and r.get("drawn", 0) > 0)
        if not ok:
            bad.append(f"{name}: dur={r['dur']} diff={r['diff']} "
                       f"drawn={r.get('drawn', 0)} error={r['error'] or '-'}")
        print(f"{name:46s} {raw.stat().st_size / 1024:7.1f}KB "
              f"{r.get('frames', 0):5.0f}f {r['dur']:5.2f}s "
              f"{'ok' if ok else 'FAIL'}")

    print(f"\n{len(data) - len([b for b in bad if 'not reached' not in b and 'over' not in b])}"
          f"/{len(data)} passed  |  {total / 1024:.0f}KB json  |  "
          f"{PLAYER.stat().st_size / 1024:.0f}KB player")
    for b in bad:
        print("FAIL " + b)
    if payload["errs"]:
        print("console: " + " | ".join(payload["errs"]))
        bad.append("console errors")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
