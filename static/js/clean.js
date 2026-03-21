/* ── CLEAN.JS ─────────────────────────────────────
   All clean tab operations, sidebar, reorder panel
──────────────────────────────────────────────── */

// ── STATE ────────────────────────────────────────
let selectedCol  = null;
let selectedType = null;

// Column type map — built from COLUMNS passed by Flask
const colTypeMap = {};
COLUMNS.forEach(col => { colTypeMap[col.name] = col.type; });

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

// ── API CALL HELPER ──────────────────────────────
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
function buildSidebar(columns) {
  const list  = document.getElementById('colList');
  const count = document.getElementById('colCount');
  count.textContent = columns.length;
  list.innerHTML = '';

  columns.forEach(col => {
    const item = document.createElement('div');
    item.className = 'col-item';
    item.dataset.col  = col.name;
    item.dataset.type = col.type;
    item.innerHTML = `
      <span class="col-dot ${col.type}"></span>
      <span>${col.name}</span>
    `;
    item.addEventListener('click', () => selectColumn(col.name, col.type, item));
    list.appendChild(item);
  });

  buildReorderList(columns.map(c => c.name));
}

// Search filter
document.getElementById('colSearch').addEventListener('input', (e) => {
  const q = e.target.value.toLowerCase();
  document.querySelectorAll('.col-item').forEach(item => {
    item.style.display = item.dataset.col.toLowerCase().includes(q) ? '' : 'none';
  });
});

document.querySelector('.btn-reset').addEventListener('click', (e) => {
  if (!confirm('Reset will restore the original file and undo ALL operations. Are you sure?')) {
    e.preventDefault();
  }
});
// ── SELECT COLUMN ────────────────────────────────
function selectColumn(name, type, el) {
  selectedCol  = name;
  selectedType = type;

  document.querySelectorAll('.col-item').forEach(i => i.classList.remove('active'));
  el.classList.add('active');

  document.getElementById('emptyState').style.display = 'none';
  document.getElementById('opsPanel').style.display   = 'flex';
  const ops = document.getElementById('opsPanel');
  ops.style.display = 'flex';
  ops.style.animation = 'none';
  ops.offsetHeight; // force reflow
  ops.style.animation = '';
  const badge = document.getElementById('selectedColType');
  document.getElementById('selectedColName').textContent = name;
  badge.textContent = type;
  badge.className   = `col-type-badge ${type}`;

  document.getElementById('toast').className = 'toast';
  
  selectedCol  = name;
  selectedType = type;
  localStorage.setItem('pilotdf-clean-col', name);  // ← add this line
  document.querySelector('.main-panel').scrollTop = 0;
  // rest of your existing code...

}

// ── CHECK URL PARAM (from right-click in view tab) ──
function checkUrlParam() {
  const params = new URLSearchParams(window.location.search);
  const col    = params.get('col') || localStorage.getItem('pilotdf-clean-col');
  if (col) {
    const item = document.querySelector(`.col-item[data-col="${col}"]`);
    if (item) item.click();
  }
}

// ── FILL NULLS ───────────────────────────────────
document.getElementById('fillMethod').addEventListener('change', (e) => {
  document.getElementById('customValRow').style.display =
    e.target.value === 'custom' ? 'flex' : 'none';
});

document.getElementById('applyFillNull').addEventListener('click', async () => {
  if (!selectedCol) return;
  const method     = document.getElementById('fillMethod').value;
  const custom_val = document.getElementById('customVal').value;
  const data = await callAPI('/clean-clean_null', makeForm({ column: selectedCol, method, custom_val }));
  data.success ? showToast('Nulls filled successfully') : showToast(data.error, 'error');
});

// ── DROP ROWS ────────────────────────────────────
document.getElementById('applyDropRows').addEventListener('click', async () => {
  if (!selectedCol) return;
  const scope  = document.getElementById('dropScope').value;
  const column = scope === 'column' ? selectedCol : '';
  const data   = await callAPI('/clean-drop_rows', makeForm({ scope, column }));
  data.success ? showToast('Rows dropped successfully') : showToast(data.error, 'error');
});

// ── RENAME COLUMN ────────────────────────────────
document.getElementById('applyRename').addEventListener('click', async () => {
  if (!selectedCol) return;
  const new_name = document.getElementById('newColName').value.trim();
  if (!new_name) return showToast('Please enter a new name', 'error');
  const data = await callAPI('/clean-rename_column', makeForm({ column: selectedCol, new_name }));
  if (data.success) {
    showToast('Column renamed successfully');
    // update sidebar
    const item = document.querySelector(`.col-item[data-col="${selectedCol}"]`);
    if (item) { item.dataset.col = new_name; item.querySelector('span:last-child').textContent = new_name; }
    selectedCol = new_name;
    document.getElementById('selectedColName').textContent = new_name;
    document.getElementById('newColName').value = '';
  } else {
    showToast(data.error, 'error');
  }
});

// ── CHANGE DTYPE ─────────────────────────────────
document.getElementById('applyDtype').addEventListener('click', async () => {
  if (!selectedCol) return;
  const type_ = document.getElementById('newDtype').value;
  const data  = await callAPI('/clean-change_dtype', makeForm({ column: selectedCol, type_ }));
  data.success ? showToast('Data type changed successfully') : showToast(data.error, 'error');
});

