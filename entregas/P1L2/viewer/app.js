import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const urlParams = new URLSearchParams(window.location.search);
const DEFAULT_MODEL_FILE = "model_combined_viewer.json";
const modelFile = urlParams.get("model") || DEFAULT_MODEL_FILE;
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
const modelSelectEl = document.querySelector("#model-select");
const copyIdentificationButton = document.querySelector("#copy-identification");

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
const selectedLabel = document.createElement("div");
let labelsVisible = false;
let selectedOutline = null;
let localAxesGroup = null;
let modelBounds = null;
let selectedObject = null;
let selectedSegment = null;
let pointerDown = null;

labelLayer.className = "label-layer";
viewport.appendChild(labelLayer);
selectedLabel.className = "viewer-label selected-label";
selectedLabel.style.display = "none";
viewport.appendChild(selectedLabel);

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

function registerObjectAliases(object, segment) {
  for (const key of [segment.id, segment.human_id, segment.elementTag, segment.solidTag, segment.legacy_solidTag]) {
    if (!key) continue;
    const normalized = String(key).toLowerCase();
    if (!objectByTag.has(normalized)) objectByTag.set(normalized, object);
  }
}

function primaryElementId(segment) {
  return segment?.id ?? segment?.human_id ?? segment?.building_master_id ?? segment?.elementTag ?? segment?.solidTag ?? "-";
}

function legacyElementTag(segment) {
  return segment?.elementTag ?? segment?.solidTag ?? segment?.legacy_solidTag ?? "-";
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
  const tag = solid.elementTag ?? solid.solidTag ?? solid.id;
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
  registerObjectAliases(object, selection);
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
    ...diaphragm,
    elementTag: diaphragm.elementTag ?? diaphragm.id ?? `DIA_${diaphragm.building}_${diaphragm.floor}`,
    floor_label: diaphragm.floor_label ?? `Diafragma ${diaphragm.floor}`,
    source_layer: diaphragm.source_layer ?? "generated",
    source_dxf: diaphragm.source_dxf ?? "generated",
    length_m: diaphragm.length_m ?? 0,
    confidence: diaphragm.confidence ?? "qa",
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
    registerObjectAliases(line, line.userData.segment);
  }

  for (const diaphragm of model.diaphragms ?? []) {
    const line = makeDiaphragm(model, diaphragm);
    root.add(line);
    rememberObject(line, diaphragm.floor, "diaphragm");
    registerObjectAliases(line, line.userData.segment);
    selectable.push(line);
  }

  scene.add(root);
  modelBounds = new THREE.Box3().setFromObject(root);
  buildControls(model);
  buildIdLabels(model);
  fitView();
  statusEl.textContent = `${modelFile}: ${model.solids?.length ?? 0} solidos, ${model.segments.length} lineas CAD, ${model.labels?.length ?? 0} etiquetas.`;
}

function buildControls(model) {
  const floors = [...objectsByFloor.keys()].sort((a, b) => floorOrder(a) - floorOrder(b));
  floorControlsEl.replaceChildren(...floors.map(makeFloorToggle));

  const categories = [...objectsByCategory.keys()].filter((category) => CATEGORY_LABELS[category]).sort();
  categoryControlsEl.replaceChildren(...categories.map((category) => makeCategoryToggle(category, categoryColor(model, category))));
}

function floorOrder(floor) {
  const order = { S1: 0, P1: 1, P2: 2, P3: 3, P4: 4, base: -1, "1S": 0, "1": 1, "2": 2, "3": 3, "4": 4 };
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
    div.textContent = primaryElementId(solid);
    div.style.display = "none";
    labelLayer.appendChild(div);
    labels.push({ div, point, tag: primaryElementId(solid) });
  }
}

function midpoint(start, end) {
  return new THREE.Vector3((start[0] + end[0]) / 2, (start[1] + end[1]) / 2, (start[2] + end[2]) / 2);
}

function shortTag(tag) {
  return String(tag).replace("SOL_", "").replace("CAD_", "");
}

