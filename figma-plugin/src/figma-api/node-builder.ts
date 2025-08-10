/**
 * Figma Node Builder - Creates nodes using proper Figma API structures
 */
import { 
  Paint, SolidPaint, GradientPaint, Effect, 
  ComponentSpec, FontName, RGB, RGBA, Transform 
} from './types'

export class FigmaNodeBuilder {
  
  static async createFromSpec(spec: ComponentSpec): Promise<SceneNode | null> {
    try {
      let node: SceneNode

      switch (spec.type) {
        case 'FRAME':
          node = figma.createFrame()
          break
        case 'TEXT':
          node = figma.createText()
          break
        case 'RECTANGLE':
          node = figma.createRectangle()
          break
        case 'ELLIPSE':
          node = figma.createEllipse()
          break
        default:
          console.warn(`Unknown node type: ${spec.type}`)
          return null
      }

      node.name = spec.name
      await this.applyProperties(node, spec.properties)

      // Add children if it's a container node
      if (spec.children && 'appendChild' in node) {
        for (const childSpec of spec.children) {
          const child = await this.createFromSpec(childSpec)
          if (child) {
            (node as FrameNode | GroupNode).appendChild(child)
          }
        }
      }

      return node

    } catch (error) {
      console.error('Error creating node from spec:', error)
      return null
    }
  }

  private static async applyProperties(node: SceneNode, props: ComponentSpec['properties']) {
    try {
      // Basic positioning and sizing
      if (props.x !== undefined && props.y !== undefined) {
        node.x = props.x
        node.y = props.y
      }

      if (props.width !== undefined && props.height !== undefined) {
        node.resize(props.width, props.height)
      }

      // Fills
      if (props.fills) {
        const validFills = this.validatePaints(props.fills)
        if (validFills.length > 0) {
          node.fills = validFills
        }
      }

      // Strokes
      if (props.strokes && props.strokeWeight !== undefined) {
        const validStrokes = this.validatePaints(props.strokes)
        if (validStrokes.length > 0) {
          node.strokes = validStrokes
          node.strokeWeight = props.strokeWeight
        }
      }

      // Corner radius
      if (props.cornerRadius !== undefined && 'cornerRadius' in node) {
        (node as RectangleNode | FrameNode).cornerRadius = props.cornerRadius
      }

      // Effects
      if (props.effects) {
        const validEffects = this.validateEffects(props.effects)
        if (validEffects.length > 0) {
          node.effects = validEffects
        }
      }

      // Auto layout properties
      if ('layoutMode' in node) {
        const frameNode = node as FrameNode
        
        if (props.layoutMode) {
          frameNode.layoutMode = props.layoutMode
        }

        if (props.primaryAxisSizingMode) {
          frameNode.primaryAxisSizingMode = props.primaryAxisSizingMode
        }

        if (props.counterAxisSizingMode) {
          frameNode.counterAxisSizingMode = props.counterAxisSizingMode
        }

        if (props.paddingTop !== undefined) frameNode.paddingTop = props.paddingTop
        if (props.paddingRight !== undefined) frameNode.paddingRight = props.paddingRight
        if (props.paddingBottom !== undefined) frameNode.paddingBottom = props.paddingBottom
        if (props.paddingLeft !== undefined) frameNode.paddingLeft = props.paddingLeft
        if (props.itemSpacing !== undefined) frameNode.itemSpacing = props.itemSpacing
      }

      // Text properties
      if (node.type === 'TEXT') {
        const textNode = node as TextNode
        
        if (props.fontName) {
          await figma.loadFontAsync(props.fontName)
          textNode.fontName = props.fontName
        }

        if (props.characters) {
          textNode.characters = props.characters
        }

        if (props.fontSize) {
          textNode.fontSize = props.fontSize
        }

        if (props.letterSpacing) {
          textNode.letterSpacing = props.letterSpacing
        }

        if (props.lineHeight) {
          textNode.lineHeight = props.lineHeight
        }

        if (props.textAlignHorizontal) {
          textNode.textAlignHorizontal = props.textAlignHorizontal
        }

        if (props.textAlignVertical) {
          textNode.textAlignVertical = props.textAlignVertical
        }
      }

    } catch (error) {
      console.error('Error applying properties to node:', error)
    }
  }

  private static validatePaints(paints: Paint[]): Paint[] {
    return paints.filter(paint => {
      try {
        if (paint.type === 'SOLID') {
          const solid = paint as SolidPaint
          return this.isValidRGB(solid.color)
        } else if (paint.type.startsWith('GRADIENT_')) {
          const gradient = paint as GradientPaint
          return gradient.gradientStops.every(stop => 
            this.isValidRGBA(stop.color) && 
            stop.position >= 0 && 
            stop.position <= 1
          )
        } else if (paint.type === 'IMAGE') {
          return paint.imageHash !== null
        }
        return false
      } catch (error) {
        console.warn('Invalid paint object:', paint, error)
        return false
      }
    })
  }

  private static validateEffects(effects: Effect[]): Effect[] {
    return effects.filter(effect => {
      try {
        if (effect.type === 'DROP_SHADOW' || effect.type === 'INNER_SHADOW') {
          return this.isValidRGBA(effect.color) && 
                 typeof effect.radius === 'number' && 
                 effect.radius >= 0
        } else if (effect.type === 'LAYER_BLUR' || effect.type === 'BACKGROUND_BLUR') {
          return typeof effect.radius === 'number' && effect.radius >= 0
        }
        return false
      } catch (error) {
        console.warn('Invalid effect object:', effect, error)
        return false
      }
    })
  }

  private static isValidRGB(color: RGB): boolean {
    return typeof color.r === 'number' && color.r >= 0 && color.r <= 1 &&
           typeof color.g === 'number' && color.g >= 0 && color.g <= 1 &&
           typeof color.b === 'number' && color.b >= 0 && color.b <= 1
  }

  private static isValidRGBA(color: RGBA): boolean {
    return this.isValidRGB(color) &&
           typeof color.a === 'number' && color.a >= 0 && color.a <= 1
  }

  // Utility methods for creating common paint types
  static createSolidPaint(r: number, g: number, b: number, opacity = 1): SolidPaint {
    return {
      type: 'SOLID',
      color: { r: r / 255, g: g / 255, b: b / 255 },
      opacity
    }
  }

  static createLinearGradient(
    stops: Array<{ position: number; color: { r: number; g: number; b: number; a?: number } }>,
    angle = 0
  ): GradientPaint {
    const radians = (angle * Math.PI) / 180
    const cos = Math.cos(radians)
    const sin = Math.sin(radians)

    const transform: Transform = [
      [cos, -sin, 0.5 - cos / 2 + sin / 2],
      [sin, cos, 0.5 - sin / 2 - cos / 2]
    ]

    return {
      type: 'GRADIENT_LINEAR',
      gradientTransform: transform,
      gradientStops: stops.map(stop => ({
        position: stop.position,
        color: {
          r: stop.color.r / 255,
          g: stop.color.g / 255,
          b: stop.color.b / 255,
          a: stop.color.a ?? 1
        }
      }))
    }
  }

  static createDropShadow(
    r: number, g: number, b: number, a: number,
    x: number, y: number, radius: number, spread = 0
  ): Effect {
    return {
      type: 'DROP_SHADOW',
      color: { r: r / 255, g: g / 255, b: b / 255, a },
      offset: { x, y },
      radius,
      spread,
      visible: true
    }
  }
}