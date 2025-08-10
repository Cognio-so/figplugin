export type ModelProvider = 'openai' | 'anthropic' | 'google' | 'local'

export interface DesignSystem {
  colors: Record<string, string>
  typography: Record<string, any>
  spacingScale: number[]
  radius: Record<string, number>
  grid?: { container: number; columns: number; gutter: number }
  components?: Record<string, any>
}

export interface SectionSpec {
  type: 'Header' | 'Hero' | 'Features' | 'Testimonials' | 'CTA' | 'Footer'
  props: Record<string, any>
}

export interface PageSpec {
  pageName: string
  sections: SectionSpec[]
  assets?: Record<string, string>
}

export interface GenerateFirstPagePayload {
  projectId?: string
  model?: string
  useAiImages?: boolean
  brief?: string
  refs?: string[]
  uploads?: Array<{ role: string; name: string; blobUrl: string }>
}

export type UIToCoreMessage =
  | { type: 'SessionStart'; payload: { projectId?: string } }
  | { type: 'GenerateFirstPage'; payload: GenerateFirstPagePayload }
  | { type: 'Redesign'; payload: { pinnedSlots?: string[] } }
  | { type: 'GenerateSitePages'; payload: { pages: string[] } }
  | { type: 'ApplyImages'; payload: { mapping: Record<string, string> } }

export type CoreToUIMessage =
  | { type: 'RenderProgress'; payload: { step: string; percent: number } }
  | { type: 'Error'; payload: { code: string; message: string; suggestion?: string } }
  | { type: 'Rendered'; payload: { pageName: string } }


