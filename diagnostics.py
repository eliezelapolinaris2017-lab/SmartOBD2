import time
import csv
import json
from datetime import datetime
import obd
from .obd_interface import read_vin, read_voltage, read_basic, read_live

def read_dtcs(connection: obd.OBD) -> list[tuple[str, str]]:
    resp = connection.query(obd.commands.GET_DTC)
    if resp.is_null():
        return []
    return list(resp.value)

def clear_dtcs(connection: obd.OBD) -> None:
    connection.query(obd.commands.CLEAR_DTC)

def log_csv(connection: obd.OBD, csv_path: str, secs: int = 60, hz: int = 5, fields: list[str] | None = None):
    interval = 1.0 / max(1, hz)
    start = time.time()
    fields = fields or ["rpm", "speed", "temp", "voltage"]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["t"] + fields)
        writer.writeheader()
        while time.time() - start < secs:
            row = {"t": round(time.time() - start, 3)}
            live = read_live(connection, fields)
            row.update(live)
            writer.writerow(row)
            time.sleep(interval)

def snapshot(connection: obd.OBD) -> dict:
    now = datetime.now().isoformat(timespec="seconds")
    vin = read_vin(connection)
    voltage = read_voltage(connection)
    basics = read_basic(connection)
    dtcs = read_dtcs(connection)
    return {
        "timestamp": now,
        "vin": vin,
        "voltage": voltage,
        "basic": basics,
        "dtcs": [{"code": c, "desc": d} for c, d in dtcs],
    }
