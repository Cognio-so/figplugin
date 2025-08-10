"""
Composer Agent - Expands PageSpec into detailed Figma node specifications
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from .planner_agent import PageSpec, Section
from .reference_agent import DesignSystem

class ImageSlot(BaseModel):
    role: str
    prompt: str
    aspectRatio: str
    styleHints: Dict[str, Any]

class FigmaNodeSpec(BaseModel):
    type: str  # FRAME, TEXT, RECTANGLE, etc.
    name: str
    properties: Dict[str, Any]
    children: Optional[List['FigmaNodeSpec']] = None
    pluginData: Optional[Dict[str, str]] = None

class ComposedPageSpec(BaseModel):
    pageName: str
    figmaNodes: List[FigmaNodeSpec]
    imageSlots: List[ImageSlot]
    totalNodes: int

class ComposerAgent:
    def __init__(self, llm_client: ChatOpenAI):
        self.llm = llm_client
        
        self.composition_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Figma composition expert for Growth99 healthcare websites.

Transform page specifications into detailed Figma node structures.

FIGMA NODE TYPES:
- FRAME: Container with auto-layout
- TEXT: Text content with typography
- RECTANGLE: Backgrounds, images, dividers
- ELLIPSE: Circular elements
- GROUP: Grouped elements

FIGMA PROPERTIES:
- layoutMode: 'VERTICAL' | 'HORIZONTAL' | 'NONE'
- primaryAxisSizingMode: 'AUTO' | 'FIXED'
- counterAxisSizingMode: 'AUTO' | 'FIXED'
- itemSpacing: number (gap between items)
- paddingTop/Right/Bottom/Left: number
- fills: [{type: 'SOLID', color: {r, g, b}}]
- fontName: {family: string, style: string}
- fontSize: number
- characters: string (text content)

HEALTHCARE DESIGN PRINCIPLES:
- Clean, professional layouts
- Adequate white space for readability
- Consistent spacing using design system scale
- Accessibility-compliant contrast ratios
- Mobile-responsive auto-layout structures

Plan complete Figma node hierarchies that will render the page sections accurately."""),
            ("human", """Compose Figma nodes for:

Page Specification:
{page_spec}

Design System:
{design_system}

Create detailed node specifications that can be rendered in Figma.""")
        ])

    async def compose_page(
        self, 
        page_spec: PageSpec, 
        design_system: DesignSystem
    ) -> ComposedPageSpec:
        """Compose detailed Figma node specifications from page spec"""
        
        # Format inputs
        page_spec_text = self._format_page_spec(page_spec)
        design_system_text = self._format_design_system(design_system)
        
        # Generate composition
        response = await self.llm.ainvoke(
            self.composition_prompt.format(
                page_spec=page_spec_text,
                design_system=design_system_text
            )
        )
        
        # Parse into structured composition
        composition_data = self._parse_composition(response.content, page_spec, design_system)
        
        return ComposedPageSpec(**composition_data)
    
    def _format_page_spec(self, page_spec: PageSpec) -> str:
        """Format page spec for composition prompt"""
        sections_text = []
        for section in page_spec.sections:
            sections_text.append(f"- {section.type}: {section.props}")
        
        return f"""
Page: {page_spec.pageName}
Sections:
{chr(10).join(sections_text)}
Assets: {page_spec.assets}
"""
    
    def _format_design_system(self, design_system: DesignSystem) -> str:
        """Format design system for composition"""
        return f"""
Colors: {design_system.colors}
Typography: {design_system.typography}
Spacing: {design_system.spacingScale}
Components: {design_system.components}
"""
    
    def _parse_composition(
        self, 
        llm_response: str, 
        page_spec: PageSpec, 
        design_system: DesignSystem
    ) -> Dict[str, Any]:
        """Parse LLM response into structured composition"""
        
        # For MVP, create a structured composition based on page spec
        figma_nodes = []
        image_slots = []
        
        # Create root container
        root_frame = {
            "type": "FRAME",
            "name": f"{page_spec.pageName}_Container", 
            "properties": {
                "layoutMode": "VERTICAL",
                "primaryAxisSizingMode": "AUTO",
                "counterAxisSizingMode": "FIXED",
                "itemSpacing": 0,
                "paddingTop": 0,
                "paddingRight": 0, 
                "paddingBottom": 0,
                "paddingLeft": 0,
                "width": 1440,
                "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('background', '#FFFFFF'))}]
            },
            "children": []
        }
        
        # Compose each section
        for section in page_spec.sections:
            section_nodes, section_images = self._compose_section(section, design_system)
            root_frame["children"].extend(section_nodes)
            image_slots.extend(section_images)
        
        figma_nodes = [root_frame]
        
        return {
            "pageName": page_spec.pageName,
            "figmaNodes": figma_nodes,
            "imageSlots": image_slots,
            "totalNodes": self._count_nodes(figma_nodes)
        }
    
    def _compose_section(self, section: Section, design_system: DesignSystem) -> tuple[List[Dict], List[ImageSlot]]:
        """Compose individual section into Figma nodes"""
        
        nodes = []
        image_slots = []
        
        # Section container
        section_frame = {
            "type": "FRAME",
            "name": f"Section_{section.type}",
            "properties": {
                "layoutMode": "VERTICAL",
                "primaryAxisSizingMode": "AUTO", 
                "counterAxisSizingMode": "FIXED",
                "itemSpacing": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                "paddingTop": design_system.spacingScale[6] if len(design_system.spacingScale) > 6 else 64,
                "paddingRight": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                "paddingBottom": design_system.spacingScale[6] if len(design_system.spacingScale) > 6 else 64,
                "paddingLeft": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                "width": 1440,
                "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}]
            },
            "children": [],
            "pluginData": {"role": f"section:{section.type.lower()}"}
        }
        
        # Add section-specific content
        if section.type == "Header":
            header_content, header_images = self._compose_header(section.props, design_system)
            section_frame["children"].extend(header_content)
            image_slots.extend(header_images)
            
        elif section.type == "Hero":
            hero_content, hero_images = self._compose_hero(section.props, design_system)
            section_frame["children"].extend(hero_content)
            image_slots.extend(hero_images)
            
        elif section.type == "Services":
            services_content, services_images = self._compose_services(section.props, design_system)
            section_frame["children"].extend(services_content)
            image_slots.extend(services_images)
            
        else:
            # Generic section composition
            generic_content = self._compose_generic_section(section, design_system)
            section_frame["children"].extend(generic_content)
        
        nodes.append(section_frame)
        
        return nodes, image_slots
    
    def _compose_header(self, props: Dict[str, Any], design_system: DesignSystem) -> tuple[List[Dict], List[ImageSlot]]:
        """Compose header section"""
        
        content = []
        images = []
        
        # Header container
        header_content = {
            "type": "FRAME",
            "name": "Header_Content",
            "properties": {
                "layoutMode": "HORIZONTAL",
                "primaryAxisSizingMode": "AUTO",
                "counterAxisSizingMode": "FIXED", 
                "itemSpacing": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                "paddingTop": design_system.spacingScale[3] if len(design_system.spacingScale) > 3 else 24,
                "paddingRight": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                "paddingBottom": design_system.spacingScale[3] if len(design_system.spacingScale) > 3 else 24,
                "paddingLeft": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                "width": 1440,
                "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('background', '#FFFFFF'))}]
            },
            "children": []
        }
        
        # Logo
        if props.get("logo"):
            logo_frame = {
                "type": "RECTANGLE", 
                "name": "Logo",
                "properties": {
                    "width": 120,
                    "height": 40,
                    "fills": [{"type": "SOLID", "color": {"r": 0.9, "g": 0.9, "b": 0.9}}]
                },
                "pluginData": {"role": "logo"}
            }
            header_content["children"].append(logo_frame)
        
        # Navigation
        if props.get("nav"):
            nav_frame = {
                "type": "FRAME",
                "name": "Navigation",
                "properties": {
                    "layoutMode": "HORIZONTAL",
                    "itemSpacing": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                    "primaryAxisSizingMode": "AUTO"
                },
                "children": []
            }
            
            for nav_item in props["nav"]:
                nav_text = {
                    "type": "TEXT",
                    "name": f"Nav_{nav_item}",
                    "properties": {
                        "characters": nav_item,
                        "fontName": {"family": design_system.typography.get("body", {}).get("family", "Inter"), "style": "Medium"},
                        "fontSize": 16,
                        "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('text', '#1F2937'))}]
                    }
                }
                nav_frame["children"].append(nav_text)
            
            header_content["children"].append(nav_frame)
        
        # CTA Button
        if props.get("cta"):
            cta_button = self._create_button(props["cta"], design_system)
            header_content["children"].append(cta_button)
        
        content.append(header_content)
        
        return content, images
    
    def _compose_hero(self, props: Dict[str, Any], design_system: DesignSystem) -> tuple[List[Dict], List[ImageSlot]]:
        """Compose hero section"""
        
        content = []
        images = []
        
        # Hero container
        hero_container = {
            "type": "FRAME",
            "name": "Hero_Container",
            "properties": {
                "layoutMode": "HORIZONTAL",
                "primaryAxisSizingMode": "AUTO",
                "counterAxisSizingMode": "FIXED",
                "itemSpacing": design_system.spacingScale[6] if len(design_system.spacingScale) > 6 else 64,
                "width": 1440,
                "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('background', '#FFFFFF'))}]
            },
            "children": []
        }
        
        # Text content
        text_content = {
            "type": "FRAME", 
            "name": "Hero_Text",
            "properties": {
                "layoutMode": "VERTICAL",
                "itemSpacing": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                "primaryAxisSizingMode": "AUTO",
                "width": 600
            },
            "children": []
        }
        
        # Title
        if props.get("title"):
            title = {
                "type": "TEXT",
                "name": "Hero_Title", 
                "properties": {
                    "characters": props["title"],
                    "fontName": {"family": design_system.typography.get("display", {}).get("family", "Inter"), "style": "Bold"},
                    "fontSize": design_system.typography.get("display", {}).get("size", 44),
                    "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('text', '#1F2937'))}],
                    "width": 600
                }
            }
            text_content["children"].append(title)
        
        # Subtitle  
        if props.get("subtitle"):
            subtitle = {
                "type": "TEXT",
                "name": "Hero_Subtitle",
                "properties": {
                    "characters": props["subtitle"],
                    "fontName": {"family": design_system.typography.get("body", {}).get("family", "Inter"), "style": "Regular"},
                    "fontSize": 18,
                    "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('textMuted', '#6B7280'))}],
                    "width": 600
                }
            }
            text_content["children"].append(subtitle)
        
        # CTA Button
        if props.get("cta"):
            cta_button = self._create_button(props["cta"], design_system)
            text_content["children"].append(cta_button)
        
        hero_container["children"].append(text_content)
        
        # Hero image
        if props.get("imageSlot"):
            image_placeholder = {
                "type": "RECTANGLE",
                "name": "Hero_Image",
                "properties": {
                    "width": 600,
                    "height": 400,
                    "fills": [{"type": "SOLID", "color": {"r": 0.9, "g": 0.9, "b": 0.9}}],
                    "cornerRadius": design_system.radius.get("lg", 12)
                },
                "pluginData": {"role": "hero"}
            }
            hero_container["children"].append(image_placeholder)
            
            # Add to image slots for AI generation
            images.append(ImageSlot(
                role="hero",
                prompt=f"Professional healthcare hero image for {props.get('title', 'medical practice')}, clean and modern",
                aspectRatio="3:2",
                styleHints={
                    "style": "professional medical photography",
                    "mood": "clean, trustworthy, modern",
                    "colors": [design_system.colors.get('primary', '#2563EB')]
                }
            ))
        
        content.append(hero_container)
        
        return content, images
    
    def _compose_services(self, props: Dict[str, Any], design_system: DesignSystem) -> tuple[List[Dict], List[ImageSlot]]:
        """Compose services section"""
        
        content = []
        images = []
        
        # Services container
        services_container = {
            "type": "FRAME",
            "name": "Services_Container", 
            "properties": {
                "layoutMode": "VERTICAL",
                "itemSpacing": design_system.spacingScale[5] if len(design_system.spacingScale) > 5 else 48,
                "primaryAxisSizingMode": "AUTO",
                "width": 1440
            },
            "children": []
        }
        
        # Section title
        if props.get("title"):
            title = {
                "type": "TEXT",
                "name": "Services_Title",
                "properties": {
                    "characters": props["title"],
                    "fontName": {"family": design_system.typography.get("h2", {}).get("family", "Inter"), "style": "Bold"},
                    "fontSize": design_system.typography.get("h2", {}).get("size", 32),
                    "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('text', '#1F2937'))}],
                    "textAlignHorizontal": "CENTER",
                    "width": 1440
                }
            }
            services_container["children"].append(title)
        
        # Services grid
        if props.get("services"):
            services_grid = {
                "type": "FRAME",
                "name": "Services_Grid",
                "properties": {
                    "layoutMode": "HORIZONTAL", 
                    "itemSpacing": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                    "primaryAxisSizingMode": "AUTO"
                },
                "children": []
            }
            
            for service in props["services"][:3]:  # Limit to 3 for layout
                service_card = {
                    "type": "FRAME",
                    "name": f"Service_{service.get('name', 'Service')}",
                    "properties": {
                        "layoutMode": "VERTICAL",
                        "itemSpacing": design_system.spacingScale[3] if len(design_system.spacingScale) > 3 else 24,
                        "padding": design_system.components.get("Card", {}).get("padding", 24),
                        "cornerRadius": design_system.components.get("Card", {}).get("radius", 12),
                        "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}],
                        "stroke": [{"type": "SOLID", "color": {"r": 0.9, "g": 0.9, "b": 0.9}}],
                        "strokeWeight": 1,
                        "width": 360
                    },
                    "children": []
                }
                
                # Service name
                service_name = {
                    "type": "TEXT",
                    "name": f"Service_Name_{service.get('name', 'Service')}",
                    "properties": {
                        "characters": service.get("name", "Service"),
                        "fontName": {"family": design_system.typography.get("h3", {}).get("family", "Inter"), "style": "SemiBold"},
                        "fontSize": design_system.typography.get("h3", {}).get("size", 24),
                        "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('text', '#1F2937'))}]
                    }
                }
                service_card["children"].append(service_name)
                
                # Service description
                if service.get("description"):
                    service_desc = {
                        "type": "TEXT", 
                        "name": f"Service_Desc_{service.get('name', 'Service')}",
                        "properties": {
                            "characters": service["description"],
                            "fontName": {"family": design_system.typography.get("body", {}).get("family", "Inter"), "style": "Regular"},
                            "fontSize": 16,
                            "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('textMuted', '#6B7280'))}],
                            "width": 300
                        }
                    }
                    service_card["children"].append(service_desc)
                
                services_grid["children"].append(service_card)
            
            services_container["children"].append(services_grid)
        
        content.append(services_container)
        
        return content, images
    
    def _compose_generic_section(self, section: Section, design_system: DesignSystem) -> List[Dict]:
        """Compose generic section with basic text content"""
        
        return [{
            "type": "FRAME",
            "name": f"Section_{section.type}",
            "properties": {
                "layoutMode": "VERTICAL", 
                "itemSpacing": design_system.spacingScale[4] if len(design_system.spacingScale) > 4 else 32,
                "paddingTop": design_system.spacingScale[5] if len(design_system.spacingScale) > 5 else 48,
                "paddingBottom": design_system.spacingScale[5] if len(design_system.spacingScale) > 5 else 48,
                "width": 1440,
                "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}]
            },
            "children": [{
                "type": "TEXT",
                "name": f"{section.type}_Placeholder",
                "properties": {
                    "characters": f"{section.type} Section Content",
                    "fontName": {"family": "Inter", "style": "Regular"},
                    "fontSize": 18,
                    "fills": [{"type": "SOLID", "color": {"r": 0.5, "g": 0.5, "b": 0.5}}],
                    "textAlignHorizontal": "CENTER",
                    "width": 1440
                }
            }]
        }]
    
    def _create_button(self, text: str, design_system: DesignSystem) -> Dict[str, Any]:
        """Create button component"""
        
        button_style = design_system.components.get("Button", {})
        
        return {
            "type": "FRAME",
            "name": f"Button_{text.replace(' ', '_')}",
            "properties": {
                "layoutMode": "HORIZONTAL",
                "primaryAxisSizingMode": "AUTO",
                "counterAxisSizingMode": "AUTO", 
                "paddingTop": button_style.get("padY", 12),
                "paddingRight": button_style.get("padX", 24),
                "paddingBottom": button_style.get("padY", 12),
                "paddingLeft": button_style.get("padX", 24),
                "cornerRadius": button_style.get("radius", 8),
                "fills": [{"type": "SOLID", "color": self._hex_to_rgb(design_system.colors.get('primary', '#2563EB'))}],
                "itemSpacing": 8
            },
            "children": [{
                "type": "TEXT",
                "name": f"Button_Text_{text.replace(' ', '_')}",
                "properties": {
                    "characters": text,
                    "fontName": {"family": design_system.typography.get("body", {}).get("family", "Inter"), "style": "SemiBold"},
                    "fontSize": 16,
                    "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}]
                }
            }],
            "pluginData": {"role": "button", "cta": text}
        }
    
    def _hex_to_rgb(self, hex_color: str) -> Dict[str, float]:
        """Convert hex color to Figma RGB format"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return {"r": 0.5, "g": 0.5, "b": 0.5}
        
        try:
            r = int(hex_color[0:2], 16) / 255
            g = int(hex_color[2:4], 16) / 255  
            b = int(hex_color[4:6], 16) / 255
            return {"r": r, "g": g, "b": b}
        except:
            return {"r": 0.5, "g": 0.5, "b": 0.5}
    
    def _count_nodes(self, nodes: List[Dict]) -> int:
        """Count total nodes in hierarchy"""
        count = 0
        for node in nodes:
            count += 1
            if node.get("children"):
                count += self._count_nodes(node["children"])
        return count