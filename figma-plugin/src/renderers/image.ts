export async function createImageRectFromUrl(url: string, role?: string): Promise<RectangleNode> {
  const rect = figma.createRectangle()
  const image = await figma.createImageAsync(url)
  rect.fills = [
    { type: 'IMAGE', scaleMode: 'FILL', imageHash: image.hash } as ImagePaint,
  ]
  if (role) rect.setPluginData('role', role)
  return rect
}

export function setPinned(node: BaseNode, pinned: boolean) {
  node.setPluginData('pinned', pinned ? 'true' : 'false')
}


