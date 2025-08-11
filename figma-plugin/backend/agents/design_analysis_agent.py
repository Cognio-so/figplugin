"""
Design Analysis Agent - Analyzes user requirements and generates custom design systems
"""

import json
import re
from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import BaseModel

class DesignAnalysis(BaseModel):
    """AI-generated design analysis based on user requirements"""
    
    # Color palette analysis
    primary_color: str  # Hex color
    secondary_color: str  # Hex color
    accent_color: str  # Hex color
    text_color: str  # Hex color
    text_muted_color: str  # Hex color
    background_color: str  # Hex color
    surface_color: str  # Hex color
    
    # Typography analysis
    heading_font_family: str
    heading_font_weight: str
    body_font_family: str
    body_font_weight: str
    h1_size: int
    h2_size: int
    h3_size: int
    body_size: int
    small_size: int
    
    # Spacing and layout
    base_spacing: int
    section_padding: int
    component_padding: int
    border_radius: int
    container_width: int
    
    # Visual style decisions
    aesthetic_style: str  # modern, minimal, luxury, clinical, warm, tech, classic
    mood: str  # professional, friendly, premium, trustworthy, innovative
    visual_weight: str  # light, medium, heavy
    shadow_intensity: str  # none, subtle, medium, strong
    
    # Component styling
    button_style: str  # flat, rounded, pill, square
    card_style: str  # flat, elevated, outlined, glass
    header_style: str  # simple, elevated, transparent, gradient
    
    # Reasoning
    design_reasoning: str
    target_audience_analysis: str
    brand_personality: str

class DesignAnalysisAgent:
    def __init__(self, llm_client: ChatOpenAI):
        self.llm = llm_client
        
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert UI/UX designer and brand strategist. Analyze the user's requirements and create a comprehensive design system that perfectly matches their needs.

ANALYSIS PROCESS:
1. **Industry Context**: Understand the business type, industry standards, and user expectations
2. **Target Audience**: Analyze who will use this website and what appeals to them
3. **Brand Personality**: Determine the tone, mood, and aesthetic that best represents the brand
4. **Reference Analysis**: If reference URLs are provided, analyze their design patterns, colors, typography, and overall aesthetic
5. **Design Psychology**: Apply color psychology, typography principles, and layout best practices

KEY CONSIDERATIONS:
- Healthcare/Medical: Clean, trustworthy, professional, calming colors (blues, greens), high contrast
- Luxury/Premium: Sophisticated, elegant, premium feel, neutral palettes with gold/silver accents
- Tech/SaaS: Modern, innovative, gradients, contemporary fonts, high contrast
- Wellness/Spa: Calming, natural, earth tones, soft gradients, relaxing aesthetic
- Corporate/B2B: Professional, authoritative, conservative colors, structured layouts
- Creative/Agency: Bold, unique, experimental, vibrant colors, distinctive typography

DESIGN SYSTEM REQUIREMENTS:
- Colors must work together harmoniously
- Typography must be highly readable and appropriate for the industry
- Spacing must create proper visual hierarchy
- Visual style must match the target audience expectations
- All elements must work cohesively to create a professional result

Return your analysis as a structured JSON object with specific, actionable design decisions."""),
            
            ("human", """Analyze the following requirements and create a custom design system:

USER INPUT: {user_input}

REFERENCE URLS: {reference_urls}

REFERENCE ANALYSIS: {reference_analysis}

Create a comprehensive design system that perfectly matches these requirements. Consider:
1. What colors, fonts, and spacing would appeal to this specific audience?
2. What visual style would build trust and credibility for this business?
3. How can the design differentiate this brand while meeting industry expectations?
4. What design decisions would optimize for conversions and user engagement?

