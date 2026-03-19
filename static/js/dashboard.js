/* ── DASHBOARD.JS ─────────────────────────────────
   Dummy data for UI testing.
   Later: replace fetchDashboardData() with real Flask API call.
──────────────────────────────────────────────── */

// ── FETCH FROM FLASK API ─────────────────────────
async function fetchDashboardData() {
  const res = await fetch('/dashboard', {
    method: 'GET',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  });
  if (!res.ok) throw new Error(`Dashboard API error: ${res.status}`);
  return await res.json();
}

// ── RENDER FILE INFO ─────────────────────────────
function renderFileInfo(data) {
  document.getElementById('fileName').textContent  = data.file_name;
  document.getElementById('rowCount').textContent  = data.rows.toLocaleString();
  document.getElementById('colCount').textContent  = data.columns;
  document.getElementById('fileSize').textContent  = data.file_size;
  document.getElementById('memSize').textContent   = data.memory_size;
  document.getElementById('colCountLabel').textContent = `Showing all ${data.columns} columns`;
}

// ── RENDER HEALTH CARD ───────────────────────────
function renderHealth(data) {
  const badge = document.getElementById('healthBadge');
  const nullBar = document.getElementById('nullBar');
  const dupBar  = document.getElementById('dupBar');
  const nullPct = document.getElementById('nullPct');
  const dupCount = document.getElementById('dupCount');
  const issuesEl = document.getElementById('healthIssues');

  nullPct.textContent  = data.null_pct + '%';
  dupCount.textContent = data.duplicate_rows;
  nullBar.style.width  = Math.min(data.null_pct, 100) + '%';
  dupBar.style.width   = data.duplicate_rows > 0
    ? Math.min((data.duplicate_rows / data.rows) * 100, 100) + '%'
    : '0%';

  if (data.health_status === 'ok') {
    badge.textContent = 'Healthy';
    badge.className   = 'health-badge ok';
  } else if (data.health_status === 'bad') {
    badge.textContent = 'Critical';
    badge.className   = 'health-badge warn';
  } else {
    badge.textContent = 'Needs Attention';
    badge.className   = 'health-badge warn';
  }

  // Render issues
  issuesEl.innerHTML = '';
  data.issues.forEach(issue => {
    const div = document.createElement('div');
    div.className = 'issue-item';
    div.innerHTML = `
      <span class="issue-dot ${issue.type}"></span>
      <span>${issue.message}</span>
    `;
    issuesEl.appendChild(div);
  });
}

// ── RENDER OVERVIEW TABLE ────────────────────────
function getTypeBadge(type) {
  const map = { int: 'type-int', float: 'type-float', object: 'type-object', datetime: 'type-datetime' };
  const cls = map[type] || 'type-object';
  return `<span class="type-badge ${cls}">${type}</span>`;
}

function getNullClass(pct) {
  return pct > 5 ? 'null-high' : 'null-ok';
}

function renderOverview(data) {
  const tbody = document.getElementById('overviewBody');
  tbody.innerHTML = '';
  data.overview.forEach((col, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="row-num">${i + 1}</td>
      <td>${col.name}</td>
      <td>${getTypeBadge(col.type)}</td>
      <td>${col.count.toLocaleString()}</td>
      <td class="${getNullClass(col.null_pct)}">${col.null_pct.toFixed(1)}%</td>
      <td>${col.unique.toLocaleString()}</td>
      <td>${col.mean}</td>
      <td>${col.min}</td>
      <td>${col.max}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ── DARK MODE TOGGLE ─────────────────────────────
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

// ── INIT ─────────────────────────────────────────
async function init() {
  initTheme();
  try {
    const data = await fetchDashboardData();
    renderFileInfo(data);
    renderHealth(data);
    renderOverview(data);
  } catch (err) {
    console.error('Dashboard load failed:', err);
  }
}

init();