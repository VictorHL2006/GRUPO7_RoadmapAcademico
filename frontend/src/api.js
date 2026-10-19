export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const token = () => sessionStorage.getItem('token')
export const rol = () => sessionStorage.getItem('rol')

function mensajeError(datos, status) {
  const detail = datos && typeof datos === 'object' && 'detail' in datos ? datos.detail : datos
  if (typeof detail === 'string' && detail.trim()) return detail
  if (Array.isArray(detail)) {
    const mensajes = detail.map(item => {
      if (typeof item === 'string') return item
      if (item && typeof item === 'object') {
        const campo = Array.isArray(item.loc) ? item.loc.filter(x => x !== 'body').join('.') : ''
        return [campo, item.msg].filter(Boolean).join(': ')
      }
      return ''
    }).filter(Boolean)
    if (mensajes.length) return mensajes.join(' · ')
  }
  if (detail && typeof detail === 'object') {
    if (typeof detail.msg === 'string') return detail.msg
    if (typeof detail.message === 'string') return detail.message
  }
  return `Error en la solicitud (${status}). Revisa los datos e inténtalo de nuevo.`
}

export function salir() {
  sessionStorage.clear()
  window.location.hash = '#/login'
}

export async function api(ruta, opciones = {}) {
  const headers = { ...(opciones.headers || {}) }
  let body = opciones.body
  if (token()) headers.Authorization = 'Bearer ' + token()
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(body)
  }
  let r
  try {
    r = await fetch(API_URL + ruta, { ...opciones, headers, body })
  } catch {
    throw new Error(`No se pudo conectar con el backend en ${API_URL}. Confirma que esté iniciado en el puerto 8000.`)
  }
  if (r.status === 401 && token()) { salir(); return }
  const datos = await r.json()
  if (!r.ok) throw new Error(mensajeError(datos, r.status))
  return datos
}

