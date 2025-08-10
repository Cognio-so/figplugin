import type { UIToCoreMessage, CoreToUIMessage } from './types'

export function postToUI(message: CoreToUIMessage) {
  figma.ui.postMessage(message)
}

export function onUIMessage(handler: (msg: UIToCoreMessage) => Promise<void> | void) {
  figma.ui.onmessage = (msg: UIToCoreMessage) => {
    try {
      const maybePromise = handler(msg)
      if (maybePromise && typeof (maybePromise as any).then === 'function') {
        ;(maybePromise as Promise<void>).catch((err) => {
          console.error('Plugin error:', err)
          figma.notify('Plugin error: ' + (err && err.message ? err.message : String(err)), { 
            error: true,
            timeout: 5000 
          })
        })
      }
    } catch (err: any) {
      console.error('Plugin error:', err)
      figma.notify('Plugin error: ' + (err && err.message ? err.message : String(err)), { 
        error: true,
        timeout: 5000 
      })
    }
  }
}


