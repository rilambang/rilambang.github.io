// Still images of every figure, for places that cannot run the animated SVG (Medium's
// "Import a story" keeps <img>, drops inline <svg>). Draws each figure's finished frame
// on a light sheet and writes site/assets/figs/<id>.png. Needs rsvg-convert
// (librsvg: `brew install librsvg`, `apt install librsvg2-bin`). Run after adding or
// changing a figure, then commit the PNGs: the build itself stays dependency-free and
// only links the stills that exist.
import fs from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { execFileSync } from 'node:child_process'
import { figures, W } from '../site/figures.mjs'

const ROOT = path.resolve(import.meta.dirname, '..')
const OUT = path.join(ROOT, 'site', 'assets', 'figs')
const TMP = fs.mkdtempSync(path.join(os.tmpdir(), 'stills-'))
const PAD = 24, SCALE = 2

// Light palette from style.css, finished state only (nothing armed, nothing playing).
const CSS = `
.bx{fill:#f9eff2;stroke:#2b0e18;stroke-width:1.5}.bx.ink{stroke:#a31d47}
.tx{fill:#2b0e18;font:500 16px "Bricolage Grotesque","Helvetica Neue",Arial,sans-serif}
.tx.sm{font-size:14px}.tx.lg{font-size:21px;font-weight:700}.tx.big{font-size:58px;font-weight:800;letter-spacing:-.04em}
.tx.code{font:400 14.5px "JetBrains Mono",Menlo,"DejaVu Sans Mono",monospace}
text.mut{fill:#6a4250}text.ink{fill:#a31d47}
.ln{fill:none;stroke:#2b0e18;stroke-width:1.6;stroke-linecap:round}.ln.mut{stroke:#6a4250}.ln.ink{stroke:#a31d47}
.hd{fill:#2b0e18}.hd.mut{fill:#6a4250}.hd.ink{fill:#a31d47}
.rg{fill:none;stroke:#a31d47;stroke-width:2.2;stroke-linecap:round}.rg.thick{stroke-width:2.8}
.tk{fill:none;stroke:#2b0e18;stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}
.bb{fill:#f9eff2;stroke:#6a4250;stroke-width:1.3}.bb.ink{stroke:#a31d47}
.fillin{fill:#2b0e18}.fillin.ink{fill:#a31d47}
.chip{fill:#f9eff2;stroke:#6a4250;stroke-width:1.2}.chip.ink{stroke:#a31d47;stroke-width:1.6}
.bar{fill:#2b0e18;opacity:.6}.bar.ink{fill:#a31d47;opacity:1}
.lk{fill:none;stroke:#a31d47;stroke-width:2.2}.lkf{fill:#a31d47}
.dim{opacity:.45}.gone{opacity:0}
`

// CSS custom properties (--dx/--dy on moved marks) do not reach rsvg, so bake the
// finished translate into each element; drop the timing vars, which only drive animation.
const bake = (svg) => svg.replace(/style="([^"]*)"/g, (_, s) => {
  const v = Object.fromEntries(s.split(';').filter(Boolean).map((d) => d.split(':').map((x) => x.trim())))
  return v['--dx'] || v['--dy'] ? `transform="translate(${parseFloat(v['--dx'] || 0)} ${parseFloat(v['--dy'] || 0)})"` : ''
}).replace(/ data-dash(?==|\s|\/|>)(="[^"]*")?/g, ' stroke-dasharray="0.035 0.025"') // .dr[data-dash] in style.css; XML needs a value

fs.mkdirSync(OUT, { recursive: true })
let n = 0
for (const [id, f] of Object.entries(figures)) {
  const r = f()
  const w = W + PAD * 2, h = r.h + PAD * 2
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${-PAD} ${-PAD} ${w} ${h}" width="${w * SCALE}" height="${h * SCALE}">` +
    `<style>${CSS}</style><rect x="${-PAD}" y="${-PAD}" width="${w}" height="${h}" fill="#fcf2f4"/>${bake(r.svg)}</svg>`
  const src = path.join(TMP, `${id}.svg`)
  fs.writeFileSync(src, svg)
  execFileSync('rsvg-convert', ['-o', path.join(OUT, `${id}.png`), src])
  n++
}
fs.rmSync(TMP, { recursive: true, force: true })
console.log(`${n} stills -> site/assets/figs/`)
