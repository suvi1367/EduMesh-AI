// teacher-setup.js
import { api } from './api.js';
import { showLoading, showError, clearState, toast } from './ui.js';

const statusBox = document.querySelector('#setup-status');
const form      = document.querySelector('#setup-form');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  showLoading(statusBox, 'Saving institution details...');

  try {
    const data = await api.institution({
      institutionName: form.institutionName.value,
      board: form.board.value,
      academicYear: form.academicYear.value,
    });

    // Save the institution ID so later screens (class creation, etc.)
    // know which institution to attach things to.
    localStorage.setItem('institutionId', data.id || 'demo-institution-id');

    clearState(statusBox);
    toast('Institution saved', 'success');
    window.location.href = 'classes.html';   // next screen: class & subject creation
  } catch (err) {
    showError(statusBox, err.message || 'Could not save institution details.');
  }
});