import { useEffect, useState } from 'react'
import './estilos-minaya.css'
import { token, rol } from './api'
import App from './App.jsx'            // V9 verificación (ya existía)
import Login from './vistas/Login.jsx'
import Registro from './vistas/Registro.jsx'
import Panel from './vistas/Panel.jsx'

// Cada integrante agrega su vista aquí: '/perfil': Perfil, '/generar': Generar, etc.
const RUTAS = {
  '/login': Login,
  '/registro': Registro,
  '/panel': Panel,
  '/verificar': App,
}
const PUBLICAS = ['/login', '/registro', '/verificar']

function EnConstruccion() {
  return <main className="rm-contenedor"><div className="alert alert-info">Vista en construcción.</div><a href="#/panel">Volver al panel</a></main>
}

export default function Router() {
  const [ruta, setRuta] = useState(() => window.location.hash.slice(1) || '/login')
  useEffect(() => {
    const alCambiar = () => setRuta(window.location.hash.slice(1) || '/login')
    window.addEventListener('hashchange', alCambiar)
    return () => window.removeEventListener('hashchange', alCambiar)
  }, [])

  const base = ruta.split('?')[0]
  if (!PUBLICAS.includes(base) && !token()) { window.location.hash = '#/login'; return null }
  if (base === '/panel' && rol() === 'tutor') { window.location.hash = '#/tutor'; return null }
  const Vista = RUTAS[base] || EnConstruccion
  return <Vista />
}
