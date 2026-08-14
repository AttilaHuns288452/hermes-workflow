---
name: capstone-project-evaluation
description: "Rank IoT capstone proposals by feasibility and defense."
version: 1.0.0
license: MIT
platforms: [windows, linux, macos]
metadata:
  hermes:
    tags: [capstone, iot, proposals, feasibility, philippines, education]
---

# Capstone / IoT Project Proposal Evaluation

Use when the user has a batch of student project proposals (downloaded docs, shared files) and wants to pick one — or rank them for teammates. Typical signal: "rank these", "top 3", "which should we pick", "say this to my teammates".

## Evaluation framework — score every proposal on 4 axes

1. **Value** — real problem, real users, impact the panel can grasp in one sentence.
2. **Ease / feasibility** — parts locally buyable, tutorials exist, team skill fit, build time fits the term. Reality-check the BOM, not just the pitch.
3. **Defense fidelity** — how convincingly the demo holds up LIVE in front of the panel. The demo IS the defense: can it fail visibly? Can the panel poke holes ("where's the real intersection?")?
4. **Practicality** — what actually changes in the real world after the demo; zero-cost hosting, reusable device, real dataset. User explicitly wants this axis named in write-ups.

Rank by value ÷ effort, then adjust for defense fidelity. Call out the "impressive but risky" picks explicitly (engineering traps that eat semesters).

## PH IoT feasibility quick facts (researched 2026-08)

- **2G/3G sunset**: NTC memorandum — Globe/Smart phase out 2G/3G by Dec 31 2026. Any proposal saying SIM800L/GSM is building on a dead network. Swap to **LTE Cat-1: A7670E** (~₱2,000 LilyGO board on Shopee/Lazada, ~₱900 used on ArduinoPH FB group). SIM800L also needs ≥470µF cap on supply or it resets on TX current spikes.
- **TEC1-12706 Peltier**: dies in seconds-minutes without a hot-side heatsink; ~10-15% Carnot efficiency; slow pull-down; condensation. Fix: buy a complete 12V thermoelectric cooler module, pre-soak compartment before drop-off, PID on DS18B20. "Hot AND cold in one small box" = the project graveyard.
- **PMS5003**: needs clean 5V ≥500mA; laser fan lives ~1-3.5 yrs; duty-cycle (1 min on / 5 min off) extends life but budget the 30s warm-up after wake.
- **YOLO on Raspberry Pi**: quantized YOLOv8n ≈ 5-7 FPS on Pi 4, YOLO11 8-25 FPS at low res — plenty for 10s-interval vehicle counting. Edge CV is NOT the blocker; real-world integration is.
- **PyMAF-X / PIXIE (SMPL-X)**: real, GitHub, single-image regression — but PyTorch + GPU (multi-GB VRAM), seconds-per-image on CPU. School machines can't run live. Fix: Colab free GPU as async job, or downgrade to MediaPipe BlazePose landmarks.
- **Solar math**: 20W panel ≈ 60-80Wh/day real. 12V 7Ah battery = 84Wh. Grow lights (24-36W) drain it in ~2-3h. Fix: solar for ESP32 + sensors + 5V pump only; lights on wall power (or 50-100W panel + LiFePO4).
- **Outdoor sensors**: use JSN-SR04T (waterproof ultrasonic) not HC-SR04; skip rain sensors (corrode); capacitive soil moisture (resistive corrodes in weeks).

Full detail + the 7-proposal case study: `references/iot-hardware-feasibility-ph.md`.

## Output format (user preference — IMPORTANT)

When the user says they'll share it with teammates ("send as text", "say to my teammates"): write a **copy-paste-ready group-chat message**, human tone, NOT a report:
- Conversational ("Guys, I looked into…", "My vote:", "Let's decide by Friday 🙏")
- Emoji per project, plain-text friendly (no markdown tables)
- Every pick states: what it is (1-2 lines) → why it wins → **practically** (parts cost, where to buy, what to fix upfront, what it's useful for after) → panel/defense angle
- End with a clear recommendation + why-not-the-others in 1 line each
- Name feasibility fixes explicitly ("we swap the 2G module for LTE because 2G is being shut down") — teammates need the fix, not just the verdict

## Reading proposal files

- `.docx` → read_file auto-extracts.
- Legacy `.doc` (OLE2) → read_file refuses; on Windows git-bash there's no `strings`. Extract with python: read bytes, `data.decode('utf-16-le', errors='ignore')`, regex `[\x20-\x7e]{4,}` for printable runs (UTF-16LE is the .doc codepage-1200 layout). Use the pip-enabled python at `C:\Users\YOUR_USERNAME\AppData\Local\Programs\Python\Python311\python.exe` if the terminal `python` is a venv without pip.
- Check for companion rubric files in the same download batch — grading criteria should break ties.
