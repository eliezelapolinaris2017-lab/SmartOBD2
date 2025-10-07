# SmartOBD-PRO 🚗🔧

Scanner OBD-II **PRO** en **Python** compatible con adaptadores **ELM327** (Bluetooth/USB).
Incluye:
- Lectura de **DTCs** y **borrado**.
- Lectura de **VIN** (modo 09 PID 02).
- **Voltaje** del módulo de control (batería) (PID 01 42).
- **Datos en vivo**: RPM, velocidad, temperatura, MAF, TPS, etc.
- **Dashboard** con gráfico de RPM en tiempo real.
- **Exportación** de diagnósticos a **CSV** y **PDF** (con fecha/hora).

> **Nota**: Funciona con PIDs OBD-II genéricos (motor). No realiza codificación/programación ECU ni pruebas bidireccionales OEM.

---

## 🚀 Requisitos
- Python 3.9+
- Adaptador ELM327 (Bluetooth/USB). Recomendado: OBDLink LX/MX+, Veepeak BLE+.
- Instalar dependencias:
```bash
pip install -r requirements.txt
```

## 🔌 Conexión
- **Windows**: empareja el ELM327 → revisa el puerto `COMx` en Administrador de dispositivos.
- **Linux/macOS**: `/dev/rfcomm0`, `/dev/ttyUSB0`, etc.

## 🧭 Uso rápido (CLI)
```bash
python src/main.py read-basic                 # RPM/Velocidad/Temperatura
python src/main.py dtc                        # Leer DTCs
python src/main.py clear-dtc                  # Borrar DTCs
python src/main.py vin                        # Leer VIN
python src/main.py battery                    # Voltaje módulo (batería)
python src/main.py live --pids rpm speed temp maf tps --secs 15
python src/main.py log --csv logs.csv --secs 60 --hz 5
python src/main.py dashboard                  # Gráfico de RPM en vivo
python src/main.py export-pdf --out report.pdf
```

Especificar puerto (opcional):
```bash
python src/main.py read-basic --port COM6
# Linux:
python src/main.py read-basic --port /dev/rfcomm0
```

## 📁 Estructura
```
SmartOBD-PRO/
├─ src/
│  ├─ main.py
│  ├─ obd_interface.py
│  ├─ diagnostics.py
│  └─ export.py
├─ requirements.txt
├─ README.md
├─ LICENSE
└─ .gitignore
```

## 🛡️ Seguridad
- Ejecuta las pruebas con el vehículo **estacionado**.
- Borrar DTCs no repara fallas físicas.
- Algunas PIDs pueden no estar soportadas por ciertos ECUs.

## 🧑‍💻 Licencia
MIT.
