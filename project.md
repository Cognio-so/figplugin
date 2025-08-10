# Growth99 Figma Plugin – Full Requirements & Implementation Spec (v1.0)

**Owner:** Ashutosh (Cognio Labs)
**Date:** Aug 10, 2025
**Scope:** Figma plugin + backend services that let Growth99 designers chat with an AI assistant, paste reference URLs, upload brand assets (logos/images), and generate a first high‑fidelity page in Figma with one‑click redesign/regenerate. Once approved, generate remaining core pages (6–8 common marketing pages) in a consistent system. Includes model selector, chat memory, Firecrawl‑based reference analysis, and optional AI‑generated images via toggle.

---

## 1) Goals & Non‑Goals

### 1.1 Goals

* **Fast first draft:** Generate a high‑fidelity, editable Figma page from a short chat brief + reference URLs.
* **Iterate quickly:** "Redesign" button to regenerate the same page while preserving brand constraints and user‑pinned elements.
* **Scale to sites:** After approval, generate additional core pages (About, Services, Pricing, Gallery, Contact, Blog/Post, FAQs, etc.) in a consistent style.
* **Reference‑aware:** Analyze a provided reference URL to infer typography, colors, spacing, components, and layout patterns for style transfer (without copying content).
* **Brand‑aware:** Respect uploaded assets: **logo** goes to header/brand locations; **hero/section images** go to specified sections.
* **Image toggle:** Optional **AI images** switch. Off → placeholders. On → generate images via Replicate (or other) and place into the design.
* **Model selector:** Designers can pick which LLM writes the design plan/code (OpenAI/Anthropic/Gemini/other).
* **Chat memory:** Conversational brief persists and informs later generations.

### 1.2 Non‑Goals

* Live production code export (HTML/CSS) beyond what’s needed to render Figma objects.
* Full CMS integration.
* Pixel‑perfect replication of references (we derive style systems, not clone).

---

## 2) Target Users & Core Use Cases

* **Growth99 designers** creating websites for spas, med‑spas, clinics, dental, hospitals, wellness, etc.
* **Use cases**:

  1. Chat → generate first page → tweak → regenerate until approved.
  2. Approve page → auto‑generate remaining core pages with same system.
  3. Provide reference URL(s) → infer style system and component patterns.
  4. Upload logo → auto‑place in header/nav; upload hero image → auto‑place in first fold.
  5. Toggle AI images on → replace placeholders with generated images that match niche/brand.

---

## 3) High‑Level Architecture

### 3.1 Components

* **Figma Plugin (TypeScript)**

  * **Plugin Core (code.ts):** Reads/writes the Figma scenegraph, creates frames/components, sets auto‑layout, images, text, and styles; persists plugin data.
  * **UI (ui.html + ui.tsx):** Chat pane, model selector, toggles, uploads, actions (Generate, Redesign, Generate Pages). Uses `postMessage` bridge to core.
* **Backend (FastAPI, Python)**

  * **LangGraph Orchestration:** Agents for (a) requirements harvest, (b) reference analysis, (c) layout planner, (d) component composer, (e) copy/placeholder generator, (f) image spec generator.
  * **Firecrawl Integration:** Extract style signals from reference URLs (fonts, color palette, spacing, common patterns).
  * **LLM Connectors:** OpenAI/Anthropic/Gemini/etc. via model selector.
  * **Image Gen Service:** Replicate (default), with room for other providers.
  * **Storage:** Postgres (projects, sessions, specs), S3/GCS (asset uploads), Redis (job queue, cache).
* **Optional Proxy:** Backend proxies outbound calls to avoid CORS/null‑origin issues from plugin UI.

### 3.2 Data Flow (Happy Path)

1. Designer opens plugin → starts chat → provides brief, reference URL(s), uploads logo/optional images.
2. UI sends `SessionStart` to backend → backend creates project/session; stores chat memory.
3. Designer clicks **Generate First Page** → backend runs:
   a) **Reference Analysis (Firecrawl)** → style tokens & patterns
   b) **Layout Planner (LLM)** → structured **PageSpec JSON**
   c) **Assets Plan (LLM)** → image slots & copy placeholders
