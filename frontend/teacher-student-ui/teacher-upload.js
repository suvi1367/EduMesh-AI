// teacher-upload.js
import { getHub } from './config.js';
import { api } from './api.js';
import { showError, clearState, toast } from './ui.js';

const form           = document.querySelector('#upload-form');
const fileInput       = document.querySelector('#file-input');
const progressWrap    = document.querySelector('#upload-progress-wrap');
const filenameLabel   = document.querySelector('#upload-filename');
const progressFill    = document.querySelector('#upload-progress-fill');
const progressPercent = document.querySelector('#upload-percent');
const processingBox   = document.querySelector('#processing-status');
const uploadStatus    = document.querySelector('#upload-status');
const continueBtn     = document.querySelector('#continue-btn');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const file = fileInput.files[0];
  if (!file) return showError(uploadStatus, 'Choose a PDF first.');

  clearState(uploadStatus);
  progressWrap.style.display = 'block';
  filenameLabel.textContent = file.name;
  progressFill.style.width = '0%';
  progressPercent.textContent = '0%';

  // fetch() can't report upload progress, so we use XMLHttpRequest here —
  // this is the one place in the whole module that needs it.
  const formData = new FormData();
  formData.append('file', file);
  formData.append('institutionId', localStorage.getItem('institutionId') || '');

  const xhr = new XMLHttpRequest();
  const token = localStorage.getItem('token');

  xhr.open('POST', `${getHub()}/documents/upload`);
  if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`);

  xhr.upload.onprogress = (event) => {
    if (!event.lengthComputable) return;
    const percent = Math.round((event.loaded / event.total) * 100);
    progressFill.style.width = `${percent}%`;
    progressPercent.textContent = `${percent}%`;
  };

  xhr.onload = () => {
    if (xhr.status < 200 || xhr.status >= 300) {
      return showError(uploadStatus, `Upload failed (${xhr.status}).`);
    }
    let data = {};
    try { data = JSON.parse(xhr.responseText); } catch {}
    toast('Upload complete', 'success');
    pollProcessingStatus(data.documentId || 'demo-doc-id');
  };

  xhr.onerror = () => showError(uploadStatus, 'Upload failed. Check your connection to the Hub.');

  xhr.send(formData);
});

// Polls the backend every 2 seconds until processing is done.
// This is how the UI knows when the PDF has finished being indexed
// into the curriculum-sharded model.
async function pollProcessingStatus(documentId) {
  processingBox.innerHTML = '<p>Processing document...</p>';

  const poll = async () => {
    try {
      const data = await api.docStatus(documentId);
      if (data.status === 'done' || data.status === 'ready') {
        processingBox.innerHTML = '<p>✔ Document ready</p>';
      } else if (data.status === 'error') {
        showError(processingBox, 'Processing failed on the server.');
      } else {
        processingBox.innerHTML = `<p>Processing document... (${data.status || 'working'})</p>`;
        setTimeout(poll, 2000);
      }
    } catch (err) {
      // Mock server doesn't implement real status tracking yet,
      // so treat any failure here as "still processing" rather than
      // showing a scary error during development.
      setTimeout(poll, 2000);
    }
  };

  poll();
}

continueBtn.addEventListener('click', () => {
  window.location.href = 'classroom.html';   // next screen: start classroom
});