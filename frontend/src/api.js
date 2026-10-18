export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const token = () => sessionStorage.getItem('token')
export const rol = () => sessionStorage.getItem('rol')

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
  const r = await fetch(API_URL + ruta, { ...opciones, headers, body })
  if (r.status === 401 && token()) { salir(); return }
  const datos = await r.json()
  if (!r.ok) throw new Error(datos.detail || 'Error en la solicitud')
  return datos
}
