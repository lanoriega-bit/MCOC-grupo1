import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const MODEL_URL = "../results/edificio1_unity.json";
const FLOOR_Z = new Map([
  [-1, 3.96],
  [1, 7.92],
  [2, 11.88],
  [3, 15.84],
  [4, 19.8],
]);
const FLOOR_LABEL = new Map([
  [-1, "1S"],
  [1, "1"],
  [2, "2"],
  [3, "3"],
  [4, "4"],
]);
const CATEGORY_LABELS = {
  slab: "Losas",
  slab_edge: "Bordes de losa",
  beam: "Vigas",
  tributary: "Tributarias",
  blocker: "Blockers",
};
const CATEGORY_COLORS = {
  slab: "#5aa7ff",
  slab_edge: "#cbe8ff",
  beam: "#ffb454",
  tributary: "#7bd88f",
  blocker: "#ff7474",
};
const DEFAULT_VISIBILITY = {
  slab: true,
  slab_edge: true,
  beam: true,
  tributary: false,
  blocker: true,
};

const viewport = document.querySelector("#viewport");
const statusEl = document.querySelector("#status");
const floorControlsEl = document.querySelector("#floor-controls");
const categoryControlsEl = document.querySelector("#category-controls");
const selectionDetailsEl = document.querySelector("#selection-details");
const modelSummaryEl = document.querySelector("#model-summary");
const blockerListEl = document.querySelector("#blocker-list");
const tagSearchEl = document.querySelector("#tag-search");
const toggleLabelsButton = document.querySelector("#toggle-labels");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x07111f);
scene.fog = new THREE.Fog(0x07111f, 95, 230);

const camera = new THREE.PerspectiveCamera(55, 1, 0.05, 700);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
viewport.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.screenSpacePanning = true;
controls.maxDistance = 240;
controls.minDistance = 2;

const raycaster = new THREE.Raycaster();
raycaster.params.Line.threshold = 0.28;
const pointer = new THREE.Vector2();
const selectable = [];
const objectsByFloor = new Map();
const objectsByCategory = new Map();
const objectByTag = new Map();
const labels = [];
const labelLayer = document.createElement("div");
let labelsVisible = false;
let selectedOutline = null;
let modelBounds = null;
let modelRoot = null;

labelLayer.className = "label-layer";
viewport.appendChild(labelLayer);

function addLights() {
  scene.add(new THREE.HemisphereLight(0xd8ecff, 0x172332, 0.95));
  const sun = new THREE.DirectionalLight(0xffffff, 1.35);
  sun.position.set(35, -45, 70);
  sun.castShadow = true;
  scene.add(sun);
}

function material(category, options = {}) {
  const color = new THREE.Color(CATEGORY_COLORS[category] ?? "#ffffff");
  if (category === "slab") {
    return new THREE.MeshStandardMaterial({ color, roughness: 0.8, metalness: 0.03, transparent: true, opacity: 0.28, side: THREE.DoubleSide, ...options });
  }
  if (category === "tributary") {
    return new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false, ...options });
  }
  if (category === "blocker") {
    return new THREE.MeshStandardMaterial({ color, roughness: 0.72, transparent: true, opacity: 0.78, ...options });
  }
  return new THREE.MeshStandardMaterial({ color, roughness: 0.66, metalness: 0.04, ...options });
}

function lineMaterial(category, options = {}) {
  return new THREE.LineBasicMaterial({ color: CATEGORY_COLORS[category] ?? "#ffffff", transparent: true, opacity: 0.72, ...options });
}

function floorZ(floorId) {
  return FLOOR_Z.get(Number(floorId)) ?? Number(floorId) * 3.96;
}

function floorName(floorId) {
  return FLOOR_LABEL.get(Number(floorId)) ?? String(floorId);
}

function remember(object, floorId, category, tag, selectableObject = true) {
  if (!objectsByFloor.has(floorId)) objectsByFloor.set(floorId, []);
  if (!objectsByCategory.has(category)) objectsByCategory.set(category, []);
  objectsByFloor.get(floorId).push(object);
  objectsByCategory.get(category).push(object);
  if (tag) objectByTag.set(String(tag).toLowerCase(), object);
  if (selectableObject) selectable.push(object);
}

function vector2(point) {
  return new THREE.Vector2(Number(point[0]), Number(point[1]));
}

function vector3xy(point, z) {
  return new THREE.Vector3(Number(point[0]), Number(point[1]), z);
}

function validPoint2(point) {
  return Array.isArray(point) && point.length >= 2 && Number.isFinite(Number(point[0])) && Number.isFinite(Number(point[1]));
}

