// Figures play once as they scroll into view. Without JS, or with reduced motion,
// nothing is armed and the finished drawings are simply there.
const calm = matchMedia('(prefers-reduced-motion: reduce)').matches
const figs = [...document.querySelectorAll('.fig')]
if (figs.length && !calm && 'IntersectionObserver' in window) {
  const play = (f) => { f.classList.remove('go'); void f.offsetWidth; f.classList.add('go') }
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { play(e.target); io.unobserve(e.target) }
  }), { threshold: 0.35 })
  figs.forEach((f) => {
    f.classList.add('armed')
    const b = f.querySelector('.fig__replay')
    b.hidden = false
    b.addEventListener('click', () => play(f))
    io.observe(f)
  })
}
const bar = document.querySelector('.progress')
if (bar) {
  const on = () => bar.style.setProperty('--p', String(scrollY / Math.max(1, document.documentElement.scrollHeight - innerHeight)))
  addEventListener('scroll', on, { passive: true }); on()
}
