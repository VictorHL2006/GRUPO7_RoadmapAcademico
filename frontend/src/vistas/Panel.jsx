import { useEffect, useState } from 'react'
import { api } from '../api'
import Menu from '../componentes/Menu'

// Si GET /perfil aún no responde se muestran valores de ejemplo (declararlo en la ficha; poner false al integrar).
const USAR_EJEMPLO_SI_FALLA = true

const ACCESOS = [
  ['Perfil', 'Datos personales e historial de cursos.', '#/perfil'],
  ['Intereses', 'Elige las áreas que te interesan.', '#/intereses'],
  ['Generar Roadmap', 'Obtén tu recomendación firmada.', '#/generar'],
  ['Mis Roadmaps', 'Consulta los documentos emitidos.', '#/roadmaps'],
]

export default function Panel() {
  const [p, setP] = useState(null)
  const [ejemplo, setEjemplo] = useState(false)

  useEffect(() => {
    api('/perfil')
      .then(setP)
      .catch(() => {
        if (!USAR_EJEMPLO_SI_FALLA) return
        setP({ nombres: 'Estudiante demo', cursos_aprobados: 12, creditos_acumulados: 34 })
        setEjemplo(true)
      })
  }, [])

  return (
    <>
      <Menu activa="/panel" />
      <main className="rm-contenedor">
        {ejemplo && <div className="alert alert-warning" role="alert">Datos de ejemplo: el endpoint /perfil aún no responde.</div>}
        <section className="rm-tarjeta mb-4" aria-label="Resumen académico">
          <h4 className="mb-3">Hola, {p ? p.nombres : 'estudiante'}</h4>
          <div className="row text-center">
            <div className="col-6"><div className="rm-numero">{p ? p.cursos_aprobados : '-'}</div><div className="text-muted">Cursos aprobados</div></div>
            <div className="col-6"><div className="rm-numero">{p ? p.creditos_acumulados : '-'}</div><div className="text-muted">Créditos acumulados</div></div>
          </div>
        </section>
        <div className="row g-3">
          {ACCESOS.map(([titulo, texto, ruta]) => (
            <div className="col-md-6 col-lg-3" key={ruta}>
              <a className="rm-tarjeta rm-acceso" href={ruta}><h5>{titulo}</h5><p className="mb-0 text-muted">{texto}</p></a>
            </div>
          ))}
        </div>
      </main>
    </>
  )
}
