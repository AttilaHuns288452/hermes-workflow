# PH IoT Hardware Feasibility — Research Notes (verified 2026-08-05)

Durable facts for feasibility-checking student IoT proposals in the Philippines. Verify prices/sunset dates again if >6 months old.

## Cellular / connectivity
- **PH 2G/3G sunset**: NTC memorandum circular — Globe and Smart required to phase out 2G and 3G area-by-area, completed by **Dec 31, 2026**. 2G shutdown already ongoing (DICT: final phaseout target Sep 30, 2025 for 2G trackers; Globe 2G started 2019). → Any SIM800L/2G-GSM design is non-viable for a project that must demo after 2026.
- **Replacement: LTE Cat-1 A7670E/A7672E** — the de-facto SIM800L successor in PH maker community. Availability: LilyGO T-Call A7670E board ~₱2,034 (Shopee) / ₱2,731 (Lazada); used modules ~₱900 (ArduinoPH FB group). Arduino/ESP32 libraries exist.
- **SIM800L known failure mode** (even where 2G works): 2A current spikes on GSM TX → brownouts/resets unless supply has ≥470µF bulk cap (ideally on 5V rail); LDO drops sag badly; don't power from an 18650 directly.

## Sensors — lifetime and gotchas
- **PMS5003 (PM2.5)**: needs clean 5V ≥500mA (USB sag causes erratic readings); laser + fan lifetime ~1-3.5 yrs continuous; sleep-cycling extends life but requires 30s warm-up after wake → duty-cycle 1 min on / 5 min off and budget warm-up in sampling cadence.
- **JSN-SR04T** (waterproof ultrasonic) correct for outdoor level sensing; plain HC-SR04 dies outdoors. Rain sensors corrode in weeks — skip or treat as disposable.
- **Soil moisture**: capacitive type only; resistive probes corrode in weeks.

## Thermal (Peltier)
- **TEC1-12706**: 60W-class heat pump, ~10-15% of Carnot efficiency. Without a proper hot-side heatsink + fan it self-destructs in seconds-to-minutes. Slow pull-down, condensation risk. → For a demo box: buy a complete 12V thermoelectric cooler module; pre-soak compartment in selected mode BEFORE the demo window; PID on DS18B20. Dual hot+cold in one small compartment is the hardest single subsystem in typical capstone stacks.

## Edge CV
- **YOLO on Raspberry Pi 4**: quantized YOLOv8n @416px ≈ 5-7 FPS; YOLOv5 ~15 FPS (tutorials); YOLO11 8-25 FPS at lower res. Sufficient for vehicle counting at 10s batch intervals → edge detection is NOT the blocker; the blocker is real-world integration (traffic signals, intersections) which capstones cannot access → mock intersection with LEDs driven by backend, validated on recorded footage.

## 3D body reconstruction
- **PyMAF-X / PIXIE** (SMPL-X mesh from monocular images): real and open-source (PyMAF-X GitHub, TPAMI 2023), regression-based, single image → mesh. But PyTorch with multi-GB VRAM; CPU inference = seconds per image. → Run as async job on Colab free GPU, or downgrade to MediaPipe BlazePose landmarks (CPU-friendly, still yields symmetry/proportion data).

## Solar sizing math
- Rule of thumb: 20W panel ≈ 60-80Wh/day real-world (PH ~4-5 peak sun hours × derating).
- 12V 7Ah SLA = 84Wh usable (less with depth-of-discharge limits).
- LED grow strips (2× 1m, 12V) ≈ 24-36W → would drain the battery in ~2-3h. → Solar for ESP32 + sensors + 5V pump only; high-draw loads on wall power, or 50-100W panel + LiFePO4.

## Case study (2026-08): 7 downloaded proposals, ranked verdicts
Batch: Guardian Alert (wearable SOS button), VisionTraffic (adaptive signals), FitInsight AI (3D body kiosk), AirWatch IoT (air/noise monitoring), Smart Greenhouse, Smart Drainage, FreshVault (food locker).

Post-fix ranking (feasibility after the fixes below):
1. **Guardian Alert** — HIGH after ONE part swap: SIM800L→A7670E LTE. Simplest hardware (button+GPS+cellular), demo = product (press → map pin). Add: 3s-hold cancel, deep sleep, active GPS antenna for indoor.
2. **Smart Greenhouse** — HIGH after power re-scope: solar only for ESP32+sensors+5V pump; grow lights on wall power (or bigger panel). ₱8.3-9k total, 7-week timeline, best visible demo (pump waters a real plant).
3. **AirWatch IoT** — HIGH as written, duty-cycle PMS5003. Monitor-only, no actuators, real dataset + 48h side-by-side calibration = strong defense; calibrate sound sensor against free phone dB-meter app.
4. **Smart Drainage** — HIGH after LTE + solar/deep-sleep, but weak classroom demo ("box in a canal"); proposal doc was a 39-line outline needing a full rewrite.
5. **FitInsight AI** — MEDIUM (Colab GPU) / HIGH (MediaPipe fallback). Novelty high; BIA scale procurement + booth logistics.
6. **VisionTraffic** — MEDIUM: real YOLO counting + LED mock intersection; 4-tier surface (edge+backend+web+RN) is the cost.
7. **FreshVault** — LOW-MEDIUM: thermal subsystem is the graveyard; buy complete TEC cooler module, pre-soak, buy a capacitive touchscreen keypad instead of copper-pads-through-glass (drifts with humidity); OTP/QR part is proven and easy.

General lessons:
- Proposals that "integrate with real-world infrastructure" (police dispatch, traffic signals, delivery platforms) are always simulation-bound → scope the simulation explicitly and honestly.
- 8-member teams map 2-per-track (IoT/backend/DB/frontend); look for proposals whose WBS does this.
- Companion rubric file in the same download batch decides tie-breaks — read it before final ranking.
