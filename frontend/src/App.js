import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [students, setStudents] = useState([]);
  const [formData, setFormData] = useState({ name: '', study_hours: '', attendance: '' });

  // 1. Fetch all students from our Django API
  const fetchStudents = async () => {
    const res = await axios.get('http://127.0.0.1:8000/api/students/');
    setStudents(res.data);
  };

  useEffect(() => { fetchStudents(); }, []);

  // 2. Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    await axios.post('http://127.0.0.1:8000/api/students/', formData);
    setFormData({ name: '', study_hours: '', attendance: '' }); // Reset form
    fetchStudents(); // Refresh the list with the new AI prediction
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>EduPredict: AI Student Assistant</h1>
      
      {/* Task 1: The Input Form */}
      <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
        <input placeholder="Name" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
        <input type="number" placeholder="Study Hours" value={formData.study_hours} onChange={e => setFormData({...formData, study_hours: e.target.value})} required />
        <input type="number" placeholder="Attendance %" value={formData.attendance} onChange={e => setFormData({...formData, attendance: e.target.value})} required />
        <button type="submit">Predict Success</button>
      </form>

      {/* Task 2: The Data Table */}
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Name</th>
            <th>Study Hours</th>
            <th>Attendance %</th>
            <th>AI Prediction</th>
          </tr>
        </thead>
        <tbody>
          {students.map(s => (
            <tr key={s.id}>
              <td>{s.name}</td>
              <td>{s.study_hours}</td>
              <td>{s.attendance}%</td>
              <td style={{ fontWeight: 'bold', color: s.prediction === 'Pass' ? 'green' : 'red' }}>
                {s.prediction}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;