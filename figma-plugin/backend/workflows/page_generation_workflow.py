"""
LangGraph Workflow - Orchestrates all agents for page generation
"""

from typing import Dict, Any, List, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

from backend.agents.requirements_agent import RequirementsAgent, Brief
from backend.agents.reference_agent import ReferenceAgent, DesignSystem
from backend.agents.planner_agent import PlannerAgent, PageSpec
from backend.agents.design_analysis_agent import DesignAnalysisAgent, DesignAnalysis
from backend.agents.composer_agent import AIComposerAgent, GeneratedPageComponents
from backend.agents.image_agent import ImageAgent, GeneratedImage
from backend.agents.verifier_agent import VerifierAgent, VerificationResult

class WorkflowState(TypedDict):
    # Input
    chat_history: List[Dict[str, str]]
    user_input: str
    reference_urls: List[str]
    page_type: str
    use_ai_images: bool
    model_name: str
    
    # Agent outputs
    brief: Optional[Brief]
    design_system: Optional[DesignSystem]
    design_analysis: Optional[DesignAnalysis]
    page_spec: Optional[PageSpec]
    composed_spec: Optional[GeneratedPageComponents]
    generated_images: Optional[List[GeneratedImage]]
    verification_result: Optional[VerificationResult]
    
    # Final output
    final_page_spec: Optional[Dict[str, Any]]
    error: Optional[str]

