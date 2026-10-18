import { useState } from 'react'
import {
  ME, HERO, STATS, APPS, ALSO, TIMELINE, CRAFT, BEFORE, OFFCLOCK, REPOS, CERTS, CONTACT,
} from './data.js'
import { Arrow, Down, Mail } from './icons.jsx'

const repo = (f) => `${import.meta.env.BASE_URL}shots/${f}`.replace(/\/+/g, '/')

/* ─── portrait ─────────────────────────────────────────── */
function Portrait({ src = `${import.meta.env.BASE_URL}me.jpg`, name }) {
  const [broken, setBroken] = useState(false)
  return (
    <div className="portrait">
      {broken ? (
        <div className="portrait__fallback" aria-hidden="true">
          {ME.initials}
          <small>add photo</small>
        </div>
      ) : (
        <img src={src} alt={`${name}, iOS engineer`} onError={() => setBroken(true)} />
      )}
    </div>
  )
}

/* ─── device frame ─────────────────────────────────────── */
const Device = ({ file, alt }) => (
  <div className="device">
    <img src={repo(file)} alt={alt} loading="lazy" decoding="async" />
  </div>
)

export default function App() {
  return (
    <>
      <a className="skip" href="#main">Skip to content</a>

      <nav className="nav">
        <div className="wrap nav__in">
          <a className="brand" href="#top">
            <span className="brand__dot" />
            {ME.short}
          </a>
          <ul className="nav__links">
            <li><a href="#work">Work</a></li>
            <li><a href="#craft">Craft</a></li>
            <li><a href="#life">Life</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </div>
      </nav>

      <main id="main">
        {/* ── hero ── */}
        <header className="hero" id="top">
          <div className="wrap hero__grid">
            <div>
              <span className="eyebrow">{HERO.eyebrow}</span>
              <h1 className="reveal">
                {HERO.headline[0]} <em>{HERO.headline[1]}</em> {HERO.headline[2]}
              </h1>
              <p className="hero__sub prose">{HERO.sub}</p>

              <div className="hero__cta">
                <a className="btn btn--solid" href="#work">
                  See the work <Down />
                </a>
                <a className="btn btn--ghost" href={`mailto:${ME.email}`}>
                  Email me <Mail />
                </a>
              </div>
            </div>

            <div className="hero__art">
              <div className="floating floating--l">
                <img src={repo('pijar-1.webp')} alt="" aria-hidden="true" />
              </div>
              <Portrait name={ME.name} />
              <div className="floating floating--r">
                <img src={repo('indihome-1.webp')} alt="" aria-hidden="true" />
              </div>
            </div>
          </div>
        </header>

        {/* ── proof strip ── */}
        <div className="shipped">
          <div className="wrap shipped__in">
            <p className="shipped__label">Also shipped</p>
            <ul className="shipped__list">
              {ALSO.map((a) => (
                <li key={a.name}>
                  <a href={a.url} target="_blank" rel="noopener noreferrer">{a.name} <Arrow /></a>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* ── the work ── */}
        <section id="work" aria-labelledby="work-h">
          <div className="wrap">
            <span className="eyebrow reveal-lift">01 — The work</span>
            <h2 id="work-h" className="reveal">
              Software that had to hold up.
            </h2>

            <dl className="stats reveal">
              {STATS.map((s) => (
                <div className="stat" key={s.label}>
                  <dt>{s.label}</dt>
                  <dd>{s.figure}<span>{s.unit}</span></dd>
                  <p>{s.note}</p>
                </div>
              ))}
            </dl>

            <div className="apps">
              {APPS.map((a) => (
                <article className="app reveal" key={a.slug}>
                  <div className="app__copy">
                    <div className="app__top">
                      <img src={repo(`${a.slug}-icon.png`)} alt="" aria-hidden="true" />
                      <span className="app__when">{a.year}</span>
                    </div>
                    <h3>{a.name}</h3>
                    <p className="app__blurb">{a.blurb}</p>
                    <ul className="app__points">
                      {a.points.map((p) => <li key={p}><span>{p}</span></li>)}
                    </ul>
                    <div className="app__meta">
                      <a className="btn btn--ghost" href={a.store} target="_blank" rel="noopener noreferrer">
                        App Store <Arrow />
                      </a>
                      <span className="app__when">{a.role}</span>
                    </div>
                  </div>
                  <div className="shots">
                    <Device file={a.shots[0]} alt={`${a.name} on the App Store`} />
                    <Device file={a.shots[1]} alt={`${a.name} screens`} />
                  </div>
                </article>
              ))}
            </div>

            <div className="also reveal">
              <h3>And the rest of it</h3>
              <div className="also__grid">
                {ALSO.map((a) => (
                  <a key={a.name} href={a.url} target="_blank" rel="noopener noreferrer">
                    <span>{a.name}</span>
                    <Arrow />
                  </a>
                ))}
              </div>
            </div>

            {/* career arc */}
            <div className="tl reveal" style={{ marginTop: 'clamp(4rem,10vw,7rem)' }}>
              <h3>The arc</h3>
              <p className="prose" style={{ color: 'var(--ink-2)', marginTop: '.75rem' }}>
                One company, eight years, four different jobs — and each promotion was really a
                different answer to the same question.
              </p>
              <div style={{ marginTop: '2rem' }}>
                {TIMELINE.map((t) => (
                  <div className="tl__row" key={t.role}>
                    <p className="tl__role">{t.role}</p>
                    <p className="tl__note">{t.note}</p>
                    <p className="tl__span">{t.span}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="also reveal" style={{ borderTop: 'none', paddingTop: 0 }}>
              <h3>Open source</h3>
              <p className="prose" style={{ color: 'var(--ink-2)', marginTop: '.75rem' }}>
                Sixteen public repos. The React Native libraries are from 2018; the modularisation
                samples are from 2023, and they are the argument in
                <a href="#craft"> Craft </a> written down in code.
              </p>
              <div className="also__grid">
                {REPOS.map((r) => (
                  <a key={r.name} href={r.url} target="_blank" rel="noopener noreferrer">
                    <span>
                      <b style={{ fontWeight: 500 }}>{r.name}</b>
                      <small style={{ display: 'block', color: 'var(--ink-3)', fontSize: '.8125rem', marginTop: '.2rem' }}>
                        {r.lang} · {r.year}
                      </small>
                    </span>
                    <Arrow />
                  </a>
                ))}
              </div>
            </div>

            <ul className="certs reveal">
              {CERTS.map((c) => (
                <li key={c.name}>
                  <a href={c.url} target="_blank" rel="noopener noreferrer">
                    <Arrow />
                    <span><b>{c.name}</b><small>{c.issuer}</small></span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* ── craft ── */}
        <section id="craft" aria-labelledby="craft-h">
          <div className="wrap">
            <span className="eyebrow reveal-lift">02 — Craft</span>
            <h2 id="craft-h" className="reveal">What I actually believe about this job.</h2>
            <div className="craft-list">
              {CRAFT.map((c) => (
                <div className="craft reveal" key={c.n}>
                  <span className="craft__n">{c.n}</span>
                  <div>
                    <h3>{c.title}</h3>
                    <p className="app__blurb">{c.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── before work ── */}
        <section id="before" aria-labelledby="before-h">
          <div className="wrap">
            <span className="eyebrow reveal-lift">03 — Before</span>
            <h2 id="before-h" className="reveal">Where it started.</h2>
            <dl className="before">
              {BEFORE.map((b) => (
                <div className="before__row reveal" key={b.k}>
                  <dt>{b.k}</dt>
                  <dd>{b.v}</dd>
                </div>
              ))}
            </dl>
          </div>
        </section>

        {/* ── life ── */}
        <section id="life" aria-labelledby="life-h">
          <div className="wrap">
            <span className="eyebrow reveal-lift">04 — Off the clock</span>
            <h2 id="life-h" className="reveal">The parts that are not software.</h2>
            <div className="craft-list">
              {OFFCLOCK.map((o) => (
                <div className="craft reveal" key={o.title}>
                  <span className="craft__n"><Down /></span>
                  <div>
                    <h3>{o.title}</h3>
                    <p className="app__blurb">{o.body}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── contact ── */}
        <section className="contact" id="contact" aria-labelledby="contact-h">
          <div className="wrap">
            <span className="eyebrow reveal-lift" style={{ justifyContent: 'center' }}>05 — Say hello</span>
            <h2 id="contact-h" className="reveal">{CONTACT.heading}</h2>
            <p className="reveal">{CONTACT.body}</p>
            <a className="contact__mail reveal" href={`mailto:${ME.email}`}>{ME.email}</a>
            <div className="contact__links reveal">
              {ME.socials.map((s) => (
                <a className="btn btn--ghost" key={s.label} href={s.url} target="_blank" rel="noopener noreferrer">
                  {s.label} <Arrow />
                </a>
              ))}
            </div>
            <ul className="meta reveal">
              <li>{ME.location}</li>
              <li>{ME.languages.join(' · ')}</li>
            </ul>
          </div>
        </section>
      </main>

      <footer className="foot">
        <div className="wrap foot__in">
          <p>{ME.name} · {ME.title}, {ME.org}</p>
          <p><a href="#top">Back to top ↑</a></p>
        </div>
      </footer>
    </>
  )
}