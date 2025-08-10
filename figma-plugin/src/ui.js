const logEl = document.getElementById('log')
const briefEl = document.getElementById('brief')
const modelEl = document.getElementById('model')
const aiImagesEl = document.getElementById('aiImages')
const generateBtn = document.getElementById('btn-generate')

function append(text) {
  const div = document.createElement('div')
  div.textContent = text
  logEl.appendChild(div)
  logEl.scrollTop = logEl.scrollHeight
}

window.onmessage = (event) => {
  const msg = event.data.pluginMessage
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
  const referenceUrls = getAllReferenceUrls()
  
  if (!brief.trim()) {
    append('Error: Please enter a project brief')
    return
  }
  
  append(`Starting generation with ${referenceUrls.length} reference URLs...`)
  parent.postMessage({ 
    pluginMessage: { 
      type: 'GenerateFirstPage', 
      payload: { brief, model, useAiImages, referenceUrls } 
    } 
  }, '*')
  append('Requested: GenerateFirstPage')
})


