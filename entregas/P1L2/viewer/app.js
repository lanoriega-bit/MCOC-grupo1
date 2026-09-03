import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const urlParams = new URLSearchParams(window.location.search);
const modelFile = urlParams.get("model") || "model_viewer.json";
const MODEL_URL = `../unity_export/${modelFile}`;
const CATEGORY_LABELS = {
  axis: "Ejes CAD",
  beam: "Vigas",
  cad_reference: "Lineas CAD ref.",
  column: "Pilares/columnas",
  column_plan: "Pilares CAD",
  diaphragm: "Diafragmas",
  slab: "Piso/techo",
  slab_edge: "Borde losa CAD",
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
scene.fog = new THREE.Fog(0x07111f, 85, 180);

const camera = new THREE.PerspectiveCamera(55, 1, 0.05, 500);
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

const raycaster = new THREE.Raycaster();
raycaster.params.Line.threshold = 0.35;
const pointer = new THREE.Vector2();
const selectable = [];
const objectsByFloor = new Map();
const objectsByCategory = new Map();
const objectByTag = new Map();
const labels = [];
const labelLayer = document.createElement("div");
let labelsVisible = false;
let selectedOutline = null;
let localAxesGroup = null;
let modelBounds = null;

labelLayer.className = "label-layer";
viewport.appendChild(labelLayer);

function addLights() {
  scene.add(new THREE.HemisphereLight(0xd8ecff, 0x172332, 0.85));
  const sun = new THREE.DirectionalLight(0xffffff, 1.4);
  sun.position.set(35, -40, 55);
  sun.castShadow = true;
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

function materialFor(model, category) {
  const color = new THREE.Color(categoryColor(model, category));
  if (category === "slab") {
    return new THREE.MeshStandardMaterial({ color, roughness: 0.8, metalness: 0.05, transparent: true, opacity: 0.18, depthWrite: false });
  }
  if (category === "wall") return new THREE.MeshStandardMaterial({ color, roughness: 0.78, metalness: 0.02, transparent: true, opacity: 0.72 });
  if (category === "support") return new THREE.MeshStandardMaterial({ color, roughness: 0.9, metalness: 0.0 });
  return new THREE.MeshStandardMaterial({ color, roughness: 0.68, metalness: 0.04 });
}

function makeLinearPrism(model, solid) {
  const start = new THREE.Vector3(...solid.start);
  const end = new THREE.Vector3(...solid.end);
  const direction = end.clone().sub(start);
  const length = Math.max(Math.hypot(direction.x, direction.y), 0.05);
  const geometry = new THREE.BoxGeometry(length, solid.width_m, solid.height_m);
  const mesh = new THREE.Mesh(geometry, materialFor(model, solid.category));
  mesh.position.copy(start.clone().add(end).multiplyScalar(0.5));
  mesh.rotation.z = Math.atan2(direction.y, direction.x);
  mesh.castShadow = solid.category !== "slab";
  mesh.receiveShadow = true;
  return mesh;
}

function makeBox(model, solid) {
  const geometry = new THREE.BoxGeometry(solid.width_m, solid.depth_m, solid.height_m);
  const mesh = new THREE.Mesh(geometry, materialFor(model, solid.category));
  mesh.position.set(...solid.center);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  return mesh;
}

function makeSlab(model, solid) {
  const geometry = new THREE.BoxGeometry(solid.width_m, solid.depth_m, solid.height_m);
  const mesh = new THREE.Mesh(geometry, materialFor(model, "slab"));
  mesh.position.set(...solid.center);
  mesh.receiveShadow = true;
  return mesh;
}

function normalizeSolidAsSelection(solid) {
  const tag = solid.solidTag;
  if (solid.kind === "linear_prism") {
    return { ...solid, elementTag: tag, points: [solid.start, solid.end] };
  }
  const center = solid.center ?? [0, 0, 0];
  const dz = (solid.height_m ?? 0) / 2;
  return { ...solid, elementTag: tag, points: [[center[0], center[1], center[2] - dz], [center[0], center[1], center[2] + dz]] };
}

function addSolid(model, root, solid) {
  let object;
  if (solid.kind === "linear_prism") object = makeLinearPrism(model, solid);
  else if (solid.kind === "slab_box") object = makeSlab(model, solid);
  else object = makeBox(model, solid);

  const selection = normalizeSolidAsSelection(solid);
  object.userData.segment = selection;
  object.userData.floor = solid.floor;
  object.userData.category = solid.category;
  root.add(object);
  rememberObject(object, solid.floor, solid.category);
  objectByTag.set(selection.elementTag.toLowerCase(), object);
  selectable.push(object);
}

function makeCadLine(model, segment) {
  const points = segment.points.map((point) => new THREE.Vector3(point[0], point[1], point[2]));
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const displayCategory = segment.category === "axis" ? "axis" : "cad_reference";
  const material = new THREE.LineBasicMaterial({ color: categoryColor(model, displayCategory), transparent: true, opacity: displayCategory === "axis" ? 0.24 : 0.28 });
  const line = new THREE.Line(geometry, material);
  line.visible = displayCategory === "axis";
  line.userData.segment = { ...segment, displayCategory };
  line.userData.floor = segment.floor;
  line.userData.category = displayCategory;
  return line;
}

function makeDiaphragm(model, diaphragm) {
  const points = diaphragm.points.map((point) => new THREE.Vector3(point[0], point[1], point[2]));
  const geometry = new THREE.BufferGeometry().setFromPoints(points);
  const material = new THREE.LineDashedMaterial({ color: categoryColor(model, "diaphragm"), dashSize: 0.9, gapSize: 0.45, transparent: true, opacity: 0.85 });
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
  root.name = "Solid building model";

  for (const solid of model.solids ?? []) addSolid(model, root, solid);

  for (const segment of model.segments) {
    const line = makeCadLine(model, segment);
    root.add(line);
    rememberObject(line, segment.floor, line.userData.category);
    objectByTag.set(segment.elementTag.toLowerCase(), line);
  }

  for (const diaphragm of model.diaphragms ?? []) {
    const line = makeDiaphragm(model, diaphragm);
    root.add(line);
    rememberObject(line, diaphragm.floor, "diaphragm");
    objectByTag.set(line.userData.segment.elementTag.toLowerCase(), line);
    selectable.push(line);
  }

  scene.add(root);
  modelBounds = new THREE.Box3().setFromObject(root);
  buildControls(model);
  buildIdLabels(model);
  fitView();
  statusEl.textContent = `${model.solids?.length ?? 0} solidos, ${model.segments.length} lineas CAD, ${model.labels?.length ?? 0} etiquetas.`;
}

function buildControls(model) {
  const floors = [...objectsByFloor.keys()].sort((a, b) => floorOrder(a) - floorOrder(b));
  floorControlsEl.replaceChildren(...floors.map(makeFloorToggle));

  const categories = [...objectsByCategory.keys()].filter((category) => CATEGORY_LABELS[category]).sort();
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
  checkbox.checked = category !== "cad_reference";
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
  for (const object of objectsByFloor.get(floor) ?? []) object.visible = visible && categoryCheckboxState(object.userData.category);
  updateLabels();
}

function setCategoryVisible(category, visible) {
  for (const object of objectsByCategory.get(category) ?? []) object.visible = visible && floorCheckboxState(object.userData.floor);
  updateLabels();
}

function floorCheckboxState(floor) {
  for (const input of floorControlsEl.querySelectorAll("input")) {
    const text = input.parentElement?.querySelector("span")?.textContent;
    if (text === `Piso ${floor}`) return input.checked;
  }
  return true;
}

function categoryCheckboxState(category) {
  for (const input of categoryControlsEl.querySelectorAll("input")) {
    const text = input.parentElement?.querySelector("span")?.textContent;
    if (text === (CATEGORY_LABELS[category] ?? category)) return input.checked;
  }
  return true;
}

function isolateFloor(floor) {
  for (const input of floorControlsEl.querySelectorAll("input")) {
    const label = input.parentElement?.querySelector("span")?.textContent ?? "";
    input.checked = label === `Piso ${floor}`;
  }
  for (const [currentFloor, objects] of objectsByFloor.entries()) {
    for (const object of objects) object.visible = currentFloor === floor && categoryCheckboxState(object.userData.category);
  }
  updateLabels();
}

function buildIdLabels(model) {
  const candidates = (model.solids ?? []).filter((solid) => ["beam", "wall", "column", "support"].includes(solid.category));
  for (const solid of candidates) {
    const point = solid.center ? new THREE.Vector3(...solid.center) : midpoint(solid.start, solid.end);
    const div = document.createElement("div");
    div.className = "viewer-label";
    div.textContent = shortTag(solid.solidTag);
    div.style.display = "none";
    labelLayer.appendChild(div);
    labels.push({ div, point, tag: solid.solidTag });
  }
}

function midpoint(start, end) {
  return new THREE.Vector3((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, (start[2] + end[2]) / 2);
}

function shortTag(tag) {
  return tag.replace("SOL_", "").replace("CAD_", "");
}

function updateLabels() {
  if (!labelsVisible) {
    for (const label of labels) label.div.style.display = "none";
    return;
  }
  const width = viewport.clientWidth;
  const height = viewport.clientHeight;
  for (const label of labels) {
    const object = objectByTag.get(label.tag.toLowerCase());
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
  const selected = object.userData.segment;
  drawSelectedOutline(object, selected);
  drawLocalAxes(selected);
  updateSelectionPanel(selected);
}

function drawSelectedOutline(object, selected) {
  if (selectedOutline) scene.remove(selectedOutline);
  if (object.isMesh) {
    const box = new THREE.BoxHelper(object, 0xffff00);
    selectedOutline = box;
  } else {
    const points = selected.points.slice(0, 2).map((point) => new THREE.Vector3(point[0], point[1], point[2]));
    const geometry = new THREE.BufferGeometry().setFromPoints(points);
    selectedOutline = new THREE.Line(geometry, new THREE.LineBasicMaterial({ color: 0xffff00 }));
  }
  scene.add(selectedOutline);
}

function drawLocalAxes(segment) {
  if (localAxesGroup) scene.remove(localAxesGroup);
  if (!segment.points || segment.points.length < 2) return;
  const start = new THREE.Vector3(...segment.points[0]);
  const end = new THREE.Vector3(...segment.points[1]);
  const midpointPoint = start.clone().add(end).multiplyScalar(0.5);
  const localX = end.clone().sub(start).normalize();
  const globalZ = new THREE.Vector3(0, 0, 1);
  let localY = new THREE.Vector3().crossVectors(globalZ, localX).normalize();
  if (!Number.isFinite(localY.x) || localY.lengthSq() < 0.001) localY = new THREE.Vector3(0, 1, 0);
  const localZ = new THREE.Vector3().crossVectors(localX, localY).normalize();
  localAxesGroup = new THREE.Group();
  localAxesGroup.add(new THREE.ArrowHelper(localX, midpointPoint, 1.7, 0xff3333));
  localAxesGroup.add(new THREE.ArrowHelper(localY, midpointPoint, 1.3, 0x33cc66));
  localAxesGroup.add(new THREE.ArrowHelper(localZ, midpointPoint, 1.3, 0x4d8dff));
  scene.add(localAxesGroup);
}

function updateSelectionPanel(segment) {
  const points = segment.points ?? [];
  const start = points[0] ?? [null, null, null];
  const end = points[1] ?? [null, null, null];
  const sec = segment.seccion_cm ?? (segment.seccion ? segment.seccion : "-");
  selectionDetailsEl.innerHTML = `
    <dt>Tag</dt><dd>${segment.elementTag}</dd>
    <dt>ID building_master</dt><dd>${segment.building_master_id ?? "-"}</dd>
    <dt>Tipo</dt><dd>${CATEGORY_LABELS[segment.category] ?? segment.category}</dd>
    <dt>Ubicacion</dt><dd>${segment.floor_id ?? segment.floor} (${segment.floor_name ?? ""})</dd>
    <dt>Seccion</dt><dd>${sec}</dd>
    <dt>Z (model_z_m)</dt><dd>${formatNumber(segment.model_z_m)} m / fuente ${formatNumber(segment.source_elevation_m)} m</dd>
    <dt>Capa CAD</dt><dd>${segment.source_layer ?? "generated"}</dd>
    <dt>Plano</dt><dd>${segment.source_dxf ?? "generated"}</dd>
    <dt>Zona / sector</dt><dd>${segment.zona ?? "-"} / ${segment.sector ?? "-"}</dd>
    <dt>Longitud</dt><dd>${formatNumber(segment.length_m)} m</dd>
    <dt>Inicio</dt><dd>${formatPoint(start)}</dd>
    <dt>Fin</dt><dd>${formatPoint(end)}</dd>
    <dt>Estado revision</dt><dd>${segment.estado_revision ?? "-"}</dd>
    <dt>Confianza</dt><dd>${segment.confidence ?? "-"} (${formatNumber(segment.confianza_score)})</dd>
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
  const radius = Math.max(size.x, size.y, size.z) * 0.95;
  controls.target.copy(center);
  camera.position.set(center.x + radius, center.y - radius, center.z + radius * 0.62);
  camera.near = 0.05;
  camera.far = radius * 8;
  camera.updateProjectionMatrix();
  controls.update();
}

function topView() {
  if (!modelBounds) return;
  const center = modelBounds.getCenter(new THREE.Vector3());
  const size = modelBounds.getSize(new THREE.Vector3());
  const radius = Math.max(size.x, size.y) * 1.05;
  controls.target.copy(center);
  camera.up.set(0, 1, 0);
  camera.position.set(center.x, center.y, center.z + radius);
  camera.lookAt(center);
  controls.update();
}

function sideView(side) {
  if (!modelBounds) return;
  const center = modelBounds.getCenter(new THREE.Vector3());
  const size = modelBounds.getSize(new THREE.Vector3());
  const dist = Math.max(size.x, size.y, size.z) * 1.5;
  const lift = size.z * 0.08;

  // Orientar la orbita: D = sur (-Y) es la referencia. Los demas son
  // rotaciones de +90° hacia la derecha: A = este, B = norte, C = oeste.
  const angles = { D: 0, A: Math.PI / 2, B: Math.PI, C: Math.PI * 1.5 };
  const angle = angles[side] ?? 0;
  const offset = new THREE.Vector3(0, -dist, 0).applyMatrix4(new THREE.Matrix4().makeRotationZ(angle));

  // Fijar la vertical del mundo (Z) como "arriba" en pantalla para que
  // el piso base quede abajo y el piso 4 arriba en los 4 lados.
  camera.up.set(0, 0, 1);
  controls.target.copy(center);
  camera.position.set(center.x + offset.x, center.y + offset.y, center.z + lift);
  camera.lookAt(center);
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
  const exact = objectByTag.get(query);
  const match = exact ?? [...objectByTag.entries()].find(([tag]) => tag.includes(query))?.[1];
  if (!match) {
    statusEl.textContent = `No encontre elementTag que contenga: ${query}`;
    return;
  }
  revealObject(match);
  selectObject(match);
  zoomToObject(match);
}

function revealObject(object) {
  for (const input of floorControlsEl.querySelectorAll("input")) {
    const label = input.parentElement?.querySelector("span")?.textContent ?? "";
    if (label === `Piso ${object.userData.floor}`) input.checked = true;
  }
  for (const input of categoryControlsEl.querySelectorAll("input")) {
    const label = input.parentElement?.querySelector("span")?.textContent ?? "";
    if (label === (CATEGORY_LABELS[object.userData.category] ?? object.userData.category)) input.checked = true;
  }
  object.visible = true;
  for (const floorObject of objectsByFloor.get(object.userData.floor) ?? []) floorObject.visible = categoryCheckboxState(floorObject.userData.category);
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
  document.querySelector("#view-side-A").addEventListener("click", sideView.bind(null, "A"));
  document.querySelector("#view-side-B").addEventListener("click", sideView.bind(null, "B"));
  document.querySelector("#view-side-C").addEventListener("click", sideView.bind(null, "C"));
  document.querySelector("#view-side-D").addEventListener("click", sideView.bind(null, "D"));
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
