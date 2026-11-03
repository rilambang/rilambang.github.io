// The whole site, from nothing: posts (markdown) + figures + content -> docs/. No dependencies.
import fs from 'node:fs'
import path from 'node:path'
import { ME, FACTS, WORK, ROLES, ALSO, REPOS, CERTS, CONTACT } from './content.mjs'
import { figures } from './figures.mjs'

const HERE = import.meta.dirname
const OUT = path.resolve(HERE, '..', 'docs')
const SITE = 'https://rilambang.github.io'
const sources = JSON.parse(fs.readFileSync(path.join(HERE, 'sources.json'), 'utf8'))
// publication order, oldest first; the pager reads in this order, the index newest first
const ORDER = ['kiosk-and-assessment-apps', 'splitting-an-app-into-local-packages', 'build-time-is-a-dependency-graph-problem',
  'uikit-to-swiftui-without-a-rewrite', 'a-design-system-is-a-review-policy', 'how-i-review-ios-pull-requests',
  'the-ios-stack-i-actually-reach-for', 'ai-native-development-process', 'what-a-green-build-does-not-prove',
  'four-gates-that-certified-nothing', 'mvvm-to-viper-part-one', 'mvvm-to-viper-part-two', 'mvvm-to-viper-part-three',
  'exam-mode-one-screen-earlier', 'what-a-year-of-ai-native-ios-still-cant-prove', 'an-audit-week-on-a-shipping-ios-app']

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

// ── markdown subset: ## h2, paragraphs, - lists, > quotes, ``` code, ::fig id ─────────
const inline = (s) => {
  const codes = []
  s = s.replace(/`([^`]+)`/g, (_, c) => `\u0000${codes.push(c) - 1}\u0000`)
  s = esc(s).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/(^|[^*])\*([^*]+)\*/g, '$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
  return s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${esc(codes[i])}</code>`)
}

