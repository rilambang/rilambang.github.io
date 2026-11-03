import { ME, FACTS, WORK, ROLES, ALSO, REPOS, CERTS, CONTACT, WRITING, STACK } from './data.js'

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
const ext = 'target="_blank" rel="noreferrer"'
const arrow = '<svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true"><path d="M4 12L12 4M12 4H6M12 4v6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
const num = (i) => String(i + 1).padStart(2, '0')

// each word rises out of its own mask; --i staggers them
const words = (text, accent) =>
  text.split(' ').map((w, i) => `<span class="w" style="--i:${i}"><span${w === accent ? ' class="acc"' : ''}>${esc(w)}</span></span>`).join(' ')

const fact = (f) => {
  const m = f.figure.match(/^(\D*)([\d.]+)(.*)$/)
  return `<div class="fact"><strong data-pre="${esc(m[1])}" data-to="${m[2]}" data-post="${esc(m[3])}">${esc(f.figure)}</strong><span>${esc(f.label)}</span></div>`
}

const panel = (w, i) => `
<article class="panel" style="--i:${i}">
  <div class="panel__inner">
    <div class="panel__text">
      <p class="panel__no">${num(i)}<span>${esc(w.year)} · ${esc(w.role)}</span></p>
      <h3>${esc(w.name)}</h3>
      <p class="panel__line">${esc(w.line)}</p>
      <p class="tags">${w.tags.map((t) => `<span>${esc(t)}</span>`).join('')}</p>
      <a class="btn" href="${esc(w.store)}" ${ext}>App Store ${arrow}</a>
    </div>
    <div class="panel__shots">
      ${w.shots.map((s, k) => `<img src="shots/${s}" alt="${esc(w.name)} screenshot ${k + 1}" loading="lazy" decoding="async">`).join('')}
    </div>
  </div>
</article>`

const cmdItems = [
  ['Work', '#work'], ['Writing', '#writing'], ['Path', '#path'], ['Contact', '#contact'],
  ...WRITING.map((w) => [`Read: ${w.title}`, `blog/${w.slug}.html`]),
  ['All writing', 'blog/'],
  [`Email ${ME.email}`, `mailto:${ME.email}`],
  ...ME.links.map((l) => [l.label, l.url]),
]

export function renderPage() {
  return `
<a class="skip" href="#main">Skip to content</a>
<div class="progress" aria-hidden="true"></div>
<div class="field" aria-hidden="true"><i></i><i></i><i></i></div>

<header class="top">
  <a class="top__name" href="#top">${esc(ME.name)}</a>
  <nav aria-label="Sections">
    <a href="#work">Work</a><a href="#writing">Writing</a><a href="#path">Path</a><a href="#contact">Contact</a>
    <button class="kbd" type="button" data-cmd aria-label="Open quick jump menu">Jump <kbd>/</kbd></button>
  </nav>
</header>

<main id="main">
  <section class="hero" id="top">
    <div class="hero__text">
      <p class="eyebrow">${esc(ME.role)} · ${esc(ME.where)}</p>
      <h1 class="hero__title">${words('I ship iOS for products that people depend on.', 'depend')}</h1>
      <p class="hero__blurb">${esc(ME.blurb)}</p>
      <p class="now"><span class="now__dot" aria-hidden="true"></span><span>Now · <span data-type="${esc(ME.now)}">${esc(ME.now)}</span></span></p>
      <p class="hero__cta">
        <a class="btn btn--fill" href="mailto:${esc(ME.email)}">${esc(ME.email)}</a>
        ${ME.links.map((l) => `<a class="btn" href="${esc(l.url)}" ${ext}>${esc(l.label)} ${arrow}</a>`).join('')}
      </p>
    </div>
    <div class="deck" aria-hidden="true">
      ${WORK.map((w, i) => `<div class="deck__card" style="--n:${i}"><img src="shots/${w.shots[0]}" alt="" decoding="async"></div>`).join('')}
    </div>
  </section>

  <section class="facts" aria-label="At a glance">${FACTS.map(fact).join('')}</section>

  <div class="marquee" aria-hidden="true"><div class="marquee__track">${[...STACK, ...STACK].map((t) => `<span>${esc(t)}</span>`).join('')}</div></div>

  <section class="sec" id="work">
    <h2 class="sec__title"><span>01</span> Selected work</h2>
    <div class="stack">${WORK.map(panel).join('')}</div>
  </section>

  <section class="sec" id="writing">
    <h2 class="sec__title"><span>02</span> Writing</h2>
    <ul class="rows">
      ${WRITING.map((w) => `<li><a href="blog/${w.slug}.html"><em>${esc(w.tag)}</em><strong>${esc(w.title)}</strong><span>${esc(w.line)}</span><i>${arrow}</i></a></li>`).join('')}
    </ul>
    <p class="more"><a href="blog/">All 15 pieces ${arrow}</a></p>
  </section>

  <section class="sec" id="path">
    <h2 class="sec__title"><span>03</span> Path</h2>
    <ol class="rail">
      ${ROLES.map((r) => `<li><span class="rail__span">${esc(r.span)}</span><strong>${esc(r.role)}</strong><span class="rail__where">${esc(r.where)}</span></li>`).join('')}
    </ol>
    <div class="elsewhere">
      <div><h3>Also shipped</h3><p>${ALSO.map((a) => `<a href="${esc(a.url)}" ${ext}>${esc(a.name)} ${arrow}</a>`).join('')}</p></div>
      <div><h3>Open source</h3><p>${REPOS.map((r) => `<a href="${esc(r.url)}" ${ext}>${esc(r.name)} <em>${esc(r.lang)}</em> ${arrow}</a>`).join('')}</p></div>
    </div>
  </section>

  <section class="contact" id="contact">
    <p class="eyebrow">04 · Contact</p>
    <h2>${esc(CONTACT.heading)}</h2>
    <p class="contact__body">${esc(CONTACT.body)}</p>
    <a class="contact__mail" href="mailto:${esc(ME.email)}" data-magnet>${esc(ME.email)}</a>
  </section>
</main>

<footer class="foot">
  <span>${esc(ME.name)} — ${esc(ME.where)} · ${CERTS.map((c) => `<a href="${esc(c.url)}" ${ext}>${esc(c.name)}</a>`).join(', ')}</span>
  <span>${ME.links.map((l) => `<a href="${esc(l.url)}" ${ext}>${esc(l.label)}</a>`).join(' · ')}</span>
</footer>

<dialog class="cmd" id="cmd" aria-label="Quick jump">
  <input type="text" placeholder="Jump to…" aria-label="Filter" autocomplete="off">
  <ul>${cmdItems.map(([t, h]) => `<li><a href="${esc(h)}"${h.startsWith('http') ? ` ${ext}` : ''}>${esc(t)}</a></li>`).join('')}</ul>
</dialog>`
}
