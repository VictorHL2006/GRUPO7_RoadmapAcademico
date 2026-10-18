import { useState } from 'react'
import { api } from '../api'

export default function Registro() {
  const [f, setF] = useState({ codigo: '', nombres: '', correo: '', clave: '', clave2: '' })
  const [aviso, setAviso] = useState(null)
  const cambiar = campo => e => setF({ ...f, [campo]: e.target.value })

  async function registrar(e) {
    e.preventDefault()
    if (!f.codigo.trim() || !f.nombres.trim() || !f.correo.trim() || !f.clave)
      return setAviso(['danger', 'Completa todos los campos.'])
    if (f.clave.length < 8) return setAviso(['danger', 'La contraseña debe tener al menos 8 caracteres.'])
    if (f.clave !== f.clave2) return setAviso(['danger', 'Las contraseñas no coinciden.'])
    try {
      await api('/auth/registro', { method: 'POST', body: {
        codigo: f.codigo.trim(), nombres: f.nombres.trim(), correo: f.correo.trim(), clave: f.clave } })
      setAviso(['success', 'Cuenta creada. Te llevamos al inicio de sesión…'])
      setTimeout(() => { window.location.hash = '#/login' }, 1500)
    } catch (err) {
      setAviso(['danger', err.message === 'Failed to fetch' ? 'No se pudo conectar con el servidor.' : err.message])
    }
  }

  return (
    <main className="rm-login">
      <form className="card shadow-sm" onSubmit={registrar}><div className="card-body">
        <h4 className="mb-3 text-center">Crear cuenta de estudiante</h4>
        {aviso && <div className={'alert alert-' + aviso[0]} role="alert">{aviso[1]}</div>}
        <input className="form-control mb-2" placeholder="Código de estudiante" aria-label="Código" value={f.codigo} onChange={cambiar('codigo')} />
        <input className="form-control mb-2" placeholder="Nombres y apellidos" aria-label="Nombres" value={f.nombres} onChange={cambiar('nombres')} />
        <input className="form-control mb-2" type="email" placeholder="Correo" aria-label="Correo" value={f.correo} onChange={cambiar('correo')} />
        <input className="form-control mb-2" type="password" placeholder="Contraseña (mínimo 8 caracteres)" aria-label="Contraseña" autoComplete="new-password" value={f.clave} onChange={cambiar('clave')} />
        <input className="form-control mb-3" type="password" placeholder="Confirmar contraseña" aria-label="Confirmar contraseña" autoComplete="new-password" value={f.clave2} onChange={cambiar('clave2')} />
        <button className="btn btn-primary w-100" type="submit">Registrar</button>
        <a href="#/login" className="d-block text-center mt-3">Volver a iniciar sesión</a>
      </div></form>
    </main>
  )
}
