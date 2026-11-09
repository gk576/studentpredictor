import { useState } from 'react';
import Login from './Login';
import Dashboard from './Dashboard';

function App() {
  const [user, setUser] = useState(localStorage.getItem('user') || null);

  const handleLogin = (username) => {
    localStorage.setItem('user', username);
    setUser(username);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return user
    ? <Dashboard user={user} onLogout={handleLogout} />
    : <Login onLogin={handleLogin} />;
}

export default App;