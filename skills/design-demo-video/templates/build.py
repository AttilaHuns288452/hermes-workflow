#!/usr/bin/env python3
"""Design-screens -> narrated demo video (HyperFrames).
Copy into the project dir alongside assets/, edit the SCENES table, run.
Expects: assets/screens/<page>.png (cropped screen renders), writes assets/vo/*.mp3 + index.html.
"""
import os, subprocess, json

D = os.path.dirname(os.path.abspath(__file__))
VO_DIR = os.path.join(D, 'assets', 'vo')
SCR_DIR = os.path.join(D, 'assets', 'screens')
os.makedirs(VO_DIR, exist_ok=True)
os.makedirs(SCR_DIR, exist_ok=True)

VOICE = os.environ.get('VO_VOICE', 'en-PH-RosaNeural')  # test the voice ID with a short line first

# (screen png or None for title card, label, kicker, vo line)
SCENES = [
    (None,  'D.A.R. Dental Clinic', 'Appointment & Record System',
     'Meet D.A.R. Dental Clinic — a complete appointment and record system for modern dental practices.'),
    ('p031','Sign In', 'Secure access',
     'Patients and staff sign in through one secure portal.'),
    ('p034','Patient Portal · Home', 'Patient experience',
     'Patient home shows confirmed visits, quick actions, and recent activity at a glance.'),
    ('p035','My Appointments', 'Patient experience',
     'My Appointments tracks every visit — upcoming, pending, completed, or cancelled.'),
    ('p036','Book Appointment', 'Patient experience',
     'Booking takes under a minute: pick a service, choose a date and time, add a note.'),
    ('p128','Request Submitted', 'Patient experience',
     'Each request goes straight to the clinic for approval.'),
    ('p037','Messages', 'Patient experience',
     'Built-in messaging keeps patient and dentist in sync before every visit.'),
    ('p039','Dentist Portal', 'Clinic management',
     'On the clinic side, dentists get their own management portal.'),
    ('p040','Clinic Dashboard', 'Clinic management',
     "The dashboard opens on today's schedule, new requests, and pending registrations."),
    ('p067','Booking Review', 'Clinic management',
     'Booking requests open in one click — review, approve, or decline.'),
    ('p042','Calendar', 'Clinic management',
     'Approved visits land on a color-coded calendar, by day, week, or month.'),
    ('p068','Patient Record · EHR', 'Clinic management',
     'Every patient has a full electronic health record with attachments and history.'),
    ('p045','Income Analytics', 'Operations',
     'Income analytics show revenue, transactions, and reports in real time.'),
    ('p046','Staff Management', 'Operations',
     'And staff accounts keep the whole team in sync.'),
    (None,  'One System', 'Appointments · Records · Income',
     'D.A.R. Dental Clinic — appointments, records, and income. One system.'),
]

PAD_IN, PAD_OUT = 0.55, 0.75   # silence around each VO inside its scene
LEAD = 0.35                    # VO starts this far into its scene

def dur(path):
    out = subprocess.run(['ffprobe','-v','error','-show_entries','format=duration',
                          '-of','csv=p=0', path], capture_output=True, text=True)
    return float(out.stdout.strip())

vos = []
for i, (_, _, _, line) in enumerate(SCENES, 1):
    mp3 = os.path.join(VO_DIR, f'vo{i:02d}.mp3')
    if not os.path.exists(mp3):
        subprocess.run(['edge-tts','--voice',VOICE,'--rate=-4%',
                        '--text',line,'--write-media',mp3], check=True,
                       capture_output=True)
    vos.append(dur(mp3))
print('VO durations:', [round(v,2) for v in vos])

# scene layout: length derives from measured VO, never hand-timed
t = 0.0
layout = []
for i, ((scr, label, kicker, _), vd) in enumerate(zip(SCENES, vos), 1):
    scene_len = LEAD + vd + PAD_OUT
    layout.append({'i': i, 'screen': scr, 'label': label, 'kicker': kicker,
                   'start': round(t, 3), 'dur': round(scene_len, 3),
                   'vo_start': round(t + LEAD, 3), 'vo_dur': round(vd, 3)})
    t += scene_len
TOTAL = round(t + 0.4, 3)
print('total:', TOTAL)