4. Backend returns **PageSpec JSON** → Plugin Core renders Figma nodes accordingly.
5. Designer clicks **Redesign** → backend regenerates new **PageSpec** using same constraints (+locked/pinned nodes).
6. Designer clicks **Generate Remaining Pages** → backend produces multi‑page **SiteSpec**; Plugin renders pages.
7. Optional **AI Images** toggle → backend gets prompts per slot → fetches from Replicate → plugin replaces placeholders with generated images.

---

## 4) Functional Requirements

### 4.1 Chat & Inputs

* Chat UI for requirements gathering with **memory** and **system prompts** tuned for Growth99 verticals.
* Inputs accepted:

  * **Text** (requirements, brand tone, CTAs, sections).
  * **Reference URLs** (one or more).
  * **Uploads**: logo (SVG/PNG), brand images.
  * **Toggles**: “Use AI Images”, “Keep header/footer fixed”, “Respect brand colors only”.
  * **Model Selector** (dropdown): lists configured models + temperature/max tokens.
* Persist last N chats and settings per **Figma file** and per **user**.

### 4.2 Generation Modes

* **Generate First Page**: Creates one page (recommended: **Home**).
* **Redesign**: Re‑plan same page; honor **Pinned** nodes/sections.
* **Generate Remaining Pages**: Produces **SiteSpec** for typical set (configurable template):

  * Home, About, Services, Pricing, Gallery/Before‑After, Blog Landing, Blog Post, Contact/Booking, FAQs.
* **Page‑level options**: add/remove sections, switch hero variant (split, centered, left image, video placeholder), components library mapping.

### 4.3 Reference‑Aware Style Extraction

* Use Firecrawl on provided URLs to infer:

  * Color palette (HEX/RGB), gradient usage
  * Typography (font families, sizes/scale, weights, letter spacing)
  * Spacing scale (8/10/12…), container widths, grid/columns
  * Common patterns (sticky header, hero variants, CTA bars, cards, feature rows, testimonial carousels, FAQ accordions, footers)
  * UI elements (button styles: radius, padding, border, shadows)
* Convert into **DesignSystem JSON** (see §7.2) with confidence scores.
* Allow multiple references: blend rules → choose **Primary** ref; borrow missing tokens from **Secondary**.

### 4.4 Brand Asset Placement

* If an uploaded image is flagged **logo**, place in header/nav and applicable footer.
* If an uploaded image is flagged **hero**, place into the first fold image slot.
* Support mapping table: `{ role: 'logo'|'hero'|'section:n'|'favicon', fileId, constraints }`
* Respect aspect ratio, min/max width, and padding guidelines from **DesignSystem**.

### 4.5 AI Images Toggle

* Default **off** → use placeholders (solid/gray or stock placeholder URLs).
* When **on** → backend generates prompts per image slot (niche, tone, palette) and calls Replicate (or provider) to generate and return URLs/bytes.
* Plugin replaces image fills for nodes tagged by role and updates **pluginData**.

### 4.6 Model Selector

* UI dropdown with preconfigured providers/models (e.g., `gpt-4.1`, `o3`, `claude-3.5`, `gemini-1.5-pro`, local via server).
* Persist per session; include temperature, top‑p, max tokens.
* Backend adapter pattern; easily add models.

### 4.7 Regeneration & Constraints

* **Pinned** sections/nodes are preserved (header/footer, brand components).
* Designer can lock the system (colors, type scale).
* Regeneration can target whole page or specific sections (hero only, testimonials only).
* Diff view: highlight changed sections on regenerate.

### 4.8 Multi‑Page Consistency

* Generate **DesignSystem** and **ComponentLibrary** first.
* All pages consume the same tokens/components.
* Provide a **Sync Styles** action to re‑apply updated tokens across pages.

### 4.9 Telemetry & Undo

* Log events (Generate/Redesign/Errors) with anonymized IDs.
* Use Figma’s native undo/redo; every node operation grouped per action.

---

## 5) Non‑Functional Requirements

* **Performance:** First page plan in ≤ 10s (cached references) and ≤ 25s cold; render ≤ 2s after spec received (typical \~100–200 nodes).
* **Reliability:** Graceful fallbacks if Firecrawl/LLM/Image provider fails.
* **Security:** All traffic TLS; signed upload URLs; sanitize URLs; content moderation on prompts if needed.
* **Privacy:** Store only project metadata and assets required; no PHI/PII beyond what designers upload.
* **Compliance:** Respect robots/crawling policies in reference analysis; provenance on AI‑generated images.

