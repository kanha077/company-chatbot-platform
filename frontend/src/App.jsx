import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import Chat from './pages/Chat';
import AdminUpload from './pages/AdminUpload';

function App() {
  return (
    <BrowserRouter>
      <div>
        <nav className="bg-gray-800 text-white p-2 flex gap-4 text-sm hidden">
          {/* Un-hide this nav in development to switch between views */}
          <Link to="/">Chat</Link>
          <Link to="/admin">Admin</Link>
        </nav>
        <Routes>
          <Route path="/" element={<Chat />} />
          <Route path="/admin" element={<AdminUpload />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
