import { build } from 'esbuild'
import { readFile, writeFile, mkdir } from 'fs/promises'
import { dirname, resolve } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const outdir = resolve(__dirname, 'dist')

const isWatch = process.argv.includes('--watch')

await mkdir(outdir, { recursive: true })

// 1) Build UI first
await build({
  entryPoints: [resolve(__dirname, 'src/ui.js')],
  bundle: true,
  outfile: resolve(outdir, 'ui.js'),
  target: 'es2018',
  platform: 'browser',
  format: 'iife',
  define: { 'process.env.NODE_ENV': '"production"' },
})

// 2) Inline UI into HTML
const uiHtml = await readFile(resolve(__dirname, 'src/ui.html'), 'utf8')
const uiJs = await readFile(resolve(outdir, 'ui.js'), 'utf8')
const inlined = uiHtml.replace('</body>', `<script>${uiJs}</script></body>`)
await writeFile(resolve(__dirname, 'src/_inlined-ui.ts'), `export default ${JSON.stringify(inlined)};\n`)

// Also emit dist/ui.html for manifest compatibility
const externalLinked = uiHtml.replace('</body>', '<script src="./ui.js"></script></body>')
await writeFile(resolve(outdir, 'ui.html'), externalLinked)

// Copy manifest.json into dist and ensure paths target dist outputs
let manifest = await readFile(resolve(__dirname, 'manifest.json'), 'utf8')
try {
  const obj = JSON.parse(manifest)
  obj.main = 'code.js'
  obj.ui = 'ui.html'
  manifest = JSON.stringify(obj, null, 2)
} catch {}
await writeFile(resolve(outdir, 'manifest.json'), manifest)

// 3) Build plugin core which imports inlined UI string
await build({
  entryPoints: [resolve(__dirname, 'src/code.ts')],
  bundle: true,
  outfile: resolve(outdir, 'code.js'),
  target: 'es2018', // Changed to es2018 for maximum compatibility
  platform: 'browser',
  format: 'iife',
  define: { 'process.env.NODE_ENV': '"production"' },
})

console.log('Build complete.')


