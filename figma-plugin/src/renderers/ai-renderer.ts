/**
 * AI-Driven Renderer - Creates Figma nodes from AI-generated component specifications
 */
import { FigmaNodeBuilder } from '../figma-api/node-builder'
import { ComponentSpec } from '../figma-api/types'

export interface AIGeneratedPage {
  pageName: string
  figmaComponents: ComponentSpec[]
  images: Array<{ role: string; url: string; prompt: string }>
  metadata: {
    totalNodes: number
    designReasoning: string
    designAnalysis?: any
    brief?: any
  }
}

export class AIRenderer {
  
  static async renderAIGeneratedPage(generatedPage: AIGeneratedPage): Promise<void> {
    try {
      // Create new page
      figma.currentPage = figma.createPage()
      figma.currentPage.name = generatedPage.pageName || 'AI Generated Page'
      
      console.log(`Rendering AI-generated page: ${generatedPage.pageName}`)
      console.log(`Design reasoning: ${generatedPage.metadata.designReasoning}`)
      console.log(`Total components to render: ${generatedPage.figmaComponents.length}`)
      
      // Create root container
      const rootContainer = figma.createFrame()
      rootContainer.name = 'AI_Generated_Container'
      rootContainer.layoutMode = 'VERTICAL'
      rootContainer.primaryAxisSizingMode = 'AUTO'
      rootContainer.counterAxisSizingMode = 'FIXED'
      rootContainer.itemSpacing = 0
      rootContainer.paddingTop = 0
      rootContainer.paddingRight = 0
      rootContainer.paddingBottom = 0
      rootContainer.paddingLeft = 0
      rootContainer.resize(1440, 800) // Default size, will auto-resize based on content
      rootContainer.fills = [{ type: 'SOLID', color: { r: 1, g: 1, b: 1 } }]
      
      figma.currentPage.appendChild(rootContainer)
      
      // Render each AI-generated component
      for (const componentSpec of generatedPage.figmaComponents) {
        try {
          console.log(`Rendering component: ${componentSpec.name} (${componentSpec.type})`)
          
          const node = await FigmaNodeBuilder.createFromSpec(componentSpec)
          if (node) {
            rootContainer.appendChild(node)
            console.log(`✓ Successfully rendered: ${componentSpec.name}`)
          } else {
            console.warn(`✗ Failed to render: ${componentSpec.name}`)
          }
        } catch (error) {
          console.error(`Error rendering component ${componentSpec.name}:`, error)
          // Continue with other components even if one fails
        }
      }
      
      // Apply generated images if available
      if (generatedPage.images && generatedPage.images.length > 0) {
        await this.applyAIGeneratedImages(generatedPage.images)
      }
      
      // Auto-resize container to fit content
      this.optimizeContainerLayout(rootContainer)
      
      console.log(`✓ AI page rendering complete: ${generatedPage.pageName}`)
      
    } catch (error) {
      console.error('Error rendering AI-generated page:', error)
      throw error
    }
  }
  
  static async applyAIGeneratedImages(images: Array<{ role: string; url: string; prompt: string }>): Promise<void> {
    try {
      console.log(`Applying ${images.length} AI-generated images`)
      
      for (const imageSpec of images) {
        try {
          // Find nodes with matching role in plugin data
          const nodes = figma.currentPage.findAllWithCriteria({
            types: ['RECTANGLE', 'FRAME']
          })
          
          for (const node of nodes) {
            const role = node.getPluginData('role')
            if (role === imageSpec.role && imageSpec.url) {
              try {
                console.log(`Applying image to ${imageSpec.role}: ${imageSpec.url}`)
                
                // Create image from URL
                const image = await figma.createImageAsync(imageSpec.url)
                
                // Apply image as fill
                if (node.type === 'RECTANGLE' || node.type === 'FRAME') {
                  (node as RectangleNode | FrameNode).fills = [{
                    type: 'IMAGE',
                    scaleMode: 'FILL',
                    imageHash: image.hash
                  }]
                  
                  console.log(`✓ Applied image to ${imageSpec.role}`)
                }
              } catch (imageError) {
                console.error(`Failed to apply image to ${imageSpec.role}:`, imageError)
              }
            }
          }
        } catch (error) {
          console.error(`Error processing image for ${imageSpec.role}:`, error)
        }
      }
    } catch (error) {
      console.error('Error applying AI-generated images:', error)
    }
  }
  
  static optimizeContainerLayout(container: FrameNode): void {
    try {
      // Auto-resize container height based on content
      let totalHeight = 0
      for (let i = 0; i < container.children.length; i++) {
        const child = container.children[i] as FrameNode
        if (child.height) {
          totalHeight += child.height
          if (i < container.children.length - 1) {
            totalHeight += container.itemSpacing
          }
        }
      }
      
      // Add padding
      totalHeight += container.paddingTop + container.paddingBottom
      
      // Resize container to fit content
      if (totalHeight > 0) {
        container.resize(container.width, totalHeight)
      }
      
      console.log(`Container optimized: ${container.width}x${totalHeight}px`)
      
    } catch (error) {
      console.error('Error optimizing container layout:', error)
    }
  }
  
  static async renderFallbackPage(pageName: string = 'AI Generated Page'): Promise<void> {
    try {
      console.log('Rendering fallback AI page...')
      
      // Create a simple fallback page structure
      figma.currentPage = figma.createPage()
      figma.currentPage.name = pageName
      
      const container = figma.createFrame()
      container.name = 'Fallback_Container'
      container.layoutMode = 'VERTICAL'
      container.itemSpacing = 32
      container.paddingTop = 80
      container.paddingRight = 80
      container.paddingBottom = 80
      container.paddingLeft = 80
      container.resize(1200, 600)
      container.fills = [{ type: 'SOLID', color: { r: 0.98, g: 0.99, b: 1 } }]
      
      // Add fallback content
      const title = figma.createText()
      title.name = 'Fallback_Title'
      await figma.loadFontAsync({ family: 'Inter', style: 'Bold' })
      title.fontName = { family: 'Inter', style: 'Bold' }
      title.fontSize = 48
      title.characters = 'AI Design Generation'
      title.fills = [{ type: 'SOLID', color: { r: 0.12, g: 0.16, b: 0.22 } }]
      
      const subtitle = figma.createText()
      subtitle.name = 'Fallback_Subtitle'
      await figma.loadFontAsync({ family: 'Inter', style: 'Regular' })
      subtitle.fontName = { family: 'Inter', style: 'Regular' }
      subtitle.fontSize = 18
      subtitle.characters = 'AI-powered design generation is now active. The system will analyze your requirements and create custom designs.'
      subtitle.fills = [{ type: 'SOLID', color: { r: 0.42, g: 0.45, b: 0.50 } }]
      subtitle.textAlignHorizontal = 'CENTER'
      
      container.appendChild(title)
      container.appendChild(subtitle)
      figma.currentPage.appendChild(container)
      
      console.log('✓ Fallback page rendered successfully')
      
    } catch (error) {
      console.error('Error rendering fallback page:', error)
      throw error
    }
  }
}