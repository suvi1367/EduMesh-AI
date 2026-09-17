// api.js
import { getHub } from './config.js';

async function request(path, { method = 'GET', body, isFile } = {}) {
  const opts = { method, headers: {} };
  const token = localStorage.getItem('token');
  if (token) opts.headers['Authorization'] = `Bearer ${token}`;
  if (isFile) opts.body = body;                    // FormData, no content-type
  else if (body) { opts.headers['Content-Type'] = 'application/json';
                   opts.body = JSON.stringify(body); }

  const res = await fetch(`${getHub()}${path}`, opts);
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || res.status);
  return res.json();
}

export const api = {
  login:        (d) => request('/login', { method:'POST', body:d }),
  institution:  (d) => request('/institution', { method:'POST', body:d }),
  createClass:  (d) => request('/classes', { method:'POST', body:d }),
  createSubject:(d) => request('/subjects', { method:'POST', body:d }),
  upload:       (fd)=> request('/documents/upload', { method:'POST', body:fd, isFile:true }),
  docStatus:    (id)=> request(`/documents/status?id=${id}`),
  startClass:   (d) => request('/classroom/start', { method:'POST', body:d }),
  joinClass:    (d) => request('/classroom/join', { method:'POST', body:d }),
  ask:          (d) => request('/question', { method:'POST', body:d }),
  approve:      (d) => request('/answer/approve', { method:'POST', body:d }),
  correct:      (d) => request('/answer/correct', { method:'POST', body:d }),
  analytics:    (id)=> request(`/analytics?classroom_id=${id}`),
};