const fileInput = document.querySelector('#evidence-file');
const dropZone = document.querySelector('#drop-zone');
const form = document.querySelector('#intake-form');
const submitButton = document.querySelector('#submit-button');
const consentInput = document.querySelector('#consent');
const callInput = document.querySelector('[name="call_records"]');
const signalInput = document.querySelector('[name="signal_data"]');
const message = document.querySelector('#form-message');
let selectedFile = null;
let currentRows = [];
const initialSearchTargets = [];
let searchTargets = loadSearchTargets();

function loadSearchTargets() {
  try {
    const saved = JSON.parse(localStorage.getItem('signal-ledger-search-targets'));
    if (Array.isArray(saved)) return [...new Set(saved.filter((number) => /^\d{3,20}$/.test(number)))];
  } catch {
    // Fall back to the requested defaults when local storage is unavailable.
  }
  try {
    localStorage.setItem('signal-ledger-search-targets', JSON.stringify(initialSearchTargets));
  } catch {
    // Keep the requested defaults for this session if storage is unavailable.
  }
  return [...initialSearchTargets];
}

function saveSearchTargets() {
  try {
    localStorage.setItem('signal-ledger-search-targets', JSON.stringify(searchTargets));
  } catch {
    setMessage('Targets are available for this session but could not be saved in this browser.');
  }
}

const now = new Date();
document.querySelector('#today').textContent = new Intl.DateTimeFormat('en', {
  weekday: 'short', month: 'short', day: '2-digit', year: 'numeric'
}).format(now).toUpperCase();

function setMessage(text, state = '') {
  message.textContent = text;
  message.className = `form-message ${state}`;
}

function refreshSubmit() {
  submitButton.disabled = !(selectedFile && consentInput.checked && (callInput.checked || signalInput.checked));
}

function showFile(file) {
  if (!file) return;
  if (!['.csv', '.json'].some((extension) => file.name.toLowerCase().endsWith(extension))) {
    selectedFile = null;
    document.querySelector('#file-preview').hidden = true;
    setMessage('Choose a CSV or JSON export.');
    refreshSubmit();
    return;
  }
  if (file.size > 25 * 1024 * 1024) {
    selectedFile = null;
    document.querySelector('#file-preview').hidden = true;
    setMessage('The selected file exceeds the 25 MB limit.');
    refreshSubmit();
    return;
  }
  selectedFile = file;
  document.querySelector('#file-name').textContent = file.name;
  document.querySelector('#file-size').textContent = `${(file.size / 1024).toLocaleString(undefined, { maximumFractionDigits: 1 })} KB`;
  document.querySelector('#file-preview').hidden = false;
  document.querySelector('#upload-title').textContent = 'Evidence ready for intake';
  document.querySelector('#upload-subtitle').textContent = 'Choose another file to replace it';
  setMessage('');
  refreshSubmit();
}

fileInput.addEventListener('change', () => showFile(fileInput.files[0]));
consentInput.addEventListener('change', refreshSubmit);
callInput.addEventListener('change', refreshSubmit);
signalInput.addEventListener('change', refreshSubmit);
document.querySelector('#remove-file').addEventListener('click', () => {
  selectedFile = null;
  fileInput.value = '';
  document.querySelector('#file-preview').hidden = true;
  document.querySelector('#upload-title').textContent = 'Drop an evidence file here';
  document.querySelector('#upload-subtitle').innerHTML = 'or <u>browse local files</u>';
  refreshSubmit();
});

for (const eventName of ['dragenter', 'dragover']) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add('dragging');
  });
}
for (const eventName of ['dragleave', 'drop']) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove('dragging');
  });
}
dropZone.addEventListener('drop', (event) => showFile(event.dataTransfer.files[0]));

function encodeBase64(bytes) {
  let binary = '';
  const chunkSize = 0x8000;
  for (let offset = 0; offset < bytes.length; offset += chunkSize) {
    binary += String.fromCharCode(...bytes.subarray(offset, offset + chunkSize));
  }
  return btoa(binary);
}