function render(md, slug) {
  const lines = md.split('\n'), out = []
  let figs = 0, i = 0
  while (i < lines.length) {
    const l = lines[i]
    if (!l.trim()) { i++; continue }
    if (l.startsWith('```')) {
      const code = []; i++
      while (i < lines.length && !lines[i].startsWith('```')) code.push(lines[i++])
      i++; out.push(`<pre><code>${esc(code.join('\n'))}</code></pre>`); continue
    }
    if (l.startsWith('::fig ')) {
      const id = l.slice(6).trim(), f = figures[id]
      if (!f) throw new Error(`${slug}: unknown figure "${id}"`)
      const r = f(); figs++
      out.push(`<figure class="fig"><div class="fig__frame"><svg viewBox="0 0 720 ${r.h}" role="img" aria-label="${esc(r.alt)}">${r.svg}</svg></div>` +
        `<figcaption><span>${esc(r.cap)}</span><button type="button" class="fig__replay" hidden>Replay</button></figcaption></figure>`)
      i++; continue
    }
    if (l.startsWith('## ')) { out.push(`<h2>${inline(l.slice(3))}</h2>`); i++; continue }
    if (l.startsWith('> ')) {
      const q = []; while (i < lines.length && lines[i].startsWith('> ')) q.push(lines[i++].slice(2))
      out.push(`<blockquote><p>${inline(q.join(' '))}</p></blockquote>`); continue
    }
    if (/^- /.test(l)) {
      const items = []
      while (i < lines.length && lines[i].trim()) {
        if (/^- /.test(lines[i])) items.push(lines[i].slice(2)); else items[items.length - 1] += ' ' + lines[i].trim()
        i++
      }
      out.push(`<ul>${items.map((t) => `<li>${inline(t)}</li>`).join('')}</ul>`); continue
    }
    const p = []
    while (i < lines.length && lines[i].trim() && !/^(## |- |> |```|::fig )/.test(lines[i])) p.push(lines[i++])
    out.push(`<p>${inline(p.join(' '))}</p>`)
  }
  if (!figs) throw new Error(`${slug}: every article needs at least one figure`)
  return out.join('\n')
}

function loadPost(slug) {
  const raw = fs.readFileSync(path.join(HERE, 'posts', `${slug}.md`), 'utf8')
  const m = raw.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/)
  const meta = Object.fromEntries(m[1].split('\n').map((l) => [l.slice(0, l.indexOf(':')).trim(), l.slice(l.indexOf(':') + 1).trim()]))
  const words = m[2].replace(/::fig .*/g, '').split(/\s+/).length
  return { slug, ...meta, body: render(m[2], slug), minutes: Math.max(1, Math.round(words / 220)) }
}
const POSTS = ORDER.map(loadPost)
const NEWEST = [...POSTS].reverse()

// ── page shell ──────────────────────────────────────────────────────────────────────
const FONTS = 'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400..800&family=JetBrains+Mono:wght@400&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..650;1,8..60,400&display=swap'
const page = ({ title, desc, url, depth, body, type = 'website', ld = '' }) => {
  const b = depth ? '../' : './'
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>${esc(title)}</title>
<meta name="description" content="${esc(desc)}">
<meta name="author" content="${esc(ME.name)}">
<link rel="canonical" href="${url}">
<meta name="theme-color" content="#f9eff2" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#1f0914" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="${type}">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${url}">
<meta property="og:image" content="${SITE}/og.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="me" href="https://github.com/rilambang"><link rel="me" href="https://x.com/rilambang">
<link rel="alternate" type="application/rss+xml" title="Writing" href="${SITE}/feed.xml">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='7' fill='%237a1c3a'/><circle cx='16' cy='16' r='7' fill='%23ffd9e2'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="${FONTS}">
<link rel="stylesheet" href="${b}assets/style.css">
${ld}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><a class="top__name" href="${b}">${esc(ME.name)}</a>
<nav aria-label="Main"><a href="${b}#work">Work</a><a href="${b}blog/">Writing</a><a href="${b}#path">Path</a><a href="${b}#contact">Contact</a></nav></header>
${body}
<script src="${b}assets/site.js" defer></script>
</body>
</html>
`
}

// ── home ────────────────────────────────────────────────────────────────────────────
// The name field of an answer sheet: one column per letter, A to Z down, the right one filled.
function nameSheet(name) {
  const cols = name.length, px = 26, py = 17, top = 62, w = cols * px + 62, h = top + 26 * py + 34
  let s = `<svg class="sheet" viewBox="0 0 ${w} ${h}" aria-hidden="true"><rect x="1" y="1" width="${w - 2}" height="${h - 2}" rx="12" class="sheet__paper"/>`
  s += `<text x="24" y="26" class="sheet__t">NAMA</text>`
  for (let r = 0; r < 26; r++) s += `<rect x="${w - 17}" y="${top + r * py - 3}" width="9" height="5" class="sheet__mark"/>`
  ;[...name].forEach((ch, c) => {
    const cx = 30 + c * px, hit = ch.charCodeAt(0) - 65
    s += `<text x="${cx}" y="50" text-anchor="middle" class="sheet__w">${ch}</text>`
    for (let r = 0; r < 26; r++) {
      const cy = top + r * py
      s += `<circle cx="${cx}" cy="${cy}" r="6.4" class="sheet__b"/><text x="${cx}" y="${cy + 2.6}" text-anchor="middle" class="sheet__l">${String.fromCharCode(65 + r)}</text>`
      if (r === hit) s += `<circle cx="${cx}" cy="${cy}" r="6.6" class="sheet__f" style="--t:${(0.5 + c * 0.32).toFixed(2)}s"/>`
    }
  })
  return s + '</svg>'
}

const work = (w) => `<article class="work"><div class="work__text"><h3>${esc(w.name)}</h3>
<p class="work__meta">${esc(w.year)}, ${esc(w.role)}</p><p>${esc(w.line)}</p>
<p class="work__tags">${w.tags.map(esc).join(', ')}</p><a href="${esc(w.store)}" target="_blank" rel="noreferrer">See ${w.also ? esc(w.name.split(" and ")[0]) + " " : "it "}on the App Store</a>${w.also ? ` <a href="${esc(w.also.store)}" target="_blank" rel="noreferrer">See ${esc(w.also.name)} on the App Store</a>` : ""}</div>
<div class="work__shots">${w.shots.map((s, i) => `<img src="assets/shots/${s}" alt="${esc(w.also && i >= 2 ? w.also.name : w.name.split(" and ")[0])} screenshot ${(i % 2) + 1}" width="360" height="640" loading="lazy" decoding="async">`).join('')}</div></article>`

const home = page({
  title: `${ME.name}, iOS engineer`,
  desc: `${ME.name}, iOS engineer in Jakarta. Nine years of mobile: React Native, then UIKit and SwiftUI across Telkom's flagship apps. Leads iOS for PIJAR.`,
  url: `${SITE}/`, depth: 0,
  ld: `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org', '@type': 'Person', name: ME.name, alternateName: ['Ilham Rilambang'], jobTitle: 'iOS Engineer',
    worksFor: { '@type': 'Organization', name: 'Telkom Indonesia' }, url: SITE + '/', image: `${SITE}/og.png`,
    address: { '@type': 'PostalAddress', addressLocality: 'Jakarta', addressCountry: 'ID' },
    sameAs: ME.links.map((l) => l.url), knowsAbout: ['Swift', 'SwiftUI', 'UIKit', 'Clean Architecture', 'iOS'],
  })}</script>\n`,
  body: `<main id="main">
<section class="hero">
<div class="hero__text">
<h1>Nine years of mobile. Now I lead iOS.</h1>
<p class="hero__lede">I started in React Native in 2017, led a platform team, then went native: UIKit, then SwiftUI, across Telkom's flagship apps. Today I lead iOS for PIJAR, an exam app for schools. One habit throughout: ship it, and leave the team able to ship without me.</p>
<p class="hero__now">Right now: ${esc(ME.now)}</p>
<p class="hero__links"><a class="hero__mail" href="mailto:${esc(ME.email)}">${esc(ME.email)}</a>${ME.links.map((l) => `<a href="${esc(l.url)}" target="_blank" rel="noreferrer">${esc(l.label)}</a>`).join('')}</p>
</div>
${nameSheet('RILAMBANG')}
</section>

<section class="facts" aria-label="At a glance"><dl>${FACTS.map((f) => `<div><dt>${esc(f.figure)}</dt><dd>${esc(f.label)}</dd></div>`).join('')}</dl></section>

<section class="block" id="work"><h2>Work</h2>${WORK.map(work).join('')}</section>

<section class="block" id="writing"><h2>Writing</h2>
<p class="block__lede">Notes from shipping iOS: what broke, what I changed, and what I would do again. Every one has a drawing that moves.</p>
<ul class="posts">${NEWEST.slice(0, 5).map((p) => `<li><a href="blog/${p.slug}.html"><strong>${esc(p.title)}</strong><span>${esc(p.summary)}</span></a></li>`).join('')}</ul>
<p><a class="more" href="blog/">All ${POSTS.length} pieces</a></p></section>

<section class="block" id="path"><h2>Path</h2>
<ol class="roles">${ROLES.map((r) => `<li><span>${esc(r.span)}</span><strong>${esc(r.role)}</strong><em>${esc(r.where)}</em></li>`).join('')}</ol>
<div class="also"><div><h3>Also shipped</h3><ul>${ALSO.map((a) => `<li><a href="${esc(a.url)}" target="_blank" rel="noreferrer">${esc(a.name)}</a></li>`).join('')}</ul></div>
<div><h3>Open source</h3><ul>${REPOS.map((r) => `<li><a href="${esc(r.url)}" target="_blank" rel="noreferrer">${esc(r.name)}</a> <em>${esc(r.lang)}</em></li>`).join('')}</ul></div></div></section>

<section class="contact" id="contact"><h2>${esc(CONTACT.heading)}</h2><p>${esc(CONTACT.body)}</p>
<a class="contact__mail" href="mailto:${esc(ME.email)}">${esc(ME.email)}</a></section>
</main>
<footer class="foot"><span>${esc(ME.name)}, ${esc(ME.where)}. ${CERTS.map((c) => `<a href="${esc(c.url)}" target="_blank" rel="noreferrer">${esc(c.name)}</a>`).join(', ')}.</span>
<span>${ME.links.map((l) => `<a href="${esc(l.url)}" target="_blank" rel="noreferrer">${esc(l.label)}</a>`).join(', ')}</span></footer>`,
})

