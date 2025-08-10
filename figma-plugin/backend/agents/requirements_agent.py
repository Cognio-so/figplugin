"""
Requirements Agent - Aggregates chat into normalized Brief
Growth99 focus: Healthcare, medical spas, wellness clinics
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

class Brief(BaseModel):
    industry: str
    business_type: str  # med-spa, dental, wellness, etc.
    tone: str  # professional, warm, modern, etc.
    key_services: List[str]
    target_audience: str
    primary_cta: str
    sections_requested: List[str]
    brand_personality: Optional[str] = None
    special_requirements: Optional[str] = None

class RequirementsAgent:
    def __init__(self, llm_client: ChatOpenAI):
        self.llm = llm_client
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a requirements analyst for Growth99, specializing in healthcare and wellness marketing websites.
            
            Your job is to analyze chat conversations and extract a structured brief for website page generation.
            
            Focus areas:
            - Medical spas, dental offices, wellness clinics, hospitals, healthcare practices
            - Professional yet approachable tone
            - Trust-building elements (certifications, testimonials, expertise)
            - Clear calls-to-action (book appointment, consultation, etc.)
            
            Extract and normalize the following information:
            - Industry/Business type
            - Tone and brand personality 
            - Key services to highlight
            - Target audience
            - Primary call-to-action
            - Requested page sections
            
            Return a structured brief that will guide page generation."""),
            ("human", "Chat history and requirements:\n{chat_input}")
        ])

    async def process(self, chat_history: List[Dict[str, str]], user_input: str) -> Brief:
        """Process chat history and current input into normalized brief"""
        
        # Combine chat history into context
        chat_context = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in chat_history
        ])
        
        combined_input = f"Previous chat:\n{chat_context}\n\nLatest input:\n{user_input}"
        
        # Generate brief using GPT-5
        formatted_prompt = self.prompt.format_messages(chat_input=combined_input)
        response = await self.llm.ainvoke(formatted_prompt)
        
        # Parse response into structured brief
        brief_data = self._parse_brief_response(response.content, user_input)
        
        return Brief(**brief_data)
    
    def _parse_brief_response(self, llm_response: str, fallback_input: str) -> Dict[str, Any]:
        """Parse LLM response into brief structure with Growth99 defaults"""
        
        # Use GPT-5 to extract structured data
        extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract structured data from the brief analysis. 
            Return ONLY a JSON object with these exact keys:
            {
                "industry": "healthcare/wellness/medical",
                "business_type": "med-spa/dental/wellness/clinic/hospital", 
                "tone": "professional/warm/modern/luxurious",
                "key_services": ["service1", "service2"],
                "target_audience": "description",
                "primary_cta": "Book Appointment/Schedule Consultation/etc",
                "sections_requested": ["Hero", "Services", "About", "Contact"],
                "brand_personality": "optional description",
                "special_requirements": "optional notes"
            }"""),
            ("human", f"Brief analysis:\n{llm_response}\n\nOriginal input:\n{fallback_input}")
        ])
        
        try:
            formatted_prompt = extraction_prompt.format_messages()
            extraction_response = self.llm.invoke(formatted_prompt)
            import json
            return json.loads(extraction_response.content)
        except:
            # Fallback to Growth99 healthcare defaults
            return {
                "industry": "healthcare",
                "business_type": "medical spa", 
                "tone": "professional",
                "key_services": ["Advanced Treatments", "Expert Care", "Personalized Service"],
                "target_audience": "Health-conscious individuals seeking professional care",
                "primary_cta": "Book a Free Consultation",
                "sections_requested": ["Hero", "Services", "About", "Testimonials", "Contact"],
                "brand_personality": "Professional, trustworthy, and caring",
                "special_requirements": None
            }