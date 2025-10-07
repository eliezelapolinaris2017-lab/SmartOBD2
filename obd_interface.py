import time
import obd

# Mapeo simple de PIDs por nombre a comandos python-OBD
PID_MAP = {
    "rpm": obd.commands.RPM,                   # 01 0C
    "speed": obd.commands.SPEED,               # 01 0D
    "temp": obd.commands.COOLANT_TEMP,         # 01 05
    "maf": obd.commands.MAF,                   # 01 10
    "tps": obd.commands.THROTTLE_POS,          # 01 11
    "intake_temp": obd.commands.INTAKE_TEMP,   # 01 0F
    "map": obd.commands.INTAKE_PRESSURE,       # 01 0B
    "fuel_level": obd.commands.FUEL_LEVEL,     # 01 2F
    "voltage": obd.commands.CONTROL_MODULE_VOLTAGE,  # 01 42
}

def connect(port: str | None = None, baud: int | None = None) -> obd.OBD:
    """Crea conexión OBD (auto o manual)."""
    if port:
        return obd.OBD(portstr=port, baudrate=baud)
    return obd.OBD()

def query(command):
    return command()

def read_vin(connection: obd.OBD) -> str | None:
    """Lee VIN (modo 09 PID 02)."""
    try:
        resp = connection.query(obd.commands.VIN)
        if resp.is_null():
            return None
        # python-OBD suele devolver el VIN como string en .value
        return str(resp.value)
    except Exception:
        return None

def read_voltage(connection: obd.OBD) -> float | None:
    resp = connection.query(PID_MAP["voltage"])
    if resp.is_null():
        return None
    val = resp.value
    try:
        return float(getattr(val, "magnitude", val))
    except Exception:
        return None

def read_basic(connection: obd.OBD) -> dict:
    data = {}
    for key in ["rpm", "speed", "temp"]:
        cmd = PID_MAP[key]
        r = connection.query(cmd)
        if r.is_null():
            data[key] = None
        else:
            v = r.value
            data[key] = getattr(v, "magnitude", v)
    return data

def read_live(connection: obd.OBD, names: list[str]) -> dict:
    data = {}
    for name in names:
        cmd = PID_MAP.get(name)
        if not cmd:
            data[name] = None
            continue
        r = connection.query(cmd)
        if r.is_null():
            data[name] = None
        else:
            v = r.value
            data[name] = getattr(v, "magnitude", v)
    return data
