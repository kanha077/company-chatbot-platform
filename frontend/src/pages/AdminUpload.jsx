import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import client from '../api/client';

export default function AdminUpload() {
  const [status, setStatus] = useState('');
  const [loading, setLoading] = useState(false);

  const onDrop = async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    
    const file = acceptedFiles[0];
    const formData = new FormData();
    formData.append('file', file);
    
    setLoading(true);
    setStatus('Uploading and processing...');
    
    try {
      const res = await client.post('/admin/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setStatus(res.data.message);
    } catch (err) {
      console.error(err);
      setStatus('Failed to upload PDF. Check console.');
    } finally {
      setLoading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: {'application/pdf': ['.pdf']} });

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Admin: Knowledge Upload</h1>
      
      <div 
        {...getRootProps()} 
        className={`border-2 border-dashed p-10 text-center rounded-lg cursor-pointer ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-gray-50'}`}
      >
        <input {...getInputProps()} />
        {
          isDragActive ?
            <p>Drop the PDF here ...</p> :
            <p>Drag & drop a company PDF here, or click to select file</p>
        }
      </div>

      {loading && <p className="mt-4 text-blue-600">Processing file. This may take a moment...</p>}
      {status && !loading && <div className="mt-4 p-4 bg-green-100 text-green-800 rounded">{status}</div>}
    </div>
  );
}
