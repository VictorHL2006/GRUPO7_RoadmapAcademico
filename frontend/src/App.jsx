import { useState } from 'react'
import './App.css'

function App() {
  const [archivo, setArchivo] = useState(null)
  const [resultado, setResultado] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState('')

  const verificarDocumento = async () => {
    if (!archivo) {
      setMensaje('Seleccione un archivo para verificar.')
      return
    }

    setCargando(true)
    setMensaje('')
    setResultado(null)

    const formulario = new FormData()
    formulario.append('archivo', archivo)

    try {
      const respuesta = await fetch('http://localhost:8000/verificar', {
        method: 'POST',
        body: formulario
      })

      const datos = await respuesta.json()

      if (!respuesta.ok) {
        throw new Error(datos.detail || 'Error al verificar el documento.')
      }

      setResultado(datos)
    } catch (error) {
      setMensaje(error.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Roadmap Académico</h1>
        <p>
          Verificación de autenticidad e integridad del documento académico
        </p>
      </header>

      <main className="contenido">
        <section className="card">
          <h2>Verificar Roadmap Académico</h2>

          <p>
            Seleccione el documento generado para comprobar su integridad
            mediante el servicio de verificación.
          </p>

          <input
            type="file"
            onChange={(e) => setArchivo(e.target.files[0])}
          />

          {archivo && (
            <p>
              Archivo seleccionado: <strong>{archivo.name}</strong>
            </p>
          )}

          <button onClick={verificarDocumento} disabled={cargando}>
            {cargando ? 'Verificando...' : 'Verificar documento'}
          </button>

          {mensaje && (
            <div className="mensaje error">
              {mensaje}
            </div>
          )}

          {resultado && (
            <div className="resultado">
              <h3>Resultado de la verificación</h3>

              <pre>
                {JSON.stringify(resultado, null, 2)}
              </pre>
            </div>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>Proyecto Roadmap Académico - UCSM</p>
      </footer>
    </div>
  )
}

export default App