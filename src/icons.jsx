// tiny inline icons, no icon library
const S = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.5, strokeLinecap: 'round', strokeLinejoin: 'round' }

export const Arrow = () => (
  <svg viewBox="0 0 16 16" aria-hidden="true" {...S}>
    <path d="M3 13 13 3M6 3h7v7" />
  </svg>
)

export const Down = () => (
  <svg viewBox="0 0 16 16" aria-hidden="true" {...S}>
    <path d="M8 2.5v10M3.5 9 8 13.5 12.5 9" />
  </svg>
)

export const Mail = () => (
  <svg viewBox="0 0 16 16" aria-hidden="true" {...S}>
    <rect x="1.5" y="3.5" width="13" height="9" rx="1.5" /><path d="m2 5 6 4.5L14 5" />
  </svg>
)

export const Phone = () => (
  <svg viewBox="0 0 16 16" aria-hidden="true" {...S}>
    <path d="M4 2h2l1.5 3.5-2 1.5a9 9 0 0 0 3.5 3.5L10.5 8.5 14 10v2a2 2 0 0 1-2.2 2A13 13 0 0 1 2 4.2 2 2 0 0 1 4 2Z" />
  </svg>
)