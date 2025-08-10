export interface UserPrefs {
  model?: string
  useAiImages?: boolean
  chatHistory?: { role: 'user' | 'assistant'; content: string }[]
}

const CLIENT_KEY = 'g99:prefs'

export async function loadUserPrefs(): Promise<UserPrefs> {
  const data = await figma.clientStorage.getAsync(CLIENT_KEY)
  return (data as UserPrefs) ?? {}
}

export async function saveUserPrefs(prefs: UserPrefs): Promise<void> {
  await figma.clientStorage.setAsync(CLIENT_KEY, prefs)
}

export function getShared(key: string): string | null {
  return figma.root.getSharedPluginData('g99', key) || null
}

export function setShared(key: string, value: string): void {
  figma.root.setSharedPluginData('g99', key, value)
}


