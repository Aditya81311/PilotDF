/* ── VIEW_DATA.JS ─────────────────────────────────
   Handles paginated data table + right-click context menu
──────────────────────────────────────────────── */

let currentPage     = 1;
let currentRows     = 25;
let currentCol      = null;

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

// ── FETCH DATA FROM FLASK ────────────────────────
async function fetchViewData(page, rows) {
  const formData = new FormData();
  formData.append('page', page);
  formData.append('rows', rows);

  const res = await fetch('/view', {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    body: formData
  });
  if (!res.ok) throw new Error(`View API error: ${res.status}`);
  return await res.json();
}

// ── RENDER TABLE HEAD ────────────────────────────
function renderHead(columns) {
  const thead = document.getElementById('tableHead');
  const tr = document.createElement('tr');

  // Row number column
  const thNum = document.createElement('th');
  thNum.textContent = '#';
  thNum.className = 'row-num-head';
  tr.appendChild(thNum);

  columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = col;
    th.dataset.col = col;

    // Right click → context menu
    th.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      showContextMenu(e.pageX, e.pageY, col);
    });

    tr.appendChild(th);
  });

  thead.innerHTML = '';
  thead.appendChild(tr);
}

// ── RENDER TABLE BODY ────────────────────────────
function renderBody(data, page, rowsPerPage) {
  const tbody = document.getElementById('tableBody');
  tbody.innerHTML = '';

  if (!data || data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="100" class="loading-cell">No data found.</td></tr>';
    return;
  }

  const startIndex = (page - 1) * rowsPerPage;

  data.forEach((row, i) => {
    const tr = document.createElement('tr');

    // Row number
    const tdNum = document.createElement('td');
    tdNum.className = 'row-num';
    tdNum.textContent = startIndex + i + 1;
    tr.appendChild(tdNum);

    row.forEach(cell => {
      const td = document.createElement('td');
      if (cell === null || cell === '' || cell === 'NaN') {
        td.innerHTML = '<span class="null-cell">null</span>';
      } else {
        td.textContent = cell;
        td.title = cell; // show full value on hover
      }
      tr.appendChild(td);
    });

    tbody.appendChild(tr);
  });
}

// ── RENDER ROWS INFO ─────────────────────────────
function renderRowsInfo(data) {
  const start = (data.page - 1) * data.rows_per_page + 1;
  const end   = Math.min(data.page * data.rows_per_page, data.total_rows);
  document.getElementById('rowsInfo').innerHTML =
    `Showing <span>${start}–${end}</span> of <span>${data.total_rows.toLocaleString()}</span> rows`;
}

// ── RENDER PAGINATION ────────────────────────────
function renderPagination(totalPages, currentPage) {
  const container = document.getElementById('pagination');
  container.innerHTML = '';

  if (totalPages <= 1) return;

  // Prev button
  const prev = document.createElement('button');
  prev.className = 'page-btn';
  prev.textContent = '←';
  prev.disabled = currentPage === 1;
  prev.addEventListener('click', () => loadPage(currentPage - 1));
  container.appendChild(prev);

  // Page numbers — show smart range
  const range = getPageRange(currentPage, totalPages);
  range.forEach(p => {
    if (p === '...') {
      const span = document.createElement('span');
      span.textContent = '...';
      span.style.cssText = 'color:var(--text-hint);padding:0 4px;';
      container.appendChild(span);
    } else {
      const btn = document.createElement('button');
      btn.className = 'page-btn' + (p === currentPage ? ' active' : '');
      btn.textContent = p;
      btn.addEventListener('click', () => loadPage(p));
      container.appendChild(btn);
    }
  });

  // Next button
  const next = document.createElement('button');
  next.className = 'page-btn';
  next.textContent = '→';
  next.disabled = currentPage === totalPages;
  next.addEventListener('click', () => loadPage(currentPage + 1));
  container.appendChild(next);
}

// Smart page range: 1 ... 4 5 6 ... 20
function getPageRange(current, total) {
  if (total <= 7) return Array.from({length: total}, (_, i) => i + 1);
  if (current <= 4) return [1, 2, 3, 4, 5, '...', total];
  if (current >= total - 3) return [1, '...', total-4, total-3, total-2, total-1, total];
  return [1, '...', current-1, current, current+1, '...', total];
}

// ── LOAD PAGE ────────────────────────────────────
async function loadPage(page) {
  currentPage = page;
  document.getElementById('tableBody').innerHTML =
    '<tr><td colspan="100" class="loading-cell">Loading...</td></tr>';

  try {
    const data = await fetchViewData(page, currentRows);
    if (data.error) {
      document.getElementById('tableBody').innerHTML =
        `<tr><td colspan="100" class="loading-cell">${data.error}</td></tr>`;
      return;
    }
    renderHead(data.columns);
    renderBody(data.data, data.page, data.rows_per_page);
    renderRowsInfo(data);
    renderPagination(data.total_pages, data.page);
  } catch (err) {
    console.error('View load failed:', err);
    document.getElementById('tableBody').innerHTML =
      '<tr><td colspan="100" class="loading-cell">Failed to load data. Please try again.</td></tr>';
  }
}

// ── ROWS PER PAGE CHANGE ─────────────────────────
document.getElementById('rowsSelect').addEventListener('change', (e) => {
  currentRows = parseInt(e.target.value);
  loadPage(1);
});

// ── CONTEXT MENU ─────────────────────────────────
const contextMenu = document.getElementById('contextMenu');

function showContextMenu(x, y, col) {
  currentCol = col;
  contextMenu.style.left = x + 'px';
  contextMenu.style.top  = y + 'px';
  contextMenu.classList.add('visible');
}

function hideContextMenu() {
  contextMenu.classList.remove('visible');
  currentCol = null;
}

document.addEventListener('click', hideContextMenu);
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') hideContextMenu(); });

// Context menu actions — navigate to tab with column pre-selected
contextMenu.querySelectorAll('.context-item').forEach(item => {
  item.addEventListener('click', () => {
    const action = item.dataset.action;
    const col    = encodeURIComponent(currentCol);
    if (action === 'clean')     window.location.href = `/clean?col=${col}`;
    if (action === 'visualize') window.location.href = `/visualize?col=${col}`;
    if (action === 'transform') window.location.href = `/transform?col=${col}`;
    hideContextMenu();
  });
});

// ── INIT ─────────────────────────────────────────
initTheme();
loadPage(1);