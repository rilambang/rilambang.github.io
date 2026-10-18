// ponytail: every word and image on the site lives here. edit this file, not App.jsx.
// PRIVACY: publish only what you'd hand a stranger at a conference.
// DO NOT add: date of birth, national ID (NIK), home address, family, client-side tracking.

export const ME = {
  name: 'Muhammad Ilham Rilambang',
  short: 'Ilham Rilambang',
  initials: 'IR',
  title: 'iOS Engineer',
  org: 'Telkom Indonesia',
  division: 'Digital Business & Technology',
  location: 'Jakarta, Indonesia',
  languages: ['Bahasa Indonesia', 'English'],
  email: 'rilambang@gmail.com',
  // phone/phoneHref removed: a public repo publishes a number permanently and it
  // can't be un-published. Email is the contact route.
  linkedin: 'https://linkedin.com/in/muhammad-ilham-rilambang-6400837b',
  github: 'https://github.com/rilambang',
  x: 'https://x.com/rilambang',
  // TODO: only add handles you've confirmed are yours. Instagram/TikTok/Threads
  // /rilambang could not be verified — check them before adding.
  socials: [
    { label: 'LinkedIn', url: 'https://linkedin.com/in/muhammad-ilham-rilambang-6400837b' },
    { label: 'GitHub', url: 'https://github.com/rilambang' },
    { label: 'X', url: 'https://x.com/rilambang' },
  ],
  // used for search engines to find you later
  keywords:
    'Ilham Rilambang, Muhammad Ilham Rilambang, iOS Developer Indonesia, SwiftUI Engineer, Telkom Indonesia, Clean Architecture Swift, MVVM Swift, iOS Engineer Jakarta',
}

export const HERO = {
  eyebrow: 'iOS Engineer · Telkom Indonesia',
  headline: ['I build the apps a country runs on,', 'and the teams that', 'keep them standing.'],
  sub:
    'Eight years in mobile, mostly at Telkom Indonesia — moving products from React Native through UIKit into SwiftUI, and myself from writing features to leading the teams that write them. Right now I lead iOS for Pijar Sekolah, an education platform carrying more than a million students.',
}

export const STATS = [
  { figure: '1', unit: 'M+', label: 'Students', note: 'sat exams on modules I architected.' },
  { figure: '99.5', unit: '%', label: 'Crash-free', note: 'sessions on Indihome Eazy after the rewrite.' },
  { figure: '25', unit: '%', label: 'Faster', note: 'load times after leaving UIKit behind.' },
  { figure: '20', unit: '%', label: 'Less debt', note: 'via modularisation and SOLID.' },
]