def scene_html(s):
    if s['screen'] is None:
        body = f'''
        <div class="hero" id="hero{s['i']}">
          <div class="logo"><span>&#129463;</span></div>
          <h1>{s['label']}</h1>
          <p>{s['kicker']}</p>
        </div>'''
    else:
        body = f'''
    <div class="phone" id="phone{s['i']}"><div class="screen"><img id="img{s['i']}" src="assets/screens/{s['screen']}.png" alt=""></div></div>
    <div class="cap" id="cap{s['i']}"><span class="kick">{s['kicker']}</span><h2>{s['label']}</h2></div>'''
    return f'''
    <div class="clip scene" id="scene{s['i']}" data-start="{s['start']}" data-duration="{s['dur']}" data-track-index="0">{body}</div>
    <audio id="vo{s['i']:02d}" class="clip" data-start="{s['vo_start']}" data-duration="{round(s['vo_dur']+0.1,3)}" data-track-index="1" src="assets/vo/vo{s['i']:02d}.mp3"></audio>'''

tl_lines = '\n'.join(
    (f"      tl.fromTo('#hero{s['i']}', {{autoAlpha:0, y:50}}, {{autoAlpha:1, y:0, duration:0.7, ease:'power2.out'}}, {s['start']});"
     if s['screen'] is None else
     f"      tl.fromTo('#phone{s['i']}', {{autoAlpha:0, y:70, scale:0.97}}, {{autoAlpha:1, y:0, scale:1, duration:0.6, ease:'power2.out'}}, {s['start']});\n"
     f"      tl.fromTo('#cap{s['i']}', {{autoAlpha:0, y:24}}, {{autoAlpha:1, y:0, duration:0.5, ease:'power2.out'}}, {s['start']+0.25});\n"
     f"      tl.fromTo('#img{s['i']}', {{y:0}}, {{y:-44, duration:{s['dur']}, ease:'none'}}, {s['start']});")
    for s in layout)

scenes_html = '\n'.join(scene_html(s) for s in layout)

html = f'''<!doctype html>
<html lang="en" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ width:1080px; height:1920px; overflow:hidden; background:#0b2b2a; }}
      #root {{ width:1080px; height:1920px; position:relative; font-family:'Inter',ui-sans-serif,system-ui,sans-serif; }}
      .scene {{ position:absolute; inset:0; overflow:hidden;
        background:linear-gradient(160deg,#0f766e 0%,#0d9488 38%,#134e4a 100%); }}
      .scene::after {{ content:''; position:absolute; inset:0;
        background:radial-gradient(900px 600px at 20% 8%, rgba(255,255,255,.10), transparent 60%); pointer-events:none; }}
      .phone {{ position:absolute; left:50%; top:118px; transform:translateX(-50%);
        width:790px; height:1530px; border-radius:52px; background:#0b1220;
        padding:14px; box-shadow:0 40px 90px rgba(0,0,0,.45), 0 0 0 2px rgba(255,255,255,.08); }}
      .screen {{ width:100%; height:100%; border-radius:40px; overflow:hidden; background:#fff; }}
      .screen img {{ width:100%; height:100%; object-fit:cover; object-position:top center; display:block; }}
      .cap {{ position:absolute; left:0; right:0; bottom:78px; text-align:center; color:#fff; }}
      .cap .kick {{ display:inline-block; font-size:26px; letter-spacing:.22em; text-transform:uppercase;
        color:#99f6e4; font-weight:600; margin-bottom:14px; }}
      .cap h2 {{ font-size:58px; font-weight:700; letter-spacing:-0.02em; text-shadow:0 2px 18px rgba(0,0,0,.35); }}
      .hero {{ position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; color:#fff; padding:0 90px; }}
      .hero .logo {{ width:190px; height:190px; border-radius:48px; background:rgba(255,255,255,.14);
        border:2px solid rgba(255,255,255,.35); display:flex; align-items:center; justify-content:center;
        font-size:104px; margin-bottom:54px; backdrop-filter:blur(4px); }}
      .hero h1 {{ font-size:96px; font-weight:800; letter-spacing:-0.03em; line-height:1.08; }}
      .hero p {{ margin-top:30px; font-size:38px; color:#99f6e4; letter-spacing:.14em; text-transform:uppercase; font-weight:600; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">{scenes_html}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
{tl_lines}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>'''

open(os.path.join(D, 'index.html'), 'w').write(html)
json.dump({'total': TOTAL, 'scenes': layout}, open(os.path.join(D, 'timeline.json'), 'w'), indent=1)
print('index.html written')
