import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // ponytail: relative base so the build works from a subpath (GitHub Pages repo sites)
  base: './',
  // GitHub Pages "Deploy from a branch" only serves / or /docs, so build straight into docs/.
  build: { outDir: 'docs' },
})