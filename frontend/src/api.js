import axios from 'axios';

const BASE = 'http://13.60.48.96:8000/api';

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return { headers: { Authorization: `Bearer ${token}` } };
};

export const login = (username, password) =>
  axios.post(`${BASE}/auth/login/`, { username, password });

export const register = (username, email, password) =>
  axios.post(`${BASE}/auth/register/`, { username, email, password });

export const getStudents = () =>
  axios.get(`${BASE}/students/`, getHeaders());

export const createStudent = (data) =>
  axios.post(`${BASE}/students/`, data, getHeaders());

export const updateStudent = (id, data) =>
  axios.put(`${BASE}/students/${id}/`, data, getHeaders());

export const deleteStudent = (id) =>
  axios.delete(`${BASE}/students/${id}/`, getHeaders());

export const getStats = () =>
  axios.get(`${BASE}/stats/`, getHeaders());
