import { useEffect, useState } from 'react'
import { api } from './api'
import './App.css'

function Resultado({ datos, reiniciar }) {
  const autentico = datos.resultado === 'auténtico'
  return (
    <section className={'resultado-verificacion ' + (autentico ? 'es-autentico' : 'es-alterado')} aria-live="polite">
      <h2>{autentico ? 'Documento auténtico' : 'Documento alterado'}</h2>
      {autentico ? <>
        <p>La firma digital coincide con el documento.</p>
        {datos.estudiante && <p><strong>Código del estudiante:</strong> {datos.estudiante}</p>}
        {datos.emitido && <p><strong>Fecha de emisión:</strong> {new Date(datos.emitido).toLocaleString('es-PE')}</p>}
        {datos.hash && <p className="hash-documento"><strong>Hash SHA-256:</strong><br />{datos.hash}</p>}
      </> : <>
        <p>La firma no coincide con el documento o el archivo no es el original.</p>
        <p>Solicita el documento original a quien lo emitió.</p>
      </>}
      <button type="button" onClick={reiniciar}>Verificar otro documento</button>
    </section>
  )
}

export default function Verificacion() {
  const [documento, setDocumento] = useState(null)
  const [firma, setFirma] = useState(null)
  const [resultado, setResultado] = useState(null)
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.split('?')[1] || '')
    const id = params.get('id')
    if (!id) return
    setCargando(true)
    api('/verificar/' + encodeURIComponent(id))
      .then(setResultado)
      .catch(e => setError(e.message || 'No se pudo verificar el documento.'))
      .finally(() => setCargando(false))
  }, [])

  async function verificarArchivo(e) {
    e.preventDefault()
    setError('')
    if (!documento || !firma) return setError('Selecciona el PDF y el archivo de firma .sig.')
    const form = new FormData()
    form.append('documento', documento)
    form.append('firma', firma)
    setCargando(true)
    try { setResultado(await api('/verificar', { method: 'POST', body: form })) }
    catch (err) { setError(err.message || 'No se pudo verificar el documento.') }
    finally { setCargando(false) }
  }

  function reiniciar() {
    setResultado(null); setError(''); setDocumento(null); setFirma(null)
    window.history.replaceState(null, '', window.location.pathname + window.location.search + '#/verificar')
  }

  return (
    <div className="app">
      <header className="header"><h1>Verificar Roadmap Académico</h1><p>Comprueba la firma digital y la integridad del documento emitido.</p></header>
      <main className="contenido">
        {cargando && <p role="status">Verificando documento…</p>}
        {error && <div className="alert alert-danger" role="alert">{error}</div>}
        {resultado ? <Resultado datos={resultado} reiniciar={reiniciar} /> : !cargando && <form className="card" onSubmit={verificarArchivo}>
          <h2>Portal público de verificación</h2>
          <p>Sube el PDF y su firma digital (.sig) para verificarlo manualmente.</p>
          <label htmlFor="pdf">Documento PDF</label>
          <input id="pdf" type="file" accept="application/pdf,.pdf" onChange={e => setDocumento(e.target.files?.[0] || null)} required />
          <label htmlFor="firma">Firma digital</label>
          <input id="firma" type="file" accept=".sig,application/octet-stream" onChange={e => setFirma(e.target.files?.[0] || null)} required />
          <button type="submit" disabled={cargando}>{cargando ? 'Verificando…' : 'Verificar documento'}</button>
        </form>}
      </main>
      <footer className="footer"><a href="#/login">Iniciar sesión</a></footer>
    </div>
  )
}
