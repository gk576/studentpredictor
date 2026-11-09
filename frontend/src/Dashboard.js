import { useCallback, useEffect, useState } from 'react';
import {
  createStudent,
  deleteStudent,
  getCourses,
  getStats,
  getStudents,
  predict,
  updateStudent,
} from './api';

const EMPTY_FORM = {
  student_number: '',
  full_name: '',
  email: '',
  course: '',
  study_hours: '',
  attendance: '',
  previous_score: '',
  actual_result: '',
};

const EMPTY_CHECK = {
  study_hours: '',
  attendance: '',
  previous_score: '',
};

const riskColour = risk => {
  if (risk === 'Low') return { background: '#e8f8e8', color: '#1e7a1e' };
  if (risk === 'Medium') return { background: '#fff4e0', color: '#a86500' };
  return { background: '#fde8e8', color: '#c0392b' };
};

function Dashboard({ user, onLogout }) {
  const [students, setStudents] = useState([]);
  const [stats, setStats] = useState(null);
  const [courses, setCourses] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [check, setCheck] = useState(EMPTY_CHECK);
  const [checkResult, setCheckResult] = useState(null);
  const [editId, setEditId] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [checkLoading, setCheckLoading] = useState(false);

  const load = useCallback(async () => {
    try {
      const [studentRes, statsRes, courseRes] = await Promise.all([
        getStudents(),
        getStats(),
        getCourses(),
      ]);
      setStudents(studentRes.data);
      setStats(statsRes.data);
      setCourses(courseRes.data);
      setError('');
    } catch (err) {
      if (err.response?.status === 401) {
        onLogout();
      } else {
        setError('Could not load data. Is the Django server running on port 8000?');
      }
    }
  }, [onLogout]);

  useEffect(() => {
    load();
  }, [load]);

  const handle = e => setForm({ ...form, [e.target.name]: e.target.value });
  const handleCheck = e => setCheck({ ...check, [e.target.name]: e.target.value });

  const buildPayload = () => ({
    student_number: form.student_number.trim(),
    full_name: form.full_name.trim(),
    email: form.email.trim(),
    course: form.course ? Number(form.course) : null,
    study_hours: Number(form.study_hours),
    attendance: Number(form.attendance),
    previous_score: Number(form.previous_score),
    actual_result: form.actual_result || '',
  });

  const submit = async e => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const payload = buildPayload();
      if (editId) {
        await updateStudent(editId, payload);
        setEditId(null);
      } else {
        await createStudent(payload);
      }
      setForm(EMPTY_FORM);
      await load();
    } catch (err) {
      const detail = err.response?.data;
      setError(
        detail
          ? `Failed to save: ${JSON.stringify(detail)}`
          : 'Failed to save. Check your inputs.'
      );
    }
    setLoading(false);
  };

  const startEdit = student => {
    setEditId(student.id);
    setForm({
      student_number: student.student_number,
      full_name: student.full_name,
      email: student.email || '',
      course: student.course || '',
      study_hours: student.study_hours,
      attendance: student.attendance,
      previous_score: student.previous_score,
      actual_result: student.actual_result || '',
    });
  };

  const remove = async id => {
    if (window.confirm('Delete this student and their prediction history?')) {
      await deleteStudent(id);
      await load();
    }
  };

  const cancel = () => {
    setEditId(null);
    setForm(EMPTY_FORM);
    setError('');
  };

  const runQuickCheck = async e => {
    e.preventDefault();
    setError('');
    setCheckLoading(true);
    try {
      const res = await predict({
        study_hours: Number(check.study_hours),
        attendance: Number(check.attendance),
        previous_score: Number(check.previous_score),
      });
      setCheckResult(res.data);
    } catch (err) {
      setError('Instant prediction failed. Check the three input values.');
    }
    setCheckLoading(false);
  };

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div>
          <h2 style={{ margin: 0 }}>EduPredict</h2>
          <div style={styles.headerSub}>Student Performance Predictor · local MVP</div>
        </div>
        <span>
          Welcome, <b>{user}</b> &nbsp;
          <button onClick={onLogout} style={styles.logoutBtn}>Logout</button>
        </span>
      </div>

      {error && <div style={styles.errorBox}>{error}</div>}

      {stats && (
        <>
          <div style={styles.statsBar}>
            <div style={styles.statCard}>
              <div style={styles.statNum}>{stats.total_students}</div>
              <div style={styles.statLabel}>Student records</div>
            </div>
            <div style={styles.statCard}>
              <div style={{ ...styles.statNum, color: '#1e7a1e' }}>{stats.pass_count}</div>
              <div style={styles.statLabel}>Predicted pass</div>
            </div>
            <div style={styles.statCard}>
              <div style={{ ...styles.statNum, color: '#c0392b' }}>{stats.fail_count}</div>
              <div style={styles.statLabel}>Predicted fail</div>
            </div>
            <div style={styles.statCard}>
              <div style={{ ...styles.statNum, color: '#a86500' }}>{stats.high_risk_count}</div>
              <div style={styles.statLabel}>High risk</div>
            </div>
            <div style={styles.statCard}>
              <div style={{ ...styles.statNum, color: '#3498db' }}>{stats.accuracy}%</div>
              <div style={styles.statLabel}>Test accuracy</div>
            </div>
          </div>

          <div style={styles.card}>
            <div style={styles.metricsHeader}>
              <h3 style={{ margin: 0 }}>Model evaluation</h3>
              <span style={styles.versionBadge}>{stats.model_version}</span>
            </div>
            <div style={styles.metricsGrid}>
              <Metric label="Precision" value={`${stats.precision}%`} />
              <Metric label="Recall" value={`${stats.recall}%`} />
              <Metric label="Training rows" value={stats.dataset_samples} />
            </div>
            <div style={styles.importanceRow}>
              <span style={styles.importanceLabel}>Feature importance:</span>
              {Object.entries(stats.feature_importance).map(([name, value]) => (
                <span key={name} style={styles.importancePill}>
                  {name.replace('_', ' ')} · {Math.round(value * 100)}%
                </span>
              ))}
            </div>
          </div>
        </>
      )}

      <div style={styles.twoColumn}>
        <div style={styles.card}>
          <h3 style={{ marginTop: 0 }}>{editId ? 'Edit student' : 'Add student'}</h3>
          <form onSubmit={submit} style={styles.form}>
            <input
              style={styles.input} name="student_number" placeholder="Student number (e.g. STU0321)"
              value={form.student_number} onChange={handle} required
            />
            <input
              style={styles.input} name="full_name" placeholder="Full name"
              value={form.full_name} onChange={handle} required
            />
            <input
              style={styles.input} name="email" type="email" placeholder="Email (optional)"
              value={form.email} onChange={handle}
            />
            <select style={styles.input} name="course" value={form.course} onChange={handle}>
              <option value="">Course (optional)</option>
              {courses.map(course => (
                <option key={course.id} value={course.id}>
                  {course.code} - {course.title}
                </option>
              ))}
            </select>
            <input
              style={styles.input} name="study_hours" type="number" step="0.5" min="0" max="168"
              placeholder="Study hours / week" value={form.study_hours} onChange={handle} required
            />
            <input
              style={styles.input} name="attendance" type="number" min="0" max="100"
              placeholder="Attendance %" value={form.attendance} onChange={handle} required
            />
            <input
              style={styles.input} name="previous_score" type="number" step="0.5" min="0" max="100"
              placeholder="Previous score %" value={form.previous_score} onChange={handle} required
            />
            <select
              style={styles.input} name="actual_result" value={form.actual_result} onChange={handle}
            >
              <option value="">Actual result (if known)</option>
              <option value="Pass">Pass</option>
              <option value="Fail">Fail</option>
            </select>
            <button style={styles.btn} type="submit" disabled={loading}>
              {loading ? 'Processing...' : editId ? 'Update & re-predict' : 'Predict & save'}
            </button>
            {editId && (
              <button type="button" onClick={cancel} style={styles.cancelBtn}>Cancel</button>
            )}
          </form>
        </div>

        <div style={styles.card}>
          <h3 style={{ marginTop: 0 }}>Instant AI check</h3>
          <p style={styles.hint}>Runs the model without saving a student record.</p>
          <form onSubmit={runQuickCheck} style={styles.form}>
            <input
              style={styles.input} name="study_hours" type="number" step="0.5" min="0" max="168"
              placeholder="Study hours / week" value={check.study_hours}
              onChange={handleCheck} required
            />
            <input
              style={styles.input} name="attendance" type="number" min="0" max="100"
              placeholder="Attendance %" value={check.attendance} onChange={handleCheck} required
            />
            <input
              style={styles.input} name="previous_score" type="number" step="0.5" min="0" max="100"
              placeholder="Previous score %" value={check.previous_score}
              onChange={handleCheck} required
            />
            <button style={styles.btn} type="submit" disabled={checkLoading}>
              {checkLoading ? 'Predicting...' : 'Run prediction'}
            </button>
          </form>
          {checkResult && (
            <div style={styles.resultBox}>
              <div style={styles.resultMain}>
                <span style={{
                  ...styles.resultBadge,
                  background: checkResult.prediction === 'Pass' ? '#e8f8e8' : '#fde8e8',
                  color: checkResult.prediction === 'Pass' ? '#1e7a1e' : '#c0392b',
                }}>
                  {checkResult.prediction}
                </span>
                <span style={{ ...styles.resultBadge, ...riskColour(checkResult.risk_level) }}>
                  {checkResult.risk_level} risk
                </span>
              </div>
              <div style={styles.resultDetails}>
                Pass probability: <b>{Math.round(checkResult.probability * 100)}%</b> ·
                Confidence: <b>{checkResult.confidence}%</b>
              </div>
            </div>
          )}
        </div>
      </div>

      <div style={styles.card}>
        <h3 style={{ marginTop: 0 }}>Student records</h3>
        {students.length === 0 ? (
          <p style={{ color: '#888' }}>No students yet. Add one above.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={styles.table}>
              <thead>
                <tr style={{ background: '#f4f6f8' }}>
                  <th style={styles.th}>Student</th>
                  <th style={styles.th}>Course</th>
                  <th style={styles.th}>Study h/wk</th>
                  <th style={styles.th}>Attendance</th>
                  <th style={styles.th}>Previous score</th>
                  <th style={styles.th}>AI prediction</th>
                  <th style={styles.th}>Actual</th>
                  <th style={styles.th}>Confidence</th>
                  <th style={styles.th}>Risk</th>
                  <th style={styles.th}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {students.map(student => (
                  <tr key={student.id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={styles.td}>
                      <b>{student.full_name}</b>
                      <div style={styles.small}>{student.student_number}</div>
                    </td>
                    <td style={styles.td}>{student.course_detail?.code || '—'}</td>
                    <td style={styles.td}>{student.study_hours}h</td>
                    <td style={styles.td}>{student.attendance}%</td>
                    <td style={styles.td}>{student.previous_score}%</td>
                    <td style={styles.td}>
                      <span style={{
                        padding: '3px 10px',
                        borderRadius: 12,
                        fontSize: 13,
                        fontWeight: 'bold',
                        background: student.prediction === 'Pass' ? '#e8f8e8' : '#fde8e8',
                        color: student.prediction === 'Pass' ? '#1e7a1e' : '#c0392b',
                      }}>
                        {student.prediction}
                      </span>
                    </td>
                    <td style={styles.td}>
                      <span style={{
                        color:
                          student.actual_result && student.actual_result !== student.prediction
                            ? '#c0392b'
                            : '#52606d',
                        fontWeight: student.actual_result ? 'bold' : 'normal',
                      }}>
                        {student.actual_result || '—'}
                      </span>
                    </td>
                    <td style={styles.td}>{student.confidence}%</td>
                    <td style={styles.td}>
                      <span style={{ ...styles.riskBadge, ...riskColour(student.risk_level) }}>
                        {student.risk_level}
                      </span>
                    </td>
                    <td style={styles.td}>
                      <button onClick={() => startEdit(student)} style={styles.editBtn}>Edit</button>
                      <button onClick={() => remove(student.id)} style={styles.deleteBtn}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div style={styles.metric}>
      <div style={styles.metricValue}>{value}</div>
      <div style={styles.metricLabel}>{label}</div>
    </div>
  );
}

const styles = {
  page: { minHeight: '100vh', background: '#f0f2f5', padding: 20, fontFamily: 'system-ui, sans-serif' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#2c3e50', color: '#fff', padding: '14px 24px', borderRadius: 8, marginBottom: 20, flexWrap: 'wrap', gap: 10 },
  headerSub: { fontSize: 12, color: '#cbd5e1', marginTop: 3 },
  logoutBtn: { background: 'transparent', color: '#fff', border: '1px solid #fff', borderRadius: 4, padding: '4px 10px', cursor: 'pointer' },
  errorBox: { background: '#fde8e8', color: '#c0392b', padding: '10px 14px', borderRadius: 6, marginBottom: 16, fontSize: 14 },
  statsBar: { display: 'flex', gap: 12, marginBottom: 20, flexWrap: 'wrap' },
  statCard: { flex: '1 1 150px', background: '#fff', padding: 16, borderRadius: 8, textAlign: 'center', boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  statNum: { fontSize: 28, fontWeight: 'bold', color: '#2c3e50' },
  statLabel: { fontSize: 12, color: '#888', marginTop: 4 },
  card: { background: '#fff', padding: 24, borderRadius: 8, marginBottom: 20, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' },
  twoColumn: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: 20 },
  metricsHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14, flexWrap: 'wrap', gap: 8 },
  versionBadge: { fontSize: 12, background: '#eef2f7', color: '#52606d', padding: '3px 8px', borderRadius: 10 },
  metricsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(110px, 1fr))', gap: 10 },
  metric: { background: '#f8fafc', borderRadius: 6, padding: '8px 10px', textAlign: 'center' },
  metricValue: { fontSize: 17, fontWeight: 'bold', color: '#2c3e50' },
  metricLabel: { fontSize: 11, color: '#7b8794', marginTop: 2 },
  importanceRow: { display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap', marginTop: 14 },
  importanceLabel: { fontSize: 12, color: '#7b8794' },
  importancePill: { fontSize: 12, background: '#f0f4ff', color: '#334e8c', padding: '3px 8px', borderRadius: 10 },
  form: { display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center' },
  input: { padding: 9, border: '1px solid #ddd', borderRadius: 4, fontSize: 14, flex: '1 1 150px', minWidth: 130, boxSizing: 'border-box' },
  btn: { padding: '9px 18px', background: '#3498db', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', fontWeight: 'bold' },
  cancelBtn: { padding: '9px 14px', background: '#95a5a6', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' },
  hint: { color: '#7b8794', fontSize: 13, marginTop: 0, marginBottom: 12 },
  resultBox: { marginTop: 16, padding: 14, background: '#f8fafc', borderRadius: 6, border: '1px solid #e5e9f0' },
  resultMain: { display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 },
  resultBadge: { padding: '4px 12px', borderRadius: 12, fontSize: 13, fontWeight: 'bold' },
  resultDetails: { fontSize: 13, color: '#52606d' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { padding: '10px 12px', textAlign: 'left', fontSize: 13, color: '#555', whiteSpace: 'nowrap' },
  td: { padding: '10px 12px', fontSize: 14 },
  small: { fontSize: 11, color: '#888' },
  riskBadge: { padding: '3px 8px', borderRadius: 10, fontSize: 12, fontWeight: 'bold' },
  editBtn: { padding: '4px 10px', background: '#f39c12', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer', marginRight: 6 },
  deleteBtn: { padding: '4px 10px', background: '#e74c3c', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' },
};

export default Dashboard;
