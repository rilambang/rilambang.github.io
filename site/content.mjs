// ponytail: every word and image on the site lives here. edit this file, not App.jsx.
// PRIVACY: publish only what you'd hand a stranger at a conference.
// DO NOT add: date of birth, national ID (NIK), home address, family, client-side tracking.
// DO NOT add a phone number: a public repo publishes it permanently.

export const ME = {
  name: 'Muhammad Ilham Rilambang',
  initials: 'IR',
  role: 'iOS engineer',
  where: 'Jakarta, Indonesia',
  email: 'rilambang@gmail.com',
  blurb:
    'Nine years of mobile: React Native, UIKit, SwiftUI. I lead iOS for PIJAR at Telkom Indonesia. One habit: ship it and leave the team able to ship without me.',
  links: [
    { label: 'LinkedIn', url: 'https://linkedin.com/in/muhammad-ilham-rilambang-6400837b' },
    { label: 'GitHub', url: 'https://github.com/rilambang' },
    { label: 'X', url: 'https://x.com/rilambang' },
  ],
  now: 'Auditing what agent-driven iOS delivery can and cannot prove.',
}

// four numbers, each one a claim with a receipt in WORK below
export const FACTS = [
  { figure: '9 yrs', label: 'shipping mobile since 2017, in React Native, UIKit and SwiftUI' },
  { figure: '270K', label: 'total app downloads across the iOS apps I have shipped' },
  { figure: '11K', label: 'iOS users on the busiest single day of an app I built' },
  { figure: '100%', label: 'crash-free iOS users on the app I lead today' },
]

export const WORK = [
  {
    slug: 'pijar',
    name: 'PIJAR',
    year: '2025 — now',
    role: 'Lead iOS engineer',
    line: 'MVVM + Clean Architecture in SwiftUI, exam modules for school-run proctored exams — and an AI-native delivery setup: agent roles, git hooks and CI gates.',
    tags: ['SwiftUI', 'MVVM', 'Coordinator', 'AI agents'],
    store: 'https://apps.apple.com/id/app/pijar-sekolah-siswa/id6746177919',
    shots: ['pijar-1.webp', 'pijar-2.webp'],
  },
  {
    slug: 'indihome',
    name: 'Indihome Eazy and Antares Eazy',
    year: '2022 — 2025',
    role: 'iOS engineer',
    line: 'Two closely related Telkom apps that I developed. Moved the flagship from UIKit to SwiftUI and from MVC to modular Clean Architecture — without breaking it.',
    tags: ['UIKit → SwiftUI', 'Clean Architecture'],
    store: 'https://apps.apple.com/us/app/indihome-eazy/id1486126278',
    shots: ['indihome-1.webp', 'indihome-2.webp', 'antares-1.webp', 'antares-2.webp'],
    also: { name: 'Antares Eazy', store: 'https://apps.apple.com/id/app/antares-eazy/id6446350716' },
  },
  {
    slug: 'agreemart',
    name: 'Agree Mart',
    year: '2021 — 2022',
    role: 'iOS engineer',
    line: 'Marketplace for small businesses. Drove SwiftUI adoption, then wrote the standards that made it stick.',
    tags: ['SwiftUI', 'Mentoring'],
    store: 'https://apps.apple.com/us/app/agree-mart/id1611114347',
    shots: ['agreemart-1.webp', 'agreemart-2.webp'],
  },
  {
    slug: 'satusehat',
    name: 'SATUSEHAT Mobile',
    year: 'National platform',
    role: 'Mobile engineer',
    line: "Indonesia's national health app — production iOS where being wrong is not a retry.",
    tags: ['iOS', 'Production'],
    store: 'https://apps.apple.com/id/app/satusehat-mobile/id1504600374',
    shots: ['satusehat-1.webp', 'satusehat-2.webp'],
  },
]

export const ROLES = [
  { role: 'Lead iOS Engineer — PIJAR', span: '2025 — now', where: 'Telkom Indonesia' },
  { role: 'iOS Engineer — Indihome Eazy, Antares Eazy', span: '2022 — 2025', where: 'Telkom Indonesia' },
  { role: 'iOS Engineer — Agree Mart', span: '2021 — 2022', where: 'Agree' },
  { role: 'Technical Lead — Agree Platform', span: '2018 — 2021', where: 'Agree' },
  { role: 'Mobile Engineer — React Native', span: '2017 — 2021', where: 'Telkom Indonesia' },
]

// three posts that show how I think; the rest live at /blog
export const WRITING = [
  { slug: 'uikit-to-swiftui-without-a-rewrite', tag: 'Migration', title: 'UIKit to SwiftUI without a rewrite', line: 'The migration succeeds or fails on one decision: who owns navigation.' },
  { slug: 'mvvm-to-viper-part-one', tag: 'Architecture', title: 'MVVM to VIPER, part one: when the view model is the app', line: 'Why a pattern that works at five screens stops being local at fifty.' },
  { slug: 'what-a-year-of-ai-native-ios-still-cant-prove', tag: 'Process', title: "What a year of AI-native iOS still can't prove", line: 'I scored my own agent setup seven out of ten. Nine failure modes, with numbers.' },
]

export const STACK = ['SwiftUI', 'UIKit', 'Combine', 'Swift Concurrency', 'Clean Architecture', 'MVVM', 'VIPER', 'Coordinator', 'SPM modularisation', 'CI gates', 'AI agents', 'React Native']

export const ALSO = [
  { name: 'Agree', url: 'https://play.google.com/store/apps/details?id=com.telkom.agreefarmer' },
  { name: 'Agree Modal', url: 'https://play.google.com/store/apps/details?id=com.agree.modal' },
  { name: 'Agree Field Assistant', url: 'https://play.google.com/store/apps/details?id=com.agree.surveyor' },
  { name: 'Antares Eazy', url: 'https://apps.apple.com/id/app/antares-eazy/id6446350716' },
  { name: 'MyPertamina', url: 'https://apps.apple.com/id/app/mypertamina/id1295039064' },
  // Teman Berbagi (id1378783617) and UMeetMe (id1506469763) dropped: iTunes lookup
  // returns resultCount 0 in every storefront, so they are delisted, not region-blocked.
]

export const REPOS = [
  { name: 'Modularization-Profile-Package', lang: 'Swift', url: 'https://github.com/rilambang/Modularization-Profile-Package' },
]

export const CERTS = [
  { name: 'iOS Developer Expert', issuer: 'Dicoding', url: 'https://www.dicoding.com/certificates/07Z6V537YXQR' },
  { name: 'Professional Scrum Developer I', issuer: 'Scrum.org', url: 'https://www.scrum.org/certificates/678723' },
]

// LinkedIn lists this era as CTO of Agree; the CV calls it Technical Lead.
export const CONTACT = {
  heading: 'Open to lead and staff iOS roles.',
  body: 'Jakarta or remote. I want to own architecture, delivery and the people who ship it — on teams that treat those as the same job.',
}
