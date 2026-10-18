import { useState } from 'react'
import { api } from '../api'

export default function Login() {
  const [correo, setCorreo] = useState('')
  const [clave, setClave] = useState('')
  const [error, setError] = useState('')

  async function ingresar(e) {
    e.preventDefault()
    setError('')
    try {
      const r = await api('/auth/login', { method: 'POST', body: { correo, clave } })
      sessionStorage.setItem('token', r.token)
      sessionStorage.setItem('rol', r.rol)
      window.location.hash = r.rol === 'tutor' ? '#/tutor' : '#/panel'
    } catch (err) {
      setError(err.message === 'Failed to fetch'
        ? 'No se pudo conectar con el servidor. Verifica que el backend esté en el puerto 8000.'
        : err.message)
    }
  }

  return (
    <main className="rm-login">
      <form className="card shadow-sm" onSubmit={ingresar}><div className="card-body">
        <h4 className="mb-3 text-center">Roadmap Académico</h4>
        {error && <div className="alert alert-danger" role="alert">{error}</div>}
        <input className="form-control mb-2" type="email" placeholder="Correo" aria-label="Correo"
          autoComplete="username" value={correo} onChange={e => setCorreo(e.target.value)} />
        <input className="form-control mb-3" type="password" placeholder="Contraseña" aria-label="Contraseña"
          autoComplete="current-password" value={clave} onChange={e => setClave(e.target.value)} />
        <button className="btn btn-primary w-100" type="submit">Ingresar</button>
        <a href="#/registro" className="d-block text-center mt-3">Crear cuenta</a>
      </div></form>
    </main>
  )
}
