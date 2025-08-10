export async function createTextNode(
  text: string,
  options: { family?: string; style?: string; size?: number; line?: number } = {}
): Promise<TextNode> {
  const node = figma.createText()
  const family = options.family || 'Inter'
  const style = options.style || 'Regular'
  
  try {
    await figma.loadFontAsync({ family, style })
    node.fontName = { family, style }
  } catch (error) {
    console.warn(`Failed to load font ${family} ${style}, using default`)
    // Fallback to default system font
    await figma.loadFontAsync({ family: 'Inter', style: 'Regular' })
    node.fontName = { family: 'Inter', style: 'Regular' }
  }
  
  node.characters = text
  if (options.size) node.fontSize = options.size
  if (options.line) node.lineHeight = { value: options.line, unit: 'PIXELS' }
  return node
}


