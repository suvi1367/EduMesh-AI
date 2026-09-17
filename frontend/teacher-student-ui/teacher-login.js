// teacher-login.js
import { api } from './api.js';
import { getHub, setHub } from './config.js';
import { showLoading, showError, clearState, toast } from './ui.js';

const statusBox = document.querySelector('#login-status');
const form      = document.querySelector('#login-form');
const hubInput  = document.querySelector('#hub-url');
const saveHubBtn= document.querySelector('#save-hub');

// Pre-fill the Hub input with whatever is already saved (or blank on first run).
hubInput.value = getHub();

saveHubBtn.addEventListener('click', () => {
  if (!hubInput.value.trim()) return toast('Enter a Hub address first', 'error');
  setHub(hubInput.value.trim());
  toast('Hub address saved', 'success');
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();          // stop the browser's default full-page reload on submit
  showLoading(statusBox, 'Logging in...');

  try {
    const data = await api.login({
      username: form.username.value,
      password: form.password.value,
    });
    localStorage.setItem('token', data.token);
    clearState(statusBox);
    toast('Login successful', 'success');
    window.location.href = 'setup.html';   // next screen: institution setup
  } catch (err) {
    showError(statusBox, err.message || 'Login failed. Check your credentials.');
  }
});