from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# LangChain LLM imports
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

load_dotenv()

app = FastAPI(
    title="Growth99 Figma Plugin API (MVP)",
    description="MVP Backend API for Growth99 AI Page Generator Figma Plugin",
    version="1.0.0"
)

# Configure CORS for Figma plugin (MVP - permissive)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

# LLM clients using LangChain partner libraries
def get_llm_client(model_name: str = "gpt-5", temperature: float = 0.7):
    """Get LLM client using LangChain partner libraries - GPT-5 as default"""
    if model_name.startswith("gpt-"):
        return ChatOpenAI(model=model_name, temperature=temperature)
    elif model_name.startswith("claude-"):
        return ChatAnthropic(model=model_name, temperature=temperature)
    elif model_name.startswith("gemini-"):
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
    elif model_name.startswith("mixtral-") or model_name.startswith("llama-"):
        return ChatGroq(model=model_name, temperature=temperature)
    else:
        # Default to OpenAI GPT-5
        return ChatOpenAI(model="gpt-5", temperature=temperature)

# Pydantic models
class SessionStartRequest(BaseModel):
    userId: Optional[str] = None
    figmaFileId: Optional[str] = None

class SessionResponse(BaseModel):
    projectId: str
    userId: str

class ReferenceAnalyzeRequest(BaseModel):
    urls: List[str]
    brief: Optional[str] = None

class DesignSystem(BaseModel):
    colors: Dict[str, str]
    typography: Dict[str, Any]
    spacingScale: List[int]
    radius: Dict[str, int]
    grid: Dict[str, Any]
    components: Dict[str, Any]

class PagePlanRequest(BaseModel):
    designSystem: DesignSystem
    pageKind: str
    constraints: Optional[Dict[str, Any]] = None
    pinnedSlots: Optional[List[str]] = None
    brief: str

class Section(BaseModel):
    type: str
    props: Dict[str, Any]

class PageSpec(BaseModel):
    pageName: str
    sections: List[Section]
    assets: Dict[str, str]

class ImageSlot(BaseModel):
    role: str
    prompt: str
    styleHints: Optional[Dict[str, Any]] = None

class ImageGenerateRequest(BaseModel):
    slots: List[ImageSlot]
    provider: str = "replicate"
    model: str = "stability-ai/sdxl"

# API Routes
@app.get("/")
async def root():
    return {"message": "Growth99 Figma Plugin API", "version": "1.0.0"}

@app.post("/v1/session/start", response_model=SessionResponse)
async def start_session(request: SessionStartRequest):
    """Initialize a new session for the plugin (MVP - simplified)"""
    project_id = f"proj_{request.figmaFileId or 'default'}"
    user_id = request.userId or "user_default"
    
    # Store in Supabase if available
    if supabase:
        try:
            supabase.table("sessions").insert({
                "project_id": project_id,
                "user_id": user_id,
                "figma_file_id": request.figmaFileId,
                "created_at": "now()"
            }).execute()
        except Exception as e:
            print(f"Failed to store session in Supabase: {e}")
    
    return SessionResponse(
        projectId=project_id,
        userId=user_id
    )

@app.post("/v1/reference/analyze", response_model=DesignSystem)
async def analyze_reference(request: ReferenceAnalyzeRequest):
    """Analyze reference URLs and extract design system using LangGraph agents"""
    
    try:
        from .agents.reference_agent import ReferenceAgent
        
        llm_client = get_llm_client()
        reference_agent = ReferenceAgent(llm_client)
        
        # Analyze URLs using Firecrawl + GPT-5
        design_system = await reference_agent.analyze_references(
            request.urls,
            request.brief or ""
        )
        
        return design_system
        
    except Exception as e:
        print(f"Reference analysis failed: {e}")
        # Fallback to default healthcare design system
        from .agents.reference_agent import ReferenceAgent
        llm_client = get_llm_client()
        agent = ReferenceAgent(llm_client)
        return agent._get_default_healthcare_design_system()

@app.post("/v1/page/plan", response_model=PageSpec)
async def plan_page(request: PagePlanRequest):
    """Generate a page specification using LangGraph planner agent"""
    
    try:
        from .agents.planner_agent import PlannerAgent
        from .agents.requirements_agent import Brief
        
        llm_client = get_llm_client()
        planner_agent = PlannerAgent(llm_client)
        
        # Convert request to Brief format (simplified for direct API call)
        brief = Brief(
            industry="healthcare",
            business_type="medical practice",
            tone="professional",
            key_services=["Professional Care", "Expert Service"],
            target_audience="Healthcare patients",
            primary_cta="Book Appointment",
            sections_requested=["Header", "Hero", "Services", "Contact"]
        )
        
        # Generate page specification
        page_spec = await planner_agent.create_page_spec(
            brief,
            request.designSystem,
            request.pageKind
        )
        
        return page_spec
        
    except Exception as e:
        print(f"Page planning failed: {e}")
        # Fallback to default page spec
        return PageSpec(
            pageName=f"{request.pageKind} Page",
            sections=[
                Section(type="Header", props={"nav": ["Home", "Services", "Contact"]}),
                Section(type="Hero", props={
                    "title": "Professional Healthcare",
                    "subtitle": "Expert care you can trust",
                    "cta": "Book Appointment"
                }),
                Section(type="Services", props={
                    "title": "Our Services",
                    "services": [{"name": "General Care", "description": "Comprehensive healthcare services"}]
                }),
                Section(type="Footer", props={})
            ],
            assets={}
        )

@app.post("/v1/images/generate")
async def generate_images(request: ImageGenerateRequest):
    """Generate AI images using Replicate integration"""
    
    try:
        from .agents.image_agent import ImageAgent
        
        llm_client = get_llm_client()
        image_agent = ImageAgent(llm_client)
        
        # Generate images using Replicate
        generated_images = await image_agent.generate_images(
            request.slots,
            business_context="healthcare medical practice"
        )
        
        # Format response
        result = {}
        for image in generated_images:
            result[image.role] = image.url
        
        return result
        
    except Exception as e:
        print(f"Image generation failed: {e}")
        # Fallback to placeholder URLs
        result = {}
        for slot in request.slots:
            result[slot.role] = f"https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=600&h=400&fit=crop&text={slot.role}"
        return result

# New comprehensive workflow endpoint
@app.post("/v1/generate/complete")
async def generate_complete_page(request: Dict[str, Any]):
    """Complete page generation using LangGraph workflow"""
    
    try:
        from .workflows.page_generation_workflow import create_workflow
        
        # Extract request parameters
        chat_history = request.get("chat_history", [])
        user_input = request.get("user_input", "Create a professional healthcare website")
        reference_urls = request.get("reference_urls", [])
        page_type = request.get("page_type", "Home")
        use_ai_images = request.get("use_ai_images", False)
        model_name = request.get("model_name", "gpt-5")
        
        # Create and execute workflow
        workflow = create_workflow(model_name)
        
        result = await workflow.generate_page(
            chat_history=chat_history,
            user_input=user_input,
            reference_urls=reference_urls,
            page_type=page_type,
            use_ai_images=use_ai_images,
            model_name=model_name
        )
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Complete page generation failed: {str(e)}",
            "final_page_spec": None
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)