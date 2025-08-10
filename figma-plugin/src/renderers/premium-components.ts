/**
 * Premium Component Library - Creates visually rich, modern design components
 * Uses safe Figma API properties to avoid runtime errors
 */
import { createAutoLayoutFrame } from './layout'
import { createTextNode } from './text'

export interface PremiumButtonProps {
  text: string
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg' | 'xl'
  gradient?: boolean
}

export interface PremiumCardProps {
  title?: string
  subtitle?: string
  content?: string
  variant?: 'elevated' | 'outlined' | 'glass' | 'gradient'
  padding?: number
  shadow?: boolean
}

export interface PremiumHeroProps {
  title: string
  subtitle?: string
  description?: string
  primaryCTA?: string
  secondaryCTA?: string
  backgroundType?: 'gradient' | 'image' | 'video' | 'pattern'
  layout?: 'centered' | 'split' | 'fullwidth'
}

export class PremiumComponentRenderer {
  
  static async createPremiumButton(props: PremiumButtonProps): Promise<FrameNode> {
    const sizes = {
      sm: { padX: 16, padY: 8, fontSize: 14, radius: 8 },
      md: { padX: 24, padY: 12, fontSize: 16, radius: 10 },
      lg: { padX: 32, padY: 16, fontSize: 18, radius: 12 },
      xl: { padX: 40, padY: 20, fontSize: 20, radius: 14 }
    }
    const size = sizes[props.size || 'md']
    
    const button = createAutoLayoutFrame({ 
      name: `Button_${props.text.replace(/\s+/g, '_')}`,
      padding: size.padY,
      spacing: 12
    })
    
    button.layoutMode = 'HORIZONTAL'
    button.paddingLeft = size.padX
    button.paddingRight = size.padX
    button.cornerRadius = size.radius
    
    // Apply styling based on variant - simplified
    if (props.variant === 'primary' || !props.variant) {
      button.fills = [{ type: 'SOLID', color: { r: 0.15, g: 0.31, b: 0.92 } }] // Blue
    } else {
      button.fills = [{ type: 'SOLID', color: { r: 0.9, g: 0.9, b: 0.9 } }]
    }
    
    // Button text
    const text = await createTextNode(props.text, { 
      family: 'Inter', 
      style: 'Bold', 
      size: size.fontSize 
    })
    text.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]
    
