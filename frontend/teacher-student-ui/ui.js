// ui.js
// Small, reusable functions for showing state on any screen.
// Every screen imports these instead of writing its own loading/error code.

// Shows a spinner + message inside a container element.
// Call this right before you start an API request.
export function showLoading(container, message = 'Loading...') {
  container.innerHTML = `
    <div class="state state-loading">
      <div class="spinner"></div>
      <p>${message}</p>
    </div>
  `;
}

// Shows an error message inside a container element.
// Call this in the catch block when an API request fails.
export function showError(container, message = 'Something went wrong.') {
  container.innerHTML = `
    <div class="state state-error">
      <p>⚠ ${message}</p>
    </div>
  `;
}

// Clears a container back to empty (used before rendering real content,
// so old loading/error messages don't linger underneath).
export function clearState(container) {
  container.innerHTML = '';
}

// Shows a small temporary popup message (e.g. "Saved!", "Upload failed").
// Doesn't need a container — it creates its own floating element and
// removes itself after a few seconds.
export function toast(message, type = 'info') {
  const el = document.createElement('div');
  el.className = `toast toast-${type}`; // type: 'info' | 'success' | 'error'
  el.textContent = message;
  document.body.appendChild(el);

  // Give the browser a frame to apply initial styles, then fade in.
  requestAnimationFrame(() => el.classList.add('toast-visible'));

  setTimeout(() => {
    el.classList.remove('toast-visible');
    setTimeout(() => el.remove(), 300); // wait for fade-out transition
  }, 3000);
}