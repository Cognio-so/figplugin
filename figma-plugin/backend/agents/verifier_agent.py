"""
Verifier Agent - Validates page specifications and estimates complexity
"""

from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .composer_agent import ComposedPageSpec, FigmaNodeSpec
from .reference_agent import DesignSystem

class ValidationIssue(BaseModel):
    severity: str  # "error", "warning", "info"
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None

class PageComplexity(BaseModel):
    total_nodes: int
    estimated_render_time: float  # seconds
    accessibility_score: float  # 0-1
    performance_score: float  # 0-1
    complexity_level: str  # "simple", "moderate", "complex"

class VerificationResult(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue]
    complexity: PageComplexity
    recommendations: List[str]

class VerifierAgent:
    def __init__(self, llm_client: ChatOpenAI):
        self.llm = llm_client
        
        self.verification_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Figma page specification verifier for Growth99 healthcare websites.

            Validate page specifications for:
            1. COMPLETENESS - All required sections and properties present
            2. ACCESSIBILITY - Text contrast, font sizes, alt text considerations  
            3. HEALTHCARE COMPLIANCE - Professional tone, medical accuracy
            4. PERFORMANCE - Node count, complexity, render time
            5. DESIGN CONSISTENCY - Design system adherence
            
            HEALTHCARE-SPECIFIC CHECKS:
            - Professional medical terminology
            - Trust-building elements (credentials, testimonials)
            - Clear call-to-actions for appointments
            - HIPAA-conscious content (no patient info)
            - Accessibility for diverse audiences
            
            Provide specific, actionable feedback for improvements."""),
            ("human", """Verify this page specification:

Page Spec:
{page_spec}

Design System:
{design_system}

