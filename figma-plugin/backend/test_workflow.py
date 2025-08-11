#!/usr/bin/env python3
"""
Test the complete workflow with new model
"""

import asyncio
import os
import sys
sys.path.insert(0, '/Users/apple/Documents/growth/plugin/figplugin/figma-plugin')

from dotenv import load_dotenv
from backend.workflows.page_generation_workflow import create_workflow

# Load environment variables
load_dotenv()

async def test_workflow():
    """Test the complete workflow"""
    
    print("Testing complete workflow with GPT-4o-2024-08-06...")
    print("=" * 60)
    
    try:
        # Create workflow
        workflow = create_workflow("gpt-4o-2024-08-06")
        
        # Test with simple input
        result = await workflow.generate_page(
            chat_history=[],
            user_input="Create a modern medical spa website",
            reference_urls=[],
            page_type="Home",
            use_ai_images=False,
            model_name="gpt-4o-2024-08-06"
        )
        
        print(f"Workflow Success: {result.get('success', False)}")
        if result.get('error'):
            print(f"Error: {result['error']}")
        
        if result.get('final_page_spec'):
            spec = result['final_page_spec']
            print(f"Page Name: {spec.get('pageName', 'N/A')}")
            print(f"Sections: {len(spec.get('sections', []))}")
            print(f"Components: {len(spec.get('figmaComponents', []))}")
            print(f"Images: {len(spec.get('images', []))}")
            print("✓ Complete workflow successful!")
            return True
        else:
            print("✗ No final page spec generated")
            return False
            
    except Exception as e:
        print(f"✗ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_workflow())
    print(f"\nWorkflow test {'PASSED' if success else 'FAILED'}")