# rilambang.com

Live at https://rilambang.github.io — GitHub Pages from `docs/`, no custom domain, no analytics.

## Build and checks

```sh
npm run stills   # only if figures changed (needs rsvg-convert)
npm run build    # site/ -> docs/, feed.xml + sitemap
npm run check:prose
npm run check:deploy   # before a release: fails unless committed docs/ matches a fresh build
```

Push to `main` is the deploy — he decides when, and it goes live in about a minute.

## Medium cross-post

"Write it on my site, it's on Medium too" is a manual two-step, not an automation.
Medium closed [new publishing API tokens in 2021](https://help.medium.com/hc/en-us/articles/213480228-why-has-my-integration-token-stopped-working)
("Medium will not be issuing any new integration tokens"). If you already hold a
pre-2021 token, an API auto-post script can be added on top of it. Without one,
Stories > [Import a story](https://medium.com/p/import) is the only official path:
paste the live article URL, Medium imports it, keeps the `<img>` stills (inline SVG
does not carry over), backdates it, and sets the canonical URL to the original
automatically ([Help 214550207](https://help.medium.com/hc/en-us/articles/214550207)).

For each post, in this order:

1. Publish on the site first: `npm run stills` if figures changed, then
   `npm run build`, commit `docs/`, push, wait ~1 min until the URL is live.
2. `npm run medium` — it lists every post's live URL (in `site/build.mjs` ORDER),
   its title/tag/summary, suggested topics (max 5), and whether its PNG stills
   exist. `npm run medium -- <slug>` shows one post.
3. Open https://medium.com/p/import and paste the URL.
4. On the draft, verify the canonical line points back at the live URL, add the
   topics, and Publish.

There is no `?url=` prefill for the import page — Medium documents none — so the
script pairs the page with copy-paste URLs instead of guessing a deep link.
