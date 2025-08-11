#!/usr/bin/env python3
"""
Test script to verify the new GPT-4o model works correctly
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json

# Load environment variables
load_dotenv()

async def test_new_model():
    """Test the new GPT-4o model"""
    
    # Create LLM client with new model
    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0.7, max_tokens=4000)
    
    print("Testing GPT-4o-2024-08-06 model...")
    print("=" * 50)
    
    # Test simple JSON generation
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Return your response as a JSON object."),
        ("human", """Return a simple JSON object with these fields:
        {{
            "name": "Test",
            "value": 123,
            "status": "active",
            "colors": {{
                "primary": "#2563EB",
                "secondary": "#059669"
            }}
        }}
        
        Return ONLY the JSON object, no other text.""")
    ])
    
    try:
        formatted_prompt = prompt.format_messages()
        response = await llm.ainvoke(formatted_prompt)
        print(f"Raw Response:\n{response.content}\n")
        
        # Extract JSON (handle code blocks)
        content = response.content.strip()
        if content.startswith('```json'):
            # Remove markdown code block markers
            content = content.replace('```json', '').replace('```', '').strip()
        elif content.startswith('```'):
            content = content.replace('```', '').strip()
        
        # Parse JSON
        parsed = json.loads(content)
        print("✓ Successfully parsed JSON:")
        print(json.dumps(parsed, indent=2))
        
        # Test design analysis
        print("\n" + "=" * 50)
        print("Testing design analysis...")
        
        design_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a design expert. Create a design analysis and return ONLY a JSON object with this structure:
            {{
                "primary_color": "#hex",
                "aesthetic_style": "modern|luxury|clinical",
                "mood": "professional|premium|trustworthy",
                "design_reasoning": "Brief explanation"
            }}"""),
            ("human", "Create a design analysis for a luxury medical spa")
        ])
        
        design_formatted = design_prompt.format_messages()
        design_response = await llm.ainvoke(design_formatted)
        print(f"Design Response:\n{design_response.content}\n")
        
        # Extract and parse design JSON
        design_content = design_response.content.strip()
        if design_content.startswith('```json'):
            design_content = design_content.replace('```json', '').replace('```', '').strip()
        elif design_content.startswith('```'):
            design_content = design_content.replace('```', '').strip()
            
        design_parsed = json.loads(design_content)
        print("✓ Successfully parsed design JSON:")
        print(json.dumps(design_parsed, indent=2))
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_new_model())
    print(f"\nTest {'PASSED' if success else 'FAILED'}")