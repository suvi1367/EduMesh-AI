// student-join.js
import { api } from './api.js';
import { getHub, setHub } from './config.js';
import { showLoading, showError, clearState, toast } from './ui.js';

const hubInput   = document.querySelector('#hub-url');
const saveHubBtn = document.querySelector('#save-hub');
const form       = document.querySelector('#join-form');
const statusBox  = document.querySelector('#join-status');

hubInput.value = getHub();

saveHubBtn.addEventListener('click', () => {
  if (!hubInput.value.trim()) return toast('Enter a Hub address first', 'error');
  setHub(hubInput.value.trim());
  toast('Hub address saved', 'success');
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  showLoading(statusBox, 'Joining classroom...');

  try {
    const data = await api.joinClass({
      studentName: form.studentName.value,
      classroomCode: form.classroomCode.value,
    });

    // Students don't log in with a password, so there's no token here —
    // instead we save their session identity so ask.html knows who's asking
    // and which classroom to send questions to.
    localStorage.setItem('studentName', form.studentName.value);
    localStorage.setItem('classroomCode', form.classroomCode.value);
    localStorage.setItem('studentSessionId', data.sessionId || `temp-${Date.now()}`);

    clearState(statusBox);
    toast('Joined classroom', 'success');
    window.location.href = 'ask.html';
  } catch (err) {
    showError(statusBox, err.message || 'Could not join classroom. Check the code.');
  }
});