---

## 6) Figma Plugin Implementation Details

### 6.1 Project Structure

```
/figma-plugin
  ├─ manifest.json
  ├─ src/
  │   ├─ code.ts            # plugin core (scenegraph)
  │   ├─ ui.html            # webview UI
  │   ├─ ui.tsx             # chat app (React/Preact)
  │   ├─ bridge.ts          # postMessage helpers
  │   ├─ renderers/
  │   │    ├─ layout.ts     # auto‑layout helpers
  │   │    ├─ text.ts       # text nodes, typography
  │   │    ├─ image.ts      # image fills, logo/hero
  │   │    └─ components.ts # cards, nav, footer, etc.
  │   ├─ storage.ts         # clientStorage + pluginData
  │   └─ types.ts           # PageSpec/DesignSystem types
  └─ package.json
```

### 6.2 Manifest Essentials

* `name`, `id`, `api`: current version
* `editorType`: `["figma"]`
* `main`: `dist/code.js`
* `ui`: `dist/ui.html`
* `networkAccess`: allow backend domain(s), Firecrawl, Replicate, and websockets if streaming
* Optional: `enableProposedApi` only if needed; `relaunchButtons` for quick reuse.

### 6.3 UI ↔ Core Messaging

* In **code.ts**: `figma.showUI(__html__, { width: 380, height: 640 })`
* Use `figma.ui.onmessage` to receive UI commands and `figma.ui.postMessage` to send status/progress.
* Define a **typed protocol** (see §7.1) for: `SessionStart`, `GenerateFirstPage`, `Redesign`, `GenerateSitePages`, `ApplyImages`, `PinNodes`, `SyncStyles`, `Error`.

### 6.4 Storage Strategy

* **Per‑user memory**: `figma.clientStorage` for chat history, user preferences, last models.
* **Per‑file/shared**: `setSharedPluginData("g99", key, value)` to store project id, style token ids, etc.
* **Per‑node**: `setPluginData("role", "logo|hero|section:n|component:Card")` for targeting.

### 6.5 Rendering Helpers (Examples)

* **Auto‑layout Frame**

```ts
const frame = figma.createFrame()
frame.layoutMode = 'VERTICAL'
frame.primaryAxisSizingMode = 'AUTO'
frame.counterAxisSizingMode = 'AUTO'
frame.itemSpacing = 24
frame.paddingTop = frame.paddingRight = frame.paddingBottom = frame.paddingLeft = 24
```

* **Text Node with Style**

```ts
const h1 = figma.createText()
await figma.loadFontAsync({ family: 'Inter', style: 'Bold' })
h1.characters = 'Radiant Wellness Clinic'
h1.fontName = { family: 'Inter', style: 'Bold' }
h1.fontSize = 44
h1.lineHeight = { value: 52, unit: 'PIXELS' }
```

* **Image Fill (logo/hero)**

```ts
const rect = figma.createRectangle()
const image = await figma.createImageAsync(srcUrl) // or createImage(Uint8Array)
rect.fills = [{ type: 'IMAGE', scaleMode: 'FILL', imageHash: image.hash }]
rect.setPluginData('role','hero')
```

* **Pin Header/Footer**: mark nodes with `pluginData.pinned = 'true'` and skip mutating them on regenerate.

### 6.6 Error Handling UX

* Non‑blocking toasts for transient errors; modal for hard failures.
* Offer **Retry** and **Fallback** (e.g., skip images, use defaults, or switch model).
* Log errors (anonymized) to backend for triage.

---

## 7) Contracts & Schemas

### 7.1 UI↔Core Message Protocol (examples)

```ts
// UI → Core
{ type: 'GenerateFirstPage', payload: {
   projectId, model, useAiImages, brief, refs: string[],
   uploads: [{role:'logo'|'hero'|'section:n', name, blobUrl}],
}}

// Core → UI
{ type: 'RenderProgress', payload: { step: 'creating-hero', percent: 35 } }
{ type: 'Error', payload: { code, message, suggestion } }
```

### 7.2 Backend API (FastAPI) – Endpoints

