#!/usr/bin/env python3
"""
Direct test of the LLM response to debug JSON parsing
"""

import asyncio
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

async def test_llm_response():
    """Test LLM response directly"""
    
    # Create LLM client
    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0.7, max_tokens=4000)
    
    print("Testing LLM response directly...")
    print("=" * 50)
    
    # Simple test prompt - escape curly braces!
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Return your response as a JSON object."),
        ("human", """Return a simple JSON object with these fields:
        {{
            "name": "Test",
            "value": 123,
            "status": "active"
        }}
        
        Return ONLY the JSON object, no other text.""")
    ])
    
    try:
        formatted_prompt = prompt.format_messages()
        response = await llm.ainvoke(formatted_prompt)
        print(f"LLM Response:\n{response.content}")
        print(f"Response type: {type(response.content)}")
        print(f"Response length: {len(response.content)} characters")
        
        # Try to parse as JSON
        import json
        parsed = json.loads(response.content)
        print(f"\n✓ Successfully parsed JSON:")
        print(json.dumps(parsed, indent=2))
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm_response())