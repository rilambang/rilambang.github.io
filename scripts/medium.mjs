// Medium handoff — no API, no token, no dependency. Medium closed new API
// integrations in 2021 (Help 213480228: "will not be issuing any new
// integration tokens"), and Import (Help 214550207) is the only official path
// for a new account: paste the live URL, Medium imports, backdates, and sets
// the canonical to the original. This script is just that list, after a build:
// live URL, title/tag/summary for topics, and whether the PNG stills that
// carry over are present.
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(import.meta.dirname, '..')
const SITE_DIR = path.join(ROOT, 'site')
const buildSrc = fs.readFileSync(path.join(SITE_DIR, 'build.mjs'), 'utf8')
const SITE = buildSrc.match(/const SITE = '([^']+)'/)?.[1] ?? 'https://rilambang.github.io'
const orderSrc = buildSrc.match(/const ORDER = \[([\s\S]*?)\]/)?.[1] ?? ''
const ORDER = [...orderSrc.matchAll(/'([^']+)'/g)].map((m) => m[1])
if (!ORDER.length) throw new Error('no ORDER found in site/build.mjs')

const IMPORT_URL = 'https://medium.com/p/import'
// Medium documents no URL-prefill param for Import, so the script hands you
// the page plus one copy-paste URL per post, rather than a guessed ?url= link.
const KNOWN = ['SwiftUI', 'UIKit', 'Swift', 'Combine', 'Xcode', 'MVVM', 'VIPER', 'Coordinator', 'Testing', 'Architecture', 'Migration', 'Modularisation']

function loadPost(slug) {
  const raw = fs.readFileSync(path.join(SITE_DIR, 'posts', `${slug}.md`), 'utf8')
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/)
  const meta = {}
  for (const l of m[1].split('\n')) {
    const i = l.indexOf(':')
    meta[l.slice(0, i).trim()] = l.slice(i + 1).trim()
  }
  const figs = [...m[2].matchAll(/^::fig (\S+)/gm)].map((x) => x[1])
  const missing = figs.filter((id) => !fs.existsSync(path.join(SITE_DIR, 'assets', 'figs', `${id}.png`)))
  const url = `${SITE}/blog/${slug}.html`
  // first tag segment drops the "part x of y" suffix; rest are tech terms the
  // title/summary actually mention, capped at Medium's 5.
  const base = (meta.tag ?? '').split(',')[0].trim()
  const text = `${meta.title ?? ''} ${meta.summary ?? ''}`
  const found = KNOWN.filter((t) => new RegExp(`\\b${t}\\b`, 'i').test(text))
  const tags = []
  for (const t of [base, 'iOS', ...found]) {
    if (t && !tags.some((x) => x.toLowerCase() === t.toLowerCase())) tags.push(t)
    if (tags.length === 5) break
  }
  return { slug, ...meta, url, figs, missing, tags }
}

const only = process.argv.slice(2).filter((a) => !a.startsWith('--'))[0]
const slugs = only ? ORDER.filter((s) => s === only) : ORDER
if (only && !slugs.length) throw new Error(`unknown slug "${only}" — try: npm run medium -- ${ORDER[ORDER.length - 1]}`)

console.log(`Medium Import — ${slugs.length} post${slugs.length === 1 ? '' : 's'} (${ORDER.length} total)`)
console.log(`1. Publish to the site first: npm run build, commit docs/, push. Wait ~1 min until live.`)
console.log(`2. Open ${IMPORT_URL} (Stories > Import a story) and paste one URL below.`)
console.log(`3. Medium backdates and sets the canonical to the live URL — verify the canonical line on the draft.`)
console.log(`4. Copy the topics line, then Publish.\n`)
for (const slug of slugs) {
  const p = loadPost(slug)
  console.log(`${p.url}`)
  console.log(`  ${p.title}`)
  console.log(`  tag: ${p.tag} | topics (max 5): ${p.tags.join(', ')}`)
  console.log(`  summary: ${p.summary}`)
  console.log(`  stills: ${p.missing.length ? `missing ${p.missing.join(', ')} — run npm run stills` : `ok (${p.figs.length} fig${p.figs.length === 1 ? '' : 's'})`}\n`)
}
console.log(`One post only: npm run medium -- <slug>`)
