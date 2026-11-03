// Figures are drawn from a tiny pencil-on-answer-sheet vocabulary: outlined boxes,
// bubbles that get filled in, lines that are drawn, marks in form ink. Every figure is
// a list of timed marks. The CSS (assets/style.css) plays them once when the figure
// scrolls into view; with no JS or reduced motion the finished drawing is simply there.
const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
const W = 720

function make(h, alt, cap, draw) {
  const p = []
  const st = (t = 0, d, extra = '') => ` style="--t:${t}s${d ? `;--d:${d}s` : ''}${extra}"`
  const cls = (tone) => (tone ? ` ${tone}` : '')
  const g = {
    raw: (s) => p.push(s),
    // outlined box with 1-2 centred lines
    box(x, y, w, hh, label, o = {}) {
      const lines = String(label).split('\n')
      const base = y + hh / 2 - (lines.length - 1) * 10 + 5
      p.push(`<g class="pop${cls(o.dim ? 'dim' : '')}"${st(o.t)}><rect x="${x}" y="${y}" width="${w}" height="${hh}" rx="9" class="bx${cls(o.tone)}"${o.dash ? ' stroke-dasharray="5 4"' : ''}/>` +
        lines.map((l, i) => `<text x="${x + w / 2 + (o.dx || 0)}" y="${base + i * 20}" text-anchor="middle" class="tx${i && o.sub !== false ? ' mut sm' : ''}${cls(o.tx)}">${esc(l)}</text>`).join('') + '</g>')
    },
    text(x, y, s, o = {}) {
      p.push(`<text x="${x}" y="${y}" text-anchor="${o.a || 'start'}" class="${o.cls || 'pop'} tx${cls(o.tone)}${o.sm ? ' sm' : ''}${o.lg ? ' lg' : ''}"${st(o.t)}>${esc(s)}</text>`)
    },
    // a drawn line, optional arrowhead
    ln(x1, y1, x2, y2, o = {}) {
      const dur = o.d || 0.6
      p.push(`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" pathLength="1" class="dr ln${cls(o.tone)}"${o.dash ? ' data-dash' : ''}${st(o.t, dur)}/>`)
      if (o.head) {
        const a = Math.atan2(y2 - y1, x2 - x1), s = 8
        const pt = (da) => `${(x2 - s * Math.cos(a + da)).toFixed(1)},${(y2 - s * Math.sin(a + da)).toFixed(1)}`
        p.push(`<polygon points="${x2},${y2} ${pt(0.45)} ${pt(-0.45)}" class="hd${cls(o.tone)}"${st((o.t || 0) + dur * 0.85)}/>`)
      }
    },
    // a bubble that is filled in at time t (or left empty)
    bub(x, y, o = {}) {
      p.push(`<circle cx="${x}" cy="${y}" r="9" class="bb fade${cls(o.tone)}"${st(o.t !== undefined ? Math.max(0, o.t - 0.25) : 0)}/>`)
      if (o.on !== false) p.push(`<circle cx="${x}" cy="${y}" r="6.5" class="fillin${cls(o.tone)}"${st(o.t)}/>`)
    },
    ring(x, y, w, hh, o = {}) {
      p.push(`<rect x="${x}" y="${y}" width="${w}" height="${hh}" rx="9" pathLength="1" class="dr rg"${st(o.t, o.d || 0.7)}/>`)
    },
    cross(x, y, s = 9, o = {}) {
      p.push(`<g class="x"${st(o.t)}><line x1="${x - s}" y1="${y - s}" x2="${x + s}" y2="${y + s}" pathLength="1" class="dr rg"${st(o.t, 0.25)}/><line x1="${x + s}" y1="${y - s}" x2="${x - s}" y2="${y + s}" pathLength="1" class="dr rg"${st((o.t || 0) + 0.2, 0.25)}/></g>`)
    },
    tick(x, y, o = {}) {
      p.push(`<polyline points="${x - 8},${y} ${x - 2},${y + 7} ${x + 9},${y - 8}" pathLength="1" class="dr tk"${st(o.t, 0.35)}/>`)
    },
    strike(x1, y, x2, o = {}) {
      p.push(`<line x1="${x1}" y1="${y}" x2="${x2}" y2="${y}" pathLength="1" class="dr rg thick"${st(o.t, 0.4)}/>`)
    },
    // group that travels (dx, dy) at time t; rests at the destination without motion
    mv(inner, dx, dy, o = {}) {
      p.push(`<g class="mv" style="--t:${o.t || 0}s;--d:${o.d || 0.9}s;--dx:${dx}px;--dy:${dy}px">${inner}</g>`)
    },
    // a group that is erased at time t
    gone(fn, t) {
      p.push(`<g class="gone"${st(t)}>`); fn(); p.push('</g>')
    },
    grow(x, y, w, hh, o = {}) {
      p.push(`<rect x="${x}" y="${y}" width="${w}" height="${hh}" rx="5" class="grow bar${cls(o.tone)}"${st(o.t, o.d || 0.9)}/>`)
    },
    lock(x, y, o = {}) {
      p.push(`<g class="pop"${st(o.t)}><path d="M${x - 7},${y - 3} v-5 a7,7 0 0 1 14,0 v5" class="lk"/><rect x="${x - 10}" y="${y - 4}" width="20" height="15" rx="3" class="lkf"/></g>`)
    },
  }
  draw(g)
  return { alt, cap, h, svg: p.join('') }
}

