/* ── TRANSFORM.JS ────────────────────────────────── */

let selectedCol  = null;
let selectedType = null;

// ── DARK MODE ────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('pilotdf-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  document.getElementById('themeIcon').textContent = saved === 'dark' ? '☀️' : '🌙';
}
document.getElementById('themeToggle').addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme');
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('pilotdf-theme', next);
  document.getElementById('themeIcon').textContent = next === 'dark' ? '☀️' : '🌙';
});

// ── TOAST ────────────────────────────────────────
function showToast(msg, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.className = `toast ${type}`;
  setTimeout(() => { toast.className = 'toast'; }, 3000);
}

// ── API HELPER ───────────────────────────────────
async function callAPI(url, formData) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    body: formData
  });
  return await res.json();
}

function makeForm(obj) {
  const fd = new FormData();
  Object.entries(obj).forEach(([k, v]) => fd.append(k, v));
  return fd;
}

// ── SIDEBAR ──────────────────────────────────────
function getTypeClass(type) {
  if (type.includes('int'))      return 'int';
  if (type.includes('float'))    return 'float';
  if (type.includes('datetime')) return 'datetime';
  return 'object';
}

function buildSidebar(columns) {
  const list  = document.getElementById('colList');
  const count = document.getElementById('colCount');
  count.textContent = columns.length;
  list.innerHTML = '';
  columns.forEach(col => {
    const tc   = getTypeClass(col.type);
    const item = document.createElement('div');
    item.className    = 'col-item';
    item.dataset.col  = col.name;
    item.dataset.type = col.type;
    item.innerHTML    = `<span class="col-dot ${tc}"></span><span>${col.name}</span>`;
    item.addEventListener('click', () => selectColumn(col.name, col.type, item));
    list.appendChild(item);
  });
}

document.getElementById('colSearch').addEventListener('input', (e) => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll('.col-item').forEach(item => {
    item.style.display = item.dataset.col.toLowerCase().includes(q) ? '' : 'none';
  });
});

// ── SELECT COLUMN ────────────────────────────────
function selectColumn(name, type, el) {
  selectedCol  = name;
  selectedType = type;
  localStorage.setItem('pilotdf-transform-col', name);

  document.querySelectorAll('.col-item').forEach(i => i.classList.remove('active'));
  el.classList.add('active');

  document.getElementById('emptyState').style.display = 'none';
  const ops = document.getElementById('opsPanel');
  ops.style.display = 'flex';
  ops.style.animation = 'none';
  ops.offsetHeight;
  ops.style.animation = '';

  const tc    = getTypeClass(type);
  const badge = document.getElementById('selectedColType');
  document.getElementById('selectedColName').textContent = name;
  badge.textContent = type;
  badge.className   = `col-type-badge ${tc}`;

  document.getElementById('toast').className = 'toast';
  document.querySelector('.main-panel').scrollTop = 0;
  updateOpsForType(tc);
}

// ── FILTER OPS BY TYPE ───────────────────────────
function updateOpsForType(tc) {
  const isNumeric  = tc === 'int' || tc === 'float';
  const isString   = tc === 'object';
  const isDatetime = tc === 'datetime';

  // normalize — numeric only
  document.getElementById('opNormalize').classList.toggle('disabled-card', !isNumeric);
  // encode — string only
  document.getElementById('opEncode').classList.toggle('disabled-card', !isString);
  // bin — numeric only
  document.getElementById('opBin').classList.toggle('disabled-card', !isNumeric);
  // datetime — datetime only
  document.getElementById('opDatetime').classList.toggle('disabled-card', !isDatetime);
  // math — numeric only
  document.getElementById('opMath').classList.toggle('disabled-card', !isNumeric);
  // new column — always available
  document.getElementById('opNewCol').classList.remove('disabled-card');
}

// ── CHECK URL / LOCALSTORAGE ─────────────────────
function checkUrlParam() {
  const params = new URLSearchParams(window.location.search);
  const col    = params.get('col') || localStorage.getItem('pilotdf-transform-col');
  if (col) {
    const item = document.querySelector(`.col-item[data-col="${col}"]`);
    if (item) item.click();
  }
}

// ── ENCODE — show/hide drop first ────────────────
document.getElementById('encodeMethod').addEventListener('change', (e) => {
  document.getElementById('dropFirstRow').style.display =
    e.target.value === 'onehot' ? 'flex' : 'none';
});
document.getElementById('dropFirstRow').style.display = 'none';

// ── NEW COLUMN ───────────────────────────────────
async function applyNewColumn() {
  const name    = document.getElementById('newColName').value.trim();
  const formula = document.getElementById('newColFormula').value.trim();
  if (!name)    return showToast('Please enter a column name', 'error');
  if (!formula) return showToast('Please enter a formula', 'error');
  const existingCols = Array.from(document.querySelectorAll('.col-item')).map(i => i.dataset.col);
  if (existingCols.includes(name)) return showToast(`Column "${name}" already exists`, 'error');
  const btn = document.getElementById('applyNewCol');
  btn.disabled = true;
  const data = await callAPI('/transform-new_column', makeForm({ name, formula }));
  btn.disabled = false;
  if (data.success) {
    showToast(`Column "${name}" created successfully`);
    document.getElementById('newColName').value    = '';
    document.getElementById('newColFormula').value = '';
    COLUMNS.push({ name, type: 'float64' });
    buildSidebar(COLUMNS);
  } else { showToast(data.error || 'Failed to create column', 'error'); }
}
document.getElementById('applyNewCol').addEventListener('click', applyNewColumn);
document.getElementById('newColGlobalBtn').addEventListener('click', () => {
  document.getElementById('emptyState').style.display = 'none';
  const ops = document.getElementById('opsPanel');
  ops.style.display = 'flex';
  document.querySelector('.main-panel').scrollTop = 0;
  updateOpsForType('global');
});

