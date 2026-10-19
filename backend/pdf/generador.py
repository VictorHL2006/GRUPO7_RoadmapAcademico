import io
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def generar_pdf(rec: dict, url_verificacion: str) -> bytes:
    """rec: estudiante, especialidad, creditos, cursos (lista de códigos)."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 790, "Roadmap Académico")
    c.setFont("Helvetica", 11)
    c.drawString(50, 760, "Estudiante: " + rec["estudiante"])
    c.drawString(50, 740, "Especialidad recomendada: " + rec["especialidad"])
    c.drawString(50, 720, "Créditos de la carga: " + str(rec["creditos"]))
    y = 690
    for codigo in rec["cursos"]:
        c.drawString(70, y, "- " + codigo)
        y -= 18
        if y < 230:  # no invadir la zona del QR
            break
    img = io.BytesIO()
    qrcode.make(url_verificacion).save(img, format="PNG")
    img.seek(0)
    c.drawImage(ImageReader(img), 400, 80, 130, 130)
    c.drawString(400, 65, "Escanee para verificar")
    c.save()
    return buf.getvalue()