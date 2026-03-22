/* ── VISUALIZE.JS — Fixed & Robust ─────────────────── */

let currentChartType = 'bar';
let charts           = [];
let chartCounter     = 0;
let dragSrcId        = null;
let plotlyLoaded     = false;

// ── COLUMN TYPE HELPERS ──────────────────────────
function getTypeClass(type) {
  if (!type) return 'object';
  const t = type.toLowerCase();
  if (t.includes('int'))      return 'int';
  if (t.includes('float'))    return 'float';
  if (t.includes('datetime')) return 'datetime';
  return 'object';
}

function isNumeric(colName) {
  const col = COLUMNS.find(c => c.name === colName);
  if (!col) return false;
  const t = getTypeClass(col.type);
  return t === 'int' || t === 'float';
}

function isCategorical(colName) {
  return !isNumeric(colName);
}

// ── CHART TYPE COMPATIBILITY ─────────────────────
const CHART_RULES = {
  bar:       { x: 'any',         y: 'numeric' },
  line:      { x: 'any',         y: 'numeric' },
  scatter:   { x: 'numeric',     y: 'numeric' },
  histogram: { x: 'numeric',     y: null      },
  pie:       { x: 'categorical', y: 'numeric' },
  box:       { x: 'any',         y: 'numeric' },
};

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

// ── ERROR MANAGER ────────────────────────────────
let errorTimer = null;
function showError(msg) {
  const el         = document.getElementById('controlsError');
  el.textContent   = msg;
  el.style.display = 'block';
  if (errorTimer) clearTimeout(errorTimer);
  errorTimer = setTimeout(() => { el.style.display = 'none'; }, 5000);
}
function hideError() {
  const el = document.getElementById('controlsError');
  el.style.display = 'none';
  if (errorTimer) { clearTimeout(errorTimer); errorTimer = null; }
}

// ── POPULATE COLUMNS ─────────────────────────────
function populateColumns() {
  if (!COLUMNS || !Array.isArray(COLUMNS) || COLUMNS.length === 0) {
    showError('No columns found. Please upload a file first.');
    return;
  }
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
  hideError();
});

function updateControlsForType(type) {
  document.getElementById('yAxisGroup').style.display       = type === 'histogram' ? 'none' : 'flex';
  document.getElementById('binsGroup').style.display        = type === 'histogram' ? 'flex' : 'none';
  document.getElementById('colorByGroup').style.display     = ['pie','box'].includes(type) ? 'none' : 'flex';
  document.getElementById('orientationGroup').style.display = type === 'bar' ? 'flex' : 'none';
  document.getElementById('xLabel').textContent             = type === 'pie' ? 'Labels Column' : 'X Axis';
  document.getElementById('yLabel').textContent             = type === 'pie' ? 'Values Column' : 'Y Axis';
}

// ── VALIDATE ─────────────────────────────────────
function validate() {
  const x    = document.getElementById('xAxis').value;
  const y    = document.getElementById('yAxis').value;
  const type = currentChartType;
  const bins = parseInt(document.getElementById('bins').value);
  const rule = CHART_RULES[type];

  if (!x) { showError('Please select X axis / Labels column'); return false; }

  if (type !== 'histogram' && !y) { showError('Please select Y axis / Values column'); return false; }

  if (x && y && x === y) { showError('X and Y axis cannot be the same column'); return false; }

  // type compatibility checks
  if (rule.x === 'numeric' && !isNumeric(x)) {
    showError(`${type} chart requires a numeric X axis column`); return false;
  }
  if (rule.x === 'categorical' && !isCategorical(x)) {
    showError(`${type} chart requires a categorical X axis column`); return false;
  }
  if (y && rule.y === 'numeric' && !isNumeric(y)) {
    showError(`${type} chart requires a numeric Y axis column`); return false;
  }
  if (type === 'histogram' && !isNumeric(x)) {
    showError('Histogram requires a numeric column'); return false;
  }
  if (type === 'histogram' && (isNaN(bins) || bins < 2)) {
    showError('Bins must be a number greater than 1'); return false;
  }

  return true;
}

