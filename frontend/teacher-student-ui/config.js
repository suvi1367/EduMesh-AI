// config.js
const DEFAULT_HUB = window.location.origin;     // served from the Hub itself
export const getHub = () => localStorage.getItem('hubUrl') || DEFAULT_HUB;
export const setHub = (url) => localStorage.setItem('hubUrl', url.replace(/\/$/, ''));