    button.appendChild(text)
    return button
  }
  
  static async createPremiumCard(props: PremiumCardProps): Promise<FrameNode> {
    const card = createAutoLayoutFrame({
      name: `Card_${props.title?.replace(/\s+/g, '_') || 'Component'}`,
      padding: props.padding || 32,
      spacing: 16
    })
    
    // Card styling
    card.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]
    card.cornerRadius = 16
    card.resize(360, card.height)
    
    // Simplified styling without complex effects
    if (props.variant === 'glass') {
      card.fills = [{ type: 'SOLID', color: { r: 0.95, g: 0.95, b: 0.97 } }]
    }
    
    // Add content
    if (props.title) {
      const title = await createTextNode(props.title, { 
        family: 'Inter', 
        style: 'Bold', 
        size: 24 
      })
      title.fills = [{ type: 'SOLID', color: { r: 0.12, g: 0.16, b: 0.22 } }]
      card.appendChild(title)
    }
    
    if (props.subtitle) {
      const subtitle = await createTextNode(props.subtitle, { 
        family: 'Inter', 
        style: 'Medium', 
        size: 16 
      })
      subtitle.fills = [{ type: 'SOLID', color: { r: 0.42, g: 0.45, b: 0.50 } }]
      card.appendChild(subtitle)
    }
    
    if (props.content) {
      const content = await createTextNode(props.content, { 
        family: 'Inter', 
        style: 'Regular', 
        size: 14 
      })
      content.fills = [{ type: 'SOLID', color: { r: 0.42, g: 0.45, b: 0.50 } }]
      card.appendChild(content)
    }
    
    return card
  }
  
  static async createPremiumHero(props: PremiumHeroProps): Promise<FrameNode> {
    const hero = createAutoLayoutFrame({
      name: 'Hero_Section',
      padding: 80,
      spacing: props.layout === 'split' ? 64 : 32
    })
    
    hero.layoutMode = props.layout === 'split' ? 'HORIZONTAL' : 'VERTICAL'
    hero.resize(1440, hero.height)
    
    // Background styling - simplified
    if (props.backgroundType === 'gradient') {
      hero.fills = [{ type: 'SOLID', color: { r: 0.15, g: 0.31, b: 0.92 } }] // Blue background
    } else {
      hero.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }] // White background
    }
    
    // Create content container
    const content = createAutoLayoutFrame({
      name: 'Hero_Content',
      padding: 0,
      spacing: 24
    })
    
    // Title
    const title = await createTextNode(props.title, { 
      family: 'Inter', 
      style: 'Bold', 
      size: 52 
    })
    title.fills = [{ type: 'SOLID', color: { r: 0.12, g: 0.16, b: 0.22 } }]
    content.appendChild(title)
    
    // Subtitle
    if (props.subtitle) {
      const subtitle = await createTextNode(props.subtitle, { 
        family: 'Inter', 
        style: 'Medium', 
        size: 24 
      })
      subtitle.fills = [{ type: 'SOLID', color: { r: 0.42, g: 0.45, b: 0.50 } }]
      content.appendChild(subtitle)
    }
    
    // Description
    if (props.description) {
      const desc = await createTextNode(props.description, { 
        family: 'Inter', 
        style: 'Regular', 
        size: 18 
      })
      desc.fills = [{ type: 'SOLID', color: { r: 0.42, g: 0.45, b: 0.50 } }]
      content.appendChild(desc)
    }
    
    // CTA buttons
    if (props.primaryCTA || props.secondaryCTA) {
      const ctaContainer = createAutoLayoutFrame({
        name: 'CTA_Container',
        padding: 0,
        spacing: 16
      })
      ctaContainer.layoutMode = 'HORIZONTAL'
      
      if (props.primaryCTA) {
        const primaryBtn = await this.createPremiumButton({
          text: props.primaryCTA,
          variant: 'primary',
          size: 'lg'
        })
        ctaContainer.appendChild(primaryBtn)
      }
      
      if (props.secondaryCTA) {
        const secondaryBtn = await this.createPremiumButton({
          text: props.secondaryCTA,
          variant: 'secondary',
          size: 'lg'
        })
        ctaContainer.appendChild(secondaryBtn)
      }
      
      content.appendChild(ctaContainer)
    }
    
    hero.appendChild(content)
    
    // Add image placeholder if split layout
    if (props.layout === 'split') {
      const imagePlaceholder = figma.createRectangle()
      imagePlaceholder.name = 'Hero_Image'
      imagePlaceholder.resize(600, 400)
      imagePlaceholder.fills = [{ type: 'SOLID', color: { r: 0.9, g: 0.9, b: 0.9 } }]
      imagePlaceholder.cornerRadius = 16
      hero.appendChild(imagePlaceholder)
    }
    
    return hero
  }
  
  static async createPremiumHeader(): Promise<FrameNode> {
    const header = createAutoLayoutFrame({
      name: 'Header_Premium',
      padding: 24,
      spacing: 32
    })
    
    header.layoutMode = 'HORIZONTAL'
    header.resize(1440, header.height)
    
    // Premium header background - simplified
    header.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]
    
    // Logo placeholder
    const logo = figma.createRectangle()
    logo.name = 'Logo_Premium'
    logo.resize(140, 48)
    logo.cornerRadius = 8
    logo.fills = [{ type: 'SOLID', color: { r: 0.15, g: 0.31, b: 0.92 } }]
    header.appendChild(logo)
    
    // Navigation
    const nav = createAutoLayoutFrame({
      name: 'Navigation',
      padding: 0,
      spacing: 32
    })
    nav.layoutMode = 'HORIZONTAL'
    
    const navItems = ['Home', 'Services', 'About', 'Contact']
    for (const item of navItems) {
      const navLink = await createTextNode(item, { 
        family: 'Inter', 
        style: 'Medium', 
        size: 16 
      })
      navLink.fills = [{ type: 'SOLID', color: { r: 0.12, g: 0.16, b: 0.22 } }]
      nav.appendChild(navLink)
    }
    
    header.appendChild(nav)
    
    // CTA button
    const ctaBtn = await this.createPremiumButton({
      text: 'Book Consultation',
      variant: 'primary',
      size: 'md'
    })
    
    header.appendChild(ctaBtn)
    
    return header
  }
}