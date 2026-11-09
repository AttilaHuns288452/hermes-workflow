# Planetary globes (Earth-style day/night spheres)

One-file Three.js globe: a single sphere with a day/night shader, an atmosphere rim, a drifting cloud shell, and a starfield. Verified headless in Chromium at 1440x900 and 390x844.

## Textures

`three`'s npm package does not ship `examples/textures`. Pull them from the upstream repo at a tag:

```
https://raw.githubusercontent.com/mrdoob/three.js/r160/examples/textures/planets/
  earth_atmos_2048.jpg     day map, clouds baked in (mean ~ (87,94,107) - genuinely dark; light for it)
  earth_lights_2048.png    city lights on black - ideal as the night term
  earth_clouds_1024.png    separate cloud shell
  earth_specular_2048.jpg  ocean gloss for a Phong/Standard material
  earth_normal_2048.jpg    relief
```

curl every URL for 200 before wiring them in: one 404 inside a `Promise.all` rejects the whole load and the page renders nothing.

## Day/night in one material

Two stacked spheres (Phong day + additive lights) cannot work: additive ignores the sun, so city lights glow over the lit hemisphere and a mid-dark earth texture loses to them. The render reads as permanent night with glitter no matter how bright the directional light is. Mix both maps by sun angle instead.

```js
const SUN = new THREE.Vector3(0.92, 0.18, 0.44).normalize();   // direction TO the sun, world space

const earth = new THREE.Mesh(
  new THREE.SphereGeometry(1, 128, 128),
  new THREE.ShaderMaterial({
    uniforms: { uDay: { value: dayTex }, uNight: { value: lightsTex },
                uSun: { value: SUN }, uNightGain: { value: 1.7 } },
    vertexShader: `varying vec2 vUv; varying vec3 vN;
      void main(){ vUv = uv; vN = normalize(mat3(modelMatrix) * normal);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform sampler2D uDay, uNight; uniform vec3 uSun; uniform float uNightGain;
      varying vec2 vUv; varying vec3 vN;
      void main(){
        vec3 n = normalize(vN);
        float d = dot(n, uSun);
        float lit = smoothstep(-0.16, 0.26, d);                 // soft terminator
        vec3 dayC = texture2D(uDay, vUv).rgb * (0.30 + 0.76 * clamp(d, 0.0, 1.0));
        vec3 nightC = texture2D(uNight, vUv).rgb * uNightGain;
        gl_FragColor = vec4(mix(nightC, dayC, lit), 1.0);
        #include <colorspace_fragment>
      }`
  })
);
```

Rules that matter:

- World normal from `mat3(modelMatrix) * normal` so the mesh can spin under a fixed sun; normalize again in the fragment shader for a smooth terminator.
- `#include <colorspace_fragment>` is required (r160-era name). Three does not append the output sRGB conversion for a custom ShaderMaterial, while `SRGBColorSpace` textures are GPU-decoded on sample - omitting it double-encodes: land goes pale/pink, oceans wash out. The symptom of a renamed chunk in a future three is the same wash-out.
- `uNightGain` ~1.5-2.0 reads right; higher turns city lights into glitter.
- Wider `smoothstep` edges (-0.3 to 0.4) give a big twilight band; tighter (-0.05 to 0.1) gives a hard line.
- Tune the initial spin so a big landmass faces the camera. A hemisphere of open ocean at t=0 looks like an unlit ball however correct the shader is - sweep rotations and pick by bright-pixel percentage.

## Atmosphere rim

Backside sphere, additive, fresnel falloff. Keep the exponent high and the radius modest or it reads as neon:

```js
const atmo = new THREE.Mesh(new THREE.SphereGeometry(1.15, 64, 64), new THREE.ShaderMaterial({
  uniforms: { uColor: { value: new THREE.Color(0x3d7ae8) } },
  vertexShader: `varying vec3 vN; void main(){ vN = normalize(normalMatrix * normal);
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: `uniform vec3 uColor; varying vec3 vN;
    void main(){ float i = pow(max(0.60 - dot(vN, vec3(0.0,0.0,1.0)), 0.0), 3.6);
      gl_FragColor = vec4(uColor, 1.0) * clamp(i, 0.0, 1.0); }`,
  side: THREE.BackSide, blending: THREE.AdditiveBlending, transparent: true, depthWrite: false
}));
```

## Cloud shell

`MeshPhongMaterial` with the cloud map at `R * 1.008`, `transparent`, `opacity 0.8`, `depthWrite: false`, spinning slightly faster than the surface. The directional light darkens it on the night side for free.

## Framing

Fit by the limiting fov, include the glow shell radius (~1.18 R), and raise `controls.maxDistance` past the portrait distance - see "Framing a single centered subject" in SKILL.md.

## Verification probe (headless)

```js
// node probe.cjs - needs playwright + pngjs from the agent's node_modules
const { chromium } = require('<hermes>/node_modules/playwright');
const { PNG } = require('<hermes>/node_modules/pngjs');
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const p = await b.newPage({ viewport: { width: 900, height: 900 } });
await p.goto('http://127.0.0.1:8791/', { waitUntil: 'networkidle' });
await p.waitForTimeout(2500);
const stats = async (label) => {                       // mean luminance + bright% over a centre box
  const img = PNG.sync.read(await p.screenshot());
  let sum = 0, bright = 0, n = 0;
  const cx = img.width >> 1, cy = img.height >> 1;
  for (let y = cy - 200; y < cy + 200; y++) for (let x = cx - 200; x < cx + 200; x++) {
    const i = (y * img.width + x) << 2;
    const l = (img.data[i] + img.data[i + 1] + img.data[i + 2]) / 3;
    sum += l; if (l > 110) bright++; n++;
  }
  console.log(label, (sum / n).toFixed(1), (100 * bright / n).toFixed(1) + '%');
};
await stats('base');
await p.evaluate(() => { window.EARTH.sunLight.intensity = 0; });   // A/B one term
await stats('sun 0');
```

Calibration from a working render:

- sun-lit land hemisphere: mean ~100-110, ~38% of pixels above 110
- night side / additive layer dominating: mean ~60-70, 8-12% bright
- sun intensity forced to 0: mean ~16 - proves which light is actually doing the work

Expose the scene for these probes (`window.EARTH = { scene, camera, renderer, sunLight, earth, clouds, atmo }`): one line, and every later tuning pass becomes scriptable instead of a re-render-and-look loop.
