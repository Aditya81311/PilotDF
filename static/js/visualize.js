/* ── VISUALIZE.JS — HTML mode ─────────────────────── */

let currentChartType = 'bar';
let charts           = [];
let chartCounter     = 0;
let dragSrcId        = null;

// ── DARK MODE ────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem('pilotdf-theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  document.getElementById('themeIcon').textContent = saved === 'dark' ? '☀️' : '🌙';
}
document.getElementById('themeToggle').addEventListener('click', () => {
  const current = document.documentElement.getAttribute('data-theme');
  const next    = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('pilotdf-theme', next);
  document.getElementById('themeIcon').textContent = next === 'dark' ? '☀️' : '🌙';
});

// ── RESET CONFIRM ────────────────────────────────
document.getElementById('resetBtn').addEventListener('click', (e) => {
  if (!confirm('Reset will restore the original file and undo ALL operations. Are you sure?')) e.preventDefault();
});

// ── POPULATE COLUMNS ─────────────────────────────
function populateColumns() {
  ['xAxis', 'yAxis', 'colorBy'].forEach(id => {
    const sel = document.getElementById(id);
    const def = id === 'colorBy' ? '— None —' : '— Select column —';
    sel.innerHTML = `<option value="">${def}</option>`;
    COLUMNS.forEach(col => {
      const o       = document.createElement('option');
      o.value       = col.name;
      o.textContent = `${col.name} (${col.type})`;
      sel.appendChild(o);
    });
  });
}

// ── CHART TYPE SELECTOR ──────────────────────────
document.getElementById('chartTypeGrid').addEventListener('click', (e) => {
  const btn = e.target.closest('.chart-type-btn');
  if (!btn) return;
  document.querySelectorAll('.chart-type-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentChartType = btn.dataset.type;
  updateControlsForType(currentChartType);
});

function updateControlsForType(type) {
  document.getElementById('yAxisGroup').style.display       = type === 'histogram' ? 'none' : 'flex';
  document.getElementById('binsGroup').style.display        = type === 'histogram' ? 'flex' : 'none';
  document.getElementById('colorByGroup').style.display     = ['pie','box'].includes(type) ? 'none' : 'flex';
  document.getElementById('orientationGroup').style.display = type === 'bar' ? 'flex' : 'none';
  document.getElementById('xLabel').textContent             = type === 'pie' ? 'Labels Column' : 'X Axis';
  document.getElementById('yLabel').textContent             = type === 'pie' ? 'Values Column' : 'Y Axis';
}

// ── ERROR ────────────────────────────────────────
function showError(msg) {
  const el         = document.getElementById('controlsError');
  el.textContent   = msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 4000);
}

// ── VALIDATE ─────────────────────────────────────
function validate() {
  const x    = document.getElementById('xAxis').value;
  const y    = document.getElementById('yAxis').value;
  const type = currentChartType;
  if (!x) { showError('Please select X axis / Labels column'); return false; }
  if (type !== 'histogram' && !y) { showError('Please select Y axis / Values column'); return false; }
  return true;
}

// ── GENERATE ─────────────────────────────────────
document.getElementById('generateBtn').addEventListener('click', async () => {
  if (!validate()) return;

  const btn       = document.getElementById('generateBtn');
  btn.disabled    = true;
  btn.textContent = 'Generating...';

  const fd = new FormData();
  fd.append('chart_type',  currentChartType);
  fd.append('x',           document.getElementById('xAxis').value);
  fd.append('y',           document.getElementById('yAxis').value);
  fd.append('title',       document.getElementById('chartTitle').value);
  fd.append('color_by',    document.getElementById('colorBy').value);
  fd.append('bins',        document.getElementById('bins').value);
  fd.append('orientation', document.getElementById('orientation').value);

  try {
    const res = await fetch('/visualize-generate', {
      method:  'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body:    fd
    });

    const data = await res.json();

    if (data.success && data.chart) {
      const title = document.getElementById('chartTitle').value || `Chart ${chartCounter + 1}`;
      addChartToGrid(data.chart, title);
    } else {
      showError(data.error || 'Failed to generate chart');
    }
  } catch (err) {
    showError('Request failed: ' + err.message);
  }

  btn.disabled    = false;
  btn.textContent = '+ Add Chart';
});

