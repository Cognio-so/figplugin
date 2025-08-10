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
          figma.notify('Error: ' + (err?.message ?? String(err)))
        })
      }
    } catch (err: any) {
      figma.notify('Error: ' + (err?.message ?? String(err)))
    }
  }
}


