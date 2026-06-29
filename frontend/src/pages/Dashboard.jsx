import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import { Plus, Settings, MessageSquare, Code, Upload, LogOut } from 'lucide-react';
import { auth } from '../firebase';
import { onAuthStateChanged, signOut } from 'firebase/auth';

export default function Dashboard() {
  const [bots, setBots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newBotName, setNewBotName] = useState('');
  const [newCompanyName, setNewCompanyName] = useState('');
  const [activeBot, setActiveBot] = useState(null);
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (currentUser) {
        setUser(currentUser);
        fetchBots(currentUser);
      } else {
        navigate('/auth');
      }
    });
    return () => unsubscribe();
  }, [navigate]);

  const fetchBots = async (currentUser) => {
    try {
      const token = await currentUser.getIdToken();
      const res = await client.get('/bots', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBots(res.data);
      if (res.data.length > 0 && !activeBot) {
        setActiveBot(res.data[0]);
      }
    } catch (err) {
      console.error("Failed to fetch bots", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateBot = async (e) => {
    e.preventDefault();
    try {
      const token = await user.getIdToken();
      await client.post('/bots', {
        bot_name: newBotName,
        company_name: newCompanyName
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowCreate(false);
      setNewBotName('');
      setNewCompanyName('');
      fetchBots(user);
    } catch (err) {
      console.error("Failed to create bot", err);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file || !activeBot) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    setUploadStatus('Uploading...');
    try {
      const token = await user.getIdToken();
      const res = await client.post(`/admin/upload-pdf/${activeBot.id}`, formData, {
        headers: { 
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      setUploadStatus(res.data.message);
      setFile(null);
    } catch (error) {
      setUploadStatus('Upload failed. Please try again.');
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
    navigate('/auth');
  };

  if (loading) return <div className="p-10 text-center">Loading...</div>;

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r shadow-sm flex flex-col">
        <div className="p-4 border-b flex justify-between items-center">
          <h1 className="text-xl font-bold text-gray-800">SaaS Dashboard</h1>
          <button onClick={handleLogout} className="text-gray-500 hover:text-red-500" title="Logout">
            <LogOut size={18} />
          </button>
        </div>
        <div className="p-4 flex-1 overflow-y-auto">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Your Chatbots</h2>
          <ul className="space-y-2">
            {bots.map(bot => (
              <li key={bot.id}>
                <button 
                  onClick={() => setActiveBot(bot)}
                  className={`w-full text-left px-3 py-2 rounded-md ${activeBot?.id === bot.id ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-700 hover:bg-gray-50'}`}
                >
                  {bot.company_name} - {bot.bot_name}
                </button>
              </li>
            ))}
          </ul>
          <button 
            onClick={() => setShowCreate(true)}
            className="mt-4 w-full flex items-center justify-center gap-2 px-4 py-2 border border-dashed border-gray-300 rounded-md text-sm text-gray-600 hover:border-gray-400 hover:text-gray-800"
          >
            <Plus size={16} /> New Chatbot
          </button>
        </div>
        <div className="p-4 border-t text-xs text-gray-400 truncate">
          Logged in as: {user?.email}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {showCreate ? (
          <div className="p-8 max-w-2xl mx-auto mt-10 bg-white rounded-xl shadow-sm border">
            <h2 className="text-2xl font-bold mb-6">Create New Chatbot</h2>
            <form onSubmit={handleCreateBot} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Company Name</label>
                <input required type="text" value={newCompanyName} onChange={e => setNewCompanyName(e.target.value)} className="w-full p-2 border rounded-md" placeholder="e.g. Acme Corp" />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Bot Name</label>
                <input required type="text" value={newBotName} onChange={e => setNewBotName(e.target.value)} className="w-full p-2 border rounded-md" placeholder="e.g. AcmeBot" />
              </div>
              <div className="flex gap-4 pt-4">
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Create</button>
                <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-md">Cancel</button>
              </div>
            </form>
          </div>
        ) : activeBot ? (
          <div className="p-8">
            <div className="mb-8 flex justify-between items-end">
              <div>
                <h2 className="text-3xl font-bold text-gray-900">{activeBot.company_name} Dashboard</h2>
                <p className="text-gray-500 mt-1">Manage your bot: {activeBot.bot_name}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Knowledge Base */}
              <div className="bg-white p-6 rounded-xl shadow-sm border">
                <div className="flex items-center gap-2 mb-4">
                  <Upload className="text-blue-600" />
                  <h3 className="text-lg font-semibold">Knowledge Base</h3>
                </div>
                <p className="text-sm text-gray-500 mb-4">Upload a PDF to train {activeBot.bot_name}.</p>
                <form onSubmit={handleUpload} className="space-y-4">
                  <input type="file" accept=".pdf" onChange={e => setFile(e.target.files[0])} className="w-full p-2 border rounded-md" />
                  <button type="submit" className="w-full py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Train Bot</button>
                  {uploadStatus && <p className="text-sm text-green-600 mt-2">{uploadStatus}</p>}
                </form>
              </div>

              {/* Embed Code */}
              <div className="bg-white p-6 rounded-xl shadow-sm border">
                <div className="flex items-center gap-2 mb-4">
                  <Code className="text-blue-600" />
                  <h3 className="text-lg font-semibold">Embed Code</h3>
                </div>
                <p className="text-sm text-gray-500 mb-4">Copy this code into your website's HTML to embed the chat widget.</p>
                <div className="bg-gray-900 rounded-md p-4 overflow-x-auto">
                  <pre className="text-green-400 text-xs">
                    {`<script src="https://your-domain.com/widget.js" data-bot-id="${activeBot.id}"></script>`}
                  </pre>
                </div>
              </div>
              
              {/* Test Bot */}
              <div className="bg-white p-6 rounded-xl shadow-sm border md:col-span-2">
                <div className="flex items-center gap-2 mb-4">
                  <MessageSquare className="text-blue-600" />
                  <h3 className="text-lg font-semibold">Test your bot</h3>
                </div>
                <p className="text-sm text-gray-500 mb-4">Open the chat interface to test {activeBot.bot_name} directly.</p>
                <a href={`/chat/${activeBot.id}`} target="_blank" rel="noreferrer" className="inline-block px-4 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50">
                  Open Chat Interface
                </a>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-gray-500">
            <MessageSquare size={48} className="mb-4 text-gray-300" />
            <p>You don't have any chatbots yet.</p>
            <button onClick={() => setShowCreate(true)} className="mt-4 text-blue-600 font-medium">Create your first bot</button>
          </div>
        )}
      </div>
    </div>
  );
}
