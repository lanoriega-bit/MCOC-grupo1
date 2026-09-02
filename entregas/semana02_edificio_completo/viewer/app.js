import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const MODEL_URL = "../unity_export/model_viewer.json";
const CATEGORY_LABELS = {
  axis: "Ejes CAD",
  beam: "Vigas",
  column_plan: "Pilares/columnas",
  diaphragm: "Diafragmas",
  slab_edge: "Borde losa",
  support: "Apoyos/fundaciones",
  wall: "Muros",
};

const viewport = document.querySelector("#viewport");
const statusEl = document.querySelector("#status");
const floorControlsEl = document.querySelector("#floor-controls");
const categoryControlsEl = document.querySelector("#category-controls");
const selectionDetailsEl = document.querySelector("#selection-details");
const tagSearchEl = document.querySelector("#tag-search");
const toggleLabelsButton = document.querySelector("#toggle-labels");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x07111f);
scene.fog = new THREE.Fog(0x07111f, 70, 150);

const camera = new THREE.PerspectiveCamera(55, 1, 0.05, 500);
camera.position.set(42, -44, 35);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
viewport.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.screenSpacePanning = true;
controls.maxDistance = 180;
controls.minDistance = 2;
controls.target.set(24, 8, 10);

const raycaster = new THREE.Raycaster();
raycaster.params.Line.threshold = 0.35;
const pointer = new THREE.Vector2();
const selectable = [];
const objectsByFloor = new Map();
const objectsByCategory = new Map();
const segmentByTag = new Map();
const labels = [];
const labelLayer = document.createElement("div");
let labelsVisible = false;
let selected = null;
let selectedLine = null;
let localAxesGroup = null;
let modelBounds = null;

labelLayer.className = "label-layer";
viewport.appendChild(labelLayer);

function addLights() {
  const ambient = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambient);
  const sun = new THREE.DirectionalLight(0xffffff, 1.1);
  sun.position.set(35, -40, 55);
  scene.add(sun);
}

function categoryColor(model, category) {
  return model.colors?.[category] ?? "#ffffff";
}

function rememberObject(object, floor, category) {
  if (!objectsByFloor.has(floor)) objectsByFloor.set(floor, []);
  if (!objectsByCategory.has(category)) objectsByCategory.set(category, []);
  objectsByFloor.get(floor).push(object);
  objectsByCategory.get(category).push(object);
}

function makeLine(segment, color) {
  const points = segment.points.map((point) => new THREE.Vector3(point[0], point[1], point[2]));
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({ color, transparent: true, opacity: opacityFor(segment.category) });
  const line = new THREE.Line(geometry, material);
  line.userData.segment = segment;
  line.userData.floor = segment.floor;
  line.userData.category = segment.category;
  return line;
}

function opacityFor(category) {
  if (category === "axis") return 0.22;
  if (category === "slab_edge") return 0.35;
  if (category === "diaphragm") return 0.55;
  return 0.95;
}

function makeDiaphragm(diaphragm, color) {
  const points = diaphragm.points.map((point) => new THREE.Vector3(point[0], point[1], point[2]));
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineDashedMaterial({ color, dashSize: 0.9, gapSize: 0.45, transparent: true, opacity: 0.65 });
  const line = new THREE.Line(geometry, material);
  line.computeLineDistances();
  line.userData.segment = {
    elementTag: `DIA_${diaphragm.floor}`,
    floor: diaphragm.floor,
    floor_label: `Diafragma ${diaphragm.floor}`,
    category: "diaphragm",
    source_layer: "generated",
    source_dxf: "generated",
    length_m: 0,
    confidence: "qa",
    points: diaphragm.points,
  };
  line.userData.floor = diaphragm.floor;
  line.userData.category = "diaphragm";
  return line;
}

