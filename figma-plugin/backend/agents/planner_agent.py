"""
Planner Agent - Creates PageSpec from Brief + DesignSystem
Specialized for Growth99 healthcare layouts
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from backend.agents.requirements_agent import Brief
from backend.agents.reference_agent import DesignSystem

class Section(BaseModel):
    type: str
    props: Dict[str, Any]

class PageSpec(BaseModel):
    pageName: str
    sections: List[Section]
    assets: Dict[str, str]

class PlannerAgent:
    def __init__(self, llm_client: ChatOpenAI):
        self.llm = llm_client
        
        self.planning_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a page layout planner for Growth99 healthcare websites.

            Create detailed page specifications that will be rendered in Figma.
            
            DESIGN EXCELLENCE PRINCIPLES:
            1. Visual Hierarchy - Bold headlines, clear typography scales, strategic use of color
            2. Rich Visual Elements - Professional imagery, gradients, shadows, modern cards
            3. Sophisticated Layout - Asymmetrical layouts, whitespace management, depth
            4. Brand Consistency - Cohesive color palette, consistent spacing, polished components
            5. Modern Aesthetics - Contemporary design trends, smooth animations, micro-interactions
            6. Trust & Credibility - Professional polish, social proof, certifications
            7. Conversion Optimization - Strategic CTAs, visual flow, user journey
            
            VISUAL ENHANCEMENT GUIDELINES:
            - Use gradient backgrounds and overlays for depth
            - Apply subtle shadows and elevation for components
            - Create visual interest with asymmetrical layouts
            - Employ rich color schemes with proper contrast
            - Include decorative elements and icons
            - Design with professional photography placeholders
            - Apply consistent rounded corners and modern styling
            
            ENHANCED SECTION TYPES WITH RICH VISUALS:
            - Header: Premium navigation with gradient background, logo, contact info, CTA button
            - Hero: Split-screen with large imagery, gradient overlays, bold typography, multiple CTAs
            - Services: Card grid with icons, hover effects, rich descriptions, pricing hints
            - About: Team showcase with professional photos, credentials, story with visual elements
            - Features: Icon-driven benefits with illustrations, statistics, visual proof points
            - Testimonials: Photo testimonials, star ratings, video testimonials, review cards
            - BeforeAfter: Interactive image comparisons, transformation galleries
            - CTA: Compelling action sections with urgency, benefits, contact methods
            - FAQ: Expandable cards with search, visual icons
            - Contact: Interactive maps, contact forms, office photos, team availability
            - Footer: Rich footer with multiple columns, social proof, certifications
            - Statistics: Number counters, progress bars, achievement displays
            - Gallery: Image showcases, before/after galleries, portfolio displays
            
            DESIGN QUALITY REQUIREMENTS:
            1. Create visually stunning layouts that rival premium website designs
            2. Include rich visual elements: gradients, shadows, professional imagery
            3. Plan sophisticated component interactions and visual hierarchy
            4. Design with mobile-first responsive principles
            5. Include micro-animations and hover effects specifications
            6. Plan comprehensive color schemes with semantic meaning
            7. Specify high-quality typography with proper scales and weights
            8. Include decorative elements and visual interest points
            
            REFERENCE URL INTEGRATION:
            When reference URLs are provided, extract and adapt their:
            - Color palettes and brand aesthetics
            - Layout patterns and visual hierarchy  
            - Component styles and interactions
            - Typography choices and spacing
            - Image treatment and visual elements
            
            Return a complete page specification with detailed props for each section that will create a visually impressive, professional design."""),
            ("human", """Create a page layout for:

Business Brief:
{brief}

Design System:
{design_system}

Page Type: {page_type}
Special Requirements: {requirements}""")
        ])

    async def create_page_spec(
        self, 
        brief: Brief, 
        design_system: DesignSystem, 
        page_type: str = "Home",
        pinned_slots: Optional[List[str]] = None,
        special_requirements: Optional[str] = None
    ) -> PageSpec:
        """Create page specification from brief and design system"""
        
        # Format inputs for prompt
        brief_text = self._format_brief(brief)
        design_text = self._format_design_system(design_system)
        requirements_text = special_requirements or "None"
        
        # Generate page specification
        formatted_prompt = self.planning_prompt.format_messages(
            brief=brief_text,
            design_system=design_text,
            page_type=page_type,
            requirements=requirements_text
        )
        response = await self.llm.ainvoke(formatted_prompt)
        
        # Parse response into structured PageSpec
        page_spec_data = await self._parse_page_spec(response.content, brief, page_type)
        
        return PageSpec(**page_spec_data)
    
    def _format_brief(self, brief: Brief) -> str:
        """Format brief for prompt context"""
        return f"""
Industry: {brief.industry}
Business Type: {brief.business_type}
Tone: {brief.tone}
Key Services: {', '.join(brief.key_services)}
Target Audience: {brief.target_audience}
Primary CTA: {brief.primary_cta}
Requested Sections: {', '.join(brief.sections_requested)}
Brand Personality: {brief.brand_personality or 'Not specified'}
"""
    
    def _format_design_system(self, design_system: DesignSystem) -> str:
        """Format design system for prompt context"""
        return f"""
Primary Color: {design_system.colors.get('primary', '#2563EB')}
Text Color: {design_system.colors.get('text', '#1F2937')}
Font Family: {design_system.typography.get('body', {}).get('family', 'Inter')}
Button Style: {design_system.components.get('Button', {})}
Spacing Scale: {design_system.spacingScale[:5]}
"""
    
    async def _parse_page_spec(self, llm_response: str, brief: Brief, page_type: str) -> Dict[str, Any]:
        """Parse LLM response into structured PageSpec"""
        
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract a structured page specification from the layout plan.
            
            Return ONLY a JSON object with this exact structure:
            {{
                "pageName": "Page Name",
                "sections": [
                    {{
                        "type": "Header",
                        "props": {{
                            "logo": true,
                            "nav": ["Home", "Services", "About", "Contact"],
                            "phone": "+1 (555) 123-4567",
                            "cta": "Book Now"
                        }}
                    }},
                    {{
                        "type": "Hero", 
                        "props": {{
                            "title": "Main Headline",
                            "subtitle": "Supporting text",
                            "cta": "Primary Button",
                            "ctaSecondary": "Secondary Button",
                            "imageSlot": "hero",
                            "variant": "split|centered|fullwidth"
                        }}
                    }}
                ],
                "assets": {{
                    "logo": "logo",
                    "hero": "hero",
                    "about": "team"
                }}
            }}
            
            Use healthcare-appropriate copy and CTAs."""),
            ("human", f"Layout plan to extract:\n{llm_response}\n\nBusiness type: {brief.business_type}")
        ])
        
        try:
            formatted_prompt = extraction_prompt.format_messages()
            extraction_response = await self.llm.ainvoke(formatted_prompt)
            import json
            import re
            
            # Extract JSON from the response
            content = extraction_response.content
            
            # Try multiple methods to extract JSON
            # Method 1: Look for JSON between ```json and ``` markers
            json_code_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
            if json_code_match:
                json_text = json_code_match.group(1).strip()
            else:
                # Method 2: Look for JSON between ``` markers
                code_match = re.search(r'```\s*([\s\S]*?)\s*```', content)
                if code_match:
                    json_text = code_match.group(1).strip()
                else:
                    # Method 3: Find the first { and last }
                    first_brace = content.find('{')
                    last_brace = content.rfind('}')
                    if first_brace != -1 and last_brace != -1:
                        json_text = content[first_brace:last_brace + 1]
                    else:
                        # Method 4: Assume entire content is JSON
                        json_text = content.strip()
            
            # Log for debugging
            print(f"Extracted page spec JSON length: {len(json_text)} characters")
            
            # Try to parse the JSON
            try:
                return json.loads(json_text)
            except json.JSONDecodeError as je:
                print(f"JSON decode error in page spec: {je}")
                print(f"Failed JSON text (first 500 chars): {json_text[:500]}")
                # Try to fix common JSON issues
                json_text = json_text.replace("'", '"')  # Replace single quotes
                json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas
                json_text = re.sub(r',\s*]', ']', json_text)  # Remove trailing commas in arrays
                return json.loads(json_text)
                
        except Exception as e:
            print(f"Failed to parse page spec: {str(e)}")
            print(f"Raw LLM response (first 500 chars): {extraction_response.content[:500] if 'extraction_response' in locals() else 'No response'}")
            return self._get_default_page_spec(brief, page_type)
    
    def _get_default_page_spec(self, brief: Brief, page_type: str) -> Dict[str, Any]:
        """Default page specification for healthcare sites"""
        
        # Healthcare-specific sections based on business type
        sections = []
        
        # Header (always included)
        sections.append({
            "type": "Header",
            "props": {
                "logo": True,
                "nav": ["Home", "Services", "About", "Contact"],
                "phone": "+1 (555) 123-4567", 
                "cta": brief.primary_cta
            }
        })
        
        # Hero section
        hero_title = self._get_hero_title(brief.business_type)
        sections.append({
            "type": "Hero",
            "props": {
                "title": hero_title,
                "subtitle": f"Professional {brief.business_type} services with expert care",
                "cta": brief.primary_cta,
                "ctaSecondary": "Learn More",
                "imageSlot": "hero",
                "variant": "split"
            }
        })
        
        # Services section
        sections.append({
            "type": "Services",
            "props": {
                "title": "Our Services",
                "subtitle": "Comprehensive care tailored to your needs",
                "services": [
                    {"name": service, "description": f"Professional {service.lower()} with expert care"}
                    for service in brief.key_services
                ]
            }
        })
        
        # About section
        sections.append({
            "type": "About",
            "props": {
                "title": "Expert Care You Can Trust",
                "content": f"Our experienced team provides the highest quality {brief.business_type} services.",
                "imageSlot": "team",
                "credentials": ["Board Certified", "Years of Experience", "Latest Technology"]
            }
        })
        
        # Testimonials
        sections.append({
            "type": "Testimonials", 
            "props": {
                "title": "What Our Patients Say",
                "testimonials": [
                    {
                        "quote": "Outstanding care and results. Highly recommend!",
                        "author": "Sarah M.",
                        "rating": 5
                    },
                    {
                        "quote": "Professional staff and excellent service.",
                        "author": "Michael R.", 
                        "rating": 5
                    }
                ]
            }
        })
        
        # CTA section
        sections.append({
            "type": "CTA",
            "props": {
                "title": "Ready to Get Started?",
                "subtitle": "Schedule your appointment today",
                "cta": brief.primary_cta,
                "phone": "+1 (555) 123-4567"
            }
        })
        
        # Footer
        sections.append({
            "type": "Footer",
            "props": {
                "logo": True,
                "address": "123 Medical Plaza, City, ST 12345",
                "phone": "+1 (555) 123-4567",
                "email": "info@practice.com",
                "hours": {
                    "Mon-Fri": "9:00 AM - 6:00 PM",
                    "Sat": "9:00 AM - 3:00 PM",
                    "Sun": "Closed"
                },
                "social": ["facebook", "instagram", "twitter"]
            }
        })
        
        return {
            "pageName": f"{page_type} - {brief.business_type.title()}",
            "sections": sections,
            "assets": {
                "logo": "logo",
                "hero": "hero", 
                "team": "team"
            }
        }
    
    def _get_hero_title(self, business_type: str) -> str:
        """Generate appropriate hero title for business type"""
        titles = {
            "medical spa": "Transform Your Skin, Elevate Your Confidence",
            "med-spa": "Advanced Aesthetics, Personalized Care", 
            "dental": "Your Smile, Our Expertise",
            "wellness": "Holistic Health, Lasting Wellness",
            "clinic": "Comprehensive Care, Exceptional Results",
            "hospital": "Advanced Medicine, Compassionate Care",
            "dermatology": "Healthy Skin, Expert Care",
            "plastic surgery": "Artistry Meets Medicine"
        }
        
        return titles.get(business_type.lower(), "Expert Healthcare, Personalized for You")