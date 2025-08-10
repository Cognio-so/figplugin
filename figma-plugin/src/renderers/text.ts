export async function createTextNode(
  text: string,
  options: { family?: string; style?: string; size?: number; line?: number } = {}
): Promise<TextNode> {
  const node = figma.createText()
  const family = options.family ?? 'Inter'
  const style = options.style ?? 'Regular'
  await figma.loadFontAsync({ family, style })
  node.characters = text
  node.fontName = { family, style }
  if (options.size) node.fontSize = options.size
  if (options.line) node.lineHeight = { value: options.line, unit: 'PIXELS' }
  return node
}


