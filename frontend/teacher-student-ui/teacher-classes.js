// teacher-classes.js
import { api } from './api.js';
import { showLoading, showError, clearState, toast } from './ui.js';

const classForm    = document.querySelector('#class-form');
const classStatus  = document.querySelector('#class-status');
const subjectForm  = document.querySelector('#subject-form');
const subjectStatus= document.querySelector('#subject-status');
const classSelect  = document.querySelector('#class-select');
const continueBtn  = document.querySelector('#continue-btn');

// Keep created classes in memory so the dropdown updates instantly
// without needing to re-fetch from the backend every time.
const createdClasses = [];

function renderClassOptions() {
  classSelect.innerHTML = createdClasses
    .map(c => `<option value="${c.id}">${c.name}</option>`)
    .join('');
}

classForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  showLoading(classStatus, 'Creating class...');

  try {
    const data = await api.createClass({
      institutionId: localStorage.getItem('institutionId'),
      className: classForm.className.value,
    });

    // Mock server won't return a real id, so fall back to a temp one —
    // swap this out once the real backend is wired in.
    const newClass = {
      id: data.id || `temp-${Date.now()}`,
      name: classForm.className.value,
    };
    createdClasses.push(newClass);
    renderClassOptions();

    clearState(classStatus);
    toast('Class created', 'success');
    classForm.reset();
  } catch (err) {
    showError(classStatus, err.message || 'Could not create class.');
  }
});

subjectForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (!classSelect.value) {
    return showError(subjectStatus, 'Create a class first.');
  }

  showLoading(subjectStatus, 'Creating subject...');

  try {
    await api.createSubject({
      classId: classSelect.value,
      subjectName: subjectForm.subjectName.value,
    });

    clearState(subjectStatus);
    toast('Subject created', 'success');
    subjectForm.reset();
  } catch (err) {
    showError(subjectStatus, err.message || 'Could not create subject.');
  }
});

continueBtn.addEventListener('click', () => {
  window.location.href = 'upload.html';   // next screen: curriculum upload
});