// ── blog ────────────────────────────────────────────────────────────────────────────
const index = page({
  title: `Writing, ${ME.name}`,
  desc: 'Notes on the craft of iOS: platform rules, modularisation, build health, migration, review practice and the agent workflow I run.',
  url: `${SITE}/blog/`, depth: 1,
  body: `<main id="main" class="index"><h1>Writing</h1>
<p class="index__lede">${POSTS.length} pieces on iOS, newest first. No client names, no internal details and no unpublished numbers: everything here can be checked against a public source. Each one has at least one drawing that plays as you reach it.</p>
<ol class="list">${NEWEST.map((p) => `<li><a href="${p.slug}.html"><h2>${esc(p.title)}</h2><p>${esc(p.summary)}</p><span>${esc(p.tag)}, ${p.minutes} min read</span></a></li>`).join('')}</ol></main>`,
})

const article = (p, i) => {
  const prev = POSTS[i - 1], next = POSTS[i + 1]
  const src = (sources[p.slug] || []).map(([t, u]) => `<li><a href="${esc(u)}" target="_blank" rel="noreferrer">${esc(t)}</a></li>`).join('')
  return page({
    title: `${p.title}, ${ME.name}`, desc: p.summary, url: `${SITE}/blog/${p.slug}.html`, depth: 1, type: 'article',
    body: `<div class="progress" aria-hidden="true"></div><main id="main"><article class="post">
<header class="post__head"><p class="post__tag">${esc(p.tag)}</p><h1>${esc(p.title)}</h1><p class="post__sum">${esc(p.summary)}</p><p class="post__meta">${p.minutes} min read</p></header>
${p.body}
<aside class="sources"><h2>Sources</h2><ul>${src}</ul></aside>
<p class="post__foot">Written from experience shipping iOS apps. No client names, no internal details, no unpublished numbers.</p>
<nav class="pager" aria-label="More writing">${prev ? `<a href="${prev.slug}.html"><span>Earlier</span>${esc(prev.title)}</a>` : '<i></i>'}${next ? `<a href="${next.slug}.html"><span>Later</span>${esc(next.title)}</a>` : '<i></i>'}</nav>
</article></main>`,
  })
}

