# Growth99 Figma Plugin – AI Page Generator

A Figma plugin that generates high-fidelity marketing pages using AI, designed specifically for Growth99's healthcare and wellness clients.

## Features

- **AI-Powered Generation**: Create complete marketing pages from chat briefs
- **Reference Analysis**: Extract design systems from existing websites
- **Brand Asset Integration**: Automatic logo and image placement
- **Multiple LLM Support**: Choose from OpenAI, Anthropic, Google models
- **AI Image Generation**: Optional Replicate integration for custom images
- **Multi-Page Consistency**: Generate entire site systems

## Quick Start

### 1. Plugin Development

```bash
# Install dependencies
npm install

# Build the plugin
npm run build

# Watch for changes during development
npm run watch
```

### 2. Backend Setup

```bash
# Install Python dependencies
npm run backend:install

# Set up environment variables
cd backend
cp .env.example .env
# Edit .env with your API keys

# Start the backend server
npm run backend
```

### 3. Load Plugin in Figma

1. Open Figma Desktop
2. Go to Plugins → Development → Import plugin from manifest
3. Select `dist/manifest.json` from this project
4. The plugin should appear in your Plugins menu

## Project Structure

```
/figma-plugin/
├── src/                    # Plugin source code
│   ├── code.ts            # Main plugin logic
│   ├── ui.tsx             # UI components
│   ├── ui.html            # UI template
│   ├── bridge.ts          # Plugin ↔ UI messaging
│   ├── types.ts           # TypeScript definitions
│   ├── storage.ts         # Data persistence
│   └── renderers/         # Figma node renderers
├── backend/               # FastAPI backend
│   ├── main.py           # API server
│   ├── requirements.txt  # Python dependencies
│   └── .env.example      # Environment template
├── dist/                 # Built plugin files
└── manifest.json         # Figma plugin manifest
```

## Development

### Plugin Development
- Run `npm run watch` to auto-rebuild on changes
- Use Figma's Developer Console for debugging
- Plugin UI runs in an iframe with postMessage communication

### Backend Development
- Backend runs on `http://localhost:8000` by default
- API docs available at `http://localhost:8000/docs`
- Implements FastAPI with automatic OpenAPI documentation

## Configuration

### Environment Variables (Backend)

Copy `backend/.env.example` to `backend/.env` and configure:

- **LLM APIs**: OpenAI, Anthropic, Google, Groq API keys (via LangChain partners)
- **Services**: Firecrawl (reference analysis), Replicate (images)
- **Database**: Supabase URL and anon key

### Plugin Permissions

The plugin manifest includes network access for:
- Backend API (api.growth99.dev)
- Firecrawl API (api.firecrawl.dev)  
- Replicate API (replicate.com)

## Usage

1. **Start Chat**: Open plugin and describe your page requirements
2. **Add References**: Paste URLs of sites with designs you like
3. **Upload Assets**: Add logo and brand images
4. **Generate**: Click "Generate First Page" to create initial design
5. **Iterate**: Use "Redesign" to refine while preserving your edits
6. **Expand**: Generate additional pages with consistent styling

## API Endpoints

- `POST /v1/session/start` - Initialize plugin session
- `POST /v1/reference/analyze` - Extract design tokens from URLs
- `POST /v1/page/plan` - Generate page specifications
- `POST /v1/images/generate` - Create AI images for placeholders

## Architecture

### Plugin (TypeScript)
- **Plugin Core**: Manages Figma scene graph, creates frames and components
- **UI Layer**: Chat interface with model selector and controls
- **Message Bridge**: Handles communication between UI and core

### Backend (Python/FastAPI)
- **LangGraph Agents**: Orchestrate the generation pipeline
- **LangChain Integration**: Uses langchain-openai, langchain-anthropic, langchain-google-genai, langchain-groq
- **Supabase Database**: Simple session and project storage
- **Reference Analysis**: Firecrawl integration for design extraction  
- **Image Generation**: Replicate integration for AI images

## MVP Setup

### Supabase Database
Create a `sessions` table in your Supabase project:
```sql
create table sessions (
  id uuid default gen_random_uuid() primary key,
  project_id text not null,
  user_id text not null,
  figma_file_id text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

## Next Implementation Steps

1. **LangGraph Agents**: Replace mock responses with actual LangGraph workflows
2. **Firecrawl Integration**: Connect reference analysis to extract design tokens
3. **Replicate Integration**: Connect image generation pipeline
4. **Enhanced Supabase Schema**: Add tables for projects, design systems, generated pages

## License

Proprietary - Growth99/Cognio Labs
