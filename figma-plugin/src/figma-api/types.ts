/**
 * Proper Figma API Types - Based on Official Documentation
 */

export interface RGB {
  r: number
  g: number
  b: number
}

export interface RGBA {
  r: number
  g: number
  b: number
  a: number
}

export interface ColorStop {
  position: number
  color: RGBA
}

export interface Transform {
  0: readonly [number, number, number]
  1: readonly [number, number, number]
}

export interface SolidPaint {
  type: 'SOLID'
  color: RGB
  visible?: boolean
  opacity?: number
}

export interface GradientPaint {
  type: 'GRADIENT_LINEAR' | 'GRADIENT_RADIAL' | 'GRADIENT_ANGULAR' | 'GRADIENT_DIAMOND'
  gradientTransform: Transform
  gradientStops: ReadonlyArray<ColorStop>
  visible?: boolean
  opacity?: number
}

export interface ImagePaint {
  type: 'IMAGE'
  scaleMode: 'FILL' | 'FIT' | 'CROP' | 'TILE'
  imageHash: string | null
  visible?: boolean
  opacity?: number
}

export type Paint = SolidPaint | GradientPaint | ImagePaint

export interface DropShadowEffect {
  type: 'DROP_SHADOW'
  color: RGBA
  offset: { x: number; y: number }
  radius: number
  spread?: number
  visible: boolean
  blendMode?: BlendMode
}

export interface InnerShadowEffect {
  type: 'INNER_SHADOW'
  color: RGBA
  offset: { x: number; y: number }
  radius: number
  spread?: number
  visible: boolean
  blendMode?: BlendMode
}

export interface BlurEffect {
  type: 'LAYER_BLUR' | 'BACKGROUND_BLUR'
  radius: number
  visible: boolean
}

export type Effect = DropShadowEffect | InnerShadowEffect | BlurEffect

export type BlendMode = 
  | 'NORMAL'
  | 'MULTIPLY' 
  | 'SCREEN'
  | 'OVERLAY'
  | 'SOFT_LIGHT'
  | 'HARD_LIGHT'
  | 'COLOR_DODGE'
  | 'COLOR_BURN'
  | 'DARKEN'
  | 'LIGHTEN'
  | 'DIFFERENCE'
  | 'EXCLUSION'
  | 'HUE'
  | 'SATURATION'
  | 'COLOR'
  | 'LUMINOSITY'

export interface FontName {
  family: string
  style: string
}

export interface LetterSpacing {
  value: number
  unit: 'PIXELS' | 'PERCENT'
}

export interface LineHeight {
  value: number
  unit: 'PIXELS' | 'PERCENT' | 'AUTO'
}

// Design Analysis Types for AI
export interface AnalyzedDesignSystem {
  colors: {
    primary: string
    secondary: string
    accent: string
    text: string
    textMuted: string
    background: string
    surface: string
    [key: string]: string
  }
  typography: {
    headingFont: FontName
    bodyFont: FontName
    sizes: {
      h1: number
      h2: number
      h3: number
      body: number
      small: number
      [key: string]: number
    }
    weights: {
      light: string
      regular: string
      medium: string
      semibold: string
      bold: string
      [key: string]: string
    }
  }
  spacing: {
    scale: number[]
    sections: number
    components: number
    text: number
  }
  effects: {
    shadows: {
      card: DropShadowEffect
      button: DropShadowEffect
      header: DropShadowEffect
    }
    blur: number
    gradients: {
      primary: GradientPaint
      secondary: GradientPaint
      accent: GradientPaint
    }
  }
  layout: {
    containerWidth: number
    columns: number
    gutter: number
    breakpoints: {
      mobile: number
      tablet: number
      desktop: number
    }
  }
  aesthetic: {
    style: 'modern' | 'minimal' | 'luxury' | 'clinical' | 'warm' | 'tech' | 'classic'
    mood: 'professional' | 'friendly' | 'premium' | 'trustworthy' | 'innovative'
    visual_weight: 'light' | 'medium' | 'heavy'
    corner_radius: 'none' | 'subtle' | 'rounded' | 'pill'
  }
}

export interface ComponentSpec {
  name: string
  type: 'FRAME' | 'TEXT' | 'RECTANGLE' | 'ELLIPSE' | 'GROUP'
  properties: {
    x?: number
    y?: number
    width?: number
    height?: number
    fills?: Paint[]
    strokes?: Paint[]
    strokeWeight?: number
    cornerRadius?: number
    effects?: Effect[]
    layoutMode?: 'NONE' | 'HORIZONTAL' | 'VERTICAL'
    primaryAxisSizingMode?: 'FIXED' | 'AUTO'
    counterAxisSizingMode?: 'FIXED' | 'AUTO'
    paddingTop?: number
    paddingRight?: number
    paddingBottom?: number
    paddingLeft?: number
    itemSpacing?: number
    fontName?: FontName
    fontSize?: number
    letterSpacing?: LetterSpacing
    lineHeight?: LineHeight
    characters?: string
    textAlignHorizontal?: 'LEFT' | 'CENTER' | 'RIGHT' | 'JUSTIFIED'
    textAlignVertical?: 'TOP' | 'CENTER' | 'BOTTOM'
  }
  children?: ComponentSpec[]
}

export interface GeneratedPageSpec {
  pageName: string
  designSystem: AnalyzedDesignSystem
  components: ComponentSpec[]
  metadata: {
    brief: string
    references: string[]
    style_analysis: string
    reasoning: string
  }
}