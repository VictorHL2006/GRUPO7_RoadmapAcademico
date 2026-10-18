const API = "http://localhost:8000";

function token() { return sessionStorage.getItem("token"); }

async function api(ruta, opciones) {
  opciones = opciones || {};
  const headers = opciones.headers || {};
  if (token()) headers["Authorization"] = "Bearer " + token();
  if (opciones.body && !(opciones.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    opciones.body = JSON.stringify(opciones.body);
  }
  const r = await fetch(API + ruta, Object.assign({}, opciones, { headers: headers }));
  if (r.status === 401 && token()) { sessionStorage.clear(); location.href = "login.html"; return; }
  const datos = await r.json();
  if (!r.ok) throw new Error(datos.detail || "Error en la solicitud");
  return datos;
}
