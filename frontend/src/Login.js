import React, { useState } from 'react';
import { login, register } from './api';

function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');

  const handle = e => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async e => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await register(form.username, form.email, form.password);
        setIsRegister(false);
        setError('Account created! Please log in.');
      } else {
        const res = await login(form.username, form.password);
        localStorage.setItem('token', res.data.access);
        onLogin(form.username);
      }
    } catch {
      setError('Invalid credentials or username already taken.');
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.box}>
        <h2 style={styles.title}>EduPredict</h2>
        <p style={styles.sub}>AI Student Success Predictor</p>

        <h3>{isRegister ? 'Create Account' : 'Login'}</h3>

        <form onSubmit={submit}>
          <input
            style={styles.input} name="username"
            placeholder="Username" value={form.username}
            onChange={handle} required
          />
          {isRegister && (
            <input
              style={styles.input} name="email" type="email"
              placeholder="Email" value={form.email}
              onChange={handle} required
            />
          )}
          <input
            style={styles.input} name="password" type="password"
            placeholder="Password" value={form.password}
            onChange={handle} required
          />
          {error && <p style={styles.error}>{error}</p>}
          <button style={styles.btn} type="submit">
            {isRegister ? 'Register' : 'Login'}
          </button>
        </form>

        <p style={{ marginTop: 12, fontSize: 13 }}>
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <span
            style={styles.link}
            onClick={() => { setIsRegister(!isRegister); setError(''); }}
          >
            {isRegister ? 'Login' : 'Register'}
          </span>
        </p>
      </div>
    </div>
  );
}

const styles = {
  page: { display:'flex', justifyContent:'center', alignItems:'center', height:'100vh', background:'#f0f2f5' },
  box: { background:'#fff', padding:40, borderRadius:8, width:320, boxShadow:'0 2px 12px rgba(0,0,0,0.1)', textAlign:'center' },
  title: { margin:0, color:'#2c3e50' },
  sub: { color:'#888', marginBottom:20, fontSize:13 },
  input: { width:'100%', padding:10, marginBottom:12, border:'1px solid #ddd', borderRadius:4, boxSizing:'border-box', fontSize:14 },
  btn: { width:'100%', padding:10, background:'#3498db', color:'#fff', border:'none', borderRadius:4, fontSize:15, cursor:'pointer' },
  error: { color:'red', fontSize:13, marginBottom:8 },
  link: { color:'#3498db', cursor:'pointer' },
};

export default Login;