const rows = (g, list, y0, step, o = {}) => list.forEach(([a, b], i) => {
  const y = y0 + i * step, t = (o.t0 ?? 0.3) + i * (o.dt ?? 0.55)
  g.bub(40, y, { t })
  g.text(66, y + 5, a, { t, cls: 'fade', tone: o.dimLast && i === list.length - 1 ? 'mut' : '' })
  if (b) g.text(o.bx ?? 250, y + 5, b, { t: t + 0.1, cls: 'fade', tone: 'mut', sm: true })
})

// a claim, struck through, and what it actually was
const claims = (g, list, y0, step) => list.forEach(([claim, truth], i) => {
  const y = y0 + i * step, t = 0.3 + i * 0.85
  g.text(30, y, claim, { t, cls: 'fade' })
  g.strike(26, y - 5, Math.min(312, 28 + claim.length * 8.8), { t: t + 0.45 })
  g.ln(318, y - 5, 372, y - 5, { t: t + 0.55, d: 0.3, head: true, tone: 'mut' })
  g.text(386, y, truth, { t: t + 0.8, tone: 'ink', cls: 'fade' })
})

export const figures = {
  // ── kiosk-and-assessment-apps ────────────────────────────────────────────
  'kiosk-lock': () => make(290, 'A session starts and four things iOS holds go locked: the app switcher, Home, notifications and other apps.', 'A session starts and four things iOS holds go locked.', (g) => {
    g.box(265, 105, 190, 80, 'Your app\nassessment session', { t: 0 })
    ;[['App switcher', 30, 30], ['Home', 30, 200], ['Notifications', 490, 30], ['Other apps', 490, 200]].forEach(([l, x, y], i) => {
      const t = 0.5 + i * 0.55, left = x < 300
      g.ln(left ? 265 : 455, 145, left ? x + 200 : x, y + 30, { t, d: 0.4, tone: 'mut' })
      g.box(x, y, 200, 60, l, { t: t + 0.35, dx: -14 })
      g.bub(x + 170, y + 30, { t: t + 0.8 })
      g.text(x + 100, y + 80, 'locked', { t: t + 0.8, a: 'middle', sm: true, tone: 'mut', cls: 'fade' })
    })
  }),
  'kiosk-entitlement': () => make(190, 'The entitlement is a request: you ask Apple, Apple reviews, and only then can a session start.', 'The entitlement is the first thing to ask for, and it is a request.', (g) => {
    g.box(30, 50, 200, 80, 'You request\nthe entitlement', { t: 0 })
    g.ln(230, 90, 265, 90, { t: 0.5, d: 0.3, tone: 'mut', head: true })
    g.box(265, 50, 190, 80, 'Apple reviews\nthe request', { t: 0.8 })
    g.ln(455, 90, 490, 90, { t: 1.4, d: 0.3, tone: 'mut', head: true })
    g.box(490, 50, 200, 80, 'A session\ncan start', { t: 1.8, tone: 'ink' })
    g.text(130, 165, 'Do this in week one', { t: 2.4, a: 'middle', tone: 'ink', sm: true })
    g.text(590, 165, 'Without it, the app is just an app', { t: 2.6, a: 'middle', tone: 'mut', sm: true })
  }),

  // ── splitting-an-app-into-local-packages ────────────────────────────────
  'split-file': () => make(290, 'One file moves from the app target into a local package, and the move takes a day while the boundary it crosses takes a quarter.', 'The file moves in a day. The boundary it crosses is the work.', (g) => {
    g.box(30, 30, 270, 200, '', { t: 0 })
    g.text(165, 62, 'App target', { t: 0, a: 'middle' })
    g.box(420, 30, 270, 200, '', { t: 0.3, tone: 'ink' })
    g.text(555, 62, 'Local package', { t: 0.3, a: 'middle', tone: 'ink' })
    ;['UserCard.swift', 'Theme.swift', 'Logger.swift'].forEach((f, i) => {
      const chip = `<rect x="60" y="${90 + i * 44}" width="210" height="32" rx="7" class="chip"/><text x="165" y="${111 + i * 44}" text-anchor="middle" class="tx sm">${f}</text>`
      i === 1 ? g.mv(chip, 390, 0, { t: 1.1, d: 1 }) : g.raw(`<g class="pop" style="--t:${0.6 + i * 0.2}s">${chip}</g>`)
    })
    g.text(360, 268, 'Moving a file: a day. Drawing the boundary: a quarter.', { t: 2.4, a: 'middle', tone: 'mut', sm: true })
  }),
  'split-order': () => make(370, 'The order a local-package split breaks in: resources, access control, build settings, names, tests, the awkward middle, and cycles.', 'What breaks first is the boundary, not the build.', (g) => {
    rows(g, [
      ['Resources', 'Bundle.main compiles, then returns nil'],
      ['Access control', 'internal turns into public'],
      ['Build settings', 'a package inherits none of them'],
      ['Names', 'User, Config and Logger all collide'],
      ['Tests', 'they cannot reach across the wall'],
      ['The awkward middle', 'everything public, nothing faster yet'],
      ['Cycles', 'now they are compile errors'],
    ], 34, 48, { dt: 0.5, bx: 230 })
  }),

  // ── build-time-is-a-dependency-graph-problem ────────────────────────────
  'build-edges': () => make(300, 'Deleting one script phase removes most of the edges in the build graph: twelve become four.', 'Twelve edges become four when the script phase goes.', (g) => {
    const ys = [28, 90, 152, 214]
    ys.forEach((y, i) => {
      g.box(30, y, 130, 44, `Module ${'ABCD'[i]}`, { t: 0 })
      g.box(560, y, 130, 44, `Module ${'WXYZ'[i]}`, { t: 0 })
      g.ln(160, y + 22, 560, y + 22, { t: 0.3 + i * 0.15, d: 0.5, tone: 'mut' })
    })
    g.gone(() => {
      g.box(300, 108, 120, 56, 'Run Script\nno inputs declared', { t: 1.4, tone: 'ink' })
      ys.forEach((y, i) => {
        g.ln(160, y + 22, 300, 136, { t: 1.8 + i * 0.12, d: 0.4, tone: 'ink', head: false })
        g.ln(420, 136, 560, y + 22, { t: 2.4 + i * 0.12, d: 0.4, tone: 'ink', head: false })
      })
      g.cross(360, 136, 16, { t: 3.7 })
    }, 4.2)
    g.gone(() => g.text(360, 290, '12 edges', { t: 1.2, a: 'middle', lg: true }), 4.4)
    g.text(360, 290, '4 edges', { t: 4.6, a: 'middle', lg: true, tone: 'ink' })
  }),
  'build-bars': () => make(250, 'A schematic of build time: faster hardware shortens the bar by a constant factor, while deleting a script phase changes the graph.', 'Faster hardware is a constant. The graph is the exponent. (Schematic, not measured.)', (g) => {
    ;[['Today', 440, ''], ['A faster Mac', 350, ''], ['Delete one script phase', 120, 'ink']].forEach(([l, w, tone], i) => {
      const y = 36 + i * 58
      g.text(30, y + 22, l, { t: i * 0.5, cls: 'fade', tone: tone ? 'ink' : '' })
      g.grow(250, y, w, 34, { t: 0.3 + i * 0.5, d: 0.9, tone })
    })
    g.text(250, 222, 'Hardware scales the line. The dependency graph changes its slope.', { t: 2.2, tone: 'mut', sm: true })
  }),

  // ── uikit-to-swiftui-without-a-rewrite ──────────────────────────────────
  'uikit-chrome': () => make(320, 'One screen converted: the navigation bar changes owner while the same four rows stay where they are.', 'Navigation changes owner. The content does not move.', (g) => {
    const screen = (x, label, tone) => {
      g.box(x, 34, 250, 56, label, { t: 0, tone, sub: false })
      ;['Welcome', 'Location', 'Ready', 'Paper'].forEach((r, i) => {
        g.raw(`<line x1="${x + 14}" y1="${126 + i * 46}" x2="${x + 236}" y2="${126 + i * 46}" class="ln mut"/>`)
        g.text(x + 16, 116 + i * 46, r, { t: 0.2, cls: 'fade' })
      })
    }
    screen(40, 'UIKit navigation controller')
    screen(430, 'SwiftUI navigation stack', 'ink')
    g.text(165, 22, 'Before', { t: 0, a: 'middle', tone: 'mut', sm: true })
    g.text(555, 22, 'After', { t: 0.8, a: 'middle', tone: 'mut', sm: true })
    g.ln(300, 62, 420, 62, { t: 0.9, d: 0.7, head: true, tone: 'ink' })
    g.ring(424, 28, 262, 68, { t: 1.7 })
    g.text(360, 306, 'Same four rows. Only the owner of navigation changed.', { t: 2.3, a: 'middle', tone: 'mut', sm: true })
  }),
  'uikit-contract': () => make(290, 'A UIKit shell that owns navigation hosts a SwiftUI screen: the parent passes a value in and receives events out.', 'The parent passes a value in and gets events out. The leaf never pushes.', (g) => {
    g.box(40, 30, 640, 230, 'UIKit shell: owns the navigation stack', { t: 0, sub: false })
    g.raw('<rect x="40" y="30" width="640" height="230" rx="9" class="bx" fill="none"/>')
    g.box(235, 120, 250, 90, 'SwiftUI screen\nrenders content', { t: 0.7, tone: 'ink' })
    g.ln(130, 100, 130, 165, { t: 1.4, d: 0.5, tone: 'mut' })
    g.ln(130, 165, 235, 165, { t: 1.8, d: 0.4, head: true, tone: 'mut' })
    g.text(130, 90, 'a value goes in', { t: 1.3, a: 'middle', sm: true, tone: 'mut' })
    g.ln(485, 165, 590, 165, { t: 2.5, d: 0.4, tone: 'mut' })
    g.ln(590, 165, 590, 100, { t: 2.9, d: 0.5, head: true, tone: 'mut' })
    g.text(590, 90, 'events come out', { t: 2.5, a: 'middle', sm: true, tone: 'mut' })
  }),

  // ── a-design-system-is-a-review-policy ──────────────────────────────────
  'design-review': () => make(290, 'A pull request adds a pasted hex colour and the review comment refuses it in favour of the token.', 'The review, not the import, is what holds the system.', (g) => {
    g.raw('<rect x="40" y="26" width="640" height="130" rx="9" class="bx"/>')
    g.text(64, 62, 'struct PayButton: View {', { t: 0, cls: 'fade code', tone: 'mut' })
    g.text(64, 98, '    .background(Color(hex: "#3F7CF5"))', { t: 0.3, cls: 'fade code' })
    g.text(64, 134, '}', { t: 0.6, cls: 'fade code', tone: 'mut' })
    g.ring(54, 76, 612, 32, { t: 1.2 })
    g.ln(360, 108, 360, 176, { t: 1.7, d: 0.4, tone: 'ink', head: true })
    g.box(110, 178, 500, 84, 'Use the surface token.\nA pasted value is the third copy.', { t: 2.1, tone: 'ink', sub: false })
  }),
  'design-copies': () => make(250, 'Three copies of a colour: the design source and the token mirror each other, while the literal pasted into a view drifts.', 'Three copies of every value. The third one ages badly.', (g) => {
    g.box(30, 50, 190, 70, 'Design source', { t: 0 })
    g.ln(220, 85, 265, 85, { t: 0.5, d: 0.3, tone: 'mut', head: true })
    g.box(265, 50, 190, 70, 'Token', { t: 0.8 })
    g.mv('<g><rect x="500" y="50" width="190" height="70" rx="9" class="bx ink" stroke-dasharray="5 4"/><text x="595" y="90" text-anchor="middle" class="tx ink">Literal in a view</text></g>', 26, 44, { t: 1.8, d: 1.6 })
    g.text(360, 230, 'It never breaks. It drifts, one hex at a time.', { t: 3.0, a: 'middle', tone: 'mut', sm: true })
  }),

  // ── how-i-review-ios-pull-requests ──────────────────────────────────────
  'review-order': () => make(300, 'The order a diff is read in: does it match the description, can it crash, what is the failure path, what was deleted, and style last.', 'Risk comes first, style last, and the order is the review.', (g) => {
    rows(g, [
      ['Does it do what the description says?', ''],
      ['Can it crash?', ''],
      ['What is the failure path?', ''],
      ['What was deleted?', ''],
      ['Style', 'last, and usually not at all'],
    ], 38, 52, { dt: 0.65, dimLast: true, bx: 190 })
  }),
  'review-comment': () => make(300, 'A review comment attached to the line that carries the risk: try? hides a failed save.', 'The comment that names the failure mode is the review.', (g) => {
    g.raw('<rect x="40" y="24" width="640" height="150" rx="9" class="bx"/>')
    g.text(64, 60, 'func save(draft: Draft) {', { t: 0, cls: 'fade code', tone: 'mut' })
    g.text(64, 96, '    try? store.write(draft)', { t: 0.3, cls: 'fade code' })
    g.text(64, 132, '    dismiss()', { t: 0.6, cls: 'fade code', tone: 'mut' })
    g.text(64, 160, '}', { t: 0.9, cls: 'fade code', tone: 'mut' })
    g.ring(54, 74, 612, 32, { t: 1.4 })
    g.ln(330, 106, 330, 190, { t: 1.9, d: 0.4, tone: 'ink', head: true })
    g.box(80, 192, 580, 84, 'try? swallows a failed save.\nThe user loses the draft and nobody finds out.', { t: 2.3, tone: 'ink', sub: false })
  }),

  // ── the-ios-stack-i-actually-reach-for ──────────────────────────────────
  'stack-rows': () => make(340, 'The stack, one decision per row, each chosen by whether the next engineer can debug it at 3am.', 'A stack chosen for who debugs it at 3am.', (g) => {
    rows(g, [
      ['Language', 'Swift, strict concurrency on'],
      ['UI', 'SwiftUI, UIKit where the platform needs it'],
      ['Structure', 'local packages, a thin app target'],
      ['Networking', 'what the codebase already has'],
      ['Persistence', 'the platform first, constraints in the schema'],
      ['Strings', 'one catalogue, referenced by key'],
      ['Tests', 'logic first, UI tests sparingly'],
    ], 30, 44, { dt: 0.45, bx: 190 })
  }),
  'stack-pages': () => make(260, 'Each dependency added to an app is one more thing that can wake someone at 3am.', 'Every dependency is a 3am page.', (g) => {
    g.box(30, 100, 150, 60, 'Your app', { t: 0 })
    ;['A', 'B', 'C', 'D'].forEach((l, i) => {
      const y = 26 + i * 62, t = 0.6 + i * 0.7
      g.ln(180, 130, 300, y + 22, { t, d: 0.4, tone: 'mut', head: false })
      g.box(300, y, 190, 44, `Dependency ${l}`, { t: t + 0.3 })
      g.bub(530, y + 22, { t: t + 0.8, tone: 'ink' })
      g.text(552, y + 27, 'can page you', { t: t + 0.8, cls: 'fade', sm: true, tone: 'mut' })
    })
  }),

  // ── ai-native-development-process ───────────────────────────────────────
  'ai-brief': () => make(290, 'Conventions, boundaries, a definition of done and stop conditions form the brief an agent starts from.', 'The agent works from the brief, not from the whole repo.', (g) => {
    ;['Conventions', 'Boundaries', 'Definition of done', 'Stop conditions'].forEach((l, i) => {
      const y = 24 + i * 62
      g.box(30, y, 210, 46, l, { t: i * 0.35 })
      g.ln(240, y + 23, 318, 143, { t: 1.6 + i * 0.12, d: 0.4, tone: 'mut', head: false })
    })
    g.box(318, 108, 110, 70, 'The brief', { t: 2.1, tone: 'ink' })
    g.ln(428, 143, 500, 143, { t: 2.6, d: 0.4, head: true, tone: 'mut' })
    g.box(500, 108, 190, 70, 'Agent\nempty context', { t: 3.0 })
    g.text(595, 210, 'starts every task with nothing', { t: 3.5, a: 'middle', sm: true, tone: 'mut' })
  }),
  'ai-gate': () => make(260, 'The agent proposes a plan, a person approves it, and credentials, payments and privacy changes stay behind a stop-and-ask line.', 'The agent proposes. The human decides.', (g) => {
    ;[['Agent', 'writes a plan'], ['The plan', 'editable, reviewed'], ['A person', 'approves'], ['Merge', '']].forEach(([a, b], i) => {
      const x = 20 + i * 178
      g.box(x, 40, 150, 70, b ? `${a}\n${b}` : a, { t: i * 0.7, tone: i === 2 ? 'ink' : '' })
      if (i < 3) g.ln(x + 150, 75, x + 178, 75, { t: i * 0.7 + 0.5, d: 0.25, head: true, tone: 'mut' })
    })
    g.ring(194, 34, 162, 82, { t: 2.6 })
    g.box(20, 160, 330, 56, 'Credentials, payments, privacy:\nstop and ask', { t: 3.0, dash: true, tone: 'ink', sub: false })
    g.cross(380, 188, 12, { t: 3.5 })
  }),

  // ── what-a-green-build-does-not-prove ───────────────────────────────────
  'green-claims': () => make(350, 'Five things reported as verified, each struck through and replaced by what was actually true.', 'Five green ticks, five claims that were not what they looked like.', (g) => {
    claims(g, [
      ['The build used the dependency list', 'it compiled the copies on that disk'],
      ['The lock file pins dependencies', 'it pinned branches'],
      ['A push deploys once', 'it deployed twice'],
      ['The release changed something', 'it changed a version string'],
      ['That analytics field is unused', 'the SDK collected it anyway'],
    ], 44, 62)
  }),
  'green-pin': () => make(270, 'A dependency pinned to a branch resolves to different code on two runs; pinned to a revision it resolves to the same code every time.', 'A branch records intent. A revision records a build.', (g) => {
    g.text(170, 24, 'Pinned to a branch', { t: 0, a: 'middle', tone: 'mut', sm: true })
    g.box(50, 60, 240, 50, 'dependency @ main', { t: 0.1 })
    g.ln(130, 110, 90, 170, { t: 0.7, d: 0.4, tone: 'mut', head: true })
    g.ln(210, 110, 250, 170, { t: 1.1, d: 0.4, tone: 'mut', head: true })
    g.box(10, 170, 160, 50, 'run 1: one commit', { t: 1.1, tone: 'ink' })
    g.box(180, 170, 160, 50, 'run 2: another', { t: 1.5, tone: 'ink' })
    g.raw('<line x1="360" y1="20" x2="360" y2="250" class="ln mut"/>')
    g.text(540, 24, 'Pinned to a revision', { t: 2.2, a: 'middle', tone: 'mut', sm: true })
    g.box(420, 60, 240, 50, 'dependency @ revision', { t: 2.3 })
    g.ln(540, 110, 540, 170, { t: 2.9, d: 0.4, tone: 'mut', head: true })
    g.box(450, 170, 180, 50, 'same code, every run', { t: 3.3 })
    g.tick(660, 195, { t: 3.7 })
  }),

  // ── four-gates-that-certified-nothing ───────────────────────────────────
  'gates-claims': () => make(290, 'Four green gates, each answering a different question than the one it was asked: a directory, two thirds of the tests, one build number, a leaked session.', 'Four gates, all green, and what each one actually measured.', (g) => {
    claims(g, [
      ['Lint gate: green', 'it linted a directory'],
      ['Pre-push: TEST SUCCEEDED', 'it ran two thirds of the tests'],
      ['Deploy job: green', 'three uploads, one build number'],
      ['Snapshots: match', 'they matched a leaked session'],
    ], 44, 62)
  }),
  'gates-build-number': () => make(270, 'Three uploads share one build number: Firebase accepts all three and App Store Connect rejects the duplicate.', 'Three uploads, one build number, two very different answers.', (g) => {
    ;[0, 1, 2].forEach((i) => {
      const y = 30 + i * 70
      g.box(30, y, 200, 50, `Upload ${i + 1}\nsame build number`, { t: i * 0.4 })
      g.ln(230, y + 25, 300, y + 25, { t: 1.4 + i * 0.1, d: 0.3, tone: 'mut', head: false })
    })
    g.ln(300, 55, 300, 195, { t: 1.9, d: 0.5, tone: 'mut', head: false })
    g.ln(300, 80, 470, 70, { t: 2.5, d: 0.4, tone: 'mut', head: true })
    g.ln(300, 170, 470, 180, { t: 2.9, d: 0.4, tone: 'mut', head: true })
    g.box(470, 40, 200, 60, 'Firebase\ngives each a release id', { t: 2.9 })
    g.tick(696, 70, { t: 3.4 })
    g.box(470, 150, 200, 60, 'App Store Connect\nrejects the duplicate', { t: 3.3, tone: 'ink' })
    g.cross(696, 180, 10, { t: 3.8 })
  }),

  // ── mvvm-to-viper-part-one ──────────────────────────────────────────────
  'mvvm-absorbs': () => make(330, 'A single view model gradually takes on answer state, send rules, the offline queue, navigation and HTTP calls.', 'Each one arrived as the smallest change, in the file that was already open.', (g) => {
    g.box(250, 20, 220, 290, '', { t: 0 })
    g.text(360, 50, 'The exam view model', { t: 0, a: 'middle', tone: 'mut', sm: true })
    ;['Answer state', 'When an answer may leave', 'Offline queue and retries', 'Navigation through the gate', 'HTTP calls'].forEach((l, i) => {
      const left = i % 2 === 0, y = 74 + i * 46
      const x0 = left ? 20 : 520, x1 = 265
      const chip = `<rect x="${x0}" y="${y}" width="200" height="34" rx="7" class="chip ink"/><text x="${x0 + 100}" y="${y + 22}" text-anchor="middle" class="tx sm">${l}</text>`
      g.mv(chip, x1 - x0, 0, { t: 0.6 + i * 0.8, d: 0.8 })
    })
  }),
  'mvvm-wire': () => make(250, 'The API finish request reaches the screen directly, then a mapper and an entity sit between them.', 'A screen that speaks wire types is authored by someone else’s schema.', (g) => {
    g.text(30, 20, 'Before', { t: 0, sm: true, tone: 'mut' })
    g.box(30, 30, 150, 50, 'API', { t: 0 })
    g.box(540, 30, 150, 50, 'Screen', { t: 0.2 })
    g.ln(180, 55, 540, 55, { t: 0.7, d: 0.8, tone: 'ink', head: true })
    g.text(360, 46, 'the server’s field names, in the UI', { t: 1.4, a: 'middle', sm: true, tone: 'ink' })
    g.text(30, 128, 'After', { t: 2.2, sm: true, tone: 'mut' })
    g.box(30, 138, 120, 50, 'API', { t: 2.2 })
    g.ln(150, 163, 200, 163, { t: 2.7, d: 0.2, head: true, tone: 'mut' })
    g.box(200, 138, 130, 50, 'Mapper', { t: 2.9 })
    g.ln(330, 163, 380, 163, { t: 3.2, d: 0.2, head: true, tone: 'mut' })
    g.box(380, 138, 130, 50, 'Entity', { t: 3.4 })
    g.ln(510, 163, 560, 163, { t: 3.7, d: 0.2, head: true, tone: 'mut' })
    g.box(560, 138, 130, 50, 'Screen', { t: 3.9, tone: 'ink' })
    g.text(360, 226, 'A renamed field now changes one file, not eleven screens.', { t: 4.4, a: 'middle', sm: true, tone: 'mut' })
  }),

  // ── mvvm-to-viper-part-two ──────────────────────────────────────────────
  'viper-forty-three': () => make(300, 'Three targets per feature across eight features plus shared modules adds up to forty-three packages.', 'Three layers per feature became forty-three packages.', (g) => {
    for (let i = 0; i < 43; i++) {
      const c = i % 9, r = Math.floor(i / 9)
      g.raw(`<rect x="${30 + c * 50}" y="${24 + r * 50}" width="36" height="36" rx="7" class="${i < 3 ? 'chip ink' : 'chip'} pop" style="--t:${i < 3 ? i * 0.3 : 1.2 + (i - 3) * 0.05}s"/>`)
    }
    g.text(520, 90, '43', { t: 3.2, cls: 'pop big', tone: 'ink' })
    g.text(520, 124, 'packages, each with its own', { t: 3.4, sm: true, tone: 'mut' })
    g.text(520, 146, 'repo, manifest, lock row', { t: 3.5, sm: true, tone: 'mut' })
    g.text(520, 168, 'and CI path', { t: 3.6, sm: true, tone: 'mut' })
  }),
  'viper-bill': () => make(280, 'Per feature, three repositories, manifests, lock rows and CI paths versus one of each.', 'Same compiler walls, a third of the bookkeeping.', (g) => {
    g.text(330, 22, 'Three packages', { t: 0, a: 'middle', tone: 'mut', sm: true })
    g.text(560, 22, 'One package', { t: 0, a: 'middle', tone: 'mut', sm: true })
    ;['Repositories', 'Manifests', 'Lock rows', 'CI paths'].forEach((l, i) => {
      const y = 62 + i * 58, t = 0.3 + i * 0.5
      g.text(30, y + 5, l, { t, cls: 'fade' })
      ;[0, 1, 2].forEach((k) => g.bub(290 + k * 26, y, { t: t + k * 0.12 }))
      g.bub(560, y, { t: t + 0.5, tone: 'ink' })
    })
  }),

  // ── mvvm-to-viper-part-three ────────────────────────────────────────────
  'viper-nineteen': () => make(300, 'Forty-three packages merge down to nineteen, one per feature.', 'Forty-three packages down to nineteen.', (g) => {
    g.gone(() => {
      for (let i = 0; i < 43; i++) g.raw(`<rect x="${30 + (i % 9) * 26}" y="${30 + Math.floor(i / 9) * 26}" width="18" height="18" rx="4" class="chip"/>`)
    }, 2.4)
    g.text(150, 190, '43', { t: 0, a: 'middle', cls: 'pop big' })
    g.ln(290, 100, 400, 100, { t: 1.4, d: 0.6, head: true, tone: 'ink' })
    for (let i = 0; i < 19; i++) g.raw(`<rect x="${440 + (i % 5) * 50}" y="${30 + Math.floor(i / 5) * 50}" width="36" height="36" rx="7" class="chip ink pop" style="--t:${2.6 + i * 0.07}s"/>`)
    g.text(565, 272, '19', { t: 4.2, a: 'middle', cls: 'pop big', tone: 'ink' })
  }),
  'viper-owner': () => make(300, 'Every layer had an owner except the screen, until a presenter and a router took it.', 'Clean fixed the data layer. The screen was the last unowned thing.', (g) => {
    rows(g, [
      ['Entities', 'domain'],
      ['Use cases', 'six interactors, one rule each'],
      ['Data', 'repository and mappers'],
    ], 34, 48, { dt: 0.5, bx: 200 })
    g.bub(40, 178, { on: false, tone: 'ink' })
    g.text(66, 183, 'The screen', { t: 2.0, cls: 'fade' })
    g.text(200, 183, 'view state, orchestration and navigation, all in one file', { t: 2.1, cls: 'fade', sm: true, tone: 'mut' })
    g.ring(26, 156, 668, 44, { t: 2.5 })
    g.bub(40, 238, { t: 3.6 })
    g.text(66, 243, 'Presenter', { t: 3.4, cls: 'fade' })
    g.text(200, 243, 'renamed from view model, so rules stop landing in it', { t: 3.5, cls: 'fade', sm: true, tone: 'mut' })
    g.bub(40, 282, { t: 4.2 })
    g.text(66, 287, 'Router', { t: 4.0, cls: 'fade' })
    g.text(200, 287, 'one question: where does this button go', { t: 4.1, cls: 'fade', sm: true, tone: 'mut' })
  }),

  // ── exam-mode-one-screen-earlier ────────────────────────────────────────
  'exam-lock-moves': () => make(290, 'The assessment lock moves from inside the paper to a preparation step before it.', 'The lock did not get stronger. It moved one screen earlier.', (g) => {
    const row = (y, names, t0) => {
      const w = 600 / names.length - 14
      names.forEach((n, i) => {
        const x = 100 + i * (w + 14)
        g.box(x, y, w, 52, n, { t: t0 + i * 0.15, sub: false, tone: n.startsWith('Activate') ? 'ink' : '' })
        if (i) g.ln(x - 14, y + 26, x, y + 26, { t: t0 + i * 0.15, d: 0.15, tone: 'mut', head: false })
      })
      return w
    }
    g.text(30, 72, 'Before', { t: 0, sm: true, tone: 'mut' })
    const w1 = row(46, ['Welcome', 'Location', 'Ready', 'Paper'], 0)
    g.gone(() => g.lock(100 + 3 * (w1 + 14) + w1 / 2, 36, { t: 1.0 }), 2.8)
    g.text(540, 120, 'questions already on screen', { t: 1.2, a: 'middle', sm: true, tone: 'ink' })
    g.text(30, 208, 'After', { t: 2.8, sm: true, tone: 'mut' })
    const w2 = row(182, ['Welcome', 'Location', 'Activate\nexam mode', 'Ready', 'Paper'], 2.8)
    g.lock(100 + 2 * (w2 + 14) + w2 / 2, 172, { t: 4.0 })
    g.text(360, 268, 'The lock starts before the paper exists.', { t: 4.4, a: 'middle', sm: true, tone: 'mut' })
  }),
  'exam-blocked': () => make(312, 'Two blocked screens share one layout but carry different words: a server verdict, and the app’s own lock not running.', 'One layout, two claims. Sharing the words made both screens wrong.', (g) => {
    const panel = (x, title, l1, l2, note, tone) => {
      g.box(x, 20, 300, 272, '', { t: 0 })
      g.raw(`<circle cx="${x + 150}" cy="70" r="20" class="bx ${tone}"/>`)
      g.text(x + 150, 135, title, { t: 1.0, a: 'middle', lg: true, tone })
      g.text(x + 150, 168, l1, { t: 1.5, a: 'middle', sm: true, tone: 'mut' })
      g.text(x + 150, 188, l2, { t: 1.5, a: 'middle', sm: true, tone: 'mut' })
      g.box(x + 70, 206, 160, 40, 'Reload assessment', { t: 0.4, sub: false })
      g.text(x + 150, 272, note, { t: 2.2, a: 'middle', sm: true, tone })
    }
    panel(30, 'Assessment blocked', 'The system detected activity', 'that breaks the rules.', 'a verdict about a person', 'ink')
    panel(390, 'Activate exam mode', 'Exam mode is not running', 'on this device.', 'a fact about the device', '')
  }),

  // ── what-a-year-of-ai-native-ios-still-cant-prove ───────────────────────
  'year-file': () => make(330, 'Three tool instruction files point at one AGENTS.md, which later grows an 18 KB copy of the docs it points to.', 'One file every tool reads, until it starts restating the docs it points to.', (g) => {
    ;['CLAUDE.md', 'GEMINI.md', 'Copilot instructions'].forEach((l, i) => {
      const y = 30 + i * 82
      g.box(20, y, 190, 48, l, { t: i * 0.3 })
      g.ln(210, y + 24, 300, 158, { t: 1.2 + i * 0.12, d: 0.4, tone: 'mut', head: false })
    })
    g.box(300, 130, 150, 56, 'AGENTS.md', { t: 1.9, tone: 'ink' })
    g.ln(450, 158, 540, 158, { t: 2.6, d: 0.4, tone: 'mut', head: true })
    g.box(540, 130, 150, 56, 'Design docs', { t: 2.9 })
    g.ln(375, 186, 375, 262, { t: 3.6, d: 0.5, tone: 'ink', head: false, dash: true })
    g.ln(375, 262, 615, 262, { t: 4.0, d: 0.7, tone: 'ink', head: false, dash: true })
    g.ln(615, 262, 615, 190, { t: 4.6, d: 0.4, tone: 'ink', head: true, dash: true })
    g.text(375, 300, 'at 18 KB it stopped pointing and started summarising', { t: 4.9, a: 'middle', sm: true, tone: 'ink' })
  }),
  'year-rules': () => make(260, 'Three rules routed to enforcement: the secret scan and SwiftLint land in pre-commit, while a paragraph in the conventions file was violated twice and became a script.', 'The rule that stayed prose is the one that drifted.', (g) => {
    ;[['Secret scan', 'pre-commit', true], ['SwiftLint', 'pre-commit', true], ['“Write the merge request like this”', 'a paragraph in the conventions file', false]].forEach(([a, b, ok], i) => {
      const y = 28 + i * 70, t = i * 0.9
      g.box(20, y, 280, 50, a, { t, sub: false })
      g.ln(300, y + 25, 380, y + 25, { t: t + 0.4, d: 0.3, tone: 'mut', head: true })
      g.box(380, y, 290, 50, b, { t: t + 0.7, sub: false, tone: ok ? '' : 'ink' })
      ok ? g.tick(690, y + 25, { t: t + 1.1 }) : g.cross(695, y + 25, 10, { t: t + 1.1 })
    })
    g.text(380, 252, 'Violated twice: now a script.', { t: 3.6, tone: 'ink', sm: true })
  }),
  'year-roles': () => make(250, 'Architect, reviewer, qa and fixer in a chain, with qa unable to edit files and the fixer unable to push.', 'The roles are real because the limits are.', (g) => {
    ;['Architect\nplans', 'Reviewer\nreads', 'qa\ntests', 'Fixer\nrepairs'].forEach((l, i) => {
      const x = 20 + i * 178
      g.box(x, 40, 150, 70, l, { t: i * 0.5 })
      if (i < 3) g.ln(x + 150, 75, x + 178, 75, { t: i * 0.5 + 0.3, d: 0.25, tone: 'mut', head: true })
    })
    g.ln(451, 110, 451, 150, { t: 2.2, d: 0.3, tone: 'mut', head: false })
    g.box(381, 150, 140, 40, 'cannot edit files', { t: 2.5, tone: 'ink', sub: false })
    g.cross(541, 170, 9, { t: 2.9 })
    g.ln(629, 110, 629, 150, { t: 3.3, d: 0.3, tone: 'mut', head: false })
    g.box(570, 150, 118, 40, 'cannot push', { t: 3.6, tone: 'ink', sub: false })
    g.cross(706, 170, 9, { t: 4.0 })
  }),
  // ── an-audit-week-on-a-shipping-ios-app ─────────────────────────────────
  'audit-ladder': () => make(352, 'An audit ranked by consequence: first what can lose a student’s work or lock them out, then what can fail quietly later, then what is slow, flaky or untidy.', 'Ranked by what a failure costs, not by how long the fix takes.', (g) => {
    ;[
      ['Lose work, or lock someone out', ['A queued answer survives a logout', 'A keychain read retries after unlock', 'Crash reporting in every build']],
      ['Fail quietly later', ['Main-actor isolation by default', 'Architecture rules enforced in lint', 'Unused dependencies and permissions removed', 'A coverage gate that can fail']],
      ['Slow, flaky or untidy', ['Navigation re-renders only what changed', 'Tests that wait for events, not clocks']],
    ].forEach(([tier, items], i) => {
      const y = 24 + [0, 112, 252][i], t = i * 1.6
      g.box(30, y, 250, 56, tier, { t, tone: i === 0 ? 'ink' : '', sub: false })
      items.forEach((it, k) => {
        g.bub(318, y + 14 + k * 24, { t: t + 0.5 + k * 0.25, tone: i === 0 ? 'ink' : '' })
        g.text(340, y + 19 + k * 24, it, { t: t + 0.5 + k * 0.25, cls: 'fade', sm: true })
      })
    })
  }),
  'audit-binary': () => make(300, 'Keeping a debugging library out of the shipping app took three attempts: compile out the calls, move it into its own framework, then fix the archive build that the move broke.', 'Compiling the calls out was not the same as shipping without the library.', (g) => {
    ;[
      ['Compile calls out of Production', 'the library stayed linked; its symbols shipped', false],
      ['Move it into its own framework', 'only Dev and Staging embed it; Production has none', true],
      ['Archive the app', 'a copied symlink dangled and signing failed', false],
      ['Copy the framework, not the link', 'archives build and sign again', true],
    ].forEach(([a, b, ok], i) => {
      const y = 34 + i * 70, t = i * 1.1
      g.box(20, y, 250, 50, a, { t, sub: false })
      g.ln(270, y + 25, 304, y + 25, { t: t + 0.4, d: 0.25, tone: 'mut', head: true })
      g.text(316, y + 30, b, { t: t + 0.7, cls: 'fade', sm: true })
      ok ? g.tick(700, y + 24, { t: t + 1.0 }) : g.cross(702, y + 24, 9, { t: t + 1.0 })
    })
  }),
  'audit-settle': () => make(260, 'A fixed sleep guesses when a reply lands; waiting for the request and then for in-flight work to reach zero does not.', 'Wait for the event. Keep the sleep only where no event exists.', (g) => {
    g.text(30, 28, 'A fixed wait', { t: 0, sm: true, tone: 'mut' })
    g.grow(30, 40, 500, 26, { t: 0.2, d: 1.2 })
    g.ring(26, 34, 508, 38, { t: 1.6 })
    g.text(550, 59, 'a guess', { t: 1.8, tone: 'ink', sm: true })
    g.text(30, 128, 'Wait for the request, then settle', { t: 2.4, sm: true, tone: 'mut' })
    ;[['request\nmade', 0], ['in flight\n1', 1], ['in flight\n0', 2]].forEach(([l, i]) => {
      const x = 30 + i * 200
      g.box(x, 142, 150, 56, l, { t: 2.6 + i * 0.7, tone: i === 2 ? 'ink' : '' })
      if (i < 2) g.ln(x + 150, 170, x + 200, 170, { t: 2.9 + i * 0.7, d: 0.3, tone: 'mut', head: true })
    })
    g.tick(640, 170, { t: 4.8 })
    g.text(360, 236, 'Where no request exists yet, the wait stays. Settling on nothing proves nothing.', { t: 5.0, a: 'middle', sm: true, tone: 'mut' })
  }),
}
export { W }
