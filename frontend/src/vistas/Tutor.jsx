import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import Menu from '../componentes/Menu'

export default function Tutor() {
  const [filas, setFilas] = useState([])
  const [busqueda, setBusqueda] = useState('')
  const [especialidad, setEspecialidad] = useState('')
  const [error, setError] = useState('')
  const [seleccionado, setSeleccionado] = useState(null)
  const [roadmaps, setRoadmaps] = useState([])

  useEffect(() => {
    api('/tutor/estudiantes').then(setFilas).catch(e => setError(e.message || 'No se pudo cargar la lista.'))
  }, [])

  const especialidades = [...new Set(filas.map(f => f.especialidad).filter(Boolean))].sort()
  const visibles = useMemo(() => filas.filter(f => {
    const q = busqueda.trim().toLocaleLowerCase('es')
    const coincideTexto = !q || (f.codigo || '').toLocaleLowerCase('es').includes(q) || (f.nombres || '').toLocaleLowerCase('es').includes(q)
    return coincideTexto && (!especialidad || f.especialidad === especialidad)
  }), [filas, busqueda, especialidad])

  async function verRoadmaps(estudiante) {
    setError(''); setSeleccionado(estudiante); setRoadmaps([])
    try { setRoadmaps(await api('/tutor/estudiantes/' + encodeURIComponent(estudiante.codigo) + '/roadmaps')) }
    catch (e) { setError(e.message || 'No se pudieron cargar los roadmaps.') }
  }

  return <><Menu activa="/tutor" /><main className="rm-contenedor">
    <h1>Panel de tutor</h1><p>Estudiantes y sus roadmaps emitidos.</p>
    {error && <div className="alert alert-danger" role="alert">{error}</div>}
    <div className="row g-2 mb-3">
      <div className="col-md-7"><label className="form-label" htmlFor="buscar">Buscar por código o nombre</label><input id="buscar" className="form-control" value={busqueda} onChange={e => setBusqueda(e.target.value)} /></div>
      <div className="col-md-5"><label className="form-label" htmlFor="especialidad">Filtrar por especialidad</label><select id="especialidad" className="form-select" value={especialidad} onChange={e => setEspecialidad(e.target.value)}><option value="">Todas</option>{especialidades.map(x => <option key={x}>{x}</option>)}</select></div>
    </div>
    <div className="table-responsive"><table className="table table-striped align-middle"><thead><tr><th>Código</th><th>Estudiante</th><th>Última especialidad</th><th>Roadmaps</th><th>Acción</th></tr></thead>
      <tbody>{visibles.map(f => <tr key={f.codigo}><td>{f.codigo || '—'}</td><td>{f.nombres}</td><td>{f.especialidad || 'Sin roadmaps'}</td><td>{f.cantidad_roadmaps}</td><td>{f.cantidad_roadmaps > 0 ? <button type="button" className="btn btn-sm btn-outline-primary" onClick={() => verRoadmaps(f)}>Ver roadmaps</button> : '—'}</td></tr>)}
      {!visibles.length && <tr><td colSpan="5" className="text-center text-muted">No hay estudiantes que coincidan.</td></tr>}</tbody></table></div>
    {seleccionado && <section className="rm-tarjeta mt-4"><h2 className="h5">Roadmaps de {seleccionado.nombres}</h2>
      {!roadmaps.length ? <p className="text-muted mb-0">No hay documentos emitidos.</p> : <ul className="mb-0">{roadmaps.map(r => <li key={r.id}>Emitido {new Date(r.emitido).toLocaleDateString('es-PE')} · {r.especialidad || 'Sin especialidad'} · {r.creditos ?? '—'} créditos — <a href={'#/verificar?id=' + encodeURIComponent(r.id)}>Verificar</a></li>)}</ul>}
    </section>}
  </main></>
}