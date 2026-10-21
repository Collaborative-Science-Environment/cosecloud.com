// Home-page hero: the SciSpinner Max as a live line drawing, frame and core turning on their real axes.
// The still drawing in the figure stays visible until the first 3D frame is ready, then cross-fades.
// Skipped (the still drawing simply stays) for reduced motion, data saver, narrow screens or no WebGL.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';

const fig = document.querySelector('[data-hero-3d]');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
// On previews (not cosecloud.com) a small line under the figure reports what the 3D hero is doing, to help diagnose a phone that stays on the still.
const status = msg => {
  console.info('[hero3d]', msg);
  if (location.hostname.endsWith('cosecloud.com') || !fig) return;
  let el = fig.querySelector('.hero-3d-status');
  if (!el) { el = document.createElement('p'); el.className = 'hero-3d-status'; el.style.cssText = 'position:absolute;left:0;top:100%;z-index:1;margin:.3rem 0 0;font:11px/1.4 var(--mono);color:var(--muted)'; fig.appendChild(el); }
  el.textContent = 'preview: 3D ' + msg + ' · ' + (navigator.userAgent.match(/iPhone|iPad|Android/) || ['desktop'])[0];
};
if (fig) { status('loading…'); const t0 = performance.now(); start().then(() => status('live after ' + ((performance.now() - t0) / 1000).toFixed(1) + ' s')).catch(e => status('failed: ' + (e && e.message || e))); }

