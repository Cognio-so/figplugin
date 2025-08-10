"""
Reference Agent - Analyzes URLs using Firecrawl and extracts design systems
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from firecrawl import FirecrawlApp

class DesignSystem(BaseModel):
    colors: Dict[str, str]
    typography: Dict[str, Any] 
    spacingScale: List[int]
    radius: Dict[str, int]
    grid: Dict[str, Any]
    components: Dict[str, Any]
    confidence: float = 0.8

class ReferenceAgent:
    def __init__(self, llm_client: ChatOpenAI):
        self.llm = llm_client
        self.firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY")) if os.getenv("FIRECRAWL_API_KEY") else None
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a design system analyst for Growth99 healthcare websites.
            
            Analyze the provided website content and extract design system tokens:
            
            1. COLOR PALETTE:
               - Primary brand colors (usually 2-3 main colors)
               - Text colors (headings, body, muted)
               - Background colors
               - Accent colors for CTAs
            
            2. TYPOGRAPHY:
               - Font families used
               - Heading hierarchy (sizes, weights)
               - Body text specifications
               - Letter spacing, line heights
            
            3. SPACING & LAYOUT:
               - Common spacing values (8px, 16px, 24px, etc.)
               - Container widths
               - Grid systems
               - Section padding patterns
            
            4. UI COMPONENTS:
               - Button styles (radius, padding, hover states)
               - Card designs
               - Navigation patterns
               - Form elements
            
            Focus on healthcare/medical aesthetics: clean, trustworthy, professional.
            
            Return a structured design system that can be applied to new pages."""),
            ("human", "Website content to analyze:\n{website_content}")
        ])

    async def analyze_references(self, urls: List[str], brief_context: str = "") -> DesignSystem:
        """Analyze reference URLs and extract design system"""
        
        if not urls:
            return self._get_default_healthcare_design_system()
        
        # Scrape URLs using Firecrawl
        scraped_content = []
        for url in urls:
            try:
                if self.firecrawl:
                    result = self.firecrawl.scrape_url(url, {
                        'formats': ['markdown'],
                        'includeTags': ['style', 'link'],
                        'excludeTags': ['script'],
                    })
                    scraped_content.append({
                        'url': url,
                        'content': result.get('markdown', ''),
                        'metadata': result.get('metadata', {})
                    })
                else:
                    # Fallback without Firecrawl
                    scraped_content.append({
                        'url': url,
                        'content': f"URL: {url} (Firecrawl not configured)",
                        'metadata': {}
                    })
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                continue
        
        if not scraped_content:
            return self._get_default_healthcare_design_system()
        
        # Combine content for analysis
        combined_content = "\n\n".join([
            f"URL: {item['url']}\n{item['content']}" for item in scraped_content
        ])
        
        # Add brief context for better analysis
        if brief_context:
            combined_content = f"Target business context: {brief_context}\n\n{combined_content}"
        
        # Analyze with GPT-5
        formatted_prompt = self.analysis_prompt.format_messages(website_content=combined_content)
        response = await self.llm.ainvoke(formatted_prompt)
        
        # Parse into design system
        design_system_data = self._parse_design_system(response.content)
        
        return DesignSystem(**design_system_data)
    
    def _parse_design_system(self, llm_response: str) -> Dict[str, Any]:
        """Parse LLM response into structured design system"""
        
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract a structured design system from the analysis.
            Return ONLY a JSON object with this exact structure:
            {
                "colors": {
                    "primary": "#hexcode",
                    "secondary": "#hexcode", 
                    "text": "#hexcode",
                    "textMuted": "#hexcode",
                    "background": "#hexcode",
                    "accent": "#hexcode"
                },
                "typography": {
                    "display": {"family": "Font Name", "size": 44, "weight": "700", "lineHeight": 1.2},
                    "h1": {"family": "Font Name", "size": 36, "weight": "700"},
                    "h2": {"family": "Font Name", "size": 28, "weight": "600"},
                    "h3": {"family": "Font Name", "size": 24, "weight": "600"},
                    "body": {"family": "Font Name", "size": 16, "lineHeight": 1.5, "weight": "400"},
                    "small": {"size": 14, "lineHeight": 1.4}
                },
                "spacingScale": [8, 12, 16, 24, 32, 48, 64, 96],
                "radius": {"sm": 4, "md": 8, "lg": 12, "xl": 16},
                "grid": {"container": 1200, "columns": 12, "gutter": 24},
                "components": {
                    "Button": {"radius": 8, "padX": 24, "padY": 12, "weight": "600"},
                    "Card": {"radius": 12, "shadow": "0 4px 12px rgba(0,0,0,0.1)", "padding": 24}
                },
                "confidence": 0.8
            }"""),
            ("human", f"Design analysis to extract:\n{llm_response}")
        ])
        
        try:
            formatted_prompt = extraction_prompt.format_messages()
            extraction_response = self.llm.invoke(formatted_prompt)
            import json
            return json.loads(extraction_response.content)
        except Exception as e:
            print(f"Failed to parse design system: {e}")
            return self._get_default_healthcare_design_system().__dict__
    
    def _get_default_healthcare_design_system(self) -> DesignSystem:
        """Default professional healthcare design system"""
        return DesignSystem(
            colors={
                "primary": "#2563EB",           # Professional blue
                "primaryDark": "#1D4ED8",       # Darker blue for gradients
                "primaryLight": "#3B82F6",      # Lighter blue for accents
                "secondary": "#059669",          # Medical green
                "secondaryDark": "#047857",     # Darker green
                "text": "#1F2937",              # Dark gray
                "textMuted": "#6B7280",         # Medium gray
                "textLight": "#9CA3AF",         # Light gray
                "background": "#FFFFFF",         # White
                "backgroundSecondary": "#F9FAFB", # Very light gray
                "backgroundLight": "#F8FAFC",    # Ultra light gray
                "accent": "#DC2626",             # Medical red for CTAs
                "accentLight": "#EF4444",        # Lighter red
                "border": "#E5E7EB",             # Border color
                "success": "#10B981",            # Success green
                "warning": "#F59E0B",            # Warning amber
                "gradient1": "#667eea",          # Gradient start
                "gradient2": "#764ba2"           # Gradient end
            },
            typography={
                "display": {"family": "Inter", "size": 44, "weight": "700", "lineHeight": 1.2},
                "h1": {"family": "Inter", "size": 36, "weight": "700"},
                "h2": {"family": "Inter", "size": 28, "weight": "600"},
                "h3": {"family": "Inter", "size": 24, "weight": "600"},
                "body": {"family": "Inter", "size": 16, "lineHeight": 1.5, "weight": "400"},
                "small": {"size": 14, "lineHeight": 1.4}
            },
            spacingScale=[8, 12, 16, 24, 32, 48, 64, 96],
            radius={"sm": 4, "md": 8, "lg": 12, "xl": 16},
            grid={"container": 1200, "columns": 12, "gutter": 24},
            components={
                "Button": {
                    "radius": 12, 
                    "padX": 32, 
                    "padY": 16, 
                    "weight": "700",
                    "shadow": "0 4px 16px rgba(37, 99, 235, 0.4)",
                    "hoverScale": 1.02
                },
                "Card": {
                    "radius": 16, 
                    "shadow": "0 8px 32px rgba(0,0,0,0.12)", 
                    "padding": 32,
                    "borderWidth": 1,
                    "hoverShadow": "0 12px 48px rgba(0,0,0,0.15)"
                },
                "Nav": {
                    "height": 88, 
                    "padding": 24,
                    "shadow": "0 2px 16px rgba(0,0,0,0.08)",
                    "backdropBlur": 12
                },
                "Hero": {
                    "minHeight": 600, 
                    "padding": 80,
                    "gradient": True,
                    "overlay": "0.1"
                },
                "Section": {
                    "padding": 96,
                    "spacing": 48
                },
                "Icon": {
                    "size": 24,
                    "stroke": 2,
                    "color": "primary"
                }
            },
            confidence=0.9
        )