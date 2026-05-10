import React, { useState, useEffect } from 'react';
import { getStudents, createStudent, updateStudent, deleteStudent, getStats } from './api';

function Dashboard({ user, onLogout }) {
  const [students, setStudents] = useState([]);
  const [stats, setStats] = useState(null);
  const [form, setForm] = useState({ name: '', study_hours: '', attendance: '' });
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const load = async () => {
    try {
      const [s, st] = await Promise.all([getStudents(), getStats()]);
      setStudents(s.data);
      setStats(st.data);
    } catch { onLogout(); }
  };

  useEffect(() => { load(); }, []);

  const handle = e => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async e => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (editId) {
        await updateStudent(editId, form);
        setEditId(null);
      } else {
        await createStudent(form);
      }
      setForm({ name: '', study_hours: '', attendance: '' });
      await load();
    } catch { setError('Failed to save. Check your inputs.'); }
    setLoading(false);
  };

  const startEdit = s => {
    setEditId(s.id);
    setForm({ name: s.name, study_hours: s.study_hours, attendance: s.attendance });
  };

  const remove = async id => {
    if (window.confirm('Delete this student?')) {
      await deleteStudent(id);
      await load();
    }
  };

  const cancel = () => {
    setEditId(null);
    setForm({ name: '', study_hours: '', attendance: '' });
  };

  return (
    <div style={styles.page}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={{ margin: 0 }}>EduPredict Dashboard</h2>
        <span>
          Welcome, <b>{user}</b> &nbsp;
          <button onClick={onLogout} style={styles.logoutBtn}>Logout</button>
        </span>
      </div>

      {/* Stats Bar */}
      {stats && (
        <div style={styles.statsBar}>
          <div style={styles.statCard}>
            <div style={styles.statNum}>{stats.total_students}</div>
            <div style={styles.statLabel}>Total Students</div>
          </div>
          <div style={styles.statCard}>
            <div style={{ ...styles.statNum, color: 'green' }}>{stats.pass_count}</div>
            <div style={styles.statLabel}>Passing</div>
          </div>
          <div style={styles.statCard}>
            <div style={{ ...styles.statNum, color: 'red' }}>{stats.fail_count}</div>
            <div style={styles.statLabel}>At Risk</div>
          </div>
          <div style={styles.statCard}>
            <div style={{ ...styles.statNum, color: '#3498db' }}>{stats.accuracy}%</div>
            <div style={styles.statLabel}>Model Accuracy</div>
          </div>
        </div>
      )}

      {/* Form */}
      <div style={styles.card}>
        <h3 style={{ marginTop: 0 }}>{editId ? '✏️ Edit Student' : '➕ Add Student'}</h3>
        <form onSubmit={submit} style={styles.form}>
          <input
            style={styles.input} name="name"
            placeholder="Full Name" value={form.name}
            onChange={handle} required
          />
          <input
            style={styles.input} name="study_hours" type="number"
            step="0.5" min="0" max="24"
            placeholder="Study Hours/Week" value={form.study_hours}
            onChange={handle} required
          />
          <input
            style={styles.input} name="attendance" type="number"
            min="0" max="100"
            placeholder="Attendance %" value={form.attendance}
            onChange={handle} required
          />
          <button style={styles.btn} type="submit" disabled={loading}>
            {loading ? 'Processing...' : editId ? 'Update & Re-predict' : 'Predict & Save'}
          </button>
          {editId && (
            <button type="button" onClick={cancel} style={styles.cancelBtn}>
              Cancel
            </button>
          )}
        </form>
        {error && <p style={{ color: 'red', marginTop: 8 }}>{error}</p>}
      </div>

      {/* Table */}
      <div style={styles.card}>
        <h3 style={{ marginTop: 0 }}>Student Records</h3>
        {students.length === 0 ? (
          <p style={{ color: '#888' }}>No students yet. Add one above!</p>
        ) : (
          <table style={styles.table}>
            <thead>
              <tr style={{ background: '#f4f6f8' }}>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Study Hours</th>
                <th style={styles.th}>Attendance %</th>
                <th style={styles.th}>AI Prediction</th>
                <th style={styles.th}>Confidence</th>
                <th style={styles.th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {students.map(s => (
                <tr key={s.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={styles.td}>{s.name}</td>
                  <td style={styles.td}>{s.study_hours}h</td>
                  <td style={styles.td}>{s.attendance}%</td>
                  <td style={styles.td}>
                    <span style={{
                      padding: '3px 10px',
                      borderRadius: 12,
                      fontSize: 13,
                      fontWeight: 'bold',
                      background: s.prediction === 'Pass' ? '#e8f8e8' : '#fde8e8',
                      color: s.prediction === 'Pass' ? 'green' : 'red',
                    }}>
                      {s.prediction}
                    </span>
                  </td>
                  <td style={styles.td}>{s.confidence}%</td>
                  <td style={styles.td}>
                    <button onClick={() => startEdit(s)} style={styles.editBtn}>Edit</button>
                    <button onClick={() => remove(s.id)} style={styles.deleteBtn}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: { minHeight: '100vh', background: '#f0f2f5', padding: 20 },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#2c3e50', color: '#fff', padding: '14px 24px', borderRadius: 8, marginBottom: 20 },
  logoutBtn: { background: 'transparent', color: '#fff', border: '1px solid #fff', borderRadius: 4, padding: '4px 10px', cursor: 'pointer' },
  statsBar: { display: 'flex', gap: 16, marginBottom: 20 },
  statCard: { flex: 1, background: '#fff', padding: 16, borderRadius: 8, textAlign: 'center', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  statNum: { fontSize: 28, fontWeight: 'bold', color: '#2c3e50' },
  statLabel: { fontSize: 12, color: '#888', marginTop: 4 },
  card: { background: '#fff', padding: 24, borderRadius: 8, marginBottom: 20, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  form: { display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' },
  input: { padding: 9, border: '1px solid #ddd', borderRadius: 4, fontSize: 14, flex: 1, minWidth: 140 },
  btn: { padding: '9px 18px', background: '#3498db', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' },
  cancelBtn: { padding: '9px 14px', background: '#95a5a6', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { padding: '10px 14px', textAlign: 'left', fontSize: 13, color: '#555' },
  td: { padding: '10px 14px', fontSize: 14 },
  editBtn: { padding: '4px 10px', background: '#f39c12', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', marginRight: 6 },
  deleteBtn: { padding: '4px 10px', background: '#e74c3c', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' },
};

export default Dashboard;