// ── ENSURE PLOTLY LOADED ─────────────────────────
function ensurePlotlyLoaded() {
  return new Promise((resolve, reject) => {
    if (typeof Plotly !== 'undefined') { resolve(); return; }
    const script   = document.createElement('script');
    script.src     = 'https://cdnjs.cloudflare.com/ajax/libs/plotly.js/2.27.0/plotly.min.js';
    script.onload  = () => { plotlyLoaded = true; resolve(); };
    script.onerror = () => reject(new Error('Failed to load Plotly.js'));
    document.head.appendChild(script);
  });
}

// ── GENERATE ─────────────────────────────────────
document.getElementById('generateBtn').addEventListener('click', async () => {
  hideError();
  if (!validate()) return;

  const btn       = document.getElementById('generateBtn');
  btn.disabled    = true;
  btn.textContent = 'Generating...';

  const bins = parseInt(document.getElementById('bins').value) || 10;
  const fd   = new FormData();
  fd.append('chart_type',  currentChartType);
  fd.append('x',           document.getElementById('xAxis').value);
  fd.append('y',           document.getElementById('yAxis').value);
  fd.append('title',       document.getElementById('chartTitle').value.trim());
  fd.append('color_by',    document.getElementById('colorBy').value);
  fd.append('bins',        bins);
  fd.append('orientation', document.getElementById('orientation').value);

  try {
    const res = await fetch('/visualize-generate', {
      method:  'POST',
      headers: { 'X-Requested-With': 'XMLHttpRequest' },
      body:    fd
    });

    if (!res.ok) { showError(`Server error: ${res.status}`); btn.disabled = false; btn.textContent = '+ Add Chart'; return; }

    const text = await res.text();
    let data;
    try { data = JSON.parse(text); }
    catch(e) { showError('Server returned invalid response'); btn.disabled = false; btn.textContent = '+ Add Chart'; return; }

    if (data.success && data.chart) {
      const title = document.getElementById('chartTitle').value.trim() || `Chart ${chartCounter + 1}`;
      addChartToGrid(data.chart, title);
    } else {
      showError(data.error || 'Failed to generate chart — check column selection');
    }
  } catch (err) {
    showError('Request failed: ' + err.message);
  }

  btn.disabled    = false;
  btn.textContent = '+ Add Chart';
});

// ── ADD CHART TO GRID ────────────────────────────
function addChartToGrid(chartHtml, title) {
  if (!chartHtml || chartHtml.trim() === '') { showError('Received empty chart from server'); return; }

  chartCounter++;
  const id = `chart-${chartCounter}`;
  charts.push({ id, title, chartHtml });

  document.getElementById('emptyState').style.display     = 'none';
  document.getElementById('downloadAllBtn').style.display = 'inline-block';
  document.getElementById('clearAllBtn').style.display    = 'inline-block';
  updateCanvasInfo();

  const card     = document.createElement('div');
  card.className = 'chart-card';
  card.id        = id;
  card.draggable = true;
  card.innerHTML = `
    <div class="chart-card-header">
      <span class="chart-card-title">${title}</span>
      <div class="chart-card-actions">
        <button class="chart-card-btn" onclick="downloadChart('${id}', '${title.replace(/'/g,"\\'")}')">⬇ PNG</button>
        <button class="chart-card-btn remove" onclick="removeChart('${id}')">✕</button>
      </div>
    </div>
    <div class="chart-card-body" id="body-${id}"></div>
  `;

  // drag events
  card.addEventListener('dragstart', (e) => {
    dragSrcId = id;
    card.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
  });
  card.addEventListener('dragend', () => {
    dragSrcId = null;
    document.querySelectorAll('.chart-card').forEach(c => c.classList.remove('dragging', 'drag-over'));
  });
  card.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (dragSrcId && dragSrcId !== id) card.classList.add('drag-over');
  });
  card.addEventListener('dragleave', () => card.classList.remove('drag-over'));
  card.addEventListener('drop', (e) => {
    e.preventDefault();
    card.classList.remove('drag-over');
    if (dragSrcId && dragSrcId !== id) swapCharts(dragSrcId, id);
  });

  document.getElementById('chartsGrid').appendChild(card);

  // inject HTML safely — use srcdoc iframe to isolate scripts
  const body   = document.getElementById(`body-${id}`);
  const iframe = document.createElement('iframe');
  iframe.style.cssText = 'width:100%;height:380px;border:none;display:block;';
  iframe.srcdoc        = chartHtml;
  iframe.onload        = () => {
    // auto-resize iframe to content
    try {
      const h = iframe.contentDocument.body.scrollHeight;
      if (h > 100) iframe.style.height = h + 'px';
    } catch(e) {}
  };
  body.appendChild(iframe);
}