function renderSignalChart(rows) {
  const samples = rows.map((row) => Number(row.rsrp)).filter(Number.isFinite);
  if (!samples.length) return;
  const width = 600;
  const height = 139;
  const min = Math.min(-120, ...samples);
  const max = Math.max(-60, ...samples);
  const span = Math.max(1, max - min);
  const points = samples.map((value, index) => ({
    x: samples.length === 1 ? width / 2 : index * width / (samples.length - 1),
    y: height - ((value - min) / span) * (height - 12) - 6
  }));
  const path = points.map((point, index) => `${index ? 'L' : 'M'}${point.x.toFixed(1)} ${point.y.toFixed(1)}`).join(' ');
  document.querySelector('#chart-line').setAttribute('d', path);
  document.querySelector('#chart-area').setAttribute('d', `${path} L${width} ${height} L0 ${height} Z`);
  const pointsGroup = document.querySelector('#chart-points');
  pointsGroup.replaceChildren(...points.filter((_, index) => index % Math.max(1, Math.ceil(points.length / 20)) === 0 || index === points.length - 1).map((point) => {
    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', point.x.toFixed(1));
    circle.setAttribute('cy', point.y.toFixed(1));
    circle.setAttribute('r', '3.2');
    circle.setAttribute('class', 'chart-point');
    return circle;
  }));
}

function renderTable(rows, query = '') {
  const headers = rows.length ? Object.keys(rows[0]) : [];
  const header = document.querySelector('#table-header');
  const body = document.querySelector('#table-body');
  header.replaceChildren();
  body.replaceChildren();
  const headerRow = document.createElement('tr');
  for (const name of headers) {
    const cell = document.createElement('th');
    cell.textContent = name.replaceAll('_', ' ').toUpperCase();
    headerRow.append(cell);
  }
  header.append(headerRow);
  for (const row of rows.slice(0, 100)) {
    const tableRow = document.createElement('tr');
    for (const name of headers) {
      const cell = document.createElement('td');
      cell.textContent = row[name] == null ? '' : String(row[name]);
      tableRow.append(cell);
    }
    body.append(tableRow);
  }
  document.querySelector('#table-count').textContent = `${rows.length} ROWS`;
  document.querySelector('#table-caption').textContent = query
    ? `${rows.length} matching evidence records`
    : rows.length > 100
      ? 'First 100 validated rows shown'
      : 'Validated rows from acquired evidence';
}

function renderPhoneNumbers(rows, query = '') {
  const counts = new Map();
  for (const row of rows) {
    const number = String(row.phone_number ?? '').trim();
    if (number) counts.set(number, (counts.get(number) || 0) + 1);
  }

  const list = document.querySelector('#number-list');
  list.replaceChildren();
  const ordered = [...counts.entries()].sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]));
  const matching = ordered.filter(([number]) => number.replace(/\D/g, '').includes(query));
  for (const [number, count] of matching) {
    const item = document.createElement('div');
    item.className = 'number-item';
    const value = document.createElement('strong');
    value.textContent = number;
    const occurrences = document.createElement('span');
    occurrences.textContent = `${count} ${count === 1 ? 'record' : 'records'}`;
    item.append(value, occurrences);
    list.append(item);
  }
  if (query && !matching.length) {
    const empty = document.createElement('p');
    empty.className = 'number-empty';
    empty.textContent = currentRows.length
      ? 'No matching number in this evidence.'
      : 'Run an examination to check this number against evidence.';
    list.append(empty);
  }
  document.querySelector('#number-count').textContent = query
    ? currentRows.length ? `${matching.length} MATCH${matching.length === 1 ? '' : 'ES'}` : 'WAITING FOR EVIDENCE'
    : `${ordered.length} NUMBERS`;
}

function applyNumberSearch() {
  const query = document.querySelector('#number-search').value.replace(/\D/g, '');
  const rows = query
    ? currentRows.filter((row) => String(row.phone_number ?? '').replace(/\D/g, '').includes(query))
    : currentRows;
  renderPhoneNumbers(rows, query);
  renderTable(rows, query);
}

function renderSearchTargets() {
  const targetList = document.querySelector('#target-list');
  targetList.replaceChildren();
  document.querySelector('#target-count').textContent = `${searchTargets.length} TARGET${searchTargets.length === 1 ? '' : 'S'}`;

  for (const number of searchTargets) {
    const matchingRecords = currentRows.filter((row) => String(row.phone_number ?? '').replace(/\D/g, '') === number).length;
    const item = document.createElement('div');
    item.className = 'target-item';

    const numberButton = document.createElement('button');
    numberButton.className = 'target-number';
    numberButton.type = 'button';
    numberButton.textContent = number;
    numberButton.setAttribute('aria-label', `Search evidence for ${number}`);
    numberButton.addEventListener('click', () => {
      document.querySelector('#number-search').value = number;
      applyNumberSearch();
      document.querySelector('#number-search').focus();
    });

    const status = document.createElement('span');
    status.className = matchingRecords ? 'target-status found' : 'target-status';
    status.textContent = currentRows.length
      ? matchingRecords ? `${matchingRecords} evidence ${matchingRecords === 1 ? 'record' : 'records'}` : 'Not present in evidence'
      : 'Upload evidence to check';

    const removeButton = document.createElement('button');
    removeButton.className = 'target-remove';
    removeButton.type = 'button';
    removeButton.textContent = 'Remove';
    removeButton.addEventListener('click', () => {
      searchTargets = searchTargets.filter((target) => target !== number);
      saveSearchTargets();
      renderSearchTargets();
    });

    item.append(numberButton, status, removeButton);
    targetList.append(item);
  }
}