async function start() {
  const stage = fig.querySelector('.hero-3d');
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2');
  if (!gl) { status('off (WebGL 2 not available)'); return; }
  const RPM_FRAME = 1.0, RPM_CORE = 1.4;           // within the instrument's 0.05–5 rpm range
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();

  const renderer = new THREE.WebGLRenderer({ canvas, context: gl, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(22, 1, 0.01, 20);

  const hullMat = new THREE.ShaderMaterial({
    side: THREE.BackSide,
    uniforms: { color: { value: new THREE.Color() }, px: { value: 1.2 }, res: { value: new THREE.Vector2(1, 1) } },
    vertexShader: `uniform float px; uniform vec2 res;
      void main(){ vec4 c = projectionMatrix * modelViewMatrix * vec4(position,1.0);
        vec3 n = normalize(normalMatrix * normal); vec2 d = normalize((projectionMatrix * vec4(n,0.0)).xy + 1e-6);
        c.xy += d * px * 2.0 / res * c.w; gl_Position = c; }`,
    fragmentShader: `uniform vec3 color; void main(){ gl_FragColor = vec4(color,1.0); }`
  });
  const lineMat = new LineMaterial({ linewidth: 1.0, worldUnits: false, polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -4 });
  const fill = { base: new THREE.MeshBasicMaterial(), frame: new THREE.MeshBasicMaterial(), chamber: new THREE.MeshBasicMaterial() };
  for (const m of Object.values(fill)) { m.polygonOffset = true; m.polygonOffsetFactor = 2; m.polygonOffsetUnits = 8; }   // fill sits behind the baked lines
  const applyTheme = () => {
    const ink = new THREE.Color(css('--draw-ink'));
    hullMat.uniforms.color.value.copy(ink); lineMat.color.copy(ink);
    fill.base.color.set(css('--bg')); fill.frame.color.set(css('--tint-frame')); fill.chamber.color.set(css('--tint-core'));
  };
  applyTheme();
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
  new MutationObserver(applyTheme).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  // Exterior-only model from the SolidWorks "Web" export: a decimated fill (47k triangles) plus the outline
  // edges taken from the full-resolution part, baked in as line segments; meshopt-compressed, about 0.27 MB.
  const gltf = await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).loadAsync('/assets/3d/scispinner-max.glb');
  const root = gltf.scene, groups = {};
  for (const name of ['base', 'frame', 'chamber']) { groups[name] = root.getObjectByName(name); groups[name].add(root.getObjectByName(name + '_lines')); }
  const pivotOuter = new THREE.Group(), pivotInner = new THREE.Group();
  scene.add(groups.base, pivotOuter); pivotOuter.add(groups.frame, pivotInner); pivotInner.add(groups.chamber);
  for (const name of ['base', 'frame', 'chamber']) {
    const meshes = [], lines = []; groups[name].traverse(o => { if (o.isMesh) meshes.push(o); else if (o.isLineSegments) lines.push(o); });
    for (const m of meshes) {
      m.material = fill[name];
      if (!m.geometry.attributes.normal) m.geometry.computeVertexNormals();   // indexed, shared vertices: smooth normals for the silhouette shell
      m.add(new THREE.Mesh(m.geometry, hullMat));
    }
    for (const l of lines) {                 // positions are quantized in the file: copy them out as plain floats for the fat-line geometry
      const pos = l.geometry.attributes.position, arr = new Float32Array(pos.count * 3);
      for (let i = 0; i < pos.count; i++) { arr[3 * i] = pos.getX(i); arr[3 * i + 1] = pos.getY(i); arr[3 * i + 2] = pos.getZ(i); }
      const fat = new LineSegments2(new LineSegmentsGeometry().setPositions(arr), lineMat);
      fat.position.copy(l.position); fat.quaternion.copy(l.quaternion); fat.scale.copy(l.scale);   // keep the node's dequantising transform
      l.parent.add(fat); l.removeFromParent();
    }
  }

  // Frame the instrument at the same three-quarter view as the drawings: fit the fixed base plus the
  // sphere the turning frame and core sweep through, as tightly as the canvas allows.
  const pts = [];
  const bb = new THREE.Box3().setFromObject(groups.base);
  for (const x of [bb.min.x, bb.max.x]) for (const y of [bb.min.y, bb.max.y]) for (const z of [bb.min.z, bb.max.z]) pts.push(new THREE.Vector3(x, y, z));
  let R = 0; for (const g of [groups.frame, groups.chamber]) {
    const b = new THREE.Box3().setFromObject(g);
    for (const x of [b.min.x, b.max.x]) for (const y of [b.min.y, b.max.y]) for (const z of [b.min.z, b.max.z]) R = Math.max(R, Math.hypot(x, y, z));
  }
  const fib = 64; for (let k = 0; k < fib; k++) {            // points spread over the swept sphere
    const y = 1 - 2 * (k + .5) / fib, rr = Math.sqrt(1 - y * y), t = k * 2.39996;
    pts.push(new THREE.Vector3(Math.cos(t) * rr * R, y * R, Math.sin(t) * rr * R));
  }
  const all = new THREE.Box3().setFromPoints(pts), c = all.getCenter(new THREE.Vector3());
  const r = all.getBoundingSphere(new THREE.Sphere()).radius;
  const az = THREE.MathUtils.degToRad(35), el = THREE.MathUtils.degToRad(20);
  const dir = new THREE.Vector3(Math.sin(az) * Math.cos(el), Math.sin(el), Math.cos(az) * Math.cos(el));
  const fit = aspect => {                                     // shortest distance at which every point is on screen
    camera.aspect = aspect; camera.updateProjectionMatrix();
    let lo = r * 0.5, hi = r * 8;
    for (let it = 0; it < 30; it++) {
      const d = (lo + hi) / 2; camera.position.copy(c).addScaledVector(dir, d); camera.lookAt(c); camera.updateMatrixWorld();
      const okAll = pts.every(p => { const q = p.clone().project(camera); return Math.abs(q.x) < 0.985 && Math.abs(q.y) < 0.985 && q.z < 1; });
      if (okAll) hi = d; else lo = d;
    }
    return hi;
  };
  const dist = fit(stage.clientWidth / stage.clientHeight || 4 / 3);
  camera.position.copy(c).addScaledVector(dir, dist);
  camera.near = Math.max(0.01, dist - r * 1.4); camera.far = dist + r * 1.4;
  const controls = new OrbitControls(camera, canvas);
  controls.target.copy(c); controls.enableZoom = false; controls.enablePan = false; controls.enableDamping = true;
  controls.minPolarAngle = 0.35; controls.maxPolarAngle = 1.75; controls.update();

  const resize = () => {
    const w = stage.clientWidth, h = stage.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
    const pr = renderer.getPixelRatio(); hullMat.uniforms.res.value.set(w * pr, h * pr); lineMat.resolution.set(w * pr, h * pr);
  };
  new ResizeObserver(resize).observe(stage); resize();

  stage.appendChild(canvas);
  let last = performance.now(), a1 = 0, a2 = 0, shown = false, visible = true;
  new IntersectionObserver(e => { visible = e[0].isIntersecting; }).observe(stage);
  renderer.setAnimationLoop(t => {
    const dt = Math.min((t - last) / 1000, 0.1); last = t;
    if (!visible || document.hidden) return;
    if (!reduceMotion) a1 += RPM_FRAME * Math.PI / 30 * dt; if (!reduceMotion) a2 += RPM_CORE * Math.PI / 30 * dt;
    pivotOuter.rotation.z = a1; pivotInner.rotation.x = a2;
    controls.update(); renderer.render(scene, camera);
    if (!shown) { shown = true; requestAnimationFrame(() => fig.classList.add('is-live'));
      if (reduceMotion) status('live, not turning (reduced motion is on in your system settings); drag to turn'); }
  });
}
