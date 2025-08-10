import type { SectionSpec } from '../types'
import { createAutoLayoutFrame } from './layout'
import { createTextNode } from './text'
import { createImageRectFromUrl } from './image'

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
  const frame = createAutoLayoutFrame({ name: 'Header', padding: 16 })
  frame.layoutMode = 'HORIZONTAL'
  frame.counterAxisSizingMode = 'AUTO'
  frame.primaryAxisSizingMode = 'FIXED'
  frame.resizeWithoutConstraints(1200, frame.height)

  const left = createAutoLayoutFrame({ name: 'Brand', padding: 0, spacing: 8 })
  const right = createAutoLayoutFrame({ name: 'Nav', padding: 0, spacing: 16 })
  right.layoutMode = 'HORIZONTAL'

  if (props?.logoUrl) {
    const logo = await createImageRectFromUrl(props.logoUrl, 'logo')
    logo.resize(120, 40)
    left.appendChild(logo)
  } else {
    const brand = await createTextNode('Brand', { family: 'Inter', style: 'Bold', size: 20 })
    left.appendChild(brand)
  }

  const items: string[] = props?.nav ?? ['Home', 'Services', 'Pricing', 'Contact']
  for (const item of items) {
    const link = await createTextNode(item, { family: 'Inter', style: 'Regular', size: 14 })
    right.appendChild(link)
  }

  frame.appendChild(left)
  frame.appendChild(right)
  return frame
}

async function renderHero(props: any): Promise<FrameNode> {
  const frame = createAutoLayoutFrame({ name: 'Hero', padding: 24, spacing: 16 })
  const title = await createTextNode(props?.title ?? 'Hero Title', { family: 'Inter', style: 'Bold', size: 44, line: 52 })
  const subtitle = await createTextNode(props?.subtitle ?? 'Subtitle text', { family: 'Inter', style: 'Regular', size: 18, line: 28 })
  frame.appendChild(title)
  frame.appendChild(subtitle)
  if (props?.imageUrl) {
    const rect = await createImageRectFromUrl(props.imageUrl, 'hero')
    rect.resize(1200, 420)
    frame.appendChild(rect)
  }
  return frame
}

async function renderFeatures(props: any): Promise<FrameNode> {
  const frame = createAutoLayoutFrame({ name: 'Features', spacing: 16 })
  const items: Array<{ title: string; desc?: string }> = props?.items ?? []
  for (const it of items) {
    const card = createAutoLayoutFrame({ name: 'Feature', padding: 16, spacing: 6 })
    const t = await createTextNode(it.title ?? 'Feature', { family: 'Inter', style: 'Bold', size: 18 })
    card.appendChild(t)
    if (it.desc) {
      const d = await createTextNode(it.desc, { family: 'Inter', style: 'Regular', size: 14, line: 22 })
      card.appendChild(d)
    }
    frame.appendChild(card)
  }
  return frame
}

async function renderCTA(props: any): Promise<FrameNode> {
  const frame = createAutoLayoutFrame({ name: 'CTA', spacing: 8, padding: 20 })
  const title = await createTextNode(props?.title ?? 'Call to Action', { family: 'Inter', style: 'Bold', size: 24 })
  frame.appendChild(title)
  const cta = await createTextNode(props?.cta ?? 'Get Started', { family: 'Inter', style: 'Bold', size: 16 })
  frame.appendChild(cta)
  return frame
}

async function renderFooter(props: any): Promise<FrameNode> {
  const frame = createAutoLayoutFrame({ name: 'Footer', spacing: 8, padding: 24 })
  const text = await createTextNode(props?.text ?? '© Growth99', { family: 'Inter', style: 'Regular', size: 12 })
  frame.appendChild(text)
  return frame
}

async function renderTestimonials(props: any): Promise<FrameNode> {
  const frame = createAutoLayoutFrame({ name: 'Testimonials', spacing: 12, padding: 20 })
  const items: Array<{ quote: string; author?: string }> = props?.items ?? [
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


