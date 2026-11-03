import './styles.css'

/* Everything here is decoration or convenience. With JS off, or reduced motion on,
   the page is already complete: render.js emitted the final content. */
const root = document.documentElement
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches
const $ = (s, el = document) => el.querySelector(s)
const $$ = (s, el = document) => [...el.querySelectorAll(s)]

/* scroll progress + parallax value, one rAF per scroll */
let raf = 0
const onScroll = () => {
  cancelAnimationFrame(raf)
  raf = requestAnimationFrame(() => {
    const h = root.scrollHeight - innerHeight
    root.style.setProperty('--scroll', h > 0 ? String(scrollY / h) : '0')
    const rail = $('.rail')
    if (rail) {
      const r = rail.getBoundingClientRect()
      const p = Math.min(1, Math.max(0, (innerHeight * 0.7 - r.top) / r.height))
      rail.style.setProperty('--p', String(p))
    }
  })
}
addEventListener('scroll', onScroll, { passive: true })
onScroll()

/* quick-jump palette: "/" or Cmd/Ctrl+K */
const dlg = $('#cmd')
const input = $('input', dlg)
const items = $$('li', dlg)
const open = () => { dlg.showModal(); input.value = ''; filter(); input.focus() }
const filter = () => {
  const q = input.value.trim().toLowerCase()
  items.forEach((li) => { li.hidden = !!q && !li.textContent.toLowerCase().includes(q) })
}
input.addEventListener('input', filter)
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') $$('li:not([hidden]) a', dlg)[0]?.click()
})
dlg.addEventListener('click', (e) => { if (e.target === dlg || e.target.closest('a')) dlg.close() })
$('[data-cmd]').addEventListener('click', open)
addEventListener('keydown', (e) => {
  const typing = /input|textarea/i.test(document.activeElement?.tagName)
  if ((e.key === '/' && !typing) || ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k')) {
    e.preventDefault()
    dlg.open ? dlg.close() : open()
  }
})

if (!calm) {
  /* pointer: hero light, deck tilt, card spotlight, magnetic mail link */
  const deck = $('.deck')
  const mail = $('[data-magnet]')
  addEventListener('pointermove', (e) => {
    root.style.setProperty('--mx', `${e.clientX}px`)
    root.style.setProperty('--my', `${e.clientY}px`)
    if (deck) {
      deck.style.setProperty('--rx', ((e.clientX / innerWidth) * 2 - 1).toFixed(3))
      deck.style.setProperty('--ry', ((e.clientY / innerHeight) * 2 - 1).toFixed(3))
    }
    const el = e.target.closest?.('.panel, .fact, .rows a')
    if (el) {
      const r = el.getBoundingClientRect()
      el.style.setProperty('--px', `${e.clientX - r.left}px`)
      el.style.setProperty('--py', `${e.clientY - r.top}px`)
    }
    if (mail) {
      const r = mail.getBoundingClientRect()
      const dx = e.clientX - (r.left + r.width / 2)
      const dy = e.clientY - (r.top + r.height / 2)
      const near = Math.hypot(dx, dy) < 260
      mail.style.transform = near ? `translate(${dx * 0.08}px, ${dy * 0.18}px)` : ''
    }
  }, { passive: true })

  /* count-up: the HTML already holds the final number */
  const count = (el) => {
    const { pre, to, post } = el.dataset
    const end = parseFloat(to)
    const dec = (to.split('.')[1] || '').length
    const from = to.length === 4 && !dec ? end - 40 : 0 // a year rolls, it does not start at 0
    const t0 = performance.now()
    const tick = (t) => {
      const k = Math.max(0, Math.min(1, (t - t0) / 1100))
      el.textContent = `${pre}${(from + (end - from) * (1 - (1 - k) ** 3)).toFixed(dec)}${post}`
      if (k < 1) requestAnimationFrame(tick)
      else el.textContent = `${pre}${to}${post}`
    }
    requestAnimationFrame(tick)
  }

  /* typed "now" line */
  const typed = $('[data-type]')
  if (typed) {
    const full = typed.dataset.type
    let n = 0
    typed.textContent = ''
    const id = setInterval(() => {
      typed.textContent = full.slice(0, ++n)
      if (n >= full.length) clearInterval(id)
    }, 26)
  }

  /* reveal on scroll, armed only now so a failed script never hides content */
  const targets = $$('.fact, .panel, .rows li, .rail li, .elsewhere > div, .contact > *, .sec__title')
  const io = new IntersectionObserver((es) => {
    for (const e of es) {
      if (!e.isIntersecting) continue
      e.target.classList.add('in')
      const c = $('[data-to]', e.target) || (e.target.dataset.to ? e.target : null)
      if (c) count(c)
      io.unobserve(e.target)
    }
  }, { threshold: 0.12 })
  targets.forEach((el, i) => { el.style.setProperty('--d', `${(i % 4) * 70}ms`); el.classList.add('arm'); io.observe(el) })
  setTimeout(() => targets.forEach((el) => el.classList.add('in')), 2500) // safety net
}
