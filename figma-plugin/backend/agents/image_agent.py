"""
Image Agent - Generates AI images via Replicate
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import replicate
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from backend.agents.composer_agent import ImageSlot

class GeneratedImage(BaseModel):
    role: str
    url: str
    prompt_used: str
    style_applied: str

class ImageAgent:
    def __init__(self, llm_client: ChatOpenAI):
        self.llm = llm_client
        self.replicate_client = replicate.Client(api_token=os.getenv("REPLICATE_API_TOKEN")) if os.getenv("REPLICATE_API_TOKEN") else None
        
        self.prompt_enhancement_template = ChatPromptTemplate.from_messages([
            ("system", """You are a prompt engineer for healthcare marketing imagery.
            
            Enhance image generation prompts for professional medical/healthcare marketing materials.
            
            GUIDELINES:
            - Professional, clean, modern aesthetic
            - Diverse representation when showing people
            - Medical accuracy and sensitivity
            - Brand-appropriate styling
            - High-quality commercial photography look
            
            OUTPUT GUIDELINES:
            - Start with subject/scene description
            - Add style and quality modifiers
            - Include technical photography terms
            - Add negative prompts for unwanted elements
            
            Keep prompts under 200 characters for optimal results."""),
            ("human", "Base prompt: {base_prompt}\nStyle hints: {style_hints}\nBusiness context: {business_context}")
        ])

    async def generate_images(
        self, 
        image_slots: List[ImageSlot], 
        business_context: str = "",
        model: str = "stability-ai/sdxl:7762fd07cf82c948538e41f63f77d685e02b063e37e496e96eefd46c929f9bdc"
    ) -> List[GeneratedImage]:
        """Generate images for all slots using Replicate"""
        
        if not self.replicate_client:
            return self._generate_placeholder_images(image_slots)
        
        generated_images = []
        
        for slot in image_slots:
            try:
                # Enhance prompt using GPT-5
                enhanced_prompt = await self._enhance_prompt(slot, business_context)
                
                # Generate image via Replicate
                image_url = await self._generate_single_image(enhanced_prompt, model)
                
                if image_url:
                    generated_images.append(GeneratedImage(
                        role=slot.role,
                        url=image_url,
                        prompt_used=enhanced_prompt,
                        style_applied=str(slot.styleHints)
                    ))
                else:
                    # Fallback to placeholder
                    generated_images.append(self._create_placeholder_image(slot))
                    
            except Exception as e:
                print(f"Failed to generate image for {slot.role}: {e}")
                generated_images.append(self._create_placeholder_image(slot))
        
        return generated_images
    
    async def _enhance_prompt(self, slot: ImageSlot, business_context: str) -> str:
        """Enhance image prompt using GPT-5"""
        
        try:
            formatted_prompt = self.prompt_enhancement_template.format_messages(
                base_prompt=slot.prompt,
                style_hints=slot.styleHints,
                business_context=business_context
            )
            response = await self.llm.ainvoke(formatted_prompt)
            return response.content.strip()
        except Exception as e:
            print(f"Failed to enhance prompt: {e}")
            return self._get_default_enhanced_prompt(slot, business_context)
    
    def _get_default_enhanced_prompt(self, slot: ImageSlot, business_context: str) -> str:
        """Get default enhanced prompt for healthcare context"""
        
        base_prompts = {
            "hero": f"Professional {business_context} facility interior, modern clean design, natural lighting, high-end medical equipment, professional photography style, 8k resolution",
            "logo": f"Professional {business_context} logo design, clean minimal modern style, medical cross or wellness symbol, trustworthy brand identity",
            "team": f"Professional {business_context} team photo, diverse medical professionals in white coats, friendly approachable smiles, modern medical facility background",
            "service": f"Professional {business_context} treatment or procedure, clean modern medical environment, professional equipment, reassuring atmosphere",
            "about": f"Modern {business_context} facility exterior or interior, professional medical building, clean architecture, welcoming entrance"
        }
        
        # Get base prompt for role or use the slot's prompt
        enhanced = base_prompts.get(slot.role, slot.prompt)
        
        # Add quality modifiers
        enhanced += ", professional commercial photography, high resolution, clean composition, professional lighting"
        
        # Add negative prompts
        enhanced += " --negative low quality, blurry, amateur, unprofessional, cluttered, dark, intimidating"
        
        return enhanced
    
    async def _generate_single_image(self, prompt: str, model: str) -> Optional[str]:
        """Generate single image via Replicate"""
        
        try:
            # Use SDXL for high-quality results
            output = self.replicate_client.run(
                model,
                input={
                    "prompt": prompt,
                    "num_outputs": 1,
                    "aspect_ratio": "16:9",  # Good for hero images
                    "output_format": "jpg",
                    "output_quality": 90,
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5
                }
            )
            
            if output and len(output) > 0:
                return output[0]  # Return first generated image URL
            
        except Exception as e:
            print(f"Replicate generation failed: {e}")
            return None
        
        return None
    
    def _generate_placeholder_images(self, image_slots: List[ImageSlot]) -> List[GeneratedImage]:
        """Generate placeholder images when Replicate is not available"""
        
        placeholders = []
        
        for slot in image_slots:
            placeholder = self._create_placeholder_image(slot)
            placeholders.append(placeholder)
        
        return placeholders
    
    def _create_placeholder_image(self, slot: ImageSlot) -> GeneratedImage:
        """Create placeholder image for slot"""
        
        # Use different placeholder services based on role
        placeholder_urls = {
            "hero": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=600&fit=crop&crop=center",  # Medical facility
            "logo": "https://via.placeholder.com/200x80/2563EB/FFFFFF?text=LOGO",
            "team": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=800&h=600&fit=crop&crop=center",  # Medical team
            "service": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?w=800&h=600&fit=crop&crop=center",  # Medical equipment
            "about": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&h=600&fit=crop&crop=center"   # Modern medical building
        }
        
        placeholder_url = placeholder_urls.get(slot.role, "https://via.placeholder.com/800x600/CCCCCC/666666?text=Image")
        
        return GeneratedImage(
            role=slot.role,
            url=placeholder_url,
            prompt_used=f"Placeholder for: {slot.prompt}",
            style_applied="placeholder"
        )
    
    async def regenerate_image(
        self, 
        slot: ImageSlot, 
        business_context: str = "",
        style_variations: Optional[Dict[str, Any]] = None
    ) -> GeneratedImage:
        """Regenerate single image with variations"""
        
        # Apply style variations to the prompt
        modified_slot = slot.copy()
        if style_variations:
            modified_slot.styleHints.update(style_variations)
        
        # Generate new image
        generated_images = await self.generate_images([modified_slot], business_context)
        
        return generated_images[0] if generated_images else self._create_placeholder_image(slot)
    
    def get_supported_styles(self) -> Dict[str, List[str]]:
        """Get available style options for image generation"""
        
        return {
            "mood": ["professional", "warm", "modern", "luxurious", "clinical", "welcoming"],
            "lighting": ["natural", "soft", "bright", "dramatic", "ambient"],
            "composition": ["centered", "rule-of-thirds", "wide-angle", "close-up", "environmental"],
            "color_palette": ["neutral", "blue-medical", "green-wellness", "warm-tones", "high-contrast"],
            "photography_style": ["commercial", "lifestyle", "clinical", "architectural", "portrait"]
        }
    
    def estimate_generation_time(self, num_images: int) -> Dict[str, Any]:
        """Estimate time and cost for image generation"""
        
        # Rough estimates for SDXL
        time_per_image = 30  # seconds
        cost_per_image = 0.05  # USD
        
        return {
            "estimated_time_seconds": num_images * time_per_image,
            "estimated_cost_usd": num_images * cost_per_image,
            "num_images": num_images,
            "model": "stability-ai/sdxl"
        }