function addModel(model) {
  const root = new THREE.Group();
  root.name = "CAD building model";

  for (const segment of model.segments) {
    const line = makeLine(segment, categoryColor(model, segment.category));
    root.add(line);
    rememberObject(line, segment.floor, segment.category);
    segmentByTag.set(segment.elementTag.toLowerCase(), line);
    if (!["axis", "slab_label"].includes(segment.category)) selectable.push(line);
  }

  for (const diaphragm of model.diaphragms ?? []) {
    const line = makeDiaphragm(diaphragm, categoryColor(model, "diaphragm"));
    root.add(line);
    rememberObject(line, diaphragm.floor, "diaphragm");
    segmentByTag.set(line.userData.segment.elementTag.toLowerCase(), line);
    selectable.push(line);
  }

  scene.add(root);
  modelBounds = new THREE.Box3().setFromObject(root);
  buildControls(model);
  buildIdLabels(model);
  fitView();
  statusEl.textContent = `${model.segments.length} segmentos CAD, ${model.labels?.length ?? 0} etiquetas, ${model.diaphragms?.length ?? 0} diafragmas.`;
}

function buildControls(model) {
  const floors = [...new Set(model.segments.map((segment) => segment.floor))];
  floors.sort((a, b) => floorOrder(a) - floorOrder(b));
  floorControlsEl.replaceChildren(...floors.map(makeFloorToggle));

  const categories = [...new Set([...model.segments.map((segment) => segment.category), "diaphragm"])]
    .filter((category) => CATEGORY_LABELS[category])
    .sort();
  categoryControlsEl.replaceChildren(...categories.map((category) => makeCategoryToggle(category, categoryColor(model, category))));
}

function floorOrder(floor) {
  const order = { base: 0, "1S": 1, "1": 2, "2": 3, "3": 4, "4": 5 };
  return order[floor] ?? 99;
}

function makeFloorToggle(floor) {
  const row = document.createElement("label");
  row.className = "toggle-row";

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = true;
  checkbox.addEventListener("change", () => setFloorVisible(floor, checkbox.checked));

  const label = document.createElement("span");
  label.textContent = `Piso ${floor}`;

  const solo = document.createElement("button");
  solo.type = "button";
  solo.className = "small-button";
  solo.textContent = "solo";
  solo.addEventListener("click", (event) => {
    event.preventDefault();
    isolateFloor(floor);
  });

  row.append(checkbox, label, solo);
  return row;
}

function makeCategoryToggle(category, color) {
  const row = document.createElement("label");
  row.className = "toggle-row";

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = true;
  checkbox.addEventListener("change", () => setCategoryVisible(category, checkbox.checked));

  const label = document.createElement("span");
  label.textContent = CATEGORY_LABELS[category] ?? category;

  const swatch = document.createElement("span");
  swatch.className = "swatch";
  swatch.style.background = color;

  row.append(checkbox, label, swatch);
  return row;
}

function setFloorVisible(floor, visible) {
  for (const object of objectsByFloor.get(floor) ?? []) object.visible = visible;
  updateLabels();
}

function setCategoryVisible(category, visible) {
  for (const object of objectsByCategory.get(category) ?? []) object.visible = visible;
  updateLabels();
}

function isolateFloor(floor) {
  for (const [currentFloor, objects] of objectsByFloor.entries()) {
    const visible = currentFloor === floor;
    for (const object of objects) object.visible = visible;
  }
  for (const input of floorControlsEl.querySelectorAll("input")) {
    const label = input.parentElement?.querySelector("span")?.textContent ?? "";
    input.checked = label === `Piso ${floor}`;
  }
  updateLabels();
}

