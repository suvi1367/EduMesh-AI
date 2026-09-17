// student-ask.js
import { api } from './api.js';
import { showLoading, showError, clearState, toast } from './ui.js';

const header       = document.querySelector('#classroom-header');
const form         = document.querySelector('#ask-form');
const questionInput= document.querySelector('#question-input');
const languageSel  = document.querySelector('#language-select');
const styleSel      = document.querySelector('#style-select');
const statusBox     = document.querySelector('#ask-status');
const answerCard    = document.querySelector('#answer-card');
const answerText    = document.querySelector('#answer-text');
const answerSource  = document.querySelector('#answer-source');
const answerChapter = document.querySelector('#answer-chapter');
const answerPage    = document.querySelector('#answer-page');

// Show which classroom/student this is, using what join.html saved.
const classroomCode = localStorage.getItem('classroomCode');
const studentName    = localStorage.getItem('studentName');
header.textContent = classroomCode ? `Classroom: ${classroomCode}` : 'Classroom';

if (!classroomCode || !studentName) {
  showError(statusBox, 'You are not in a classroom. Please join first.');
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  answerCard.style.display = 'none';
  showLoading(statusBox, 'Sending question...');

  try {
    const data = await api.ask({
      classroomCode,
      studentName,
      sessionId: localStorage.getItem('studentSessionId'),
      question: questionInput.value,
      language: languageSel.value,
      style: styleSel.value,
    });

    clearState(statusBox);

    // Render the answer with its source metadata, even if the mock
    // server only sends back placeholder values — the task sheet
    // requires this metadata to be visibly displayed, not just the text.
    answerText.textContent = data.answer || '(No answer text returned yet — backend not wired in.)';
    answerSource.textContent = data.source || '—';
    answerChapter.textContent = data.chapter || '—';
    answerPage.textContent = data.page || '—';
    answerCard.style.display = 'block';

    questionInput.value = '';
  } catch (err) {
    showError(statusBox, err.message || 'Could not get an answer. Try again.');
  }
});