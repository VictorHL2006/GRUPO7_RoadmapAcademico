const API = window.API_URL || 'http://localhost:8000'
function token() { return sessionStorage.getItem('token') }
async function api(ruta, opciones = {}) {
  const headers = { ...(opciones.headers || {}) }
  let body = opciones.body
  if (token()) headers.Authorization = 'Bearer ' + token()
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
    body = JSON.stringify(body)
  }
  const response = await fetch(API + ruta, { ...opciones, headers, body })
  if (response.status === 401 && token()) {
    sessionStorage.clear()
    window.location.href = 'login.html'
    throw new Error('La sesión venció. Inicia sesión nuevamente.')
  }
  const type = response.headers.get('content-type') || ''
  const data = type.includes('application/json') ? await response.json() : await response.text()
  if (!response.ok) {
    const detail = data && typeof data === 'object' ? data.detail : data
    throw new Error(typeof detail === 'string' ? detail : 'Error en la solicitud (' + response.status + ')')
  }
  return data
}
function salir() { sessionStorage.clear(); window.location.href = 'login.html' }
