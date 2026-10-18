import { rol, salir } from '../api'

export default function Menu({ activa }) {
  const items = rol() === 'tutor'
    ? [['Estudiantes', '/tutor']]
    : [['Panel', '/panel'], ['Perfil', '/perfil'], ['Intereses', '/intereses'],
       ['Generar', '/generar'], ['Mis Roadmaps', '/roadmaps']]
  return (
    <nav className="navbar navbar-expand-lg navbar-dark bg-primary px-3">
      <a className="navbar-brand" href="#/panel">Roadmap Académico</a>
      <ul className="navbar-nav me-auto">
        {items.map(([texto, ruta]) => (
          <li className="nav-item" key={ruta}>
            <a className={'nav-link ' + (ruta === activa ? 'active' : '')} href={'#' + ruta}>{texto}</a>
          </li>
        ))}
      </ul>
      <button className="btn btn-light btn-sm" onClick={salir}>Cerrar sesión</button>
    </nav>
  )
}
