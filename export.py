from datetime import datetime
import os
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

def export_json(data: dict, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def export_pdf(data: dict, out_path: str):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    x_margin, y_margin = 20*mm, 20*mm
    y = height - y_margin

    def line(txt, size=12, dy=14):
        nonlocal y
        c.setFont("Helvetica", size)
        c.drawString(x_margin, y, txt)
        y -= dy

    line("SmartOBD-PRO - Reporte de Diagnóstico", 16, 20)
    line(f"Fecha: {data.get('timestamp', '')}")
    line(f"VIN:   {data.get('vin') or 'No disponible'}")
    line(f"Voltaje módulo: {data.get('voltage')} V")
    line("")

    basic = data.get("basic", {})
    line("Lecturas básicas:", 14, 18)
    for k in ["rpm", "speed", "temp"]:
        line(f" - {k.upper()}: {basic.get(k)}")

    line("")
    line("Códigos DTC:", 14, 18)
    dtcs = data.get("dtcs", [])
    if not dtcs:
        line(" - Sin DTCs almacenados ✅")
    else:
        for d in dtcs:
            line(f" - {d.get('code')}: {d.get('desc')}")

    c.showPage()
    c.save()
