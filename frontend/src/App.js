import React from 'react';
import HyperPage from './pages/HyperPage';
import { Toaster } from 'sonner';
import './App.css';

function App() {
  return (
    <div className="App">
      <HyperPage />
      <Toaster
        position="bottom-right"
        theme="dark"
        toastOptions={{
          style: {
            background: '#0a0e1a',
            border: '1px solid rgba(0,240,255,0.15)',
            color: '#00F0FF',
            borderRadius: 0,
            fontFamily: 'JetBrains Mono, monospace',
            fontSize: '11px',
          }
        }}
      />
    </div>
  );
}

export default App;