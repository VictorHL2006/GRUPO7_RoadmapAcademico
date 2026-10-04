import { useState } from 'react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [documento, setDocumento] = useState(null)
  const [firma, setFirma] = useState(null)
  const [resultado, setResultado] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState('')

  const seleccionarDocumento = (evento) => {
    setDocumento(evento.target.files[0] || null)
    setResultado(null)
    setMensaje('')
  }

  const seleccionarFirma = (evento) => {
    setFirma(evento.target.files[0] || null)
    setResultado(null)
    setMensaje('')
  }

  const verificarDocumento = async () => {
    if (!documento) {
      setMensaje('Seleccione el documento que desea verificar.')
      return
    }

    if (!firma) {
      setMensaje('Seleccione el archivo de firma digital (.sig).')
      return
    }

    setCargando(true)
    setMensaje('')
    setResultado(null)

    const formulario = new FormData()

    formulario.append('documento', documento)
    formulario.append('firma', firma)

    try {
      const respuesta = await fetch(
        `${API_URL}/verificar`,
        {
          method: 'POST',
          body: formulario
        }
      )

      const datos = await respuesta.json()

      if (!respuesta.ok) {
        throw new Error(
          datos.detail || 'Error al verificar el documento.'
        )
      }

      setResultado(datos)

    } catch (error) {
      setMensaje(
        error.message || 'No se pudo conectar con el servidor.'
      )
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="app">

      <header className="header">
        <h1>Roadmap Académico</h1>

        <p>
          Sistema de verificación de autenticidad e integridad
          del documento académico.
        </p>
      </header>

      <main className="contenido">

        <section className="card">

          <h2>Verificar Roadmap Académico</h2>

          <p>
            Seleccione el documento y su firma digital para
            comprobar su autenticidad e integridad.
          </p>

          <label>
            Documento:
          </label>

          <input
            type="file"
            onChange={seleccionarDocumento}
          />

          {documento && (
            <p>
              Documento seleccionado:{' '}
              <strong>{documento.name}</strong>
            </p>
          )}

          <br />

          <label>
            Firma digital:
          </label>

          <input
            type="file"
            onChange={seleccionarFirma}
          />

          {firma && (
            <p>
              Firma seleccionada:{' '}
              <strong>{firma.name}</strong>
            </p>
          )}

          <button
            onClick={verificarDocumento}
            disabled={cargando}
          >
            {cargando
              ? 'Verificando...'
              : 'Verificar documento'}
          </button>

          {mensaje && (
            <div className="mensaje error">
              {mensaje}
            </div>
          )}

          {resultado && (
            <div className="resultado">

              <h3>Resultado de la verificación</h3>

              <p>
                Resultado:{' '}
                <strong>{resultado.resultado}</strong>
              </p>

            </div>
          )}

        </section>

      </main>

      <footer className="footer">
        <p>
          Proyecto Roadmap Académico - UCSM
        </p>
      </footer>

    </div>
  )
}

export default App