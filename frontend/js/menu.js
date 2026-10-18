function cargarMenu(activa) {
  const rol = sessionStorage.getItem("rol");
  const items = rol === "tutor"
    ? [["Estudiantes", "tutor.html"]]
    : [["Panel", "panel.html"], ["Perfil", "perfil.html"], ["Intereses", "intereses.html"],
       ["Generar", "generar.html"], ["Mis Roadmaps", "roadmaps.html"]];
  const links = items.map(function (i) {
    return '<li class="nav-item"><a class="nav-link ' + (i[1] === activa ? "active" : "") +
           '" href="' + i[1] + '">' + i[0] + '</a></li>';
  }).join("");
  document.getElementById("menu").innerHTML =
    '<nav class="navbar navbar-expand-lg navbar-dark bg-primary px-3">' +
    '<a class="navbar-brand" href="panel.html">Roadmap Académico</a>' +
    '<ul class="navbar-nav me-auto">' + links + '</ul>' +
    '<button class="btn btn-light btn-sm" onclick="salir()">Cerrar sesión</button></nav>';
}
function salir() { sessionStorage.clear(); location.href = "login.html"; }
// Úsalo al inicio de las vistas privadas: exigirSesion("estudiante") o exigirSesion("tutor")
function exigirSesion(rolPermitido) {
  if (!token() || (rolPermitido && sessionStorage.getItem("rol") !== rolPermitido)) {
    location.href = "login.html";
  }
}