function polygonCenter(points) {
  const center = points.reduce((acc, point) => acc.add(vector2(point)), new THREE.Vector2());
  return center.multiplyScalar(1 / Math.max(points.length, 1));
}

function makeShape(points) {
  const clean = points.filter(validPoint2);
  const shape = new THREE.Shape();
  clean.forEach((point, index) => {
    const p = vector2(point);
    if (index === 0) shape.moveTo(p.x, p.y);
    else shape.lineTo(p.x, p.y);
  });
  shape.closePath();
  return shape;
}

function addSlab(root, slab) {
  const vertices = slab.vertices ?? [];
  if (vertices.length < 3) return;
  const z = floorZ(slab.floor_id);
  const thickness = Math.max(Number(slab.thickness_m) || 0.12, 0.04);
  const geometry = new THREE.ExtrudeGeometry(makeShape(vertices), { depth: thickness, bevelEnabled: false });
  geometry.translate(0, 0, z - thickness * 0.5);
  const mesh = new THREE.Mesh(geometry, material("slab", { opacity: slab.gravity_verified ? 0.28 : 0.15 }));
  const center = polygonCenter(vertices);
  mesh.receiveShadow = true;
  mesh.userData.info = {
    tag: slab.slab_id,
    type: "Losa",
    category: "slab",
    floor_id: slab.floor_id,
    center: [center.x, center.y, z],
    rows: slabRows(slab),
  };
  root.add(mesh);
  remember(mesh, slab.floor_id, "slab", slab.slab_id);
  addPolygonLine(root, vertices, z + thickness * 0.52, slab, "slab_edge");
  addLabel(slab.slab_id, [center.x, center.y, z + 0.12], slab.floor_id, "slab");
}

function addPolygonLine(root, vertices, z, source, category) {
  if (vertices.length < 2) return;
  const points = vertices.map((point) => vector3xy(point, z));
  points.push(points[0].clone());
  const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(points), lineMaterial(category));
  line.userData.info = {
    tag: `${source.slab_id ?? source.beam_id}_EDGE`,
    type: CATEGORY_LABELS[category] ?? category,
    category,
    floor_id: source.floor_id,
    center: points[Math.floor(points.length / 2)].toArray(),
    rows: [["ID", source.slab_id ?? source.beam_id], ["Piso", floorName(source.floor_id)]],
  };
  root.add(line);
  remember(line, source.floor_id, category, line.userData.info.tag, false);
}

function addBeam(root, beam) {
  if (!validPoint2(beam.node_i) || !validPoint2(beam.node_j)) return;
  const z = floorZ(beam.floor_id) + 0.1;
  const start = vector3xy(beam.node_i, z);
  const end = vector3xy(beam.node_j, z);
  const direction = end.clone().sub(start);
  const length = Math.max(direction.length(), 0.05);
  const geometry = new THREE.BoxGeometry(length, 0.24, 0.42);
  const mesh = new THREE.Mesh(geometry, material("beam"));
  mesh.position.copy(start.clone().add(end).multiplyScalar(0.5));
  mesh.rotation.z = Math.atan2(direction.y, direction.x);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  mesh.userData.info = {
    tag: beam.beam_id,
    type: "Viga",
    category: "beam",
    floor_id: beam.floor_id,
    points: [start.toArray(), end.toArray()],
    center: mesh.position.toArray(),
    rows: beamRows(beam),
  };
  root.add(mesh);
  remember(mesh, beam.floor_id, "beam", beam.beam_id);
  addLabel(beam.beam_id, mesh.position.toArray(), beam.floor_id, "beam");
}

function addTributaries(root, beam) {
  const z = floorZ(beam.floor_id) + 0.17;
  for (const trib of beam.poligonos_tributarios ?? []) {
    const polygon = trib.polygon ?? [];
    if (polygon.length < 3) continue;
    const geometry = new THREE.ShapeGeometry(makeShape(polygon));
    geometry.translate(0, 0, z);
    const mesh = new THREE.Mesh(geometry, material("tributary"));
    const center = polygonCenter(polygon);
    const tag = `${beam.beam_id}__${trib.slab_id}`;
    mesh.userData.info = {
      tag,
      type: "Poligono tributario",
      category: "tributary",
      floor_id: beam.floor_id,
      center: [center.x, center.y, z],
      rows: [["Viga", beam.beam_id], ["Losa", trib.slab_id], ["Piso", floorName(beam.floor_id)], ["Area", `${formatNumber(trib.area_m2)} m2`], ["w lineal", `${formatNumber(beam.w_lineal_kN_m)} kN/m`]],
    };
    root.add(mesh);
    remember(mesh, beam.floor_id, "tributary", tag);
  }
}

