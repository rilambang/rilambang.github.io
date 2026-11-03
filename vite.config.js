import { defineConfig } from 'vite'
import { renderPage } from './src/render.js'

// The home page is plain HTML rendered at build time from src/data.js: content
// works with JS off and is greppable in the deployed file. main.js only adds motion.
const staticHome = () => ({
  name: 'static-home',
  transformIndexHtml: { order: 'pre', handler: (html) => html.replace('<!--app-->', renderPage()) },
})

export default defineConfig({
  plugins: [staticHome()],
  // relative base so the build works from a subpath (GitHub Pages repo sites)
  base: './',
  // GitHub Pages "Deploy from a branch" only serves / or /docs, so build straight into docs/.
  build: { outDir: 'docs' },
})