// ── FIND & REPLACE ───────────────────────────────
document.getElementById('applyReplace').addEventListener('click', async () => {
  if (!selectedCol) return;
  const find_val    = document.getElementById('findVal').value;
  const replace_val = document.getElementById('replaceVal').value;
  const exact_match = document.getElementById('exactMatch').value;
  if (!find_val) return showToast('Please enter a value to find', 'error');
  const data = await callAPI('/clean-replace_val', makeForm({ column: selectedCol, find_val, replace_val, exact_match }));
  data.success ? showToast('Values replaced successfully') : showToast(data.error, 'error');
});

// ── TRIM WHITESPACE ──────────────────────────────
document.getElementById('applyTrim').addEventListener('click', async () => {
  if (!selectedCol) return;
  const data = await callAPI('/clean-trim_space', makeForm({ column: selectedCol }));
  data.success ? showToast('Whitespace trimmed successfully') : showToast(data.error, 'error');
});

// ── CHANGE CASE ──────────────────────────────────
document.getElementById('applyCase').addEventListener('click', async () => {
  if (!selectedCol) return;
  const case_ = document.getElementById('caseType').value;
  const data  = await callAPI('/clean-change_case', makeForm({ column: selectedCol, case: case_ }));
  data.success ? showToast('Case changed successfully') : showToast(data.error, 'error');
});

// ── DROP COLUMN ──────────────────────────────────
document.getElementById('applyDropCol').addEventListener('click', async () => {
  if (!selectedCol) return;
  if (!confirm(`Drop column "${selectedCol}"? This cannot be undone easily.`)) return;
  const data = await callAPI('/clean-drop_column', makeForm({ column: selectedCol }));
  if (data.success) {
    showToast('Column dropped successfully');
    const item = document.querySelector(`.col-item[data-col="${selectedCol}"]`);
    if (item) item.remove();
    selectedCol = null;
    document.getElementById('emptyState').style.display = 'flex';
    document.getElementById('opsPanel').style.display   = 'none';
  } else {
    showToast(data.error, 'error');
  }
});

// ── REMOVE DUPLICATES MODAL ──────────────────────
document.getElementById('removeDupBtn').addEventListener('click', () => {
  document.getElementById('dupModal').style.display = 'flex';
});
document.getElementById('cancelDup').addEventListener('click', () => {
  document.getElementById('dupModal').style.display = 'none';
});
document.getElementById('confirmDup').addEventListener('click', async () => {
  const keep = document.getElementById('dupKeep').value;
  const data = await callAPI('/clean-remove_duplicates', makeForm({ keep }));
  document.getElementById('dupModal').style.display = 'none';
  data.success ? showToast('Duplicates removed successfully') : showToast(data.error, 'error');
});

// ── DROP ALL NULL ROWS ───────────────────────────
document.getElementById('dropAllNullBtn').addEventListener('click', async () => {
  if (!confirm('Drop all rows with at least one null value?')) return;
  const data = await callAPI('/clean-drop_rows', makeForm({ scope: 'any', column: '' }));
  data.success ? showToast('Null rows dropped successfully') : showToast(data.error, 'error');
});

// ── UNDO ─────────────────────────────────────────
document.getElementById('undoBtn').addEventListener('click', async () => {
  const res  = await fetch('/clean-undo', {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  });
  const data = await res.json();
  data.success ? showToast('Last operation undone') : showToast(data.error || 'Nothing to undo', 'error');
  if (data.success) {
    showToast('Last operation undone');
    localStorage.removeItem('pilotdf-clean-col');  // clear so it doesn't try to restore
    setTimeout(() => window.location.reload(), 800);
}

});

// ── REORDER PANEL ────────────────────────────────
function buildReorderList(columns) {
  const list = document.getElementById('reorderList');
  list.innerHTML = '';
  columns.forEach(col => {
    const item = document.createElement('div');
    item.className   = 'reorder-item';
    item.draggable   = true;
    item.dataset.col = col;
    item.innerHTML   = `<span class="drag-handle">⠿</span><span>${col}</span>`;
    list.appendChild(item);
  });
  initDragDrop();
}

function initDragDrop() {
  const list  = document.getElementById('reorderList');
  let dragEl  = null;

  list.querySelectorAll('.reorder-item').forEach(item => {
    item.addEventListener('dragstart', () => { dragEl = item; item.classList.add('dragging'); });
    item.addEventListener('dragend',   () => { dragEl = null; item.classList.remove('dragging'); });
    item.addEventListener('dragover',  (e) => {
      e.preventDefault();
      if (dragEl && dragEl !== item) {
        list.querySelectorAll('.reorder-item').forEach(i => i.classList.remove('drag-over'));
        item.classList.add('drag-over');
        const rect = item.getBoundingClientRect();
        const mid  = rect.top + rect.height / 2;
        if (e.clientY < mid) list.insertBefore(dragEl, item);
        else list.insertBefore(dragEl, item.nextSibling);
      }
    });
    item.addEventListener('dragleave', () => item.classList.remove('drag-over'));
    item.addEventListener('drop', (e) => { e.preventDefault(); item.classList.remove('drag-over'); });
  });
}

document.getElementById('applyReorder').addEventListener('click', async () => {
  const items     = document.querySelectorAll('.reorder-item');
  const new_order = Array.from(items).map(i => i.dataset.col);
  const fd        = new FormData();
  new_order.forEach(col => fd.append('new_order', col));
  const res  = await fetch('/clean-reorder_columns', {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    body: fd
  });
  const data = await res.json();
  data.success ? showToast('Columns reordered successfully') : showToast(data.error, 'error');
});

// ── INIT ─────────────────────────────────────────
initTheme();
buildSidebar(COLUMNS);
checkUrlParam();