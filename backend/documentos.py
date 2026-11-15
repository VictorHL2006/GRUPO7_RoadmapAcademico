"""Generación del PDF del roadmap con código QR de verificación."""
import io
from datetime import datetime, timezone
from xml.sax.saxutils import escape
 
import qrcode
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
def _qr_png(texto: str) -> io.BytesIO:
    buf = io.BytesIO()
    qrcode.make(texto, box_size=8, border=2).save(buf, format="PNG")
    buf.seek(0)
    return buf
 
 
def generar_pdf(usuario, recomendacion, malla, codigo_verificacion, url_verificacion) -> bytes:
    nombres = {c["codigo"]: c["nombre"] for c in malla["cursos"]}
    creditos = {c["codigo"]: c["creditos"] for c in malla["cursos"]}
    est = getSampleStyleSheet()
    titulo = ParagraphStyle("t", parent=est["Title"], textColor=colors.HexColor("#1F3864"))
    normal, pequeno = est["BodyText"], ParagraphStyle("p", parent=est["BodyText"], fontSize=8)
 
    historia = [Paragraph("ROADMAP ACADÉMICO", titulo),
                Paragraph("Plan de estudios personalizado", est["Heading3"]), Spacer(1, 8)]
    historia += [
        Paragraph(f"<b>Estudiante:</b> {escape(usuario['nombres'])} "
                  f"({escape(usuario['codigo'])})", normal),
        Paragraph("<b>Especialidad sugerida:</b> "
                  + escape(recomendacion["especialidad"] or "Sin coincidencia con tus intereses"),
                  normal),
        Paragraph("<b>Emitido:</b> " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                  normal), Spacer(1, 10)]
 
    filas = [["Ciclo", "Cursos", "Créditos"]]
    for ciclo in recomendacion["roadmap"]:
        detalle = "\n".join(f"{c} - {nombres.get(c, c)}" for c in ciclo["cursos"])
        filas.append([str(ciclo["ciclo"]), detalle, str(ciclo["creditos"])])
    if len(filas) == 1:
        filas.append(["-", "No hay cursos pendientes por programar.", "0"])
    tabla = Table(filas, colWidths=[1.6 * cm, 12 * cm, 2.4 * cm], repeatRows=1)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F3864")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("FONTSIZE", (0, 0), (-1, -1), 9)]))
    historia += [tabla, Spacer(1, 10)]
    for a in recomendacion["advertencias"]:
        historia.append(Paragraph("• " + escape(a), pequeno))
 
    historia += [Spacer(1, 16),
                 Image(_qr_png(url_verificacion), width=3.6 * cm, height=3.6 * cm),
                 Paragraph("Escanea el código QR para verificar la autenticidad de este documento.",
                           pequeno),
                 Paragraph(escape(url_verificacion), pequeno)]
 
    def pie(canvas, _doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.drawString(2 * cm, 1.2 * cm, f"Código de verificación: {codigo_verificacion}")
        canvas.drawString(2 * cm, 0.8 * cm,
                          "Documento firmado digitalmente (RSA-2048, SHA-256). "
                          "Cualquier modificación invalida la firma.")
        canvas.restoreState()
 
    buf = io.BytesIO()
    SimpleDocTemplate(buf, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                      topMargin=2 * cm, bottomMargin=2.2 * cm,
                      title="Roadmap Académico").build(historia, onFirstPage=pie, onLaterPages=pie)
    return buf.getvalue()
