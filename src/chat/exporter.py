from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def export_txt(chat_text: str) -> bytes:
    return chat_text.encode("utf-8")

def export_pdf(chat_text: str) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    x = 50
    y = height - 50
    line_height = 14

    for line in chat_text.splitlines():
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(x, y, line[:120])  # avoid very long line overflow
        y -= line_height

    c.save()
    buffer.seek(0)
    return buffer.read()