function buildIdLabels(model) {
  const candidates = model.segments.filter((segment) => {
    if (["axis", "slab_label", "slab_edge"].includes(segment.category)) return false;
    return segment.length_m >= 1.2;
  });

  for (const segment of candidates) {
    const midpoint = new THREE.Vector3(
      (segment.points[0][0] + segment.points[1][0]) / 2,
      (segment.points[0][1] + segment.points[1][1]) / 2,
      (segment.points[0][2] + segment.points[1][2]) / 2,
    );
    const div = document.createElement("div");
    div.className = "viewer-label";
    div.textContent = shortTag(segment.elementTag);
    div.style.display = "none";
    labelLayer.appendChild(div);
    labels.push({ div, point: midpoint, segment });
  }
}

function shortTag(tag) {
  return tag.replace("CAD_", "");
}

function updateLabels() {
  if (!labelsVisible) {
    for (const label of labels) label.div.style.display = "none";
    return;
  }

  const width = viewport.clientWidth;
  const height = viewport.clientHeight;
  for (const label of labels) {
    const object = segmentByTag.get(label.segment.elementTag.toLowerCase());
    if (!object?.visible) {
      label.div.style.display = "none";
      continue;
    }
    const projected = label.point.clone().project(camera);
    const visible = projected.z >= -1 && projected.z <= 1;
    label.div.style.display = visible ? "block" : "none";
    label.div.style.left = `${(projected.x * 0.5 + 0.5) * width}px`;
    label.div.style.top = `${(-projected.y * 0.5 + 0.5) * height}px`;
  }
}

function selectObject(object) {
  if (!object) return;
  selected = object.userData.segment;
  drawSelectedLine(selected);
  drawLocalAxes(selected);
  updateSelectionPanel(selected);
}

function drawSelectedLine(segment) {
  if (selectedLine) scene.remove(selectedLine);
  const points = segment.points.slice(0, 2).map((point) => new THREE.Vector3(point[0], point[1], point[2]));
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineBasicMaterial({ color: 0xffff00, transparent: false });
  selectedLine = new THREE.Line(geometry, material);
  selectedLine.renderOrder = 10;
  scene.add(selectedLine);
}

function drawLocalAxes(segment) {
  if (localAxesGroup) scene.remove(localAxesGroup);
  if (!segment.points || segment.points.length < 2) return;

  const start = new THREE.Vector3(...segment.points[0]);
  const end = new THREE.Vector3(...segment.points[1]);
  const midpoint = start.clone().add(end).multiplyScalar(0.5);
  const localX = end.clone().sub(start).normalize();
  const globalZ = new THREE.Vector3(0, 0, 1);
  let localY = new THREE.Vector3().crossVectors(globalZ, localX).normalize();
  if (!Number.isFinite(localY.x)) localY = new THREE.Vector3(0, 1, 0);
  const localZ = new THREE.Vector3().crossVectors(localX, localY).normalize();

  localAxesGroup = new THREE.Group();
  localAxesGroup.add(new THREE.ArrowHelper(localX, midpoint, 1.5, 0xff3333));
  localAxesGroup.add(new THREE.ArrowHelper(localY, midpoint, 1.2, 0x33cc66));
  localAxesGroup.add(new THREE.ArrowHelper(localZ, midpoint, 1.2, 0x4d8dff));
  scene.add(localAxesGroup);
}

function updateSelectionPanel(segment) {
  const points = segment.points ?? [];
  const start = points[0] ?? [null, null, null];
  const end = points[1] ?? [null, null, null];
  selectionDetailsEl.innerHTML = `
    <dt>Tag</dt><dd>${segment.elementTag}</dd>
    <dt>Tipo</dt><dd>${CATEGORY_LABELS[segment.category] ?? segment.category}</dd>
    <dt>Piso</dt><dd>${segment.floor} (${segment.floor_label ?? "sin etiqueta"})</dd>
    <dt>Capa CAD</dt><dd>${segment.source_layer ?? "generated"}</dd>
    <dt>Plano</dt><dd>${segment.source_dxf ?? "generated"}</dd>
    <dt>Longitud</dt><dd>${formatNumber(segment.length_m)} m</dd>
    <dt>Inicio</dt><dd>${formatPoint(start)}</dd>
    <dt>Fin</dt><dd>${formatPoint(end)}</dd>
    <dt>Confianza</dt><dd>${segment.confidence ?? "-"}</dd>
  `;
}

