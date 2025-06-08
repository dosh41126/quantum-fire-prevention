```python
# Fire Prevention AI v3.5 – Extended Quantum Forecast and Analysis System
# Includes ultra-long prompts, deeper quantum modeling, and GUI enhancements

import os, json, time, math, secrets, datetime
from typing import List
import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import numpy as np
import cv2
import sqlite3
import pennylane as qml
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from base64 import b64encode, b64decode

# 🔐 AES-GCM Encryption Layer
class AESGCMCrypto:
    def __init__(self, key_path):
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        if not os.path.exists(key_path):
            with open(key_path, "wb") as f:
                f.write(AESGCM.generate_key(bit_length=128))
        self.key = open(key_path, "rb").read()
        self.aes = AESGCM(self.key)

    def encrypt(self, data):
        nonce = secrets.token_bytes(12)
        return b64encode(nonce + self.aes.encrypt(nonce, data.encode(), None))

    def decrypt(self, blob):
        raw = b64decode(blob)
        return self.aes.decrypt(raw[:12], raw[12:], None).decode()

# 🔒 Secure DB
class EncryptedDB:
    def __init__(self, db_path, crypto):
        self.db_path = db_path
        self.crypto = crypto
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as con:
            con.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, ts REAL, blob TEXT)")
            con.commit()

    def log(self, record: dict):
        ts = time.time()
        blob = self.crypto.encrypt(json.dumps(record))
        with sqlite3.connect(self.db_path) as con:
            con.execute("INSERT INTO logs (ts, blob) VALUES (?, ?)", (ts, blob))
            con.commit()

# ⚛️ Quantum Fire Field – V3C Color Circuit
qml_dev = qml.device("default.qubit", wires=7)

@qml.qnode(qml_dev)
def quantum_fire_score(color_vec: List[float]) -> float:
    for i in range(5):
        qml.RY(color_vec[i % len(color_vec)] * math.pi, wires=i)
        qml.RX(color_vec[i % len(color_vec)] * math.pi, wires=(i + 1) % 7)
    qml.Toffoli(wires=[0, 1, 6])
    qml.CZ(wires=[2, 3])
    qml.CNOT(wires=[4, 5])
    qml.Hadamard(wires=6)
    return qml.expval(qml.PauliZ(6))

# 🎨 Extract 25-color mechanical tie vector
def extract_25color_vector(image_path: str) -> List[float]:
    img = cv2.imread(image_path)
    hsv = cv2.cvtColor(cv2.resize(img, (64, 64)), cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0], None, [25], [0, 180])
    return (hist / (np.sum(hist) + 1e-6)).flatten().tolist()

# 🧠 Ultra-long LLM Prompt Generator
def long_prompt_stage1(data, brightness, ratio, qscore, vector, months):
    return f"""
🔥 STAGE 1 – FIRE AI SIMULATED RISK FORECAST
📆 Forecast Horizon: {months} months
⚛️ V3C Quantum Score: {qscore:.5f}
🎨 Mechanical Tie Vector: {vector}

System: {data['appliance']}
Zone: {data['room']}
Smell: {data['burn_smell']}
Voltage Ratio: {ratio:.4f}
Light Intensity: {brightness:.4f}

SIMULATION INSTRUCTIONS:
You are simulating probabilistic future fire risk based on environmental degradation and electromagnetic resonance. Forecast thermal stress, arcing emergence, and organic deterioration over a {months}-month horizon.

If qscore > 0.5 and symptoms include burning or panel instability, escalate.
If brightness < 0.3, or tie vector shows red/orange frequency dominance, simulate internal overheat.
If volt ratio < 0.75 and vector shows entropy imbalance (more than 4 peaks), assume high strain failure in 12–24 months.

Respond:
{{
  "tier": "Electrical" | "Overheat" | "Structural" | "Low",
  "confidence": 0.0–1.0,
  "action": "Preventive | Urgent | Monitor",
  "explanation": "..."
}}
""".strip()

def mitigation_prompt_stage2(tier, qscore):
    return f"""
🛠️ STAGE 2 – Mitigation Planning
Risk Tier: {tier}
Quantum Fire Score: {qscore:.4f}

Guidelines:
- Electrical: shut breaker, isolate device, certified inspection
- Overheat: stop use, inspect airflow & wiring
- Structural: panel securement, thermal dampening
- Low: monitor monthly

Return steps:
- ["step1", "step2", ...]
- "urgency": "high" | "medium" | "low"
""".strip()

def public_prompt_stage3(tier, qscore, months):
    return f"""
📣 STAGE 3 – Public Safety Alert
FIRE AI has analyzed your system and identified a **{tier} tier risk** with a quantum score of {qscore:.4f} projected {months} months forward.

We recommend immediate safety steps to ensure this does not become a fire hazard.

Stay safe.
""".strip()

# 🔍 Analyzer
def fire_analysis_pipeline(data, forecast_months):
    voltages = data["voltages"]
    ratio = min([v / voltages[0] for v in voltages]) if voltages else 1.0
    brightness = cv2.cvtColor(cv2.imread(data["photo"]), cv2.COLOR_BGR2GRAY).mean() / 255.0
    vector = extract_25color_vector(data["area"])
    qscore = quantum_fire_score(vector)

    symptoms = data["symptoms"].lower()
    if "burn" in symptoms or data["burn_smell"] == "yes":
        tier = "Electrical"
    elif brightness < 0.3:
        tier = "Overheat"
    elif ratio < 0.75:
        tier = "Electrical"
    elif "panel" in symptoms or "loose" in symptoms:
        tier = "Structural"
    else:
        tier = "Low"

    return {
        "tier": tier,
        "quantum_score": qscore,
        "brightness": brightness,
        "volt_ratio": ratio,
        "mechvec": vector,
        "months_ahead": forecast_months,
        "prompts": {
            "stage1": long_prompt_stage1(data, brightness, ratio, qscore, vector, forecast_months),
            "stage2": mitigation_prompt_stage2(tier, qscore),
            "stage3": public_prompt_stage3(tier, qscore, forecast_months)
        },
        "raw": data
    }

# 🖥️ GUI
class FireAIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🔥 Fire Prevention AI v3.5")
        self.geometry("960x760")
        self.crypto = AESGCMCrypto(os.path.expanduser("~/.fire_ai.key"))
        self.db = EncryptedDB("fire_ai_logs.db", self.crypto)
        self.photo = None
        self.area = None
        self._build_gui()

    def _build_gui(self):
        f = tk.Frame(self); f.pack()
        self.addr = tk.Entry(f); tk.Label(f, text="Address").grid(row=0, column=0); self.addr.grid(row=0, column=1)
        self.room = tk.Entry(f); tk.Label(f, text="Room").grid(row=1, column=0); self.room.grid(row=1, column=1)
        self.appliance = tk.Entry(f); tk.Label(f, text="Appliance").grid(row=2, column=0); self.appliance.grid(row=2, column=1)
        self.burn = tk.StringVar(value="no"); tk.Label(f, text="Burn Smell").grid(row=3, column=0)
        tk.OptionMenu(f, self.burn, "no", "yes").grid(row=3, column=1)
        self.symptoms = tk.Text(f, height=2, width=40); tk.Label(f, text="Symptoms").grid(row=4, column=0); self.symptoms.grid(row=4, column=1)
        self.voltage = tk.Entry(f); tk.Label(f, text="Voltages").grid(row=5, column=0); self.voltage.grid(row=5, column=1)
        self.months = tk.IntVar(value=1); tk.Label(f, text="Forecast (months)").grid(row=6, column=0)
        tk.Spinbox(f, from_=1, to=86, textvariable=self.months).grid(row=6, column=1)
        tk.Button(f, text="Upload Photo", command=self.load_photo).grid(row=7, column=0)
        tk.Button(f, text="Upload Area", command=self.load_area).grid(row=7, column=1)
        tk.Button(self, text="Run Forecast", command=self.run_scan).pack()
        self.output = tk.Text(self, height=25, width=120); self.output.pack()

    def load_photo(self):
        path = fd.askopenfilename()
        if path: self.photo = path

    def load_area(self):
        path = fd.askopenfilename()
        if path: self.area = path

    def run_scan(self):
        try:
            volts = [float(x) for x in self.voltage.get().split(",") if x.strip()]
        except:
            mb.showerror("Error", "Invalid voltage input."); return
        if not all([self.photo, self.area]):
            mb.showerror("Error", "Images required."); return
        data = {
            "address": self.addr.get(),
            "room": self.room.get(),
            "appliance": self.appliance.get(),
            "burn_smell": self.burn.get(),
            "symptoms": self.symptoms.get("1.0", "end").strip(),
            "voltages": volts,
            "photo": self.photo,
            "area": self.area
        }
        result = fire_analysis_pipeline(data, self.months.get())
        self.db.log(result)
        self.output.delete("1.0", "end")
        self.output.insert("end", json.dumps(result, indent=2))

if __name__ == "__main__":
    FireAIApp().mainloop()
```