class PageGenerationWorkflow:
    def __init__(self, llm_client: ChatOpenAI):
        self.llm = llm_client
        
        # Initialize all agents
        self.requirements_agent = RequirementsAgent(llm_client)
        self.reference_agent = ReferenceAgent(llm_client)
        self.design_analysis_agent = DesignAnalysisAgent(llm_client)
        self.planner_agent = PlannerAgent(llm_client)
        self.ai_composer_agent = AIComposerAgent(llm_client)
        self.image_agent = ImageAgent(llm_client)
        self.verifier_agent = VerifierAgent(llm_client)
        
        # Build workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (agents)
        workflow.add_node("requirements", self._requirements_step)
        workflow.add_node("reference_analysis", self._reference_analysis_step)
        workflow.add_node("design_analysis", self._design_analysis_step)
        workflow.add_node("planning", self._planning_step)
        workflow.add_node("ai_composition", self._ai_composition_step)
        workflow.add_node("image_generation", self._image_generation_step)
        workflow.add_node("verification", self._verification_step)
        workflow.add_node("finalization", self._finalization_step)
        
        # Define workflow edges
        workflow.add_edge(START, "requirements")
        workflow.add_edge("requirements", "reference_analysis")
        workflow.add_edge("reference_analysis", "design_analysis")
        workflow.add_edge("design_analysis", "planning")
        workflow.add_edge("planning", "ai_composition")
        workflow.add_edge("ai_composition", "image_generation")
        workflow.add_edge("image_generation", "verification")
        workflow.add_edge("verification", "finalization")
        workflow.add_edge("finalization", END)
        
        return workflow.compile()
    
    async def generate_page(
        self,
        chat_history: List[Dict[str, str]],
        user_input: str,
        reference_urls: List[str] = None,
        page_type: str = "Home",
        use_ai_images: bool = False,
        model_name: str = "gpt-4o-2024-08-06"
    ) -> Dict[str, Any]:
        """Execute complete page generation workflow"""
        
        initial_state: WorkflowState = {
            "chat_history": chat_history or [],
            "user_input": user_input,
            "reference_urls": reference_urls or [],
            "page_type": page_type,
            "use_ai_images": use_ai_images,
            "model_name": model_name,
            "brief": None,
            "design_system": None,
            "design_analysis": None,
            "page_spec": None,
            "composed_spec": None,
            "generated_images": None,
            "verification_result": None,
            "final_page_spec": None,
            "error": None
        }
        
        try:
            # Execute workflow
            final_state = await self.workflow.ainvoke(initial_state)
            return self._format_output(final_state)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "final_page_spec": None
            }
    
    async def _requirements_step(self, state: WorkflowState) -> WorkflowState:
        """Step 1: Process requirements into structured brief"""
        
        try:
            brief = await self.requirements_agent.process(
                state["chat_history"],
                state["user_input"]
            )
            state["brief"] = brief
            
        except Exception as e:
            state["error"] = f"Requirements processing failed: {str(e)}"
        
        return state
    
    async def _reference_analysis_step(self, state: WorkflowState) -> WorkflowState:
        """Step 2: Analyze reference URLs for design system extraction"""
        
        if state["error"]:
            return state
        
        try:
            brief_context = f"{state['brief'].business_type} {state['brief'].industry}" if state["brief"] else ""
            
            design_system = await self.reference_agent.analyze_references(
                state["reference_urls"],
                brief_context
            )
            state["design_system"] = design_system
            
        except Exception as e:
            state["error"] = f"Reference analysis failed: {str(e)}"
        
        return state
    
    async def _design_analysis_step(self, state: WorkflowState) -> WorkflowState:
        """Step 2.5: AI-driven design analysis based on user requirements and references"""
        
        if state["error"]:
            return state
        
        try:
            # Analyze user requirements and references to generate custom design system
            reference_analysis_text = ""
            if state["design_system"]:
                reference_analysis_text = f"Reference design system extracted with {len(state['reference_urls'])} URLs analyzed"
            
            design_analysis = await self.design_analysis_agent.analyze_design_requirements(
                state["user_input"],
                state["reference_urls"],
                reference_analysis_text
            )
            
            state["design_analysis"] = design_analysis
            
        except Exception as e:
            state["error"] = f"Design analysis failed: {str(e)}"
        
        return state
    
    async def _planning_step(self, state: WorkflowState) -> WorkflowState:
        """Step 3: Create page specification from brief and design system"""
        
        if state["error"]:
            return state
        
        try:
            page_spec = await self.planner_agent.create_page_spec(
                state["brief"],
                state["design_system"],
                state["page_type"]
            )
            state["page_spec"] = page_spec
            
        except Exception as e:
            state["error"] = f"Page planning failed: {str(e)}"
        
        return state
    
    async def _ai_composition_step(self, state: WorkflowState) -> WorkflowState:
        """Step 4: AI-driven composition of dynamic Figma components"""
        
        if state["error"]:
            return state
        
        try:
            # Generate dynamic components based on AI design analysis
            composed_spec = await self.ai_composer_agent.generate_figma_components(
                state["page_spec"],
                state["design_analysis"],
                state["user_input"]
            )
            state["composed_spec"] = composed_spec
            
        except Exception as e:
            state["error"] = f"AI composition failed: {str(e)}"
        
        return state
    
    async def _image_generation_step(self, state: WorkflowState) -> WorkflowState:
        """Step 5: Generate AI images if requested"""
        
        if state["error"]:
            return state
        
        try:
            if state["use_ai_images"] and state["composed_spec"].imageSlots:
                business_context = f"{state['brief'].business_type} {state['brief'].industry}" if state['brief'] else state["user_input"]
                
                generated_images = await self.image_agent.generate_images(
                    state["composed_spec"].imageSlots,
                    business_context
                )
                state["generated_images"] = generated_images
            else:
                state["generated_images"] = []
                
        except Exception as e:
            # Don't fail workflow for image generation errors
            print(f"Image generation failed: {e}")
            state["generated_images"] = []
        
        return state
    
    async def _verification_step(self, state: WorkflowState) -> WorkflowState:
        """Step 6: Verify page specification quality and compliance"""
        
        if state["error"]:
            return state
        
        try:
            verification_result = await self.verifier_agent.verify_page(
                state["composed_spec"],
                state["design_system"],
                state["brief"].target_audience
            )
            state["verification_result"] = verification_result
            
        except Exception as e:
            # Don't fail for verification errors, but log them
            print(f"Verification failed: {e}")
            state["verification_result"] = None
        
        return state
    
    async def _finalization_step(self, state: WorkflowState) -> WorkflowState:
        """Step 7: Finalize output format for Figma plugin"""
        
        if state["error"]:
            return state
        
        try:
            # Create final page specification for Figma plugin
            final_spec = {
                "pageName": state["composed_spec"].pageName,
                "sections": self._convert_to_plugin_format(state["page_spec"].sections) if state["page_spec"] else [],
                "assets": state["page_spec"].assets if state["page_spec"] else {},
                "figmaComponents": [comp.__dict__ for comp in state["composed_spec"].components],
                "images": [img.__dict__ for img in state["generated_images"]] if state["generated_images"] else [],
                "metadata": {
                    "totalNodes": state["composed_spec"].totalNodes,
                    "designReasoning": state["composed_spec"].designReasoning,
                    "brief": state["brief"].__dict__ if state["brief"] else None,
                    "designSystem": state["design_system"].__dict__ if state["design_system"] else None,
                    "designAnalysis": state["design_analysis"].__dict__ if state["design_analysis"] else None,
                    "verification": state["verification_result"].__dict__ if state["verification_result"] else None
                }
            }
            
            state["final_page_spec"] = final_spec
            
        except Exception as e:
            state["error"] = f"Finalization failed: {str(e)}"
        
        return state
    
    def _convert_to_plugin_format(self, sections) -> List[Dict[str, Any]]:
        """Convert sections to plugin-compatible format"""
        
        plugin_sections = []
        for section in sections:
            plugin_sections.append({
                "type": section.type,
                "props": section.props
            })
        
        return plugin_sections
    
    def _format_output(self, final_state: WorkflowState) -> Dict[str, Any]:
        """Format final workflow output"""
        
        if final_state["error"]:
            return {
                "success": False,
                "error": final_state["error"],
                "final_page_spec": None
            }
        
        return {
            "success": True,
            "final_page_spec": final_state["final_page_spec"],
            "verification": final_state["verification_result"].__dict__ if final_state["verification_result"] else None,
            "images_generated": len(final_state["generated_images"]) if final_state["generated_images"] else 0
        }

# Workflow instance for easy reuse
def create_workflow(model_name: str = "gpt-4o-2024-08-06") -> PageGenerationWorkflow:
    """Create and return a configured workflow instance"""
    
    llm_client = ChatOpenAI(model=model_name, temperature=0.7, max_tokens=4000)
    return PageGenerationWorkflow(llm_client)