function updateLabels() {
  if (!labelsVisible) {
    for (const label of labels) label.div.style.display = "none";
    updateSelectedLabel();
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
  updateSelectedLabel();
}

function updateSelectedLabel() {
  if (!selectedObject || !selectedSegment || !selectedObject.visible) {
    selectedLabel.style.display = "none";
    return;
  }
  const box = new THREE.Box3().setFromObject(selectedObject);
  const point = box.getCenter(new THREE.Vector3());
  point.z = box.max.z + 0.55;
  const projected = point.project(camera);
  const visible = projected.z >= -1 && projected.z <= 1;
  selectedLabel.style.display = visible ? "block" : "none";
  selectedLabel.textContent = primaryElementId(selectedSegment);
  selectedLabel.style.left = `${(projected.x * 0.5 + 0.5) * viewport.clientWidth}px`;
  selectedLabel.style.top = `${(-projected.y * 0.5 + 0.5) * viewport.clientHeight}px`;
}

function selectObject(object) {
  if (!object) return;
  const selected = object.userData.segment;
  selectedObject = object;
  selectedSegment = selected;
  drawSelectedOutline(object, selected);
  drawLocalAxes(selected);
  updateSelectionPanel(selected);
  updateSelectedLabel();
}

function clearSelection() {
  selectedObject = null;
  selectedSegment = null;
  if (selectedOutline) scene.remove(selectedOutline);
  if (localAxesGroup) scene.remove(localAxesGroup);
  selectedOutline = null;
  localAxesGroup = null;
  selectedLabel.style.display = "none";
  if (copyIdentificationButton) copyIdentificationButton.disabled = true;
  const fragment = document.createDocumentFragment();
  addDetailRow(fragment, "Estado", "Haz click sobre una viga, muro, pilar o apoyo.");
  selectionDetailsEl.replaceChildren(fragment);
}

function drawSelectedOutline(object, selected) {
  if (selectedOutline) scene.remove(selectedOutline);
  if (object.isMesh) {
    const box = new THREE.BoxHelper(object, 0xffff00);
    selectedOutline = box;
  } else {
    const points = selected.points.map((point) => new THREE.Vector3(point[0], point[1], point[2]));
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
  const fragment = document.createDocumentFragment();
  addDetailRow(fragment, "ID", primaryElementId(segment));
  addDetailRow(fragment, "elementTag", legacyElementTag(segment));
  addDetailRow(fragment, "Tipo", CATEGORY_LABELS[segment.category] ?? segment.category);
  addDetailRow(fragment, "Edificio", segment.building ?? "-");
  addDetailRow(fragment, "Piso", `${segment.floor_id ?? segment.floor}${segment.source_floor ? ` (fuente ${segment.source_floor})` : ""}`);
  addDetailRow(fragment, "Ubicacion", segment.location_description ?? "-");
  addDetailRow(fragment, "Ejes", formatAxes(segment));
  addDetailRow(fragment, "Coordenadas", formatCoordinates(segment));
  addDetailRow(fragment, "Propiedades", formatSection(segment));
  addDetailRow(fragment, "Material", formatMaterial(segment));
  addDetailRow(fragment, "Fuente label", formatSourceLabel(segment));
  addDetailRow(fragment, "Plano", `${segment.source_dxf ?? "generated"}${segment.source_sheet ? ` (${segment.source_sheet})` : ""}`);
  addDetailRow(fragment, "Capa CAD", segment.source_layer ?? "generated");
  addDetailRow(fragment, "Source tags", formatSourceTags(segment));
  addDetailRow(fragment, "Nivel", segment.level_kind ?? "FLOOR");
  addDetailRow(fragment, "Clasificacion", formatClassification(segment));
  addDetailRow(fragment, "Confianza", `${segment.confidence ?? "-"}${segment.section_confidence ? `; seccion ${segment.section_confidence}` : ""}${segment.thickness_confidence ? `; espesor ${segment.thickness_confidence}` : ""}`);
  selectionDetailsEl.replaceChildren(fragment);
  if (copyIdentificationButton) copyIdentificationButton.disabled = false;
}

function addDetailRow(fragment, key, value) {
  const dt = document.createElement("dt");
  const dd = document.createElement("dd");
  dt.textContent = key;
  dd.textContent = value ?? "-";
  if (String(value ?? "").includes("\n")) dd.style.whiteSpace = "pre-line";
  fragment.append(dt, dd);
}

function formatSection(segment) {
  const parts = [];
  if (Number.isFinite(segment.section_width_m) && Number.isFinite(segment.section_height_m)) {
    parts.push(`Seccion ${formatCm(segment.section_width_m)} x ${formatCm(segment.section_height_m)} cm`);
  } else if (segment.category === "beam" || segment.category === "support") {
    parts.push("Seccion UNKNOWN");
  }
  if (Number.isFinite(segment.section_depth_m)) parts.push(`prof=${formatCm(segment.section_depth_m)} cm`);
  if (Number.isFinite(segment.wall_thickness_m)) parts.push(`Espesor ${formatCm(segment.wall_thickness_m)} cm`);
  else if (segment.category === "wall") parts.push("Espesor UNKNOWN");
  if (Number.isFinite(segment.length_m)) parts.push(`L=${formatNumber(segment.length_m)} m`);
  if (segment.section_source) parts.push(`section_source=${segment.section_source}`);
  if (segment.section_confidence) parts.push(`section_confidence=${segment.section_confidence}`);
  if (segment.thickness_source) parts.push(`thickness_source=${segment.thickness_source}`);
  if (segment.thickness_confidence) parts.push(`thickness_confidence=${segment.thickness_confidence}`);
  return parts.length ? parts.join("; ") : "-";
}

function formatMaterial(segment) {
  if (!segment.material || segment.material === "UNKNOWN") return `UNKNOWN (${segment.material_source ?? "UNKNOWN"})`;
  return `${segment.material}; fuente=${segment.material_source ?? "-"}; confianza=${segment.material_confidence ?? "-"}`;
}

function formatSourceLabel(segment) {
  if (!segment.source_label && !segment.source_label_tag) return "-";
  return `${segment.source_label ?? "-"} | ${segment.source_label_tag ?? "-"} | d=${formatNumber(segment.source_label_distance_m)} m`;
}

function formatSourceTags(segment) {
  const tags = segment.sourceTags ?? segment.sourceTag ?? segment.legacy_solidTag ?? null;
  if (!tags) return "-";
  return Array.isArray(tags) ? tags.join(", ") : String(tags);
}

function formatClassification(segment) {
  const parts = [];
  if (segment.axis_status) parts.push(segment.axis_status);
  if (segment.position_classification) parts.push(segment.position_classification);
  if (segment.position_classification_confidence) parts.push(segment.position_classification_confidence);
  if (segment.position_classification_reason) parts.push(segment.position_classification_reason);
  return parts.length ? parts.join("; ") : "-";
}

function formatCoordinates(segment) {
  const coords = segment.coordinates ?? {};
  if (segment.category === "column") {
    return `Centro ${formatPoint(coords.center ?? segment.center)}\nZ inferior ${formatNumber(coords.z_bottom_m)} m\nZ superior ${formatNumber(coords.z_top_m)} m`;
  }
  if (segment.category === "beam" || segment.category === "support") {
    return `Nodo i ${formatPoint(coords.start ?? segment.start)}\nNodo j ${formatPoint(coords.end ?? segment.end)}\nCentro ${formatPoint(coords.center)}`;
  }
  if (segment.category === "wall") {
    return `Desde ${formatPoint(coords.start ?? segment.start)}\nHasta ${formatPoint(coords.end ?? segment.end)}\nCentro ${formatPoint(coords.center)}\nZ inferior ${formatNumber(coords.z_bottom_m)} m\nZ superior ${formatNumber(coords.z_top_m)} m`;
  }
  if (coords.center) return `Centro ${formatPoint(coords.center)}`;
  const points = segment.points ?? [];
  return points.length ? points.map((point, index) => `P${index + 1} ${formatPoint(point)}`).join("\n") : "-";
}

function formatAxes(segment) {
  const axes = segment.axis_location ?? segment.axes ?? segment.ejes_aproximados;
  if (!axes) return "-";
  if (typeof axes === "string") return axes;
  if (Array.isArray(axes)) return axes.join(", ");
  if (axes.center?.X && axes.center?.Y) {
    const rows = [`Centro: X ${formatAxisRelation(axes.center.X)} / Y ${formatAxisRelation(axes.center.Y)}`];
    if (axes.start?.X && axes.start?.Y) rows.push(`Inicio: X ${formatAxisRelation(axes.start.X)} / Y ${formatAxisRelation(axes.start.Y)}`);
    if (axes.end?.X && axes.end?.Y) rows.push(`Fin: X ${formatAxisRelation(axes.end.X)} / Y ${formatAxisRelation(axes.end.Y)}`);
    return rows.join("\n");
  }
  return Object.entries(axes).map(([key, value]) => `${key}: ${JSON.stringify(value)}`).join("; ");
}

function formatAxisRelation(axis) {
  const base = axis.relation ?? axis.axis ?? "-";
  if (Number.isFinite(axis.offset_m) && Math.abs(axis.offset_m) > 0.001) return `${base} (offset ${axis.offset_m >= 0 ? "+" : ""}${formatNumber(axis.offset_m)} m desde ${axis.axis})`;
  return base;
}

function formatNumber(value) {
  return Number.isFinite(value) ? value.toFixed(3) : "-";
}

function formatCm(value) {
  return Number.isFinite(value) ? Math.round(value * 100).toString() : "-";
}

function formatPoint(point) {
  if (!point || point.some((value) => value === null || value === undefined)) return "-";
  return `(${point.map((value) => formatNumber(value)).join(", ")})`;
}

function compactAxisId(segment) {
  const center = segment.axis_location?.center;
  if (!center?.X || !center?.Y) return "ejes -";
  if (center.X.status === "ON_AXIS" && center.Y.status === "ON_AXIS") return `${center.X.axis}-${center.Y.axis}`;
  return `X ${center.X.relation ?? center.X.axis} / Y ${center.Y.relation ?? center.Y.axis}`;
}

function compactCoordinates(segment) {
  const center = segment.coordinates?.center ?? segment.center;
  if (!center) return "X=- Y=-";
  return `X=${formatNumber(center[0])} Y=${formatNumber(center[1])}${Number.isFinite(center[2]) ? ` Z=${formatNumber(center[2])}` : ""}`;
}

function identificationText(segment) {
  return [
    primaryElementId(segment),
    CATEGORY_LABELS[segment.category] ?? segment.category,
    compactAxisId(segment),
    compactCoordinates(segment),
    segment.floor ?? "-",
    legacyElementTag(segment),
  ].join(" | ");
}

async function copySelectedIdentification() {
  if (!selectedSegment) return;
  const text = identificationText(selectedSegment);
  try {
    await navigator.clipboard.writeText(text);
    statusEl.textContent = `Copiado: ${text}`;
    copyIdentificationButton?.classList.add("copy-flash");
    window.setTimeout(() => copyIdentificationButton?.classList.remove("copy-flash"), 700);
  } catch (_error) {
    window.prompt("Copia la identificacion:", text);
  }
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
  pointerDown = { x: event.clientX, y: event.clientY, time: performance.now() };
}

function onPointerUp(event) {
  if (!pointerDown) return;
  const moved = Math.hypot(event.clientX - pointerDown.x, event.clientY - pointerDown.y);
  const elapsed = performance.now() - pointerDown.time;
  pointerDown = null;
  if (moved > 4 || elapsed > 650) return;

  const rect = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(selectable.filter((object) => object.visible), false);
  const hit = chooseSelectionHit(hits);
  if (hit) selectObject(hit.object);
  else clearSelection();
}

function chooseSelectionHit(hits) {
  if (!hits.length) return null;
  const priority = { column: 0, beam: 1, wall: 2, support: 3, diaphragm: 4, slab: 5 };
  return [...hits].sort((a, b) => {
    const pa = priority[a.object.userData.category] ?? 9;
    const pb = priority[b.object.userData.category] ?? 9;
    return pa === pb ? a.distance - b.distance : pa - pb;
  })[0];
}

function searchTag() {
  const query = tagSearchEl.value.trim().toLowerCase();
  if (!query) return;
  const exact = objectByTag.get(query);
  const match = exact ?? [...objectByTag.entries()].find(([tag]) => tag.includes(query))?.[1];
  if (!match) {
    statusEl.textContent = `No encontre ID/elementTag que contenga: ${query}`;
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
  if (modelSelectEl) {
    modelSelectEl.value = modelFile;
    modelSelectEl.addEventListener("change", () => {
      const next = modelSelectEl.value;
      window.location.href = `?model=${encodeURIComponent(next)}`;
    });
  }
  addLights();
  resize();
  window.addEventListener("resize", resize);
  renderer.domElement.addEventListener("pointerdown", onPointerDown);
  renderer.domElement.addEventListener("pointerup", onPointerUp);
  document.querySelector("#view-side-A").addEventListener("click", sideView.bind(null, "A"));
  document.querySelector("#view-side-B").addEventListener("click", sideView.bind(null, "B"));
  document.querySelector("#view-side-C").addEventListener("click", sideView.bind(null, "C"));
  document.querySelector("#view-side-D").addEventListener("click", sideView.bind(null, "D"));
  document.querySelector("#top-view").addEventListener("click", topView);
  document.querySelector("#search-button").addEventListener("click", searchTag);
  copyIdentificationButton?.addEventListener("click", copySelectedIdentification);
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