function addBlockerMarker(root, blocker) {
  const floorId = blocker.floor_id ?? blocker.floor;
  const z = floorZ(floorId) + 0.65;
  const geometry = new THREE.OctahedronGeometry(0.55, 0);
  const mesh = new THREE.Mesh(geometry, material("blocker"));
  mesh.position.set(-2, -2, z);
  mesh.userData.info = {
    tag: blocker.slab_id,
    type: "Blocker geometrico",
    category: "blocker",
    floor_id: floorId,
    center: mesh.position.toArray(),
    rows: [["ID", blocker.slab_id], ["Piso", floorName(floorId)], ["Estado", blocker.status], ["Area", `${formatNumber(blocker.area_m2)} m2`], ["Razon", (blocker.reasons ?? []).join("; ")], ["Final", blocker.final_reason ?? "-"]],
  };
  root.add(mesh);
  remember(mesh, floorId, "blocker", blocker.slab_id);
  addLabel(blocker.slab_id, mesh.position.toArray(), floorId, "blocker");
}

function addGrid(root, data) {
  const allPoints = [];
  for (const slab of data.losas ?? []) for (const point of slab.vertices ?? []) if (validPoint2(point)) allPoints.push(vector2(point));
  for (const beam of data.vigas ?? []) {
    if (validPoint2(beam.node_i)) allPoints.push(vector2(beam.node_i));
    if (validPoint2(beam.node_j)) allPoints.push(vector2(beam.node_j));
  }
  if (!allPoints.length) return;
  const box = new THREE.Box2().setFromPoints(allPoints);
  const size = new THREE.Vector2();
  const center = new THREE.Vector2();
  box.getSize(size);
  box.getCenter(center);
  const helper = new THREE.GridHelper(Math.max(size.x, size.y) * 1.2, 24, 0x2d5f87, 0x1b3349);
  helper.rotation.x = Math.PI / 2;
  helper.position.set(center.x, center.y, 0);
  root.add(helper);
}

function slabRows(slab) {
  return [
    ["ID", slab.slab_id],
    ["Piso", floorName(slab.floor_id)],
    ["Estado", slab.gravity_verified ? "gravity_verified" : (slab.status ?? slab.load_status ?? "no verificado")],
    ["Area efectiva", `${formatNumber(slab.area_efectiva_m2)} m2`],
    ["Espesor", `${formatNumber(slab.thickness_m)} m`],
    ["qG", maybeLoad(slab.qG_kN_m2, "kN/m2")],
    ["PP losa", maybeLoad(slab.pp_kN_m2, "kN/m2")],
    ["PM adic", maybeLoad(slab.pm_adic_kN_m2, "kN/m2")],
    ["SC", maybeLoad(slab.sc_kN_m2, "kN/m2")],
    ["Carga total", maybeLoad(slab.total_carga_kN, "kN")],
    ["Receptores", (slab.receiver_beam_ids ?? []).join(", ") || "-"],
    ["Plano", slab.source_plan ?? "-"],
  ];
}

function beamRows(beam) {
  return [
    ["ID", beam.beam_id],
    ["Piso", floorName(beam.floor_id)],
    ["Longitud", `${formatNumber(beam.longitud_m)} m`],
    ["Nodo i", formatPoint2(beam.node_i)],
    ["Nodo j", formatPoint2(beam.node_j)],
    ["Area trib.", `${formatNumber(beam.area_tributaria_m2)} m2`],
    ["qG", maybeLoad(beam.qG_kN_m2, "kN/m2")],
    ["P", maybeLoad(beam.P_kN, "kN")],
    ["w", maybeLoad(beam.w_lineal_kN_m, "kN/m")],
    ["Losas", (beam.slab_ids ?? []).join(", ") || "-"],
    ["Verificada", String(Boolean(beam.gravity_verified))],
  ];
}

function maybeLoad(value, unit) {
  return Number.isFinite(Number(value)) ? `${formatNumber(value)} ${unit}` : "-";
}

function formatNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(3) : "-";
}

function formatPoint2(point) {
  if (!validPoint2(point)) return "-";
  return `(${formatNumber(point[0])}, ${formatNumber(point[1])})`;
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
}

