/* ── REPORT.JS ───────────────────────────────────── */

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
  if (!confirm('Reset will restore the original file and undo ALL operations. Are you sure?')) {
    e.preventDefault();
  }
});

// ── INIT ─────────────────────────────────────────
initTheme();