#!/usr/bin/env python3
"""
Test script to verify the JSON parsing fixes
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up path for imports
import sys
sys.path.insert(0, '/Users/apple/Documents/growth/plugin/figplugin/figma-plugin')

# Import the agents
from backend.agents.design_analysis_agent import DesignAnalysisAgent
from backend.agents.planner_agent import PlannerAgent
from backend.agents.requirements_agent import RequirementsAgent, Brief
from backend.agents.reference_agent import ReferenceAgent
from langchain_openai import ChatOpenAI

async def test_json_parsing():
    """Test the JSON parsing improvements"""
    
    # Create LLM client with proper model name
    llm = ChatOpenAI(model="gpt-4o-2024-08-06", temperature=0.7, max_tokens=4000)
    
    print("Testing JSON parsing fixes...")
    print("=" * 50)
    
    # Test 1: Design Analysis Agent
    print("\n1. Testing Design Analysis Agent...")
    design_agent = DesignAnalysisAgent(llm)
    
    try:
        result = await design_agent.analyze_design_requirements(
            user_input="Create a modern medical spa website with luxury aesthetics",
            reference_urls=[],
            reference_analysis=""
        )
        print(f"✓ Design Analysis successful")
        print(f"  Primary color: {result.primary_color}")
        print(f"  Aesthetic style: {result.aesthetic_style}")
    except Exception as e:
        print(f"✗ Design Analysis failed: {e}")
    
    # Test 2: Planner Agent
    print("\n2. Testing Planner Agent...")
    planner_agent = PlannerAgent(llm)
    reference_agent = ReferenceAgent(llm)
    
    # Create a test brief
    brief = Brief(
        industry="healthcare",
        business_type="medical spa",
        tone="luxury",
        key_services=["Botox", "Laser Treatment", "Facials"],
        target_audience="Affluent women 35-55",
        primary_cta="Book Consultation",
        sections_requested=["Header", "Hero", "Services", "About", "Contact"]
    )
    
    # Get a design system
    design_system = reference_agent._get_default_healthcare_design_system()
    
    try:
        page_spec = await planner_agent.create_page_spec(
            brief=brief,
            design_system=design_system,
            page_type="Home"
        )
        print(f"✓ Page Planning successful")
        print(f"  Page name: {page_spec.pageName}")
        print(f"  Sections: {len(page_spec.sections)}")
    except Exception as e:
        print(f"✗ Page Planning failed: {e}")
    
    print("\n" + "=" * 50)
    print("Testing complete!")

if __name__ == "__main__":
    asyncio.run(test_json_parsing())