function rowsToHtml(rows) {
  return rows.map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value)}</dd>`).join("");
}

function addLabel(tag, point, floorId, category) {
  const div = document.createElement("div");
  div.className = "viewer-label";
  div.textContent = shortTag(tag);
  div.style.display = "none";
  labelLayer.appendChild(div);
  labels.push({ div, point: new THREE.Vector3(...point), tag, floorId, category });
}

function shortTag(tag) {
  return String(tag).replace("E1_", "").replace("__", " / ");
}

function addModel(data) {
  modelRoot = new THREE.Group();
  modelRoot.name = "Edificio 1 gravedad";
  addGrid(modelRoot, data);
  for (const slab of data.losas ?? []) addSlab(modelRoot, slab);
  for (const beam of data.vigas ?? []) addBeam(modelRoot, beam);
  for (const beam of data.vigas ?? []) addTributaries(modelRoot, beam);
  for (const blocker of data.geometric_blockers ?? []) addBlockerMarker(modelRoot, blocker);
  scene.add(modelRoot);
  modelBounds = new THREE.Box3().setFromObject(modelRoot);
  buildControls();
  applyAllVisibility();
  updateSummary(data);
  updateBlockers(data.geometric_blockers ?? []);
  fitView("iso");
  statusEl.textContent = `${data.building_id}: ${data.losas?.length ?? 0} losas, ${data.vigas?.length ?? 0} vigas, ${(data.geometric_blockers ?? []).length} blocker.`;
}

function updateSummary(data) {
  const ver = data.verificacion ?? {};
  const blockers = data.geometric_blockers ?? [];
  modelSummaryEl.innerHTML = rowsToHtml([
    ["Formato", data.formato],
    ["Pisos", (data.pisos_presentes ?? []).map(floorName).join(", ")],
    ["Gravedad", (data.gravedad_verificada_pisos ?? []).map(floorName).join(", ")],
    ["Losas", `${data.losas?.length ?? 0}`],
    ["Vigas", `${data.vigas?.length ?? 0}`],
    ["Blockers", `${blockers.length}`],
    ["Area diff", `${formatNumber(ver.diferencia_area_m2)} m2`],
    ["Carga diff", `${formatNumber(ver.diferencia_carga_kN)} kN`],
  ]);
}

function updateBlockers(blockers) {
  if (!blockers.length) {
    blockerListEl.textContent = "Sin blockers geometricos.";
    return;
  }
  blockerListEl.replaceChildren(...blockers.map((blocker) => {
    const item = document.createElement("button");
    item.type = "button";
    item.className = "blocker-item";
    item.textContent = `${blocker.slab_id} - piso ${floorName(blocker.floor_id)} - ${blocker.status}`;
    item.addEventListener("click", () => {
      const object = objectByTag.get(String(blocker.slab_id).toLowerCase());
      if (object) {
        revealObject(object);
        selectObject(object);
        zoomToObject(object);
      }
    });
    return item;
  }));
}

function buildControls() {
  const floors = [...objectsByFloor.keys()].sort((a, b) => Number(a) - Number(b));
  floorControlsEl.replaceChildren(...floors.map(makeFloorToggle));
  const categories = Object.keys(CATEGORY_LABELS).filter((category) => objectsByCategory.has(category));
  categoryControlsEl.replaceChildren(...categories.map(makeCategoryToggle));
}

function makeFloorToggle(floorId) {
  const row = document.createElement("label");
  row.className = "toggle-row";
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = true;
  checkbox.dataset.floor = String(floorId);
  checkbox.addEventListener("change", applyAllVisibility);
  const label = document.createElement("span");
  label.textContent = `Piso ${floorName(floorId)}`;
  const solo = document.createElement("button");
  solo.type = "button";
  solo.className = "small-button";
  solo.textContent = "solo";
  solo.addEventListener("click", (event) => {
    event.preventDefault();
    isolateFloor(floorId);
  });
  row.append(checkbox, label, solo);
  return row;
}

function makeCategoryToggle(category) {
  const row = document.createElement("label");
  row.className = "toggle-row";
  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.checked = DEFAULT_VISIBILITY[category] ?? true;
  checkbox.dataset.category = category;
  checkbox.addEventListener("change", applyAllVisibility);
  const label = document.createElement("span");
  label.textContent = CATEGORY_LABELS[category];
  const swatch = document.createElement("span");
  swatch.className = "swatch";
  swatch.style.background = CATEGORY_COLORS[category];
  row.append(checkbox, label, swatch);
  return row;
}

function floorVisible(floorId) {
  const input = floorControlsEl.querySelector(`input[data-floor="${String(floorId)}"]`);
  return input ? input.checked : true;
}

function categoryVisible(category) {
  const input = categoryControlsEl.querySelector(`input[data-category="${category}"]`);
  return input ? input.checked : true;
}

function applyAllVisibility() {
  for (const objects of objectsByCategory.values()) {
    for (const object of objects) object.visible = floorVisible(object.userData.info.floor_id) && categoryVisible(object.userData.info.category);
  }
  updateLabels();
}

function isolateFloor(floorId) {
  for (const input of floorControlsEl.querySelectorAll("input")) input.checked = input.dataset.floor === String(floorId);
  applyAllVisibility();
}

function showAll() {
  for (const input of floorControlsEl.querySelectorAll("input")) input.checked = true;
  for (const input of categoryControlsEl.querySelectorAll("input")) input.checked = true;
  applyAllVisibility();
}

function selectObject(object) {
  if (!object) return;
  if (selectedOutline) scene.remove(selectedOutline);
  selectedOutline = object.isMesh ? new THREE.BoxHelper(object, 0xffff00) : makeLineOutline(object);
  scene.add(selectedOutline);
  selectionDetailsEl.innerHTML = rowsToHtml(object.userData.info.rows);
}

function makeLineOutline(object) {
  const clone = object.clone();
  clone.material = new THREE.LineBasicMaterial({ color: 0xffff00 });
  return clone;
}

function revealObject(object) {
  const floorInput = floorControlsEl.querySelector(`input[data-floor="${String(object.userData.info.floor_id)}"]`);
  const categoryInput = categoryControlsEl.querySelector(`input[data-category="${object.userData.info.category}"]`);
  if (floorInput) floorInput.checked = true;
  if (categoryInput) categoryInput.checked = true;
  applyAllVisibility();
}

function zoomToObject(object) {
  const box = new THREE.Box3().setFromObject(object);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const radius = Math.max(size.x, size.y, size.z, 4);
  controls.target.copy(center);
  camera.position.set(center.x + radius * 2.2, center.y - radius * 2.2, center.z + radius * 1.3);
  camera.up.set(0, 0, 1);
  controls.update();
}

function updateLabels() {
  if (!labelsVisible) {
    for (const label of labels) label.div.style.display = "none";
    return;
  }
  const width = viewport.clientWidth;
  const height = viewport.clientHeight;
  for (const label of labels) {
    const object = objectByTag.get(String(label.tag).toLowerCase());
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

function fitView(mode = "iso") {
  if (!modelBounds) return;
  const center = modelBounds.getCenter(new THREE.Vector3());
  const size = modelBounds.getSize(new THREE.Vector3());
  const radius = Math.max(size.x, size.y, size.z, 10);
  controls.target.copy(center);
  camera.up.set(0, 0, 1);
  if (mode === "top") camera.position.set(center.x, center.y, center.z + radius * 1.65);
  else if (mode === "north") camera.position.set(center.x, center.y + radius * 1.55, center.z + size.z * 0.08);
  else if (mode === "south") camera.position.set(center.x, center.y - radius * 1.55, center.z + size.z * 0.08);
  else if (mode === "east") camera.position.set(center.x + radius * 1.55, center.y, center.z + size.z * 0.08);
  else if (mode === "west") camera.position.set(center.x - radius * 1.55, center.y, center.z + size.z * 0.08);
  else camera.position.set(center.x + radius * 0.9, center.y - radius * 1.05, center.z + radius * 0.55);
  camera.near = 0.05;
  camera.far = radius * 8;
  camera.lookAt(center);
  camera.updateProjectionMatrix();
  controls.update();
}

function searchTag() {
  const query = tagSearchEl.value.trim().toLowerCase();
  if (!query) return;
  const exact = objectByTag.get(query);
  const partial = exact ?? [...objectByTag.entries()].find(([tag]) => tag.includes(query))?.[1];
  if (!partial) {
    statusEl.textContent = `No encontre ID que contenga: ${query}`;
    return;
  }
  revealObject(partial);
  selectObject(partial);
  zoomToObject(partial);
}

function onPointerDown(event) {
  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(selectable.filter((object) => object.visible), false);
  if (hits.length) selectObject(hits[0].object);
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
  document.querySelector("#view-iso").addEventListener("click", () => fitView("iso"));
  document.querySelector("#view-top").addEventListener("click", () => fitView("top"));
  document.querySelector("#view-north").addEventListener("click", () => fitView("north"));
  document.querySelector("#view-east").addEventListener("click", () => fitView("east"));
  document.querySelector("#view-south").addEventListener("click", () => fitView("south"));
  document.querySelector("#view-west").addEventListener("click", () => fitView("west"));
  document.querySelector("#show-all").addEventListener("click", showAll);
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
  const data = await response.json();
  addModel(data);
  animate();
}

boot().catch((error) => {
  console.error(error);
  statusEl.textContent = `Error: ${error.message}`;
});
