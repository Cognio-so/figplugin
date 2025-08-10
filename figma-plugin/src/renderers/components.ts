import type { SectionSpec } from '../types'
import { createAutoLayoutFrame } from './layout'
import { createTextNode } from './text'
import { createImageRectFromUrl } from './image'
import { PremiumComponentRenderer } from './premium-components'

export async function renderSection(section: SectionSpec): Promise<FrameNode | GroupNode> {
  switch (section.type) {
    case 'Header':
      return renderHeader(section.props)
    case 'Hero':
      return renderHero(section.props)
    case 'Features':
      return renderFeatures(section.props)
    case 'CTA':
      return renderCTA(section.props)
    case 'Footer':
      return renderFooter(section.props)
    case 'Testimonials':
      return renderTestimonials(section.props)
    default: {
      const frame = createAutoLayoutFrame({ name: section.type })
      const label = await createTextNode(section.type, { family: 'Inter', style: 'Bold', size: 18 })
      frame.appendChild(label)
      return frame
    }
  }
}

async function renderHeader(props: any): Promise<FrameNode> {
  // Use premium header for enhanced visual appeal
  return await PremiumComponentRenderer.createPremiumHeader()
}

async function renderHero(props: any): Promise<FrameNode> {
  // Use premium hero with enhanced visual styling
  return await PremiumComponentRenderer.createPremiumHero({
    title: (props && props.title) ? props.title : 'Transform Your Health Journey',
    subtitle: (props && props.subtitle) ? props.subtitle : 'Expert Care, Premium Results',
    description: 'Experience the difference with our state-of-the-art treatments and personalized approach to wellness.',
    primaryCTA: (props && props.cta) ? props.cta : 'Book Consultation',
    secondaryCTA: 'Learn More',
    backgroundType: 'gradient',
    layout: 'split'
  })
}

async function renderFeatures(props: any): Promise<FrameNode> {
  const frame = createAutoLayoutFrame({ name: 'Features', spacing: 24, padding: 80 })
  frame.layoutMode = 'HORIZONTAL'
  frame.primaryAxisSizingMode = 'AUTO'
  frame.counterAxisSizingMode = 'FIXED'
  frame.resizeWithoutConstraints(1440, frame.height)
  
  // Premium background - simplified to solid color
  frame.fills = [{ type: 'SOLID', color: { r: 0.98, g: 0.99, b: 1 } }]
  
  const items: Array<{ title: string; desc?: string }> = (props && props.items) ? props.items : []
  for (const it of items) {
    const card = await PremiumComponentRenderer.createPremiumCard({
      title: it.title || 'Premium Feature',
      content: it.desc || 'Experience excellence with our advanced approach to healthcare.',
      variant: 'gradient',
      shadow: true,
      padding: 32
    })
    card.resizeWithoutConstraints(360, card.height)
    frame.appendChild(card)
  }
  return frame
}

async function renderCTA(props: any): Promise<FrameNode> {
  const frame = createAutoLayoutFrame({ name: 'CTA', spacing: 32, padding: 80 })
  frame.counterAxisSizingMode = 'FIXED'
  frame.resizeWithoutConstraints(1440, frame.height)
  
  // Premium gradient background - simplified to solid color
  frame.fills = [{ type: 'SOLID', color: { r: 0.15, g: 0.31, b: 0.92 } }]
  
  const title = await createTextNode((props && props.title) ? props.title : 'Ready to Transform Your Health?', { 
    family: 'Inter', 
    style: 'Bold', 
    size: 36 
  })
  title.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]
  frame.appendChild(title)
  
  const subtitle = await createTextNode('Join thousands who have already experienced the difference', { 
    family: 'Inter', 
    style: 'Regular', 
    size: 18 
  })
  subtitle.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1, a: 0.9 } }]
  frame.appendChild(subtitle)
  
  const ctaBtn = await PremiumComponentRenderer.createPremiumButton({
    text: (props && props.cta) ? props.cta : 'Schedule Your Consultation',
    variant: 'secondary',
    size: 'xl'
  })
  // Make CTA button white on the gradient background
  ctaBtn.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]
  frame.appendChild(ctaBtn)
  
  return frame
}

async function renderFooter(props: any): Promise<FrameNode> {
  const frame = createAutoLayoutFrame({ name: 'Footer', spacing: 8, padding: 24 })
  const text = await createTextNode((props && props.text) ? props.text : '© Growth99', { family: 'Inter', style: 'Regular', size: 12 })
  frame.appendChild(text)
  return frame
}

async function renderTestimonials(props: any): Promise<FrameNode> {
  const frame = createAutoLayoutFrame({ name: 'Testimonials', spacing: 12, padding: 20 })
  const items: Array<{ quote: string; author?: string }> = (props && props.items) ? props.items : [
    { quote: 'Amazing service!', author: 'Client' },
  ]
  for (const it of items) {
    const card = createAutoLayoutFrame({ name: 'Testimonial', spacing: 6, padding: 16 })
    const q = await createTextNode(`“${it.quote}”`, { family: 'Inter', style: 'Italic', size: 16, line: 24 })
    card.appendChild(q)
    if (it.author) {
      const a = await createTextNode(`— ${it.author}`, { family: 'Inter', style: 'Regular', size: 12 })
      card.appendChild(a)
    }
    frame.appendChild(card)
  }
  return frame
}


