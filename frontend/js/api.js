const API = window.API_URL || 'http://localhost:8000'
function token() { return sessionStorage.getItem('token') }
function mensajeError(data, status) {
  const detail = data && typeof data === 'object' && 'detail' in data ? data.detail : data
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
  return 'Error en la solicitud (' + status + '). Revisa los datos e inténtalo de nuevo.'
}
async function api(ruta, opciones = {}) {
  const headers = { ...(opciones.headers || {}) }
  let body = opciones.body
  if (token()) headers.Authorization = 'Bearer ' + token()
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(body)
  }
  let response
  try {
    response = await fetch(API + ruta, { ...opciones, headers, body })
  } catch (cause) {
    throw new Error('No se pudo conectar con el backend en ' + API + '. Confirma que esté iniciado en el puerto 8000.')
  }
  if (response.status === 401 && token()) {
    sessionStorage.clear()
    window.location.href = 'login.html'
    throw new Error('La sesión venció. Inicia sesión nuevamente.')
  }
  const type = response.headers.get('content-type') || ''
  const data = type.includes('application/json') ? await response.json() : await response.text()
  if (!response.ok) {
    throw new Error(mensajeError(data, response.status))
  }
  return data
}
function salir() { sessionStorage.clear(); window.location.href = 'login.html' }
