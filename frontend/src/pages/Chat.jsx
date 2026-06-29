import React, { useState, useEffect, useRef } from 'react';
import client from '../api/client';
import { v4 as uuidv4 } from 'uuid';
import { Send } from 'lucide-react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hello! I am Aria, your virtual assistant. How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState('');
  const messagesEndRef = useRef(null);

  useEffect(() => {
    setSessionId(uuidv4());
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const res = await client.post('/chat', {
        session_id: sessionId,
        message: userMsg
      });
      setMessages(prev => [...prev, { role: 'assistant', text: res.data.reply }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'assistant', text: "Sorry, I couldn't reach the server right now." }]);
    } finally {
      setLoading(false);
    }
  };

  const renderMarkdown = (text) => {
    const rawMarkup = marked(text, { breaks: true });
    const cleanMarkup = DOMPurify.sanitize(rawMarkup);
    return { __html: cleanMarkup };
  };

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto bg-gray-50">
      <header className="bg-blue-600 text-white p-4 text-center font-bold shadow-md">
        Company Assistant
      </header>
      
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-br-none' : 'bg-white shadow text-gray-800 rounded-bl-none'}`}>
              <div className="prose prose-sm max-w-none" dangerouslySetInnerHTML={renderMarkdown(msg.text)} />
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white shadow text-gray-800 p-3 rounded-lg rounded-bl-none italic text-sm">
              Typing...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      <footer className="p-4 bg-white border-t">
        <form onSubmit={handleSend} className="flex gap-2">
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="flex-1 p-2 border rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Type your message here..."
            disabled={loading}
          />
          <button 
            type="submit" 
            className="bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center w-10 h-10"
            disabled={loading}
          >
            <Send size={18} />
          </button>
        </form>
        <div className="text-center text-xs text-gray-400 mt-2">
          Powered by Your Company
        </div>
      </footer>
    </div>
  );
}
