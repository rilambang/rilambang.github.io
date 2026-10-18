import { useLayoutEffect } from 'react'
import { ME, FACTS, WORK, TENURE, ROLES, ALSO, REPOS, CERTS, CONTACT } from './data.js'

const asset = (f) => `${import.meta.env.BASE_URL}shots/${f}`.replace(/\/+/g, '/')

/* Reveal-on-scroll. Nothing is hidden until JS has armed it and started observing,
   so a failed bundle shows the page, never a blank one. Reduced motion opts out. */
function useReveal() {
  useLayoutEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return
    if (!('IntersectionObserver' in window)) return
    const els = Array.from(document.querySelectorAll('[data-reveal]'))
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue
        e.target.classList.add('in')
        io.unobserve(e.target)
      }
    }, { threshold: 0.08 })
    els.forEach((el, i) => {
      el.style.setProperty('--i', String(i % 4))
      el.dataset.armed = 'true'
      io.observe(el)
    })
    // safety net: if the observer never fires (odd renderer, no paint, headless
    // prerender), reveal everything rather than leave the page blank.
    const t = window.setTimeout(() => els.forEach((el) => el.classList.add('in')), 1200)
    return () => {
      window.clearTimeout(t)
      io.disconnect()
    }
  }, [])
}

const year = (iso) => Number(iso.slice(0, 4)) + (Number(iso.slice(5, 7)) - 1) / 12
const AXIS = [2017, 2027]

const Tenure = () => {
  const pct = (n) => ((n - AXIS[0]) / (AXIS[1] - AXIS[0])) * 100
  return (
    <div className="tenure" data-reveal>
      <div className="tenure__head">
        <span className="tenure__label">First listed</span>
        <span className="tenure__label tenure__label--end">Last update</span>
      </div>
      <ol className="tenure__rows">
        {TENURE.rows.map((r) => {
          const a = year(r.from)
          const b = year(r.to)
          return (
            <li key={r.name}>
              <span className="tenure__name">{r.name}</span>
              <span className="tenure__track">
                <span
                  className={`tenure__bar${r.live ? ' is-live' : ''}`}
                  style={{ left: `${pct(a)}%`, width: `${pct(b) - pct(a)}%` }}
                />
              </span>
              <span className="tenure__years">
                {r.from.slice(0, 4)}–{r.live ? 'now' : r.to.slice(0, 4)}
              </span>
            </li>
          )
        })}
      </ol>
      <div className="tenure__axis" aria-hidden="true">
        {[2017, 2019, 2021, 2023, 2025, 2027].map((y) => (
          <span key={y} style={{ left: `${pct(y)}%` }}>{y}</span>
        ))}
      </div>
      <p className="tenure__note">
        Public App Store listing dates, as of {TENURE.asOf} — {TENURE.source}.
        No account analytics: installs, retention and crash rate are not public.
      </p>
    </div>
  )
}

const Arrow = () => (
  <svg viewBox="0 0 16 16" width="12" height="12" aria-hidden="true">
    <path d="M4 12L12 4M12 4H6M12 4v6" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

export default function App() {
  useReveal()
  return (
    <>
      <a className="skip" href="#main">Skip to content</a>

      <header className="top">
        <div className="top__inner">
          <a className="top__name" href="#top">{ME.name}</a>
          <nav className="top__nav" aria-label="Sections">
            <a href="#work">Work</a>
            <a href="#path">Shipping</a>
            <a href="#roles">Path</a>
            <a href="blog/">Writing</a>
            <a href="#contact">Contact</a>
          </nav>
        </div>
      </header>

      <main id="main">
        <section className="hero" id="top">
          <p className="hero__eyebrow">{ME.role} · {ME.where}</p>
          <h1 className="hero__title">
            I ship iOS for products that<br />
            people depend on.
          </h1>
          <p className="hero__blurb">{ME.blurb}</p>
          <p className="hero__links">
            <a href={`mailto:${ME.email}`}>{ME.email}</a>
            {ME.links.map((l) => (
              <a key={l.label} href={l.url} target="_blank" rel="noreferrer">
                {l.label} <Arrow />
              </a>
            ))}
          </p>
        </section>

        <section className="facts" aria-label="At a glance" data-reveal>
          {FACTS.map((f) => (
            <div className="fact" key={f.figure}>
              <strong>{f.figure}</strong>
              <span>{f.label}</span>
            </div>
          ))}
        </section>

        <section id="work" className="section">
          <h2 className="section__title" data-reveal>Selected work</h2>
          <div className="work">
            {WORK.map((w) => (
              <article className="card" key={w.slug} data-reveal>
                <div className="card__shots">
                  {w.shots.map((s, i) => (
                    <img key={s} src={asset(s)} alt={`${w.name} screenshot ${i + 1}`} loading="lazy" decoding="async" />
                  ))}
                </div>
                <div className="card__body">
                  <p className="card__meta">{w.year} · {w.role}</p>
                  <h3>{w.name}</h3>
                  <p className="card__line">{w.line}</p>
                  <p className="card__tags">{w.tags.map((t) => <span key={t}>{t}</span>)}</p>
                  <a className="card__link" href={w.store} target="_blank" rel="noreferrer">
                    App Store <Arrow />
                  </a>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section id="path" className="section">
          <h2 className="section__title" data-reveal>Shipped, and still shipping</h2>
          <Tenure />
        </section>

        <section id="roles" className="section">
          <h2 className="section__title" data-reveal>Path</h2>
          <ol className="roles" data-reveal>
            {ROLES.map((r) => (
              <li key={r.role}>
                <span className="roles__span">{r.span}</span>
                <span className="roles__role">{r.role}</span>
                <span className="roles__where">{r.where}</span>
              </li>
            ))}
          </ol>

          <div className="grid2">
            <div>
              <h3 className="mini">Also shipped</h3>
              <ul className="links">
                {ALSO.map((a) => (
                  <li key={a.name}>
                    <a href={a.url} target="_blank" rel="noreferrer">{a.name} <Arrow /></a>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="mini">Open source</h3>
              <ul className="links">
                {REPOS.map((r) => (
                  <li key={r.name}>
                    <a href={r.url} target="_blank" rel="noreferrer">{r.name} <Arrow /></a>
                    <em>{r.lang}</em>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <h3 className="mini">Certificates</h3>
          <ul className="links links--row">
            {CERTS.map((c) => (
              <li key={c.name}>
                <a href={c.url} target="_blank" rel="noreferrer">{c.name} <Arrow /></a>
                <em>{c.issuer}</em>
              </li>
            ))}
          </ul>
        </section>

        <section id="contact" className="contact" data-reveal>
          <h2>{CONTACT.heading}</h2>
          <p>{CONTACT.body}</p>
          <a className="contact__mail" href={`mailto:${ME.email}`}>{ME.email}</a>
        </section>
      </main>

      <footer className="foot">
        <span>{ME.name} — {ME.where}</span>
        <span>{ME.links.map((l, i) => (
          <span key={l.label}>
            {i > 0 && ' · '}
            <a href={l.url} target="_blank" rel="noreferrer">{l.label}</a>
          </span>
        ))}</span>
      </footer>
    </>
  )
}
