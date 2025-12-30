import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Landing from './pages/Landing';
import Trades from './pages/Trades';
import RobotCreation from './pages/RobotCreation';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Admin from './pages/Admin';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Robots from './pages/Robots';
import Social from './pages/Social';

const App = () => {
  return (
    <Router>
      <div className="flex bg-background min-h-screen">
        <SidebarWrapper />
        <main className="flex-1 min-w-0">
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/trades" element={<Trades />} />
            <Route path="/robots" element={<RobotCreation />} />
            <Route path="/marketplace" element={<Robots />} />
            <Route path="/social" element={<Social />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/chat" element={<Chat />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/profile" element={<Profile />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

const SidebarWrapper = () => {
  // Hide sidebar on login/signup pages
  const location = useLocation();
  const hideSidebar = location.pathname === '/login' || location.pathname === '/signup';
  if (hideSidebar) return null;
  return <Sidebar />;
};

export default App;