export const APPS = [
  {
    slug: 'pijar',
    name: 'Pijar Sekolah',
    year: '2025 — now',
    role: 'Lead iOS Developer',
    blurb:
      'A national education platform used by thousands of schools. I lead the iOS team, and the architecture underneath it.',
    points: [
      'MVVM + Clean Architecture, written in SwiftUI',
      'Coordinator pattern over NavigationStack',
      'Exam modules carrying more than a million students',
    ],
    tags: ['SwiftUI', 'MVVM', 'Clean Architecture', 'Coordinator'],
    store: 'https://apps.apple.com/id/app/pijar-sekolah-siswa/id6746177919',
    shots: ['pijar-1.webp', 'pijar-2.webp'],
  },
  {
    slug: 'indihome',
    name: 'Indihome Eazy',
    year: '2022 — 2025',
    role: 'iOS Developer',
    blurb:
      'One of Telkom Indonesia’s highest-priority apps. Migrating it is where I properly learned Clean Architecture — on a codebase that could not afford to break.',
    points: [
      'UIKit → SwiftUI',
      'MVC → modular Clean Architecture',
      'Load times down 25%, crash-free sessions to 99.5%',
    ],
    tags: ['SwiftUI', 'UIKit', 'Clean Architecture'],
    store: 'https://apps.apple.com/us/app/indihome-eazy/id1486126278',
    shots: ['indihome-1.webp', 'indihome-2.webp'],
  },
  {
    slug: 'agreemart',
    name: 'Agree Mart',
    year: '2021 — 2022',
    role: 'iOS Developer',
    blurb:
      'A marketplace for Indonesian small businesses. I drove the SwiftUI adoption, then wrote down the standards so it would stick.',
    points: [
      'Spearheaded SwiftUI adoption across the project',
      'Mentored junior developers on Swift practice',
      'Reworked the codebase around real-world use cases',
    ],
    tags: ['SwiftUI', 'Mentoring', 'Standards'],
    store: 'https://apps.apple.com/us/app/agree-mart/id1611114347',
    shots: ['agreemart-1.webp', 'agreemart-2.webp'],
  },
  {
    slug: 'satusehat',
    name: 'SATUSEHAT Mobile',
    year: 'National health platform',
    role: 'Mobile Developer',
    blurb:
      'Indonesia’s national health app — the category where being wrong has consequences that an offline retry cannot fix.',
    points: [
      'Production iOS work at national scale',
      'Reliability and performance under real load',
    ],
    tags: ['iOS', 'Production'],
    store: 'https://apps.apple.com/id/app/satusehat-mobile/id1504600374',
    shots: ['satusehat-1.webp', 'satusehat-2.webp'],
  },
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

// LinkedIn lists this era as CTO of Agree; the CV calls it Technical Lead.
export const TIMELINE = [
  {
    role: 'Lead iOS Developer, Pijar Sekolah',
    span: '2025 — now',
    note: 'Architecting the exam modules more than a million students sit, and the SwiftUI codebase behind them.',
  },
  {
    role: 'iOS Developer, Eazy',
    span: '2022 — 2025',
    note: 'Indihome Eazy and Antares Eazy — two of Telkom’s highest-priority apps, taken from UIKit into SwiftUI.',
  },
  {
    role: 'iOS Developer, Agree Mart',
    span: '2021 — 2022',
    note: 'Drove SwiftUI adoption and mentored junior developers on Swift practice and coding standards.',
  },
  {
    role: 'Technical Lead, Agree',
    span: '2018 — 2021',
    note: 'Led groups of developers building the Agree Platform — an all-inclusive environment for banks, enterprises and end farmers.',
  },
  {
    role: 'Mobile App Developer, Telkom Indonesia',
    span: '2017 — 2021',
    note: 'React Native across the Digital Business division. Where I learned to ship.',
  },
]

// the working philosophy, grounded in real decisions rather than adjectives
export const CRAFT = [
  {
    n: '01',
    title: 'The migration is the work',
    body:
      'Twice now I have moved a live product off an old stack — UIKit to SwiftUI, MVC to modular Clean Architecture. The rewrite is never the interesting part. Shipping it on a Friday without paging anyone is.',
  },
  {
    n: '02',
    title: 'Modularise, or it rots',
    body:
      'Enforcing SOLID and splitting things into modules cut our technical debt by about 20% and made the team faster. Structure is a speed feature.',
  },
  {
    n: '03',
    title: 'Performance is a feature',
    body:
      'A 25% cut in load time and 99.5% crash-free sessions are not numbers I chased. They are what happens when you treat the app as something a person depends on.',
  },
  {
    n: '04',
    title: 'Consistency beats taste',
    body:
      'I have leaned on a shared design system rather than personal preference, and written coding standards down so a team of any size produces the same work.',
  },
  {
    n: '05',
    title: 'Leave the team better',
    body:
      'The measure of a lead is not what they wrote. It is whether the people around them can ship without asking. I mentor, and I try to be the reason nobody gets stuck.',
  },
]

export const BEFORE = [
  { k: 'CompFest 2014', v: 'Finalist. Built a product using Intel RealSense that picked clothes based on the wearer’s body measurements — a teenager deciding what a camera could do.' },
  { k: 'Universitas Indonesia', v: '2012 — 2016.' },
  { k: 'STMIK Tasikmalaya', v: '2016.' },
  { k: 'TOEFL', v: '523, 2012. Enough English to read an Apple docs page in 2013 and understand most of it.' },
]

export const OFFCLOCK = [
  {
    title: 'Low end, loud room',
    body:
      'I play bass and I arrange music — and for years I was the bassist in Agree Band, which is a slightly absurd thing to be able to say about an app called Agree. I still play at campus events when someone needs a rhythm section.',
  },
  {
    title: 'Why I still write it all myself',
    body:
      'Eight years in, and the part I like has not changed: a hard problem, an empty file, and the specific quiet of figuring it out. Leadership changed my calendar, not that.',
  },
  {
    title: 'Bands, and other things that scale badly',
    body:
      'Software is the only thing I have ever tried to make reliable that was designed to fall apart. Music is a hobby precisely because it does not owe me a test suite.',
  },
]

// real repos from github.com/rilambang — the RN libraries and the modularisation samples
export const REPOS = [
  {
    name: 'react-native-svg-uri',
    year: '2018',
    lang: 'JavaScript',
    body:
      'Render SVG in React Native from a URL or a static file. Written in the React Native years, when the platform still needed most things handed to it.',
    url: 'https://github.com/rilambang/react-native-svg-uri',
  },
  {
    name: 'react-native-photo-view',
    year: '2018',
    lang: 'Objective-C',
    body:
      'Pinch-to-zoom image view for React Native on both iOS and Android. The kind of component that should never have needed writing.',
    url: 'https://github.com/rilambang/react-native-photo-view',
  },
  {
    name: 'Modularization-Profile-Package',
    year: '2023',
    lang: 'Swift',
    body:
      'A worked example of splitting an iOS codebase into Swift packages. Principle 02 on this page, in actual commits — modularisation you can read.',
    url: 'https://github.com/rilambang/Modularization-Profile-Package',
  },
  {
    name: 'react-native-modal-dropdown',
    year: '2018',
    lang: 'JavaScript',
    body: 'A cross-platform dropdown picker for React Native, back when iOS and Android still diverged on everything.',
    url: 'https://github.com/rilambang/react-native-modal-dropdown',
  },
]

export const CERTS = [
  { name: 'iOS Developer Expert', issuer: 'Dicoding Indonesia', url: 'https://www.dicoding.com/certificates/07Z6V537YXQR' },
  { name: 'Professional Scrum Developer I', issuer: 'Scrum.org', url: 'https://www.scrum.org/certificates/678723' },
]

export const CONTACT = {
  heading: 'Open to a frontend or software engineering role.',
  body:
    'I care about clean architecture, fast apps, and teams that can keep going without me. If that sounds like the room you are building, I would like to hear from you.',
}