* `POST /v1/session/start` → `{ projectId, userId }`
* `POST /v1/reference/analyze` → body: `{ urls: string[], brief?: string }` → returns **DesignSystem**
* `POST /v1/page/plan` → body: `{ designSystem, pageKind, constraints, pinnedSlots, brief }` → returns **PageSpec**
* `POST /v1/site/plan` → body: `{ designSystem, pages: PageKind[], brief }` → returns **SiteSpec**
* `POST /v1/images/generate` → body: `{ slots: ImageSlot[], styleHints, provider, model }` → returns `{ slotId -> url }`
* `POST /v1/upload/sign` → returns signed URL for asset upload
* `GET /v1/session/{id}` → restore memory/chat
* **SSE/Webhooks** for streaming progress (optional)

### 7.3 DesignSystem JSON (sample)

```json
{
  "colors": {"primary": "#3B82F6", "text": "#0F172A", "muted": "#64748B"},
  "typography": {"display": {"family":"Inter","size":44,"weight":"700"},
                  "h2": {"size":32,"weight":"700"},
                  "body": {"size":16,"line":24}},
  "spacingScale": [8,12,16,24,32],
  "radius": {"sm":8, "md":12, "lg":20},
  "grid": {"container": 1200, "columns": 12, "gutter": 24},
  "components": {"Button":{"radius":12,"padX":20,"padY":12,"weight":"600"}}
}
```

### 7.4 PageSpec JSON (sample)

```json
{
  "pageName": "Home",
  "sections": [
    {"type":"Header","props":{"logoSlot":"logo","nav":["Home","Services","Pricing","Contact"]}},
    {"type":"Hero","props":{"title":"Radiant Skin, Confident You","subtitle":"Advanced med‑spa treatments","cta":"Book a Free Consult","imageSlot":"hero"}},
    {"type":"Features","props":{"items":[{"title":"FDA‑approved","desc":"Safe & effective"},{"title":"Expert Team","desc":"Board‑certified clinicians"}]}},
    {"type":"Testimonials","props":{}},
    {"type":"CTA","props":{"title":"See Our Packages","cta":"View Pricing"}},
    {"type":"Footer","props":{}}
  ],
  "assets": {"logo":"assetId:logo.png","hero":"assetId:hero.jpg"}
}
```

### 7.5 Node Tagging (pluginData)

* `role`: `logo|hero|section:<index>|component:<name>`
* `pinned`: `true|false`
* `tokenRef`: references token ids for colors/typography so Sync Styles can re‑apply.

---

## 8) Backend Logic (LangGraph Agents)

1. **Requirements Agent** – aggregates chat into a normalized **Brief** (industry, tone, goals, key sections, CTA).
2. **Reference Agent** – calls Firecrawl; extracts tokens/patterns; outputs **DesignSystem** with confidence.
3. **Planner Agent** – produces **PageSpec** from Brief + DesignSystem; ensures accessibility (contrast, text sizes).
4. **Composer Agent** – expands components into concrete node plans; prepares **ImageSlot** prompts.
5. **Image Agent** – when enabled, generates images on Replicate (or provider) and returns URLs/bytes.
6. **Verifier Agent** – validates spec (no missing tokens, sensible hierarchy); estimates node count.
7. **Diff Agent** – when regenerating, respects **pinned** nodes; keeps system constants.

---

## 9) Image Handling

* **Uploads**: files go to S3 via signed URL; backend returns accessible URLs; plugin loads via `createImageAsync(url)`.
* **Replicate** (toggle ON): for each slot, backend builds prompt with industry + palette + lighting/style; waits for output URL; plugin swaps fills.
* **Fallbacks**: if image fails, revert to placeholder; show toast.

---

## 10) CORS & Networking Strategy

* Figma plugin UI runs in a **null‑origin iframe**; many APIs block this. Prefer **calling backend only** from the UI; backend then calls Firecrawl/Replicate and returns results.
* Manifest `networkAccess.allowedDomains` should include the backend domain (and ws/wss if streaming).
* Timeouts and retries implemented server‑side; client uses exponential backoff.

---

## 11) Security & Compliance

* Validate and sanitize all user URLs and uploads.
* Respect robots/no‑scrape where applicable for reference analysis.
* Store minimal project metadata; encrypt secrets; rotate keys.
* Add allow‑list to restrict plugin use to Growth99 team if required.

---

## 12) UX Spec (Plugin UI)

