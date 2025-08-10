type UIMessage =
  | { type: 'RenderProgress'; payload: { step: string; percent: number } }
  | { type: 'Error'; payload: { code: string; message: string; suggestion?: string } }
  | { type: 'Rendered'; payload: { pageName: string } }

const logEl = document.getElementById('log') as HTMLDivElement
const briefEl = document.getElementById('brief') as HTMLTextAreaElement
const modelEl = document.getElementById('model') as HTMLSelectElement
const aiImagesEl = document.getElementById('aiImages') as HTMLInputElement
const generateBtn = document.getElementById('btn-generate') as HTMLButtonElement

function append(text: string) {
  const div = document.createElement('div')
  div.textContent = text
  logEl.appendChild(div)
  logEl.scrollTop = logEl.scrollHeight
}

window.onmessage = (event: MessageEvent) => {
  const msg = event.data.pluginMessage as UIMessage
  if (!msg) return
  if (msg.type === 'RenderProgress') {
    append(`${msg.payload.step} ${msg.payload.percent}%`)
  } else if (msg.type === 'Rendered') {
    append(`Rendered page: ${msg.payload.pageName}`)
  } else if (msg.type === 'Error') {
    append(`Error: ${msg.payload.message}`)
  }
}

generateBtn.addEventListener('click', () => {
  const brief = briefEl.value
  const model = modelEl.value
  const useAiImages = aiImagesEl.checked
  parent.postMessage({ pluginMessage: { type: 'GenerateFirstPage', payload: { brief, model, useAiImages } } }, '*')
  append('Requested: GenerateFirstPage')
})


