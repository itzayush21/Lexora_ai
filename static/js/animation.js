// === THREE.JS 3D BACKGROUND ===
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  75, window.innerWidth / window.innerHeight, 0.1, 1000
);

const renderer = new THREE.WebGLRenderer({
  canvas: document.getElementById('bg-canvas'),
  alpha: true, // transparent background
});
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.setPixelRatio(window.devicePixelRatio);

// 3D Object: Torus Knot
const geometry = new THREE.TorusKnotGeometry(10, 1.2, 100, 16);
const material = new THREE.MeshStandardMaterial({
  color: 0xcd853f,
  wireframe: true,
});
const torusKnot = new THREE.Mesh(geometry, material);
scene.add(torusKnot);

// Light
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);

camera.position.z = 40;

function animate() {
  requestAnimationFrame(animate);
  torusKnot.rotation.x += 0.004;
  torusKnot.rotation.y += 0.006;
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

// === ANIME.JS FADE-IN ANIMATION ===
anime({
  targets: '.hero-text h1, .hero-text p, .hero-list li, .btn-glow',
  opacity: [0, 1],
  translateY: [50, 0],
  delay: anime.stagger(200, { start: 500 }),
  duration: 1200,
  easing: 'easeOutExpo'
});