* **Left pane (chat)**: conversation, quick chips (Industry, Tone, Pages), model selector, toggles, file dropzone.
* **Right pane (actions)**: Generate First Page, Redesign, Generate Remaining Pages, Sync Styles.
* **Progress indicators** with granular steps (Reference → Plan → Compose → Render → Images).
* **Inspector** for DesignSystem tokens (editable) with "Apply".

---

## 13) Acceptance Criteria

* Provide a brief + logo + 1 reference URL → **Home page** renders with header (logo placed), hero (image slot populated per toggle), 3+ sections, footer.
* **Redesign** preserves header/footer and pinned hero, while changing layout/style within system bounds.
* **Generate Remaining Pages** creates at least 5 other pages using same tokens/components.
* Toggling **AI Images ON** generates non‑empty images for hero + at least one section.
* Switching **model** changes copy/layout diversity without breaking tokens.

---

## 14) Deliverables

* Figma plugin (TS) with build scripts (Vite/ESBuild).
* FastAPI service (Dockerized) with LangGraph flows, Firecrawl client, model adapters, Replicate integration.
* Schema‑validated contracts (Pydantic).
* Seed templates for common sections/components.
* README with environment setup; `.env.example` for keys.

---

## 15) Implementation Checklist (Engineer‑Ready)

### Plugin

* [ ] `manifest.json` with `networkAccess.allowedDomains` (backend, ws/wss)
* [ ] `code.ts` scaffolding: show UI, message handlers, undo group wrappers
* [ ] `ui.tsx` chat app with model selector, toggles, uploads, progress
* [ ] `storage.ts` (clientStorage + shared plugin data)
* [ ] Renderers: auto‑layout, text, image, components
* [ ] Node tagging & pinning, selective regenerate
* [ ] Error toasts, retry paths

### Backend

* [ ] FastAPI + LangGraph project; Pydantic models for Brief/DesignSystem/PageSpec/SiteSpec
* [ ] Firecrawl client with prompts/schemas for style extraction
* [ ] LLM adapters + registry (OpenAI, Anthropic, Gemini, local)
* [ ] Image service: Replicate (sync or webhook)
* [ ] AuthN (API key) + rate limiting + logging
* [ ] Tests: unit (schemas), integration (end‑to‑end mock), golden PageSpec snapshots

---

## 16) Provided Context to the Coding Agent

* Attach **official Figma Plugin API docs** and relevant pages (manifest, messaging, clientStorage, images, auto‑layout).
* Provide Firecrawl docs (/extract, /scrape) usage for reference analysis.
* Provide Replicate HTTP API docs for image generation.

---

## 17) Appendix – Sample Snippets

### A. manifest.json (template)

```json
{
  "name": "Growth99 – AI Page Generator",
  "id": "com.cognio.growth99.ai-pages",
  "api": "1.0.0",
  "main": "dist/code.js",
  "ui": "dist/ui.html",
  "editorType": ["figma"],
  "networkAccess": {
    "allowedDomains": [
      "https://api.growth99.dev",
      "wss://api.growth99.dev",
      "https://api.firecrawl.dev",
      "https://replicate.com",
      "https://*.replicate.delivery" // model output CDN
    ],
    "reasoning": "Plugin UI calls our backend; backend fans out to Firecrawl & Replicate."
  }
}
```

### B. UI→Backend: Create Page Plan

```ts
await fetch(`${BASE}/v1/page/plan`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
  body: JSON.stringify({ designSystem, pageKind: 'Home', brief, pinnedSlots })
})
```

### C. Core: Render PageSpec

```ts
function renderPage(spec: PageSpec) {
  const page = figma.createPage();
  page.name = spec.pageName;
  const root = createAutoLayoutFrame({ name: 'Container', width: 1200 });
  page.appendChild(root);
  for (const section of spec.sections) {
    const node = renderSection(section); // creates frames/text/images
    root.appendChild(node);
  }
}
```

### D. Image Replacement (toggle ON)

```ts
for (const slot of imageSlots) {
  const node = findNodeByPluginData({ role: slot.role });
  if (!node) continue;
  const img = await figma.createImageAsync(slot.url);
  node.fills = [{ type: 'IMAGE', scaleMode: 'FILL', imageHash: img.hash }];
}
```

---

## 18) Future Enhancements

* Export tokens/components to a design system library file.
* Variable fonts & color variables integration.
* Real‑time co‑edit prompts per selection (contextual generation).
* Template marketplace for vertical‑specific blocks.
