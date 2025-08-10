# Growth99 Figma Plugin Backend (MVP)

FastAPI backend service for the Growth99 AI Page Generator Figma Plugin, optimized for MVP development.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and Supabase credentials
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   Or with uvicorn:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## MVP Features

- **Supabase Integration**: Simple database with sessions table
- **LangChain Partner Libraries**: Uses langchain-openai, langchain-anthropic, langchain-google-genai, langchain-groq
- **Simplified Security**: No JWT tokens or complex auth (MVP focused)
- **Ready for LangGraph**: Structure prepared for LangGraph agents implementation

## API Endpoints

- `POST /v1/session/start` - Initialize plugin session (stores in Supabase)
- `POST /v1/reference/analyze` - Analyze reference URLs with Firecrawl  
- `POST /v1/page/plan` - Generate page specifications using LangChain LLMs
- `POST /v1/images/generate` - Generate AI images via Replicate

## Required Setup

### API Keys
- **OpenAI/Anthropic/Google/Groq**: For LLM-based page planning via LangChain
- **Firecrawl**: For reference URL analysis
- **Replicate**: For AI image generation

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

## LangChain Integration

The backend uses LangChain partner libraries for all LLM interactions:
- `langchain-openai` for GPT models
- `langchain-anthropic` for Claude models  
- `langchain-google-genai` for Gemini models
- `langchain-groq` for Mixtral/Llama models

Example usage (ready in `get_llm_client()` function):
```python
llm = get_llm_client("gpt-4")
response = llm.invoke("Create a homepage for a medical spa")
```

## Development

- Server runs on `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Simplified MVP setup - focus on functionality over security

## Next Implementation Steps

1. **LangGraph Agents**: Replace mock responses with actual LangGraph workflows
2. **Firecrawl Integration**: Connect reference analysis to extract design tokens
3. **Replicate Integration**: Connect image generation pipeline
4. **Enhanced Supabase Schema**: Add tables for projects, design systems, generated pages