// ── ADD CHART TO GRID ────────────────────────────
function addChartToGrid(chartHtml, title) {
  chartCounter++;
  const id = `chart-${chartCounter}`;
  charts.push({ id, title, chartHtml });

  document.getElementById('emptyState').style.display     = 'none';
  document.getElementById('downloadAllBtn').style.display = 'inline-block';
  document.getElementById('clearAllBtn').style.display    = 'inline-block';
  updateCanvasInfo();

  const card       = document.createElement('div');
  card.className   = 'chart-card';
  card.id          = id;
  card.draggable   = true;
  card.innerHTML   = `
    <div class="chart-card-header">
      <span class="chart-card-title">${title}</span>
      <div class="chart-card-actions">
        <button class="chart-card-btn remove" onclick="removeChart('${id}')">✕ Remove</button>
      </div>
    </div>
    <div class="chart-card-body" id="body-${id}"></div>
  `;

  // drag events
  card.addEventListener('dragstart', () => { dragSrcId = id; card.classList.add('dragging'); });
  card.addEventListener('dragend',   () => { card.classList.remove('dragging'); document.querySelectorAll('.chart-card').forEach(c => c.classList.remove('drag-over')); });
  card.addEventListener('dragover',  (e) => { e.preventDefault(); if (dragSrcId !== id) card.classList.add('drag-over'); });
  card.addEventListener('dragleave', () => card.classList.remove('drag-over'));
  card.addEventListener('drop',      (e) => { e.preventDefault(); card.classList.remove('drag-over'); swapCharts(dragSrcId, id); });

  document.getElementById('chartsGrid').appendChild(card);

  // inject HTML into body div
  const body = document.getElementById(`body-${id}`);
  body.innerHTML = chartHtml;

  // execute any scripts inside the injected HTML
  body.querySelectorAll('script').forEach(oldScript => {
    const newScript = document.createElement('script');
    newScript.textContent = oldScript.textContent;
    oldScript.parentNode.replaceChild(newScript, oldScript);
  });
}

// ── SWAP CHARTS ──────────────────────────────────
function swapCharts(aId, bId) {
  const grid  = document.getElementById('chartsGrid');
  const a     = document.getElementById(aId);
  const b     = document.getElementById(bId);
  if (!a || !b) return;
  const aNext = a.nextSibling;
  if (aNext === b) { grid.insertBefore(b, a); }
  else { const bNext = b.nextSibling; grid.insertBefore(a, b); grid.insertBefore(b, aNext); }
}

// ── REMOVE CHART ─────────────────────────────────
function removeChart(id) {
  const card = document.getElementById(id);
  if (card) card.remove();
  charts = charts.filter(c => c.id !== id);
  updateCanvasInfo();
  if (charts.length === 0) {
    document.getElementById('emptyState').style.display     = 'flex';
    document.getElementById('downloadAllBtn').style.display = 'none';
    document.getElementById('clearAllBtn').style.display    = 'none';
  }
}

// ── DOWNLOAD ALL (screenshot via html2canvas) ────
document.getElementById('downloadAllBtn').addEventListener('click', async () => {
  if (charts.length === 0) return;
  const grid = document.getElementById('chartsGrid');
  // use browser print as fallback
  window.print();
});

// ── CLEAR ALL ────────────────────────────────────
document.getElementById('clearAllBtn').addEventListener('click', () => {
  if (!confirm('Remove all charts?')) return;
  document.getElementById('chartsGrid').innerHTML = '';
  charts       = [];
  chartCounter = 0;
  document.getElementById('emptyState').style.display     = 'flex';
  document.getElementById('downloadAllBtn').style.display = 'none';
  document.getElementById('clearAllBtn').style.display    = 'none';
  updateCanvasInfo();
});

// ── CANVAS INFO ──────────────────────────────────
function updateCanvasInfo() {
  const n = charts.length;
  document.getElementById('canvasInfo').textContent = n === 0 ? 'No charts yet' : `${n} chart${n > 1 ? 's' : ''}`;
}

// ── URL PARAM ────────────────────────────────────
function checkUrlParam() {
  const col = new URLSearchParams(window.location.search).get('col');
  if (col) document.getElementById('xAxis').value = col;
}

// ── INIT ─────────────────────────────────────────
initTheme();
populateColumns();
updateControlsForType('bar');
checkUrlParam();