// ── write ───────────────────────────────────────────────────────────────────────────
fs.rmSync(OUT, { recursive: true, force: true })
fs.mkdirSync(path.join(OUT, 'blog'), { recursive: true })
fs.cpSync(path.join(HERE, 'assets'), path.join(OUT, 'assets'), { recursive: true })
fs.copyFileSync(path.join(HERE, 'assets', 'og.png'), path.join(OUT, 'og.png'))
fs.writeFileSync(path.join(OUT, 'index.html'), home)
fs.writeFileSync(path.join(OUT, 'blog', 'index.html'), index)
POSTS.forEach((p, i) => fs.writeFileSync(path.join(OUT, 'blog', `${p.slug}.html`), article(p, i)))
fs.writeFileSync(path.join(OUT, 'robots.txt'), `User-agent: *\nAllow: /\nSitemap: ${SITE}/sitemap.xml\n`)
fs.writeFileSync(path.join(OUT, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">` +
  [`${SITE}/`, `${SITE}/blog/`, ...POSTS.map((p) => `${SITE}/blog/${p.slug}.html`)].map((u) => `<url><loc>${u}</loc></url>`).join('') + '</urlset>\n')
fs.writeFileSync(path.join(OUT, 'feed.xml'), `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>${esc(ME.name)}: Writing</title><link>${SITE}/blog/</link><description>Notes on the craft of iOS.</description>` +
  NEWEST.map((p) => `<item><title>${esc(p.title)}</title><link>${SITE}/blog/${p.slug}.html</link><guid>${SITE}/blog/${p.slug}.html</guid><description>${esc(p.summary)}</description></item>`).join('') + '</channel></rss>\n')
console.log(`${POSTS.length} articles, ${POSTS.reduce((n, p) => n + (p.body.match(/class="fig"/g) || []).length, 0)} figures -> docs/`)
