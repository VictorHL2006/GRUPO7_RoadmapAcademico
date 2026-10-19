import { useEffect, useState } from 'react'
import './estilos-minaya.css'
import { token, rol } from './api'
import Verificacion from './App.jsx'
import Login from './vistas/Login.jsx'
import Registro from './vistas/Registro.jsx'
import Panel from './vistas/Panel.jsx'
import Tutor from './vistas/Tutor.jsx'

const RUTAS = {
  '/login': Login, '/registro': Registro, '/panel': Panel,
  '/verificar': Verificacion, '/tutor': Tutor,
}
const PAGINAS_ESTATICAS = {
  '/perfil': '/perfil.html', '/intereses': '/intereses.html',
  '/generar': '/generar.html', '/roadmaps': '/roadmaps.html', '/visor': '/visor.html',
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
  if (base === '/tutor' && rol() !== 'tutor') { window.location.hash = token() ? '#/panel' : '#/login'; return null }
  if (PAGINAS_ESTATICAS[base]) { window.location.replace(PAGINAS_ESTATICAS[base] + (ruta.includes('?') ? '?' + ruta.split('?')[1] : '')); return null }
  const Vista = RUTAS[base] || EnConstruccion
  return <Vista />
}