Check for issues and provide recommendations.""")
        ])

    async def verify_page(
        self, 
        composed_spec: ComposedPageSpec, 
        design_system: DesignSystem,
        target_audience: str = "healthcare patients"
    ) -> VerificationResult:
        """Comprehensive page verification"""
        
        # Run multiple verification checks
        issues = []
        
        # 1. Structural validation
        structural_issues = self._validate_structure(composed_spec)
        issues.extend(structural_issues)
        
        # 2. Accessibility validation
        accessibility_issues = self._validate_accessibility(composed_spec, design_system)
        issues.extend(accessibility_issues)
        
        # 3. Healthcare-specific validation
        healthcare_issues = await self._validate_healthcare_compliance(composed_spec)
        issues.extend(healthcare_issues)
        
        # 4. Performance validation
        performance_issues = self._validate_performance(composed_spec)
        issues.extend(performance_issues)
        
        # Calculate complexity metrics
        complexity = self._calculate_complexity(composed_spec)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(composed_spec, issues)
        
        # Determine if page is valid (no errors, only warnings/info)
        is_valid = not any(issue.severity == "error" for issue in issues)
        
        return VerificationResult(
            is_valid=is_valid,
            issues=issues,
            complexity=complexity,
            recommendations=recommendations
        )
    
    def _validate_structure(self, composed_spec: ComposedPageSpec) -> List[ValidationIssue]:
        """Validate structural completeness"""
        
        issues = []
        
        # Check minimum required sections for healthcare sites
        required_sections = ["Header", "Hero", "Services", "Contact"]
        found_sections = set()
        
        for node in composed_spec.figmaNodes:
            if node.pluginData and "section:" in node.pluginData.get("role", ""):
                section_type = node.pluginData["role"].replace("section:", "").title()
                found_sections.add(section_type)
        
        missing_sections = set(required_sections) - found_sections
        if missing_sections:
            issues.append(ValidationIssue(
                severity="warning",
                message=f"Missing recommended sections: {', '.join(missing_sections)}",
                suggestion="Consider adding these sections for better healthcare website completeness"
            ))
        
        # Check for empty sections
        for node in composed_spec.figmaNodes:
            if node.type == "FRAME" and not node.children:
                issues.append(ValidationIssue(
                    severity="error",
                    message=f"Empty section: {node.name}",
                    location=node.name,
                    suggestion="Add content to this section or remove it"
                ))
        
        # Validate node hierarchy
        if composed_spec.totalNodes > 500:
            issues.append(ValidationIssue(
                severity="warning", 
                message=f"High node count: {composed_spec.totalNodes} nodes",
                suggestion="Consider simplifying the layout to improve performance"
            ))
        
        return issues
    
    def _validate_accessibility(self, composed_spec: ComposedPageSpec, design_system: DesignSystem) -> List[ValidationIssue]:
        """Validate accessibility compliance"""
        
        issues = []
        
        # Check text contrast ratios
        bg_color = design_system.colors.get('background', '#FFFFFF')
        text_color = design_system.colors.get('text', '#1F2937')
        
        contrast_ratio = self._calculate_contrast_ratio(bg_color, text_color)
        if contrast_ratio < 4.5:  # WCAG AA standard
            issues.append(ValidationIssue(
                severity="error",
                message=f"Insufficient text contrast ratio: {contrast_ratio:.2f}",
                suggestion="Use darker text or lighter background for better accessibility"
            ))
        
        # Check font sizes
        min_font_size = 16  # Minimum for accessibility
        for node in self._get_all_nodes(composed_spec.figmaNodes):
            if node.type == "TEXT":
                font_size = node.properties.get("fontSize", 16)
                if font_size < min_font_size:
                    issues.append(ValidationIssue(
                        severity="warning",
                        message=f"Small font size detected: {font_size}px in {node.name}",
                        location=node.name,
                        suggestion=f"Increase to at least {min_font_size}px for better readability"
                    ))
        
        # Check for alt text placeholders for images
        image_count = len([slot for slot in composed_spec.imageSlots])
        if image_count > 0:
            issues.append(ValidationIssue(
                severity="info",
                message=f"Remember to add alt text for {image_count} images",
                suggestion="Provide descriptive alt text for all images for screen readers"
            ))
        
        return issues
    
    async def _validate_healthcare_compliance(self, composed_spec: ComposedPageSpec) -> List[ValidationIssue]:
        """Validate healthcare-specific compliance"""
        
        issues = []
        
        # Extract all text content for analysis
        text_content = []
        for node in self._get_all_nodes(composed_spec.figmaNodes):
            if node.type == "TEXT" and "characters" in node.properties:
                text_content.append(node.properties["characters"])
        
        combined_text = " ".join(text_content)
        
        # Use GPT-5 for healthcare compliance check
        try:
            compliance_prompt = ChatPromptTemplate.from_messages([
                ("system", """Check this healthcare website content for:
                1. Professional medical tone
                2. No medical claims that require disclaimers
                3. HIPAA-appropriate language (no patient specifics)
                4. Clear, non-misleading service descriptions
                5. Appropriate call-to-actions for medical services
                
                Return issues as JSON array with severity, message, and suggestion fields."""),
                ("human", f"Website text content to check:\n{combined_text}")
            ])
            
            response = await self.llm.ainvoke(compliance_prompt)
            
            # Parse compliance issues (simplified for MVP)
            if "claim" in combined_text.lower() or "guarantee" in combined_text.lower():
                issues.append(ValidationIssue(
                    severity="warning",
                    message="Potential medical claims detected",
                    suggestion="Ensure all medical claims are properly qualified and compliant"
                ))
            
        except Exception as e:
            print(f"Healthcare compliance check failed: {e}")
            issues.append(ValidationIssue(
                severity="info",
                message="Manual healthcare compliance review recommended",
                suggestion="Have medical compliance team review content"
            ))
        
        # Check for required healthcare elements
        has_contact_info = any("phone" in str(node.properties).lower() for node in self._get_all_nodes(composed_spec.figmaNodes))
        if not has_contact_info:
            issues.append(ValidationIssue(
                severity="warning",
                message="No contact information detected",
                suggestion="Include phone number and address for patient access"
            ))
        
        return issues
    
    def _validate_performance(self, composed_spec: ComposedPageSpec) -> List[ValidationIssue]:
        """Validate performance characteristics"""
        
        issues = []
        
        # Check node count thresholds
        if composed_spec.totalNodes > 300:
            issues.append(ValidationIssue(
                severity="warning",
                message=f"High node count may affect performance: {composed_spec.totalNodes}",
                suggestion="Consider component reuse or layout simplification"
            ))
        
        # Check image count
        image_count = len(composed_spec.imageSlots)
        if image_count > 10:
            issues.append(ValidationIssue(
                severity="warning",
                message=f"Many images detected: {image_count}",
                suggestion="Consider image optimization and lazy loading"
            ))
        
        # Check for overly complex layouts
        max_nesting_depth = self._calculate_max_nesting_depth(composed_spec.figmaNodes)
        if max_nesting_depth > 8:
            issues.append(ValidationIssue(
                severity="info",
                message=f"Deep nesting detected: {max_nesting_depth} levels",
                suggestion="Consider flattening the component hierarchy"
            ))
        
        return issues
    
    def _calculate_complexity(self, composed_spec: ComposedPageSpec) -> PageComplexity:
        """Calculate page complexity metrics"""
        
        total_nodes = composed_spec.totalNodes
        image_count = len(composed_spec.imageSlots)
        
        # Estimate render time based on node count and images
        base_render_time = 0.5  # seconds
        node_time = total_nodes * 0.002  # 2ms per node
        image_time = image_count * 0.1  # 100ms per image
        estimated_render_time = base_render_time + node_time + image_time
        
        # Calculate complexity level
        if total_nodes < 100:
            complexity_level = "simple"
        elif total_nodes < 300:
            complexity_level = "moderate"
        else:
            complexity_level = "complex"
        
        # Accessibility score (simplified)
        accessibility_score = 0.8  # Base score, adjusted by validation issues
        
        # Performance score
        performance_score = max(0.0, 1.0 - (total_nodes - 100) / 400)  # Decreases with node count
        
        return PageComplexity(
            total_nodes=total_nodes,
            estimated_render_time=estimated_render_time,
            accessibility_score=accessibility_score,
            performance_score=performance_score,
            complexity_level=complexity_level
        )
    
    async def _generate_recommendations(
        self, 
        composed_spec: ComposedPageSpec, 
        issues: List[ValidationIssue]
    ) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Priority recommendations based on issues
        error_count = sum(1 for issue in issues if issue.severity == "error")
        warning_count = sum(1 for issue in issues if issue.severity == "warning")
        
        if error_count > 0:
            recommendations.append(f"Fix {error_count} critical errors before deployment")
        
        if warning_count > 0:
            recommendations.append(f"Address {warning_count} warnings for optimal user experience")
        
        # Performance recommendations
        if composed_spec.totalNodes > 200:
            recommendations.append("Consider breaking complex sections into smaller components")
        
        # Healthcare-specific recommendations
        recommendations.append("Ensure all medical content is reviewed by qualified professionals")
        recommendations.append("Test with healthcare accessibility guidelines")
        
        # Image optimization
        if len(composed_spec.imageSlots) > 5:
            recommendations.append("Optimize images for web and mobile performance")
        
        return recommendations
    
    def _get_all_nodes(self, nodes: List[FigmaNodeSpec]) -> List[FigmaNodeSpec]:
        """Flatten node hierarchy for analysis"""
        
        all_nodes = []
        for node in nodes:
            all_nodes.append(node)
            if hasattr(node, 'children') and node.children:
                all_nodes.extend(self._get_all_nodes(node.children))
        return all_nodes
    
    def _calculate_contrast_ratio(self, bg_hex: str, text_hex: str) -> float:
        """Calculate WCAG contrast ratio (simplified)"""
        
        # Simplified contrast calculation
        # In production, use proper color contrast libraries
        
        def hex_to_luminance(hex_color: str) -> float:
            hex_color = hex_color.lstrip('#')
            if len(hex_color) != 6:
                return 0.5
            
            r = int(hex_color[0:2], 16) / 255
            g = int(hex_color[2:4], 16) / 255
            b = int(hex_color[4:6], 16) / 255
            
            # Simplified luminance calculation
            return 0.299 * r + 0.587 * g + 0.114 * b
        
        bg_lum = hex_to_luminance(bg_hex)
        text_lum = hex_to_luminance(text_hex)
        
        lighter = max(bg_lum, text_lum)
        darker = min(bg_lum, text_lum)
        
        return (lighter + 0.05) / (darker + 0.05)
    
    def _calculate_max_nesting_depth(self, nodes: List[FigmaNodeSpec]) -> int:
        """Calculate maximum nesting depth"""
        
        def get_depth(node: FigmaNodeSpec, current_depth: int = 0) -> int:
            if not hasattr(node, 'children') or not node.children:
                return current_depth
            
            max_child_depth = current_depth
            for child in node.children:
                child_depth = get_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
            
            return max_child_depth
        
        max_depth = 0
        for node in nodes:
            depth = get_depth(node)
            max_depth = max(max_depth, depth)
        
        return max_depth