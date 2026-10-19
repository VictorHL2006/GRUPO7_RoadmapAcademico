function cargarMenu(activa) {
  const rol = sessionStorage.getItem('rol')
  if (!sessionStorage.getItem('token')) { window.location.href = 'login.html'; return }
  if (window.location.pathname.endsWith('tutor.html') && rol !== 'tutor') { window.location.href = 'panel.html'; return }
  if (rol === 'tutor' && !window.location.pathname.endsWith('tutor.html')) { window.location.href = 'tutor.html'; return }
  const items = rol === 'tutor'
    ? [['Estudiantes', 'tutor.html']]
    : [['Panel', 'panel.html'], ['Perfil', 'perfil.html'], ['Intereses', 'intereses.html'], ['Generar', 'generar.html'], ['Mis Roadmaps', 'roadmaps.html']]
  const links = items.map(([label, href]) => '<li class="nav-item"><a class="nav-link ' + (href === activa ? 'active' : '') + '" href="' + href + '">' + label + '</a></li>').join('')
  const host = document.getElementById('menu') || document.getElementById('menu-container')
  if (host) host.innerHTML = '<nav class="navbar navbar-expand-lg navbar-dark bg-primary px-3"><a class="navbar-brand" href="panel.html">Roadmap Académico</a><ul class="navbar-nav me-auto">' + links + '</ul><button class="btn btn-light btn-sm" onclick="salir()">Cerrar sesión</button></nav>'
}