function formatNumber(value) {
  return Number.isFinite(value) ? value.toFixed(3) : "-";
}

function formatPoint(point) {
  if (!point || point.some((value) => value === null)) return "-";
  return `(${point.map((value) => formatNumber(value)).join(", ")})`;
}

function fitView() {
  if (!modelBounds) return;
  const center = modelBounds.getCenter(new THREE.Vector3());
  const size = modelBounds.getSize(new THREE.Vector3());
  const radius = Math.max(size.x, size.y, size.z) * 0.85;
  controls.target.copy(center);
  camera.position.set(center.x + radius, center.y - radius, center.z + radius * 0.55);
  camera.near = 0.05;
  camera.far = radius * 8;
  camera.updateProjectionMatrix();
  controls.update();
}

function topView() {
  if (!modelBounds) return;
  const center = modelBounds.getCenter(new THREE.Vector3());
  const size = modelBounds.getSize(new THREE.Vector3());
  const radius = Math.max(size.x, size.y) * 0.95;
  controls.target.copy(center);
  camera.position.set(center.x, center.y, center.z + radius);
  controls.update();
}

function onPointerDown(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(selectable.filter((object) => object.visible), false);
  if (hits.length) selectObject(hits[0].object);
}

function searchTag() {
  const query = tagSearchEl.value.trim().toLowerCase();
  if (!query) return;
  const exact = segmentByTag.get(query);
  const match = exact ?? [...segmentByTag.entries()].find(([tag]) => tag.includes(query))?.[1];
  if (!match) {
    statusEl.textContent = `No encontre elementTag que contenga: ${query}`;
    return;
  }
  revealObject(match);
  selectObject(match);
  zoomToObject(match);
}

function revealObject(object) {
  object.visible = true;
  for (const floorObject of objectsByFloor.get(object.userData.floor) ?? []) floorObject.visible = true;
  for (const categoryObject of objectsByCategory.get(object.userData.category) ?? []) categoryObject.visible = true;
}

function zoomToObject(object) {
  const box = new THREE.Box3().setFromObject(object);
  const center = box.getCenter(new THREE.Vector3());
  controls.target.copy(center);
  camera.position.set(center.x + 8, center.y - 8, center.z + 6);
  controls.update();
}

function resize() {
  const width = viewport.clientWidth;
  const height = viewport.clientHeight;
  camera.aspect = width / height;
  camera.updateProjectionMatrix();
  renderer.setSize(width, height);
  updateLabels();
}

function animate() {
  controls.update();
  renderer.render(scene, camera);
  updateLabels();
  requestAnimationFrame(animate);
}

async function boot() {
  addLights();
  resize();
  window.addEventListener("resize", resize);
  renderer.domElement.addEventListener("pointerdown", onPointerDown);
  document.querySelector("#reset-view").addEventListener("click", fitView);
  document.querySelector("#fit-view").addEventListener("click", fitView);
  document.querySelector("#top-view").addEventListener("click", topView);
  document.querySelector("#search-button").addEventListener("click", searchTag);
  tagSearchEl.addEventListener("keydown", (event) => {
    if (event.key === "Enter") searchTag();
  });
  toggleLabelsButton.addEventListener("click", () => {
    labelsVisible = !labelsVisible;
    toggleLabelsButton.textContent = `IDs: ${labelsVisible ? "on" : "off"}`;
    updateLabels();
  });

  const response = await fetch(MODEL_URL);
  if (!response.ok) throw new Error(`No se pudo cargar ${MODEL_URL}`);
  const model = await response.json();
  addModel(model);
  animate();
}

boot().catch((error) => {
  console.error(error);
  statusEl.textContent = `Error: ${error.message}`;
});
