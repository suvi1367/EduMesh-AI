// teacher-classroom.js
import { getHub } from './config.js';
import { api } from './api.js';
import { showLoading, showError, clearState, toast } from './ui.js';

const preStart       = document.querySelector('#pre-start');
const startBtn       = document.querySelector('#start-btn');
const subjectInput   = document.querySelector('#subject-name');
const classroomInfo  = document.querySelector('#classroom-info');
const codeLabel      = document.querySelector('#classroom-code');
const addressLabel   = document.querySelector('#classroom-address');
const studentCount   = document.querySelector('#student-count');
const studentList    = document.querySelector('#student-list');
const statusBox      = document.querySelector('#classroom-status');

let classroomId = null;
let pollTimer = null;

startBtn.addEventListener('click', async () => {
  showLoading(statusBox, 'Starting classroom...');

  try {
    const data = await api.startClass({
      institutionId: localStorage.getItem('institutionId'),
      subjectLabel: subjectInput.value,
    });

    classroomId = data.id || 'DEMO-CLASS';
    localStorage.setItem('classroomId', classroomId);

    codeLabel.textContent = data.code || classroomId;
    addressLabel.textContent = getHub();

    clearState(statusBox);
    preStart.style.display = 'none';
    classroomInfo.style.display = 'block';
    toast('Classroom started', 'success');

    pollConnectedStudents();
  } catch (err) {
    showError(statusBox, err.message || 'Could not start classroom.');
  }
});

function pollConnectedStudents() {
  const poll = async () => {
    try {
      const data = await api.analytics(classroomId);
      const students = data.connectedStudents || [];

      studentCount.textContent = students.length;
      studentList.innerHTML = students.length
        ? students.map(s => `<li>${s.name || s}</li>`).join('')
        : '<li><em>No students connected yet</em></li>';
    } catch (err) {
      // Mock server won't return real student data — fail silently
    }
    pollTimer = setTimeout(poll, 5000);
  };
  poll();
}