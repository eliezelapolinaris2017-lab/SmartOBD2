import argparse
from datetime import datetime
import os

import matplotlib.pyplot as plt
import time

import obd
from obd_interface import connect, read_basic, read_vin, read_voltage, read_live
from diagnostics import read_dtcs, clear_dtcs, log_csv, snapshot
from export import export_json, export_pdf

def cmd_read_basic(args):
    conn = connect(args.port, args.baud)
    print("Estado:", conn.status())
    print(read_basic(conn))

def cmd_dtc(args):
    conn = connect(args.port, args.baud)
    dtcs = read_dtcs(conn)
    if not dtcs:
        print("Sin DTCs ✅")
    else:
        for code, desc in dtcs:
            print(f"{code}: {desc}")

def cmd_clear(args):
    conn = connect(args.port, args.baud)
    clear_dtcs(conn)
    print("DTCs borrados ✅")

def cmd_vin(args):
    conn = connect(args.port, args.baud)
    vin = read_vin(conn)
    print("VIN:", vin or "No disponible")

def cmd_battery(args):
    conn = connect(args.port, args.baud)
    v = read_voltage(conn)
    print("Voltaje módulo (batería):", v, "V")

def cmd_live(args):
    conn = connect(args.port, args.baud)
    fields = args.pids or ["rpm", "speed", "temp", "voltage"]
    t_end = time.time() + args.secs
    while time.time() < t_end:
        data = read_live(conn, fields)
        print(data)
        time.sleep(1)

def cmd_log(args):
    conn = connect(args.port, args.baud)
    os.makedirs(os.path.dirname(args.csv) or ".", exist_ok=True)
    print(f"Registrando {args.secs}s a {args.hz} Hz -> {args.csv}")
    log_csv(conn, args.csv, secs=args.secs, hz=args.hz)

def cmd_dashboard(args):
    conn = connect(args.port, args.baud)
    cmd = obd.commands.RPM
    times, rpms = [], []
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot(times, rpms)
    ax.set_xlabel("Tiempo (s)")
    ax.set_ylabel("RPM")
    t0 = time.time()
    try:
        while True:
            r = conn.query(cmd)
            if not r.is_null():
                elapsed = time.time() - t0
                val = getattr(r.value, "magnitude", r.value)
                times.append(elapsed)
                rpms.append(val)
                line.set_xdata(times)
                line.set_ydata(rpms)
                ax.relim()
                ax.autoscale_view()
                plt.pause(0.1)
    except KeyboardInterrupt:
        print("Dashboard detenido.")

def cmd_export_pdf(args):
    conn = connect(args.port, args.baud)
    data = snapshot(conn)
    out = args.out or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    export_pdf(data, out)
    print("PDF generado:", out)

def cmd_export_json(args):
    conn = connect(args.port, args.baud)
    data = snapshot(conn)
    out = args.out or f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    export_json(data, out)
    print("JSON generado:", out)

def build_parser():
    p = argparse.ArgumentParser(description="SmartOBD-PRO - Scanner OBD-II (ELM327)")
    p.add_argument("--port", help="Puerto serial (COMx o /dev/rfcomm0)", default=None)
    p.add_argument("--baud", help="Baudrate", type=int, default=9600)

    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("read-basic", help="Lectura básica (RPM/Velocidad/Temp)")
    s.set_defaults(func=cmd_read_basic)

    s = sub.add_parser("dtc", help="Leer códigos DTC")
    s.set_defaults(func=cmd_dtc)

    s = sub.add_parser("clear-dtc", help="Borrar DTCs")
    s.set_defaults(func=cmd_clear)

    s = sub.add_parser("vin", help="Leer VIN")
    s.set_defaults(func=cmd_vin)

    s = sub.add_parser("battery", help="Voltaje del módulo (batería)")
    s.set_defaults(func=cmd_battery)

    s = sub.add_parser("live", help="Live data en consola")
    s.add_argument("--pids", nargs="*", default=None, help="Lista de PIDs: rpm speed temp maf tps voltage ...")
    s.add_argument("--secs", type=int, default=15, help="Segundos a mostrar")
    s.set_defaults(func=cmd_live)

    s = sub.add_parser("log", help="Registro CSV de datos")
    s.add_argument("--csv", default="logs.csv", help="Ruta del CSV")
    s.add_argument("--secs", type=int, default=60, help="Segundos de captura")
    s.add_argument("--hz", type=int, default=5, help="Frecuencia de muestreo")
    s.set_defaults(func=cmd_log)

    s = sub.add_parser("dashboard", help="Gráfico en vivo de RPM")
    s.set_defaults(func=cmd_dashboard)

    s = sub.add_parser("export-pdf", help="Exportar snapshot a PDF")
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_export_pdf)

    s = sub.add_parser("export-json", help="Exportar snapshot a JSON")
    s.add_argument("--out", default=None)
    s.set_defaults(func=cmd_export_json)

    return p

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
