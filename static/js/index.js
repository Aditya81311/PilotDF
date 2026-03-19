/* ── INDEX.JS — Upload page logic ─────────────────── */

const dropZone      = document.getElementById('dropZone');
const fileInput     = document.getElementById('fileInput');
const fileSelected  = document.getElementById('fileSelected');
const selectedName  = document.getElementById('selectedFileName');
const selectedSize  = document.getElementById('selectedFileSize');
const fileRemove    = document.getElementById('fileRemove');
const uploadBtn     = document.getElementById('uploadBtn');
const uploadBtnText = document.getElementById('uploadBtnText');
const uploadSpinner = document.getElementById('uploadSpinner');
const uploadError   = document.getElementById('uploadError');

let selectedFile = null;

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

// ── FORMAT FILE SIZE ─────────────────────────────
function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ── ALLOWED FILE CHECK ───────────────────────────
function isAllowed(filename) {
  return /\.(csv|xlsx|xls)$/i.test(filename);
}

// ── SHOW FILE ────────────────────────────────────
function showFile(file) {
  if (!isAllowed(file.name)) {
    showError('Only CSV and Excel (.xlsx, .xls) files are supported.');
    return;
  }
  if (file.size > 50 * 1024 * 1024) {
    showError('File size exceeds 50MB limit.');
    return;
  }
  selectedFile = file;
  hideError();
  dropZone.style.display = 'none';
  fileSelected.style.display = 'flex';
  selectedName.textContent = file.name;
  selectedSize.textContent = formatSize(file.size);
  uploadBtn.disabled = false;
  uploadBtnText.textContent = 'Analyse File →';
}

// ── CLEAR FILE ───────────────────────────────────
function clearFile() {
  selectedFile = null;
  fileInput.value = '';
  dropZone.style.display = 'flex';
  fileSelected.style.display = 'none';
  uploadBtn.disabled = true;
  uploadBtnText.textContent = 'Select a file to continue';
  hideError();
}

// ── ERROR HELPERS ────────────────────────────────
function showError(msg) {
  uploadError.textContent = msg;
  uploadError.style.display = 'block';
}
function hideError() {
  uploadError.style.display = 'none';
}

// ── DRAG & DROP ──────────────────────────────────
dropZone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) showFile(fileInput.files[0]);
});
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  if (e.dataTransfer.files[0]) showFile(e.dataTransfer.files[0]);
});
fileRemove.addEventListener('click', clearFile);

// ── UPLOAD ───────────────────────────────────────
uploadBtn.addEventListener('click', async () => {
  if (!selectedFile) return;

  uploadBtn.disabled = true;
  uploadBtnText.textContent = 'Uploading...';
  uploadSpinner.style.display = 'inline';
  hideError();

  const formData = new FormData();
  formData.append('file', selectedFile);

  try {
    const res = await fetch('/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();

    if (data.success) {
      window.location.href = data.redirect;
    } else {
      showError(data.error || 'Upload failed. Please try again.');
      uploadBtn.disabled = false;
      uploadBtnText.textContent = 'Analyse File →';
      uploadSpinner.style.display = 'none';
    }
  } catch (err) {
    showError('Something went wrong. Please try again.');
    uploadBtn.disabled = false;
    uploadBtnText.textContent = 'Analyse File →';
    uploadSpinner.style.display = 'none';
  }
});

// ── INIT ─────────────────────────────────────────
initTheme();