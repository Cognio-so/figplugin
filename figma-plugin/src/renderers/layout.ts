export interface FrameOptions {
  name?: string
  width?: number
  padding?: number
  spacing?: number
}

export function createAutoLayoutFrame(options: FrameOptions = {}): FrameNode {
  const frame = figma.createFrame()
  frame.name = options.name ?? 'Frame'
  frame.layoutMode = 'VERTICAL'
  frame.primaryAxisSizingMode = 'AUTO'
  frame.counterAxisSizingMode = 'AUTO'
  frame.itemSpacing = options.spacing ?? 24
  const pad = options.padding ?? 24
  frame.paddingTop = pad
  frame.paddingRight = pad
  frame.paddingBottom = pad
  frame.paddingLeft = pad
  if (options.width) {
    frame.resizeWithoutConstraints(options.width, frame.height)
  }
  return frame
}