// ── SWAP CHARTS ──────────────────────────────────
function swapCharts(aId, bId) {
  const grid = document.getElementById('chartsGrid');
  const a    = document.getElementById(aId);
  const b    = document.getElementById(bId);
  if (!a || !b || a === b) return;

  // get positions
  const allCards = Array.from(grid.children);
  const aIdx     = allCards.indexOf(a);
  const bIdx     = allCards.indexOf(b);

  if (aIdx < bIdx) {
    grid.insertBefore(b, a);
    grid.insertBefore(a, allCards[bIdx + 1] || null);
  } else {
    grid.insertBefore(a, b);
    grid.insertBefore(b, allCards[aIdx + 1] || null);
  }
}

// ── REMOVE CHART ─────────────────────────────────
function removeChart(id) {
  const card = document.getElementById(id);
  if (card) {
    card.style.animation = 'fadeOut 0.2s ease';
    setTimeout(() => {
      card.remove();
      charts = charts.filter(c => c.id !== id);
      updateCanvasInfo();
      if (charts.length === 0) {
        document.getElementById('emptyState').style.display     = 'flex';
        document.getElementById('downloadAllBtn').style.display = 'none';
        document.getElementById('clearAllBtn').style.display    = 'none';
      }
    }, 200);
  }
}

// ── DOWNLOAD SINGLE ──────────────────────────────
function downloadChart(id, title) {
  const body   = document.getElementById(`body-${id}`);
  if (!body) return;
  const iframe = body.querySelector('iframe');
  if (!iframe) return;

  try {
    const iDoc  = iframe.contentDocument || iframe.contentWindow.document;
    const iPlot = iframe.contentWindow.Plotly;
    const div   = iDoc.querySelector('.plotly-graph-div');
    if (iPlot && div) {
      iPlot.downloadImage(div, {
        format:   'png',
        filename: title.replace(/\s+/g, '_').toLowerCase(),
        width:    1200,
        height:   600
      });
    } else {
      // fallback: open iframe content in new tab
      const blob = new Blob([iframe.srcdoc], { type: 'text/html' });
      const url  = URL.createObjectURL(blob);
      window.open(url, '_blank');
    }
  } catch(e) {
    showError('Download failed: ' + e.message);
  }
}

// ── DOWNLOAD ALL ─────────────────────────────────
document.getElementById('downloadAllBtn').addEventListener('click', async () => {
  if (charts.length === 0) return;
  const btn       = document.getElementById('downloadAllBtn');
  btn.disabled    = true;
  btn.textContent = 'Downloading...';

  for (let i = 0; i < charts.length; i++) {
    const c = charts[i];
    downloadChart(c.id, `${c.title}_${i + 1}`);
    await new Promise(r => setTimeout(r, 800));
  }

  btn.disabled    = false;
  btn.textContent = '⬇ Download All';
});

// ── CLEAR ALL ────────────────────────────────────
document.getElementById('clearAllBtn').addEventListener('click', () => {
  if (!confirm(`Remove all ${charts.length} chart${charts.length > 1 ? 's' : ''}?`)) return;
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
  if (!col) return;
  const xSel = document.getElementById('xAxis');
  const opt  = Array.from(xSel.options).find(o => o.value === col);
  if (opt) {
    xSel.value = col;
    // auto-select best chart type based on column type
    if (isNumeric(col)) {
      document.querySelector('[data-type="histogram"]').click();
    }
  }
}

// ── FADE OUT ANIMATION IN CSS ────────────────────
const style       = document.createElement('style');
style.textContent = '@keyframes fadeOut { from { opacity:1; transform:scale(1); } to { opacity:0; transform:scale(0.95); } }';
document.head.appendChild(style);

// ── INIT ─────────────────────────────────────────
initTheme();
populateColumns();
updateControlsForType('bar');
checkUrlParam();