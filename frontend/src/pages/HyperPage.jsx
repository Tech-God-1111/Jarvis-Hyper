import React, { useState } from 'react';
import { toast } from 'sonner';
import Layout from '../components/Layout';
import Telemetry from '../components/Telemetry';
import ChatPanel from '../components/ChatPanel';
import DataPanel from '../components/DataPanel';
import { streamChat, playAudio } from '../lib/api';

export default function HyperPage() {
  const [messages, setMessages] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const [attachment, setAttachment] = useState(null);   // ← NEW: holds the file

  const sendMessage = async (text) => {
    if (!text.trim() || busy) return;

    setMessages(prev => [...prev, {
      role: 'user',
      content: text,
      hasAttachment: !!attachment,
    }]);
    setInput('');
    setBusy(true);

    try {
      let fullResponse = '';
      setMessages(prev => [...prev, { role: 'assistant', content: '', streaming: true }]);

      await streamChat({
        message: text,
        attachment: attachment,          // ← SEND FILE TO BACKEND
        onDelta: (chunk) => {
          fullResponse += chunk;
          setMessages(prev => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.streaming) last.content = fullResponse;
            return updated;
          });
        },
        onVoice: async (audioData) => {
          try {
            const audioBuffer = new Uint8Array(audioData).buffer;
            playAudio(audioBuffer);
            setIsSpeaking(true);
            setTimeout(() => setIsSpeaking(false), 2000);
          } catch (err) {
            console.error('Audio playback error:', err);
          }
        },
        onDone: () => {
          setMessages(prev => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last) last.streaming = false;
            return updated;
          });
          setBusy(false);
          setAttachment(null);   // Clear file after sending
        },
        onError: (err) => {
          toast.error('Failed: ' + err.message);
          setMessages(prev => {
            const updated = [...prev];
            const last = updated[updated.length - 1];
            if (last && last.streaming) {
              last.content = '[Error: ' + err.message + ']';
              last.streaming = false;
            }
            return updated;
          });
          setBusy(false);
        }
      });
    } catch (err) {
      toast.error('Communication error: ' + err.message);
      setBusy(false);
    }
  };

  return (
    <Layout>
      <div className="flex-1 flex gap-2 p-2 min-h-0 overflow-hidden">
        {/* Left Panel */}
        <div className="w-1/5 min-w-[150px] border border-cyan-500/5 bg-[#0a0e1a]/80 overflow-hidden flex flex-col flex-shrink-0 hide-on-mobile">
          <div className="flex-shrink-0 border-b border-cyan-500/5 px-3 py-1.5">
            <span className="text-[8px] text-cyan-400/30 font-mono tracking-widest uppercase">⚡ System</span>
          </div>
          <div className="flex-1 overflow-hidden">
            <Telemetry />
          </div>
        </div>

        {/* Center - Chat */}
        <div className="flex-1 border border-cyan-500/5 bg-[#0a0e1a]/80 overflow-hidden flex flex-col min-w-0">
          <div className="flex-shrink-0 border-b border-cyan-500/5 px-3 py-1.5 flex items-center justify-between">
            <span className="text-[8px] text-cyan-400/30 font-mono tracking-widest uppercase">💬 Terminal</span>
            <span className="text-[7px] text-cyan-400/20 font-mono">NVIDIA NIM</span>
          </div>
          <ChatPanel
            messages={messages}
            input={input}
            setInput={setInput}
            sendMessage={sendMessage}
            busy={busy}
            isListening={isListening}
            attachment={attachment}
            onClearAttachment={() => setAttachment(null)}
          />
        </div>

        {/* Right - Data */}
        <div className="w-1/5 min-w-[150px] border border-amber-500/5 bg-[#0a0e1a]/80 overflow-hidden flex flex-col flex-shrink-0 hide-on-mobile">
          <div className="flex-shrink-0 border-b border-amber-500/5 px-3 py-1.5">
            <span className="text-[8px] text-amber-400/30 font-mono tracking-widest uppercase">📊 Data</span>
          </div>
          <div className="flex-1 overflow-hidden">
            <DataPanel onAttach={setAttachment} />
          </div>
        </div>
      </div>
    </Layout>
  );
}