// ── NORMALIZE ────────────────────────────────────
document.getElementById('applyNormalize').addEventListener('click', async () => {
  if (!selectedCol) return;
  const method = document.getElementById('normalizeMethod').value;
  const btn    = document.getElementById('applyNormalize');
  btn.disabled = true;
  const data   = await callAPI('/transform-normalize', makeForm({ column: selectedCol, method }));
  btn.disabled = false;
  data.success ? showToast('Column normalized successfully') : showToast(data.error, 'error');
});

// ── ENCODE ───────────────────────────────────────
document.getElementById('applyEncode').addEventListener('click', async () => {
  if (!selectedCol) return;
  const method     = document.getElementById('encodeMethod').value;
  const drop_first = document.getElementById('dropFirst').value;
  const btn        = document.getElementById('applyEncode');
  btn.disabled     = true;
  const data       = await callAPI('/transform-encode', makeForm({ column: selectedCol, method, drop_first }));
  btn.disabled     = false;
  if (data.success) {
    showToast('Column encoded successfully');
    if (method === 'onehot') {
      // reload page to reflect new columns from one-hot
      setTimeout(() => window.location.reload(), 800);
    }
  } else { showToast(data.error, 'error'); }
});

// ── BIN ──────────────────────────────────────────
document.getElementById('applyBin').addEventListener('click', async () => {
  if (!selectedCol) return;
  const bins   = document.getElementById('binCount').value;
  const labels = document.getElementById('binLabels').value.trim();
  if (!bins || bins < 2) return showToast('Please enter at least 2 bins', 'error');
  if (labels) {
    const labelList = labels.split(',');
    if (labelList.length !== parseInt(bins)) return showToast(`Labels count (${labelList.length}) must match bins (${bins})`, 'error');
  }
  const btn    = document.getElementById('applyBin');
  btn.disabled = true;
  const data   = await callAPI('/transform-bin', makeForm({ column: selectedCol, bins, labels }));
  btn.disabled = false;
  if (data.success) {
    showToast('Column binned successfully');
    document.getElementById('binCount').value  = '';
    document.getElementById('binLabels').value = '';
  } else { showToast(data.error, 'error'); }
});

// ── EXTRACT DATETIME ─────────────────────────────
document.getElementById('applyExtract').addEventListener('click', async () => {
  if (!selectedCol) return;
  const extract = document.getElementById('extractType').value;
  const btn     = document.getElementById('applyExtract');
  btn.disabled  = true;
  const data    = await callAPI('/transform-extract', makeForm({ column: selectedCol, extract }));
  btn.disabled  = false;
  if (data.success) {
    showToast(`Extracted "${selectedCol}_${extract}" column`);
    COLUMNS.push({ name: `${selectedCol}_${extract}`, type: 'int64' });
    buildSidebar(COLUMNS);
  } else { showToast(data.error, 'error'); }
});

// ── APPLY MATH ───────────────────────────────────
document.getElementById('applyMath').addEventListener('click', async () => {
  if (!selectedCol) return;
  const operation = document.getElementById('mathOp').value;
  if (['log', 'sqrt'].includes(operation)) {
    if (!confirm(`${operation === 'log' ? 'Log' : 'Sqrt'} will fail on negative or zero values. Proceed?`)) return;
  }
  const btn     = document.getElementById('applyMath');
  btn.disabled  = true;
  const data    = await callAPI('/transform-maths', makeForm({ column: selectedCol, operation }));
  btn.disabled  = false;
  data.success ? showToast(`${operation} applied successfully`) : showToast(data.error, 'error');
});

// ── UNDO ─────────────────────────────────────────
document.getElementById('undoBtn').addEventListener('click', async () => {
  const btn    = document.getElementById('undoBtn');
  btn.disabled = true;
  const res    = await fetch('/transform-undo', {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  });
  const data = await res.json();
  if (data.success) {
    showToast('Last operation undone');
    // localStorage.removeItem('pilotdf-transform-col');
    setTimeout(() => window.location.reload(), 800);
  } else {
    btn.disabled = false;
    showToast(data.error || 'Nothing to undo', 'error');
  }
});

// ── RESET CONFIRM ────────────────────────────────
document.getElementById('resetBtn').addEventListener('click', (e) => {
  if (!confirm('Reset will restore the original file and undo ALL operations. Are you sure?')) {
    e.preventDefault();
  }
});

// ── INIT ─────────────────────────────────────────
initTheme();
buildSidebar(COLUMNS);
checkUrlParam();