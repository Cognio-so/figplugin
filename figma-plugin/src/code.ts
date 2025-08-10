import { onUIMessage, postToUI } from './bridge'
import type { PageSpec, UIToCoreMessage } from './types'
import { createAutoLayoutFrame } from './renderers/layout'
import { renderSection } from './renderers/components'
import { AIRenderer, AIGeneratedPage } from './renderers/ai-renderer'
// Inline UI HTML for figma.showUI
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
import inlinedUI from './_inlined-ui'

figma.showUI(inlinedUI, { width: 380, height: 640 })

// Handle plugin close
figma.on('close', () => {
  console.log('Growth99 plugin closing')
})

onUIMessage(async (msg: UIToCoreMessage) => {
  if (msg.type === 'GenerateFirstPage') {
    try {
      // Test backend connectivity first
      postToUI({ type: 'RenderProgress', payload: { step: 'connecting-backend', percent: 10 } })
      
      // Try to call the backend API
      const backendUrl = 'http://localhost:8000'
      
      // Extract data from message payload
      const { brief, model, useAiImages, referenceUrls } = msg.payload || {}
      const userInput = brief || "Create a professional medical spa homepage with modern, luxurious design"
      const urls = referenceUrls || []
      const modelName = model || "gpt-5"
      const aiImages = useAiImages || false
      
      postToUI({ type: 'RenderProgress', payload: { step: 'analyzing-requirements', percent: 5 } })
      
      // Test complete page generation workflow
      const response = await fetch(`${backendUrl}/v1/generate/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_input: userInput,
          reference_urls: urls,
          page_type: "Home",
          use_ai_images: aiImages,
          model_name: modelName
        })
      })
      
      if (response.ok) {
        const result = await response.json()
        
        if (result.success && result.final_page_spec) {
          postToUI({ type: 'RenderProgress', payload: { step: 'rendering-ai-components', percent: 80 } })
          
          // Check if we have AI-generated components
          if (result.final_page_spec.figmaComponents && result.final_page_spec.figmaComponents.length > 0) {
            // Render using AI renderer
            console.log('Using AI renderer for dynamic components')
            await AIRenderer.renderAIGeneratedPage(result.final_page_spec as AIGeneratedPage)
          } else {
            // Fallback to traditional rendering
            console.log('Using traditional renderer (fallback)')
            await renderGeneratedPage(result.final_page_spec)
          }
          
          postToUI({ type: 'Rendered', payload: { pageName: result.final_page_spec.pageName } })
          
        } else {
          throw new Error(result.error || 'Page generation failed')
        }
      } else {
        throw new Error(`Backend error: ${response.status}`)
      }
      
    } catch (error) {
      console.error('Backend connection failed:', error)
      postToUI({ type: 'Error', payload: { 
        code: 'BACKEND_ERROR', 
        message: `Backend unavailable: ${error.message}`, 
        suggestion: 'Using fallback local generation'
      }})
      
      // Fallback to AI renderer demonstration
      console.log('Using AI renderer fallback to demonstrate new system')
      await AIRenderer.renderFallbackPage('AI-Powered Design Demo')
      postToUI({ type: 'Rendered', payload: { pageName: 'AI-Powered Design Demo' } })
    }
    return
  }
})

async function renderPage(spec: PageSpec) {
  figma.currentPage = figma.createPage()
  figma.currentPage.name = spec.pageName
  const root = createAutoLayoutFrame({ name: 'Container', padding: 24, spacing: 24 })
  figma.currentPage.appendChild(root)

  for (const section of spec.sections) {
    postToUI({ type: 'RenderProgress', payload: { step: `creating-${section.type.toLowerCase()}`, percent: 10 } })
    const node = await renderSection(section)
    root.appendChild(node)
  }
}

async function renderGeneratedPage(generatedSpec: any) {
  // Create new page
  figma.currentPage = figma.createPage()
  figma.currentPage.name = generatedSpec.pageName || 'AI Generated Page'
  
  if (generatedSpec.figmaNodes && generatedSpec.figmaNodes.length > 0) {
    // Render from detailed Figma node specifications
    await renderFromFigmaNodes(generatedSpec.figmaNodes)
  } else if (generatedSpec.sections) {
    // Fallback to section-based rendering
    const pageSpec: PageSpec = {
      pageName: generatedSpec.pageName,
      sections: generatedSpec.sections,
      assets: generatedSpec.assets || {}
    }
    await renderPage(pageSpec)
  }
  
  // Apply any generated images
  if (generatedSpec.images && generatedSpec.images.length > 0) {
    await applyGeneratedImages(generatedSpec.images)
  }
}

async function renderFromFigmaNodes(figmaNodes: any[]) {
  for (const nodeSpec of figmaNodes) {
    try {
      const node = await createFigmaNode(nodeSpec)
      if (node) {
        figma.currentPage.appendChild(node)
      }
    } catch (error) {
      console.error('Failed to render node:', nodeSpec.name, error)
    }
  }
}

async function createFigmaNode(nodeSpec: any): Promise<SceneNode | null> {
  try {
    switch (nodeSpec.type) {
      case 'FRAME':
        const frame = figma.createFrame()
        frame.name = nodeSpec.name
        
        // Apply frame properties
        if (nodeSpec.properties) {
          applyFrameProperties(frame, nodeSpec.properties)
        }
        
        // Add children recursively
        if (nodeSpec.children && nodeSpec.children.length > 0) {
          for (const childSpec of nodeSpec.children) {
            const child = await createFigmaNode(childSpec)
            if (child) {
              frame.appendChild(child)
            }
          }
        }
        
        return frame
        
      case 'TEXT':
        const text = figma.createText()
        text.name = nodeSpec.name
        
        if (nodeSpec.properties) {
          await applyTextProperties(text, nodeSpec.properties)
        }
        
        return text
        
      case 'RECTANGLE':
        const rect = figma.createRectangle()
        rect.name = nodeSpec.name
        
        if (nodeSpec.properties) {
          applyRectangleProperties(rect, nodeSpec.properties)
        }
        
        return rect
        
      default:
        console.warn('Unknown node type:', nodeSpec.type)
        return null
    }
  } catch (error) {
    console.error('Error creating node:', error)
    return null
  }
}

function applyFrameProperties(frame: FrameNode, props: any) {
  if (props.layoutMode) frame.layoutMode = props.layoutMode
  if (props.primaryAxisSizingMode) frame.primaryAxisSizingMode = props.primaryAxisSizingMode
  if (props.counterAxisSizingMode) frame.counterAxisSizingMode = props.counterAxisSizingMode
  if (typeof props.itemSpacing === 'number') frame.itemSpacing = props.itemSpacing
  if (typeof props.paddingTop === 'number') frame.paddingTop = props.paddingTop
  if (typeof props.paddingRight === 'number') frame.paddingRight = props.paddingRight
  if (typeof props.paddingBottom === 'number') frame.paddingBottom = props.paddingBottom
  if (typeof props.paddingLeft === 'number') frame.paddingLeft = props.paddingLeft
  if (typeof props.width === 'number') frame.resize(props.width, frame.height)
  if (props.fills) frame.fills = convertFills(props.fills)
  if (typeof props.cornerRadius === 'number') frame.cornerRadius = props.cornerRadius
}

async function applyTextProperties(text: TextNode, props: any) {
  if (props.characters) {
    // Load font first
    if (props.fontName) {
      await figma.loadFontAsync(props.fontName)
      text.fontName = props.fontName
    }
    text.characters = props.characters
  }
  if (typeof props.fontSize === 'number') text.fontSize = props.fontSize
  if (props.fills) text.fills = convertFills(props.fills)
  if (props.textAlignHorizontal) text.textAlignHorizontal = props.textAlignHorizontal
  if (typeof props.width === 'number') text.resize(props.width, text.height)
}

function applyRectangleProperties(rect: RectangleNode, props: any) {
  if (typeof props.width === 'number' && typeof props.height === 'number') {
    rect.resize(props.width, props.height)
  }
  if (props.fills) rect.fills = convertFills(props.fills)
  if (typeof props.cornerRadius === 'number') rect.cornerRadius = props.cornerRadius
}

function convertFills(fillSpecs: any[]): Paint[] {
  return fillSpecs.map(fillSpec => {
    if (fillSpec.type === 'SOLID') {
      return {
        type: 'SOLID',
        color: fillSpec.color
      }
    }
    // Add other fill types as needed
    return {
      type: 'SOLID',
      color: { r: 0.5, g: 0.5, b: 0.5 }
    }
  })
}

async function applyGeneratedImages(images: any[]) {
  for (const imageSpec of images) {
    try {
      // Find nodes with matching role
      const nodes = figma.currentPage.findAllWithCriteria({
        types: ['RECTANGLE']
      })
      
      for (const node of nodes) {
        const role = node.getPluginData('role')
        if (role === imageSpec.role && imageSpec.url) {
          try {
            const image = await figma.createImageAsync(imageSpec.url)
            
            if (node.type === 'RECTANGLE') {
              node.fills = [{
                type: 'IMAGE',
                scaleMode: 'FILL',
                imageHash: image.hash
              }]
            }
          } catch (error) {
            console.error('Failed to apply image:', imageSpec.url, error)
          }
        }
      }
    } catch (error) {
      console.error('Failed to process image:', imageSpec, error)
    }
  }
}

async function getSamplePlan(): Promise<PageSpec> {
  return {
    pageName: 'Premium Medical Spa',
    sections: [
      { type: 'Header', props: { nav: ['Home', 'Services', 'About', 'Contact'], logo: true, cta: 'Book Now' } },
      { type: 'Hero', props: { 
        title: 'Transform Your Skin, Elevate Your Confidence', 
        subtitle: 'Advanced Medical Spa Treatments',
        cta: 'Schedule Consultation',
        imageSlot: 'hero'
      } },
      { type: 'Features', props: { 
        title: 'Why Choose Our Premium Care',
        items: [ 
          { title: 'FDA-Approved Treatments', desc: 'Safe, effective procedures with proven results' }, 
          { title: 'Expert Medical Team', desc: 'Board-certified professionals with years of experience' },
          { title: 'Personalized Approach', desc: 'Customized treatment plans for your unique needs' }
        ] 
      } },
      { type: 'Testimonials', props: { 
        title: 'Client Success Stories',
        items: [ 
          { quote: 'Life-changing results! The team made me feel comfortable throughout the entire process.', author: 'Sarah M.' },
          { quote: 'Professional, caring, and absolutely amazing results. Highly recommend!', author: 'Jennifer R.' }
        ] 
      } },
      { type: 'CTA', props: { 
        title: 'Ready to Begin Your Transformation?', 
        subtitle: 'Book your complimentary consultation today',
        cta: 'Schedule Your Consultation' 
      } },
      { type: 'Footer', props: { 
        address: '123 Beauty Blvd, Medical Plaza',
        phone: '(555) 123-4567',
        email: 'hello@premiummedspa.com'
      } },
    ],
    assets: {
      hero: 'hero-image',
      logo: 'brand-logo'
    },
  }
}


