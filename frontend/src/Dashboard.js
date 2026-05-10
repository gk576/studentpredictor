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
    } catch (err) {
      if (err.response && err.response.status === 401) onLogout();
      else setError('Failed to load data. Please try again.');
    }
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
    <div style={{minHeight:'100vh',background:'#f0f2f5',padding:20}}>
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',background:'#2c3e50',color:'#fff',padding:'14px 24px',borderRadius:8,marginBottom:20}}>
        <h2 style={{margin:0}}>EduPredict Dashboard</h2>
        <span>Welcome, <b>{user}</b> &nbsp;
          <button onClick={onLogout} style={{background:'transparent',color:'#fff',border:'1px solid #fff',borderRadius:4,padding:'4px 10px',cursor:'pointer'}}>Logout</button>
        </span>
      </div>

      {stats && (
        <div style={{display:'flex',gap:16,marginBottom:20}}>
          {[['Total Students',stats.total_students,'#2c3e50'],['Passing',stats.pass_count,'green'],['At Risk',stats.fail_count,'red'],['Model Accuracy',stats.accuracy+'%','#3498db']].map(([label,val,color])=>(
            <div key={label} style={{flex:1,background:'#fff',padding:16,borderRadius:8,textAlign:'center',boxShadow:'0 1px 4px rgba(0,0,0,0.08)'}}>
              <div style={{fontSize:28,fontWeight:'bold',color}}>{val}</div>
              <div style={{fontSize:12,color:'#888',marginTop:4}}>{label}</div>
            </div>
          ))}
        </div>
      )}

      <div style={{background:'#fff',padding:24,borderRadius:8,marginBottom:20,boxShadow:'0 1px 4px rgba(0,0,0,0.08)'}}>
        <h3 style={{marginTop:0}}>{editId ? '✏️ Edit Student' : '➕ Add Student'}</h3>
        <form onSubmit={submit} style={{display:'flex',gap:10,flexWrap:'wrap',alignItems:'center'}}>
          <input style={{padding:9,border:'1px solid #ddd',borderRadius:4,fontSize:14,flex:1,minWidth:140}} name="name" placeholder="Full Name" value={form.name} onChange={handle} required />
          <input style={{padding:9,border:'1px solid #ddd',borderRadius:4,fontSize:14,flex:1,minWidth:140}} name="study_hours" type="number" step="0.5" min="0" max="24" placeholder="Study Hours/Week" value={form.study_hours} onChange={handle} required />
          <input style={{padding:9,border:'1px solid #ddd',borderRadius:4,fontSize:14,flex:1,minWidth:140}} name="attendance" type="number" min="0" max="100" placeholder="Attendance %" value={form.attendance} onChange={handle} required />
          <button style={{padding:'9px 18px',background:'#3498db',color:'#fff',border:'none',borderRadius:4,cursor:'pointer',fontWeight:'bold'}} type="submit" disabled={loading}>
            {loading ? 'Processing...' : editId ? 'Update & Re-predict' : 'Predict & Save'}
          </button>
          {editId && <button type="button" onClick={cancel} style={{padding:'9px 14px',background:'#95a5a6',color:'#fff',border:'none',borderRadius:4,cursor:'pointer'}}>Cancel</button>}
        </form>
        {error && <p style={{color:'red',marginTop:8}}>{error}</p>}
      </div>

      <div style={{background:'#fff',padding:24,borderRadius:8,boxShadow:'0 1px 4px rgba(0,0,0,0.08)'}}>
        <h3 style={{marginTop:0}}>Student Records</h3>
        {students.length === 0 ? <p style={{color:'#888'}}>No students yet. Add one above!</p> : (
          <table style={{width:'100%',borderCollapse:'collapse'}}>
            <thead>
              <tr style={{background:'#f4f6f8'}}>
                {['Name','Study Hours','Attendance %','AI Prediction','Confidence','Actions'].map(h=>(
                  <th key={h} style={{padding:'10px 14px',textAlign:'left',fontSize:13,color:'#555'}}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {students.map(s => (
                <tr key={s.id} style={{borderBottom:'1px solid #eee'}}>
                  <td style={{padding:'10px 14px',fontSize:14}}>{s.name}</td>
                  <td style={{padding:'10px 14px',fontSize:14}}>{s.study_hours}h</td>
                  <td style={{padding:'10px 14px',fontSize:14}}>{s.attendance}%</td>
                  <td style={{padding:'10px 14px',fontSize:14}}>
                    <span style={{padding:'3px 10px',borderRadius:12,fontSize:13,fontWeight:'bold',background:s.prediction==='Pass'?'#e8f8e8':'#fde8e8',color:s.prediction==='Pass'?'green':'red'}}>
                      {s.prediction}
                    </span>
                  </td>
                  <td style={{padding:'10px 14px',fontSize:14}}>{s.confidence}%</td>
                  <td style={{padding:'10px 14px',fontSize:14}}>
                    <button onClick={()=>startEdit(s)} style={{padding:'4px 10px',background:'#f39c12',color:'#fff',border:'none',borderRadius:4,cursor:'pointer',marginRight:6}}>Edit</button>
                    <button onClick={()=>remove(s.id)} style={{padding:'4px 10px',background:'#e74c3c',color:'#fff',border:'none',borderRadius:4,cursor:'pointer'}}>Delete</button>
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

export default Dashboard;
