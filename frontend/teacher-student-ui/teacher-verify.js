// teacher-verify.js
import { api } from './api.js';
import { showLoading, showError, clearState, toast } from './ui.js';

const refreshBtn = document.querySelector('#refresh-btn');
const statusBox  = document.querySelector('#queue-status');
const listBox    = document.querySelector('#queue-list');

// Mock server has no real queue endpoint yet, so we keep a small
// in-memory list here to demonstrate the full approve/correct/reject
// flow. Swap loadQueue() for a real api.* call once the backend
// exposes GET /question/queue.
let queue = [
  {
    id: 'q1',
    studentName: 'Demo Student',
    question: 'What is photosynthesis?',
    aiAnswer: 'Photosynthesis is how plants convert sunlight into energy.',
    source: 'NCERT Science', chapter: '6', page: '112',
    status: 'pending',
  },
];

function renderQueue() {
  if (!queue.length) {
    listBox.innerHTML = '<p><em>No questions waiting for review.</em></p>';
    return;
  }

  listBox.innerHTML = queue.map(q => `
    <div class="queue-card" data-id="${q.id}">
      <p><strong>${q.studentName}</strong> asked:</p>
      <p class="question-text">${q.question}</p>

      <p><strong>AI Answer:</strong></p>
      <p>${q.aiAnswer}</p>
      <p class="source-line">Source: ${q.source} · Chapter: ${q.chapter} · Page: ${q.page}</p>

      <div class="action-row">
        <button class="approve-btn" data-id="${q.id}">Approve</button>
        <button class="reject-btn" data-id="${q.id}">Reject</button>
        <button class="correct-toggle-btn" data-id="${q.id}">Correct</button>
      </div>

      <div class="correction-form" id="correction-${q.id}" style="display:none;">
        <label>Corrected Answer</label>
        <textarea class="correction-text" rows="3"></textarea>
        <button class="submit-correction-btn" data-id="${q.id}">Submit Correction</button>
      </div>

      <p class="item-status" id="status-${q.id}"></p>
    </div>
  `).join('');

  attachRowHandlers();
}

function attachRowHandlers() {
  document.querySelectorAll('.approve-btn').forEach(btn =>
    btn.addEventListener('click', () => handleApprove(btn.dataset.id)));

  document.querySelectorAll('.reject-btn').forEach(btn =>
    btn.addEventListener('click', () => handleReject(btn.dataset.id)));

  document.querySelectorAll('.correct-toggle-btn').forEach(btn =>
    btn.addEventListener('click', () => {
      const form = document.querySelector(`#correction-${btn.dataset.id}`);
      form.style.display = form.style.display === 'none' ? 'block' : 'none';
    }));

  document.querySelectorAll('.submit-correction-btn').forEach(btn =>
    btn.addEventListener('click', () => handleCorrect(btn.dataset.id)));
}

async function handleApprove(id) {
  const statusEl = document.querySelector(`#status-${id}`);
  statusEl.textContent = 'Approving...';
  try {
    await api.approve({ questionId: id });
    statusEl.textContent = '✔ Approved';
    toast('Answer approved', 'success');
  } catch (err) {
    statusEl.textContent = '';
    showError(statusEl, err.message || 'Could not approve.');
  }
}

async function handleReject(id) {
  const statusEl = document.querySelector(`#status-${id}`);
  statusEl.textContent = 'Rejecting...';
  try {
    // Reject reuses the correct endpoint with an empty correction —
    // the task sheet's API contract only lists approve/correct, so
    // "reject" is modeled as a correction marking it unusable.
    await api.correct({ questionId: id, correctedAnswer: null, rejected: true });
    statusEl.textContent = '✘ Rejected';
    toast('Answer rejected', 'success');
  } catch (err) {
    statusEl.textContent = '';
    showError(statusEl, err.message || 'Could not reject.');
  }
}

async function handleCorrect(id) {
  const form = document.querySelector(`#correction-${id}`);
  const textarea = form.querySelector('.correction-text');
  const statusEl = document.querySelector(`#status-${id}`);

  if (!textarea.value.trim()) {
    return showError(statusEl, 'Enter a corrected answer first.');
  }

  statusEl.textContent = 'Submitting correction...';
  try {
    await api.correct({ questionId: id, correctedAnswer: textarea.value });
    statusEl.textContent = '✔ Correction submitted';
    toast('Correction submitted', 'success');
    form.style.display = 'none';
  } catch (err) {
    statusEl.textContent = '';
    showError(statusEl, err.message || 'Could not submit correction.');
  }
}

refreshBtn.addEventListener('click', () => {
  showLoading(statusBox, 'Refreshing queue...');
  // Simulated refresh — replace with a real GET call once available.
  setTimeout(() => {
    clearState(statusBox);
    renderQueue();
    toast('Queue refreshed', 'success');
  }, 400);
});
renderQueue();