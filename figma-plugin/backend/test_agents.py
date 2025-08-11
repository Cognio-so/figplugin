#!/usr/bin/env python3
"""
Test individual agents with new model
"""

import asyncio
import os
import sys
sys.path.insert(0, '/Users/apple/Documents/growth/plugin/figplugin/figma-plugin')

from dotenv import load_dotenv
from backend.agents.design_analysis_agent import DesignAnalysisAgent
from backend.agents.requirements_agent import RequirementsAgent, Brief
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

async def test_agents():
    """Test individual agents"""
    
    print("Testing individual agents with GPT-4o-2024-08-06...")
    print("=" * 60)
    
    # Create LLM client
    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0.7, max_tokens=4000)
    
    try:
        # Test Requirements Agent
        print("1. Testing Requirements Agent...")
        req_agent = RequirementsAgent(llm)
        brief = await req_agent.process(
            chat_history=[],
            user_input="Create a modern medical spa website with luxury aesthetics"
        )
        print(f"✓ Brief created: {brief.business_type} in {brief.industry}")
        print(f"  Services: {brief.key_services[:3]}...")
        
        # Test Design Analysis Agent
        print("\n2. Testing Design Analysis Agent...")
        design_agent = DesignAnalysisAgent(llm)
        analysis = await design_agent.analyze_design_requirements(
            user_input="Create a modern medical spa website with luxury aesthetics",
            reference_urls=[],
            reference_analysis=""
        )
        print(f"✓ Design analysis created")
        print(f"  Primary color: {analysis.primary_color}")
        print(f"  Style: {analysis.aesthetic_style}")
        print(f"  Mood: {analysis.mood}")
        
        print("\n✓ All agents working correctly with GPT-4o!")
        return True
        
    except Exception as e:
        print(f"✗ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_agents())
    print(f"\nAgent tests {'PASSED' if success else 'FAILED'}")