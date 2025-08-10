# Growth99 Figma Plugin - Setup & Testing Guide

This guide will walk you through setting up and testing the Growth99 AI Page Generator plugin from scratch.

## Prerequisites

- **Figma Desktop App** (required for plugin development)
- **Node.js** (v16+ recommended)
- **Python** (3.8+ recommended)
- **API Keys** (see below)

## Step 1: Clone and Setup Project

```bash
# Navigate to your project directory
cd /Users/apple/Documents/growth/plugin/figplugin/figma-plugin

# Install Node dependencies for the plugin
npm install
```

## Step 2: Configure Backend Environment

### 2.1 Install Python Dependencies

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2.2 Setup API Keys

Create `.env` file in the backend directory:

```bash
cp .env.example .env
```

Edit `.env` with your actual API keys:

```env
# Required for AI generation
OPENAI_API_KEY=sk-your-actual-openai-key-here  # For GPT-5/GPT-4

# Optional but recommended
ANTHROPIC_API_KEY=your-anthropic-key            # For Claude fallback
GOOGLE_API_KEY=your-google-key                  # For Gemini
GROQ_API_KEY=your-groq-key                      # For Mixtral/Llama

# For enhanced features
REPLICATE_API_TOKEN=your-replicate-token        # For AI image generation
FIRECRAWL_API_KEY=your-firecrawl-key           # For reference URL analysis

# Supabase (optional for MVP)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### 2.3 Setup Supabase Database (Optional)

If using Supabase, run this SQL in your Supabase dashboard:

```sql
-- Create sessions table
create table if not exists sessions (
  id uuid default gen_random_uuid() primary key,
  project_id text not null,
  user_id text not null,
  figma_file_id text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

## Step 3: Start the Backend Server

```bash
# In the backend directory with virtual environment activated
python main.py

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Test the backend is running:
```bash
# In a new terminal
curl http://localhost:8000/
# Should return: {"message":"Growth99 Figma Plugin API","version":"1.0.0"}
```

View API documentation:
- Open browser to `http://localhost:8000/docs`

## Step 4: Build the Figma Plugin

```bash
# Return to main plugin directory
cd /Users/apple/Documents/growth/plugin/figplugin/figma-plugin

# Build the plugin
npm run build

# You should see: "Build complete."
```

## Step 5: Load Plugin in Figma

1. **Open Figma Desktop App**
2. Create a new design file or open an existing one
3. Go to **Menu → Plugins → Development → Import plugin from manifest...**
4. Navigate to your plugin directory
5. Select `dist/manifest.json`
6. Click "Open"

The plugin should now appear in your Plugins menu as "Growth99 – AI Page Generator"

## Step 6: Test the Plugin

### Basic Test (Without Backend)

1. Run the plugin: **Plugins → Development → Growth99 – AI Page Generator**
2. Click **"Generate First Page"** button
3. The plugin will create a sample healthcare page using local generation

### Full AI Test (With Backend)

1. Ensure backend is running (`python main.py` in backend directory)
2. Run the plugin in Figma
3. Enter a brief in the chat area (optional):
   - Example: "Create a modern medical spa homepage with services, testimonials, and booking CTA"
4. Click **"Generate First Page"**
5. Watch the progress indicators:
   - "connecting-backend" - Establishing API connection
   - "rendering-page" - AI generating page specification
   - Page creation in Figma

## Step 7: Testing Different Features

### Test Reference URL Analysis
```javascript
// The plugin will analyze design from URLs
// Add URLs in the UI or modify the request in code.ts:
reference_urls: ["https://example-medical-site.com"]
```

### Test AI Image Generation
```javascript
// Enable AI images in the request:
use_ai_images: true  // Requires REPLICATE_API_TOKEN
```

### Test Different AI Models
```javascript
// Change model in the request:
model_name: "gpt-4"     // or "claude-3.5-sonnet", "gemini-1.5-pro"
```

## Step 8: Monitor and Debug

### Backend Logs
Watch the terminal running `python main.py` for:
- Incoming requests
- Agent processing steps
- Any errors or warnings

### Figma Console
1. In Figma: **Plugins → Development → Open Console**
2. Watch for:
   - "Backend connection failed" - Backend not running
   - "Rendering node" messages - Successful generation
   - Error stack traces

### API Testing
Use the FastAPI docs at `http://localhost:8000/docs` to:
- Test individual endpoints
- View request/response schemas
- Debug API issues

## Common Issues and Solutions

### Issue: "Backend unavailable"
**Solution**: 
- Ensure backend is running: `python main.py`
- Check backend logs for errors
- Verify API keys in `.env`

### Issue: "No module named 'fastapi'"
**Solution**:
```bash
pip install -r requirements.txt
# Or individually:
pip install fastapi uvicorn
```

### Issue: Plugin doesn't appear in Figma
**Solution**:
- Rebuild: `npm run build`
- Re-import manifest in Figma
- Restart Figma if needed

### Issue: "Failed to render node"
**Solution**:
- Check Figma console for specific errors
- Ensure you're in a Figma design file (not FigJam)
- Try with a simpler prompt first

## Testing Checklist

- [ ] Backend starts without errors
- [ ] API docs accessible at `/docs`
- [ ] Plugin builds successfully
- [ ] Plugin loads in Figma
- [ ] Local generation works (without backend)
- [ ] Backend connection successful
- [ ] AI generates page specification
- [ ] Figma nodes render correctly
- [ ] Progress indicators show
- [ ] Error handling works (stop backend, try again)

## Next Steps

1. **Test with real API keys** for full AI capabilities
2. **Try different prompts** for various healthcare businesses
3. **Upload reference URLs** for style extraction
4. **Enable AI images** for custom imagery
5. **Monitor performance** and optimize as needed

## Support

- Backend API docs: `http://localhost:8000/docs`
- Figma Plugin Console: Plugins → Development → Open Console
- Check `backend/CLAUDE.md` for backend architecture
- Check `Function.md` for detailed technical documentation