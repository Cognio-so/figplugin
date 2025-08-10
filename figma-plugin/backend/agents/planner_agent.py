"""
Planner Agent - Creates PageSpec from Brief + DesignSystem
Specialized for Growth99 healthcare layouts
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .requirements_agent import Brief
from .reference_agent import DesignSystem

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
            
            HEALTHCARE LAYOUT PRINCIPLES:
            1. Trust & Credibility First - Professional header, certifications visible
            2. Clear Value Proposition - Hero section with primary service/benefit
            3. Social Proof - Testimonials, before/after, credentials
            4. Service Clarity - Clear service descriptions with benefits
            5. Easy Action - Prominent, clear call-to-action buttons
            
            AVAILABLE SECTION TYPES:
            - Header: Logo, navigation, contact info
            - Hero: Main headline, subtitle, CTA, hero image/video
            - Services: Service cards with descriptions
            - About: Team, credentials, story
            - Features: Key differentiators, benefits
            - Testimonials: Client reviews, ratings
            - BeforeAfter: Visual proof (for med-spas)
            - CTA: Strong call-to-action section
            - FAQ: Common questions
            - Contact: Location, hours, booking
            - Footer: Links, contact, legal
            
            Consider the business type, target audience, and brand tone.
            Plan sections that build trust and drive conversions.
            
            Return a complete page specification with detailed props for each section."""),
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
        response = await self.llm.ainvoke(
            self.planning_prompt.format(
                brief=brief_text,
                design_system=design_text,
                page_type=page_type,
                requirements=requirements_text
            )
        )
        
        # Parse response into structured PageSpec
        page_spec_data = self._parse_page_spec(response.content, brief, page_type)
        
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
    
    def _parse_page_spec(self, llm_response: str, brief: Brief, page_type: str) -> Dict[str, Any]:
        """Parse LLM response into structured PageSpec"""
        
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract a structured page specification from the layout plan.
            
            Return ONLY a JSON object with this exact structure:
            {
                "pageName": "Page Name",
                "sections": [
                    {
                        "type": "Header",
                        "props": {
                            "logo": true,
                            "nav": ["Home", "Services", "About", "Contact"],
                            "phone": "+1 (555) 123-4567",
                            "cta": "Book Now"
                        }
                    },
                    {
                        "type": "Hero", 
                        "props": {
                            "title": "Main Headline",
                            "subtitle": "Supporting text",
                            "cta": "Primary Button",
                            "ctaSecondary": "Secondary Button",
                            "imageSlot": "hero",
                            "variant": "split|centered|fullwidth"
                        }
                    }
                ],
                "assets": {
                    "logo": "logo",
                    "hero": "hero",
                    "about": "team"
                }
            }
            
            Use healthcare-appropriate copy and CTAs."""),
            ("human", f"Layout plan to extract:\n{llm_response}\n\nBusiness type: {brief.business_type}")
        ])
        
        try:
            extraction_response = self.llm.invoke(extraction_prompt)
            import json
            return json.loads(extraction_response.content)
        except Exception as e:
            print(f"Failed to parse page spec: {e}")
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