document.querySelector('#add-target').addEventListener('click', () => {
  const value = document.querySelector('#number-search').value.replace(/\D/g, '');
  if (value.length < 3 || value.length > 20) {
    setMessage('Enter a phone number with 3 to 20 digits to add it as a target.');
    return;
  }
  if (searchTargets.includes(value)) {
    setMessage('That number is already in your saved search targets.');
    return;
  }
  searchTargets.push(value);
  saveSearchTargets();
  renderSearchTargets();
  setMessage(`${value} added as a search target. Evidence has not been changed.`, 'success');
});

function showResults(result) {
  const calls = result.analysis.calls;
  const signal = result.analysis.signal;
  const network = result.analysis.network || {};
  document.querySelector('#metric-records').innerHTML = `${result.evidence.records} <small>records</small>`;
  document.querySelector('#metric-file').textContent = result.evidence.filename;
  document.querySelector('#metric-integrity').innerHTML = 'SHA-256 <small>verified</small>';
  document.querySelector('#pipeline-state').innerHTML = '<i class="state-dot live"></i> COMPLETE';
  document.querySelector('#result-filename').textContent = result.evidence.filename;
  document.querySelector('#result-records').textContent = result.evidence.records;
  document.querySelector('#result-duplicates').textContent = result.evidence.duplicates;
  document.querySelector('#digest-value').textContent = result.evidence.sha256;
  document.querySelector('#call-total').textContent = calls ? calls.total_records : '—';
  document.querySelector('#incoming-count').textContent = calls ? calls.incoming : '—';
  document.querySelector('#outgoing-count').textContent = calls ? calls.outgoing : '—';
  document.querySelector('#missed-count').textContent = calls ? calls.missed : '—';
  document.querySelector('#duration-total').textContent = calls ? `${calls.total_duration.toLocaleString()} sec` : 'Not authorized';
  document.querySelector('#average-rsrp').textContent = signal ? signal.average_rsrp.toFixed(1) : '—';
  document.querySelector('#strongest-rsrp').textContent = signal ? `${signal.strongest_rsrp} dBm` : '—';
  document.querySelector('#weakest-rsrp').textContent = signal ? `${signal.weakest_rsrp} dBm` : '—';
  const chips = document.querySelector('#radio-types');
  chips.replaceChildren();
  for (const [type, count] of Object.entries(network.network_types || {})) {
    const chip = document.createElement('span');
    chip.className = 'radio-chip';
    chip.textContent = `${type} `;
    const bold = document.createElement('b');
    bold.textContent = count;
    chip.append(bold);
    chips.append(chip);
  }
  renderSignalChart(result.rows);
  currentRows = result.rows;
  applyNumberSearch();
  renderSearchTargets();
  const reportLink = document.querySelector('#report-link');
  reportLink.href = `/api/reports/${encodeURIComponent(result.report)}`;
  document.querySelector('#results').hidden = false;
  document.querySelector('#results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

document.querySelector('#number-search').addEventListener('input', applyNumberSearch);
renderSearchTargets();

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  if (!selectedFile || !consentInput.checked) return;
  submitButton.disabled = true;
  submitButton.innerHTML = '<span class="loading-state"><i class="spinner"></i> Processing evidence</span><b>&#8230;</b>';
  setMessage('Running acquisition, validation, integrity verification, analysis, and report generation…');
  document.querySelector('#pipeline-state').innerHTML = '<i class="state-dot"></i> PROCESSING';
  try {
    const bytes = new Uint8Array(await selectedFile.arrayBuffer());
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        filename: selectedFile.name,
        content_base64: encodeBase64(bytes),
        consent: consentInput.checked,
        categories: { call_records: callInput.checked, signal_data: signalInput.checked }
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || 'The examination could not be completed.');
    showResults(result);
    setMessage('Examination complete. Integrity verified and report generated.', 'success');
  } catch (error) {
    document.querySelector('#pipeline-state').innerHTML = '<i class="state-dot"></i> STANDBY';
    setMessage(error.message || 'The local service could not be reached. Start Backend.web and try again.');
  } finally {
    submitButton.innerHTML = '<span>Run examination</span><b>&#8594;</b>';
    refreshSubmit();
  }
});

fetch('/api/status').catch(() => setMessage('Local service unavailable. Start it with: python -m Backend.web'));