Provide specific hex codes, font names, pixel values, and detailed reasoning for each decision.""")
        ])

    async def analyze_design_requirements(
        self,
        user_input: str,
        reference_urls: List[str] = None,
        reference_analysis: str = ""
    ) -> DesignAnalysis:
        """Analyze user requirements and generate custom design system"""
        
        try:
            # Format inputs
            urls_text = ", ".join(reference_urls) if reference_urls else "None provided"
            reference_text = reference_analysis if reference_analysis else "No reference analysis available"
            
            # Generate design analysis
            formatted_prompt = self.analysis_prompt.format_messages(
                user_input=user_input,
                reference_urls=urls_text,
                reference_analysis=reference_text
            )
            response = await self.llm.ainvoke(formatted_prompt)
            
            # Parse response into structured data
            design_data = await self._parse_design_analysis(response.content, user_input)
            
            return DesignAnalysis(**design_data)
            
        except Exception as e:
            print(f"Design analysis failed: {e}")
            return self._get_fallback_design_analysis(user_input)

    async def _parse_design_analysis(self, llm_response: str, user_input: str) -> Dict[str, Any]:
        """Parse LLM response into structured design analysis"""
        
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract a structured design analysis from the provided text.

Return ONLY a JSON object with this exact structure:
{{
    "primary_color": "#hex",
    "secondary_color": "#hex", 
    "accent_color": "#hex",
    "text_color": "#hex",
    "text_muted_color": "#hex",
    "background_color": "#hex",
    "surface_color": "#hex",
    "heading_font_family": "Font Name",
    "heading_font_weight": "Bold",
    "body_font_family": "Font Name", 
    "body_font_weight": "Regular",
    "h1_size": 48,
    "h2_size": 36,
    "h3_size": 24,
    "body_size": 16,
    "small_size": 14,
    "base_spacing": 8,
    "section_padding": 80,
    "component_padding": 24,
    "border_radius": 8,
    "container_width": 1200,
    "aesthetic_style": "modern|minimal|luxury|clinical|warm|tech|classic",
    "mood": "professional|friendly|premium|trustworthy|innovative",
    "visual_weight": "light|medium|heavy",
    "shadow_intensity": "none|subtle|medium|strong",
    "button_style": "flat|rounded|pill|square",
    "card_style": "flat|elevated|outlined|glass",
    "header_style": "simple|elevated|transparent|gradient",
    "design_reasoning": "Explanation of design decisions",
    "target_audience_analysis": "Analysis of target audience",
    "brand_personality": "Brand personality description"
}}

All colors must be valid hex codes. All fonts must be web-safe or Google Fonts. All sizes must be in pixels."""),
            ("human", f"Design analysis to extract:\n{llm_response}\n\nOriginal user input: {user_input}")
        ])
        
        try:
            formatted_prompt = extraction_prompt.format_messages()
            extraction_response = await self.llm.ainvoke(formatted_prompt)
            
            # Clean the response to extract JSON
            json_text = self._extract_json_from_text(extraction_response.content)
            
            # Log the extracted JSON for debugging
            print(f"Extracted JSON length: {len(json_text)} characters")
            
            # Try to parse the JSON
            try:
                return json.loads(json_text)
            except json.JSONDecodeError as je:
                print(f"JSON decode error: {je}")
                print(f"Failed JSON text (first 500 chars): {json_text[:500]}")
                # Try to fix common JSON issues
                json_text = json_text.replace("'", '"')  # Replace single quotes with double
                json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas
                json_text = re.sub(r',\s*]', ']', json_text)  # Remove trailing commas in arrays
                return json.loads(json_text)
                
        except Exception as e:
            print(f"Failed to parse design analysis: {str(e)}")
            print(f"Raw LLM response (first 500 chars): {extraction_response.content[:500] if 'extraction_response' in locals() else 'No response'}")
            return self._get_fallback_design_data(user_input)

    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON object from text response"""
        # Try multiple methods to extract JSON
        
        # Method 1: Look for JSON between ```json and ``` markers
        json_code_match = re.search(r'```json\s*([\s\S]*?)\s*```', text)
        if json_code_match:
            return json_code_match.group(1).strip()
        
        # Method 2: Look for JSON between ``` markers
        code_match = re.search(r'```\s*([\s\S]*?)\s*```', text)
        if code_match:
            potential_json = code_match.group(1).strip()
            if potential_json.startswith('{'):
                return potential_json
        
        # Method 3: Find the first { and last } for a complete JSON object
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
            potential_json = text[first_brace:last_brace + 1]
            # Basic validation - check if it has quotes
            if '"' in potential_json:
                return potential_json
        
        # Method 4: If the entire text starts with {, assume it's JSON
        trimmed = text.strip()
        if trimmed.startswith('{') and trimmed.endswith('}'):
            return trimmed
        
        # If no JSON found, return the original text
        return text

    def _get_fallback_design_analysis(self, user_input: str) -> DesignAnalysis:
        """Fallback design analysis if AI fails"""
        return DesignAnalysis(**self._get_fallback_design_data(user_input))

    def _get_fallback_design_data(self, user_input: str) -> Dict[str, Any]:
        """Generate fallback design based on user input keywords"""
        
        # Analyze user input for industry/type
        text_lower = user_input.lower()
        
        if any(word in text_lower for word in ['medical', 'healthcare', 'clinic', 'hospital', 'doctor', 'health']):
            return self._get_healthcare_design()
        elif any(word in text_lower for word in ['luxury', 'premium', 'high-end', 'exclusive', 'elegant']):
            return self._get_luxury_design()
        elif any(word in text_lower for word in ['tech', 'software', 'saas', 'app', 'digital', 'startup']):
            return self._get_tech_design()
        elif any(word in text_lower for word in ['spa', 'wellness', 'beauty', 'relaxation', 'calm']):
            return self._get_wellness_design()
        else:
            return self._get_professional_design()

    def _get_healthcare_design(self) -> Dict[str, Any]:
        """Healthcare-focused design system"""
        return {
            "primary_color": "#2563EB",
            "secondary_color": "#059669",
            "accent_color": "#DC2626",
            "text_color": "#1F2937",
            "text_muted_color": "#6B7280",
            "background_color": "#FFFFFF",
            "surface_color": "#F9FAFB",
            "heading_font_family": "Inter",
            "heading_font_weight": "Bold",
            "body_font_family": "Inter",
            "body_font_weight": "Regular",
            "h1_size": 48,
            "h2_size": 36,
            "h3_size": 24,
            "body_size": 16,
            "small_size": 14,
            "base_spacing": 8,
            "section_padding": 80,
            "component_padding": 24,
            "border_radius": 8,
            "container_width": 1200,
            "aesthetic_style": "clinical",
            "mood": "trustworthy",
            "visual_weight": "medium",
            "shadow_intensity": "subtle",
            "button_style": "rounded",
            "card_style": "elevated",
            "header_style": "simple",
            "design_reasoning": "Clean, professional healthcare design that builds trust and credibility",
            "target_audience_analysis": "Patients and healthcare consumers seeking reliable medical services",
            "brand_personality": "Professional, trustworthy, caring, and authoritative"
        }

    def _get_luxury_design(self) -> Dict[str, Any]:
        """Luxury-focused design system"""
        return {
            "primary_color": "#1F2937",
            "secondary_color": "#D4AF37",
            "accent_color": "#EF4444",
            "text_color": "#111827",
            "text_muted_color": "#6B7280",
            "background_color": "#FFFFFF",
            "surface_color": "#FAFAFA",
            "heading_font_family": "Playfair Display",
            "heading_font_weight": "Bold",
            "body_font_family": "Inter",
            "body_font_weight": "Regular",
            "h1_size": 56,
            "h2_size": 40,
            "h3_size": 28,
            "body_size": 18,
            "small_size": 14,
            "base_spacing": 12,
            "section_padding": 120,
            "component_padding": 32,
            "border_radius": 4,
            "container_width": 1400,
            "aesthetic_style": "luxury",
            "mood": "premium",
            "visual_weight": "heavy",
            "shadow_intensity": "medium",
            "button_style": "square",
            "card_style": "outlined",
            "header_style": "elevated",
            "design_reasoning": "Sophisticated luxury design with premium materials and elegant typography",
            "target_audience_analysis": "High-income individuals seeking premium services and experiences",
            "brand_personality": "Exclusive, sophisticated, premium, and authoritative"
        }

    def _get_tech_design(self) -> Dict[str, Any]:
        """Tech-focused design system"""
        return {
            "primary_color": "#3B82F6",
            "secondary_color": "#8B5CF6",
            "accent_color": "#10B981",
            "text_color": "#111827",
            "text_muted_color": "#6B7280",
            "background_color": "#FFFFFF",
            "surface_color": "#F8FAFC",
            "heading_font_family": "Inter",
            "heading_font_weight": "Bold",
            "body_font_family": "Inter",
            "body_font_weight": "Regular",
            "h1_size": 52,
            "h2_size": 36,
            "h3_size": 24,
            "body_size": 16,
            "small_size": 14,
            "base_spacing": 8,
            "section_padding": 96,
            "component_padding": 24,
            "border_radius": 12,
            "container_width": 1200,
            "aesthetic_style": "modern",
            "mood": "innovative",
            "visual_weight": "medium",
            "shadow_intensity": "medium",
            "button_style": "rounded",
            "card_style": "elevated",
            "header_style": "gradient",
            "design_reasoning": "Modern tech design with innovation-focused aesthetics and clean interface",
            "target_audience_analysis": "Tech-savvy users and businesses seeking modern digital solutions",
            "brand_personality": "Innovative, modern, reliable, and forward-thinking"
        }

    def _get_wellness_design(self) -> Dict[str, Any]:
        """Wellness-focused design system"""
        return {
            "primary_color": "#059669",
            "secondary_color": "#0D9488",
            "accent_color": "#F59E0B",
            "text_color": "#1F2937",
            "text_muted_color": "#6B7280",
            "background_color": "#FFFFFF",
            "surface_color": "#F0FDF4",
            "heading_font_family": "Inter",
            "heading_font_weight": "SemiBold",
            "body_font_family": "Inter",
            "body_font_weight": "Regular",
            "h1_size": 48,
            "h2_size": 32,
            "h3_size": 24,
            "body_size": 18,
            "small_size": 14,
            "base_spacing": 8,
            "section_padding": 80,
            "component_padding": 32,
            "border_radius": 16,
            "container_width": 1200,
            "aesthetic_style": "warm",
            "mood": "friendly",
            "visual_weight": "light",
            "shadow_intensity": "subtle",
            "button_style": "pill",
            "card_style": "elevated",
            "header_style": "transparent",
            "design_reasoning": "Calming wellness design that promotes relaxation and natural healing",
            "target_audience_analysis": "Health-conscious individuals seeking wellness and spa services",
            "brand_personality": "Caring, natural, peaceful, and nurturing"
        }

    def _get_professional_design(self) -> Dict[str, Any]:
        """Generic professional design system"""
        return {
            "primary_color": "#1F2937",
            "secondary_color": "#3B82F6",
            "accent_color": "#EF4444",
            "text_color": "#111827",
            "text_muted_color": "#6B7280",
            "background_color": "#FFFFFF",
            "surface_color": "#F9FAFB",
            "heading_font_family": "Inter",
            "heading_font_weight": "Bold",
            "body_font_family": "Inter",
            "body_font_weight": "Regular",
            "h1_size": 48,
            "h2_size": 32,
            "h3_size": 24,
            "body_size": 16,
            "small_size": 14,
            "base_spacing": 8,
            "section_padding": 80,
            "component_padding": 24,
            "border_radius": 8,
            "container_width": 1200,
            "aesthetic_style": "modern",
            "mood": "professional",
            "visual_weight": "medium",
            "shadow_intensity": "subtle",
            "button_style": "rounded",
            "card_style": "elevated",
            "header_style": "simple",
            "design_reasoning": "Clean, professional design suitable for business and corporate applications",
            "target_audience_analysis": "General business audience seeking professional services",
            "brand_personality": "Professional, reliable, competent, and trustworthy"
        }