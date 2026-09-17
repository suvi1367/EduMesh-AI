// teacher-analytics.js
import { api } from './api.js';
import { showLoading, showError, clearState, toast } from './ui.js';

const refreshBtn   = document.querySelector('#refresh-btn');
const statusBox    = document.querySelector('#analytics-status');
const connectedEl  = document.querySelector('#stat-connected');
const totalEl      = document.querySelector('#stat-total');
const uniqueEl     = document.querySelector('#stat-unique');
const reviewEl     = document.querySelector('#stat-review');
const topicsList   = document.querySelector('#topics-list');

async function loadAnalytics() {
  showLoading(statusBox, 'Loading analytics...');

  try {
    const classroomId = localStorage.getItem('classroomId') || 'DEMO-CLASS';
    const data = await api.analytics(classroomId);

    // Mock server returns { ok: true } with no real fields, so every
    // value here falls back to 0 / empty — this is expected until the
    // real analytics endpoint is wired in by the backend.
    connectedEl.textContent = data.connectedStudents?.length || 0;
    totalEl.textContent     = data.totalQuestions || 0;
    uniqueEl.textContent    = data.uniqueQuestions || 0;
    reviewEl.textContent    = data.needsReview || 0;

    const topics = data.frequentTopics || [];
    topicsList.innerHTML = topics.length
      ? topics.map(t => `<li>${t}</li>`).join('')
      : '<li><em>No topic data yet</em></li>';

    clearState(statusBox);
  } catch (err) {
    showError(statusBox, err.message || 'Could not load analytics.');
  }
}

refreshBtn.addEventListener('click', () => {
  loadAnalytics();
  toast('Analytics refreshed', 'success');
});

loadAnalytics();