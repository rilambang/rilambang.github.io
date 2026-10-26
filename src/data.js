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
    'I lead iOS for Pijar Sekolah at Telkom Indonesia — the exam modules a million students sit. Mobile since 2017, three stacks, one habit: ship it and leave the team able to ship without me.',
  links: [
    { label: 'LinkedIn', url: 'https://linkedin.com/in/muhammad-ilham-rilambang-6400837b' },
    { label: 'GitHub', url: 'https://github.com/rilambang' },
    { label: 'X', url: 'https://x.com/rilambang' },
  ],
  keywords:
    'Ilham Rilambang, Muhammad Ilham Rilambang, iOS Developer Indonesia, SwiftUI Engineer, Telkom Indonesia, Clean Architecture Swift, MVVM Swift, iOS Engineer Jakarta',
}

// four numbers, each one a claim with a receipt in WORK below
export const FACTS = [
  { figure: '1M+', label: 'students sat exams on modules I architected' },
  { figure: '99.5%', label: 'crash-free sessions on Indihome Eazy after the rewrite' },
  { figure: '25%', label: 'faster load times after leaving UIKit behind' },
  { figure: '2017', label: 'shipping mobile — React Native, UIKit, SwiftUI' },
]

export const WORK = [
  {
    slug: 'pijar',
    name: 'Pijar Sekolah',
    year: '2025 — now',
    role: 'Lead iOS engineer',
    line: 'MVVM + Clean Architecture in SwiftUI, exam modules carrying a million students.',
    tags: ['SwiftUI', 'MVVM', 'Coordinator'],
    store: 'https://apps.apple.com/id/app/pijar-sekolah-siswa/id6746177919',
    shots: ['pijar-1.webp', 'pijar-2.webp'],
  },
  {
    slug: 'indihome',
    name: 'Indihome Eazy',
    year: '2022 — 2025',
    role: 'iOS engineer',
    line: 'Took a Telkom flagship from UIKit to SwiftUI and MVC to modular Clean Architecture — without breaking it.',
    tags: ['UIKit → SwiftUI', 'Clean Architecture'],
    store: 'https://apps.apple.com/us/app/indihome-eazy/id1486126278',
    shots: ['indihome-1.webp', 'indihome-2.webp'],
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

// My time on each app, not the app's App Store life. IndiHome and Antares were
// carried together, so those two are the only bars that overlap; the rest are
// sequential. MyPertamina and SATUSEHAT were occasional work inside the Agree
// years — left off the chart until their dates are precise enough to draw.
export const TENURE = {
  rows: [
    { name: 'Pijar Sekolah', from: 2025.5, to: null, live: true },
    { name: 'Antares Eazy', from: 2023.25, to: 2025.5 },
    { name: 'IndiHome Eazy', from: 2022, to: 2025.5 },
    { name: 'Agree Mart', from: 2021, to: 2022 },
  ],
}

export const ROLES = [
  { role: 'Lead iOS Engineer — Pijar Sekolah', span: '2025 — now', where: 'Telkom Indonesia' },
  { role: 'iOS Engineer — Indihome Eazy, Antares Eazy', span: '2022 — 2025', where: 'Telkom Indonesia' },
  { role: 'iOS Engineer — Agree Mart', span: '2021 — 2022', where: 'Agree' },
  { role: 'Technical Lead — Agree Platform', span: '2018 — 2021', where: 'Agree' },
  { role: 'Mobile Engineer — React Native', span: '2017 — 2021', where: 'Telkom Indonesia' },
]

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
  { name: 'react-native-svg-uri', lang: 'JavaScript', url: 'https://github.com/rilambang/react-native-svg-uri' },
  { name: 'react-native-photo-view', lang: 'Objective-C', url: 'https://github.com/rilambang/react-native-photo-view' },
]

export const CERTS = [
  { name: 'iOS Developer Expert', issuer: 'Dicoding', url: 'https://www.dicoding.com/certificates/07Z6V537YXQR' },
  { name: 'Professional Scrum Developer I', issuer: 'Scrum.org', url: 'https://www.scrum.org/certificates/678723' },
]

// LinkedIn lists this era as CTO of Agree; the CV calls it Technical Lead.
export const CONTACT = {
  heading: 'Open to iOS and mobile engineering roles.',
  body: 'Especially teams that treat architecture and shipping as the same job.',
}
